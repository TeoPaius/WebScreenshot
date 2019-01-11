from selenium import webdriver
import pika
import sys
import json
import base64
import uuid


class WebClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.readCallback, no_ack=True,
                                   queue=self.callback_queue)



    def processUrlName(self, url):
        return url.strip('\n').replace('/', '_').replace(':', '_').replace('.', '_').replace('-', '_') + '.png'

    def takeScreenshot(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--test-type")
        # options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application"
        driver = webdriver.Chrome(
            'D:\\faculta an3\\detectify\\chromedriver_win32\\chromedriver.exe')  # Optional argument, if not specified will search path.

        driver.get(url)

        element = driver.find_element_by_tag_name('body')
        element_png = element.screenshot_as_png
        print("[-SCREEN-] TOOK SCREENSHOT")

        driver.close()
        return element_png

    def sendtoDb(self, data, url):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        # channel.queue_declare(queue='task_queue', durable=True)
        name = self.processUrlName(url)
        print("[-SCREEN-] SENDING TO BD " + name)
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
        if self.corr_id == props.correlation_id:
            self.response = body.decode("ascii")

    def fetchFromDb(self, url):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='read_queue',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=self.processUrlName(url))
        while self.response is None:
            self.connection.process_data_events()
        return self.response


client = WebClient()

if len(sys.argv) == 2 :
    screen = client.takeScreenshot(sys.argv[1])
    client.sendtoDb(screen, sys.argv[1])

if sys.argv[1] == 'r':
    print("[-READ-] PERFORMING READ on : " + sys.argv[2])
    print("[-READ-] READ FROM BD FILE(S) : " + client.fetchFromDb(sys.argv[2]))

