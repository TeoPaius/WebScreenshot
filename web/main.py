# this is the main module of the service

from selenium import webdriver
import pika
import sys
import json
import base64
import uuid
import cv2
import numpy as np
import matplotlib.pyplot

class WebClient:
    # as much as i wanted to make this without retaining state, for this client i needed a class to store
    # i needed this to wait for the result of the read requests, but most certainly there should be a way
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True) # anynomous queue used for read responses to web client
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.readCallback, no_ack=True,
                                   queue=self.callback_queue)



    def processUrlName(self, url):
        # this eliminates the "harming" characters from the url to change it in an actual file name
        return url.strip('\n').replace('/', '_').replace(':', '_').replace('.', '_').replace('-', '_') + '.png'

    def takeScreenshot(self, url):
        # here i used selenium and a chrome driver to launch virtual pages for those urls
        # sadly it opens a new window for each url, but i have read that this problem could be solved used phantomJS
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--test-type")
        # options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application"
        driver = webdriver.Chrome(
            '../chromedriver_win32/chromedriver.exe')  # Optional argument, if not specified will search path.

        driver.get(url)

        # this may be a workarround but when i tried to get the screenshot of the window it got only the part that appeared on the screen
        # by getting the body i fixed this and it makes screenshot to the whole element
        # there may be better ways to do this though but this seemed ok to me
        element = driver.find_element_by_tag_name('body')
        element_png = element.screenshot_as_png
        print("[-SCREEN-] TOOK SCREENSHOT")

        driver.close()
        return element_png

    def sendtoDb(self, data, url):
        # here the client sends to the db the image toghether with its name using the task queue to be saved
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        name = self.processUrlName(url)
        print("[-SCREEN-] SENDING TO BD " + name)
        # cant json serialize byte arrays so i turn them to strings encoded in b64
        message = {'name': name, 'data': base64.encodebytes(data).decode('ascii')}
        channel.basic_publish(exchange='',
                              routing_key='task_queue',
                              body=json.dumps(message),
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # make message persistent
                              ))
        print("[-SCREEN-] SENT TO DB")
        connection.close()


    def readCallback(self, ch, method, props, body):
        # this is triggered when receiving a read response
        # sets the response field from the class and then the while block from fetchFromDb method will pass
        # this is the part i hate the most from my solution, i needed some way to block until i get a response
        # and so the fetch from db is not a pure function as it depends on external factors (that response)

        if self.corr_id == props.correlation_id:
            self.response = body.decode("ascii")

    def showImg(self, img):
        nparr = np.frombuffer(img, dtype=np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        cv2.imshow("test display", img)
        cv2.waitKey(-1)
        cv2.destroyAllWindows()

    def fetchFromDb(self, url):
        # sends the read request
        # response = {filename: string, img: bytearray as string}
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='read_queue',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=self.processUrlName(url))
        # here waits until it get a response from read and then sets the respons member of the class to be use
        while self.response is None:
            self.connection.process_data_events()

        json_response = json.loads(self.response)
        element_png = base64.b64decode(json_response['data'])
        self.showImg(element_png)

        return json_response["filename"]


client = WebClient()

if len(sys.argv) == 2 :
    screen = client.takeScreenshot(sys.argv[1])
    client.sendtoDb(screen, sys.argv[1])

if sys.argv[1] == 'r':
    print("[-READ-] PERFORMING READ on : " + sys.argv[2])
    print("[-READ-] READ FROM BD FILE(S) : " + client.fetchFromDb(sys.argv[2]))

