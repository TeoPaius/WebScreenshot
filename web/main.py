from selenium import webdriver
import pika
import sys
import json
import base64

def takeScreenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    # options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application"
    driver = webdriver.Chrome(
        'D:\\faculta an3\\detectify\\chromedriver_win32\\chromedriver.exe')  # Optional argument, if not specified will search path.

    driver.get(url)

    element = driver.find_element_by_tag_name('body')
    element_png = element.screenshot_as_png
    print("TOOK SCREENSHOT")

    driver.close()
    return element_png

def sendtoDb(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)


    message = {'name': 'test2.png', 'data': base64.encodebytes(data).decode('ascii')}
    channel.basic_publish(exchange='',
                          routing_key='task_queue',
                          body=json.dumps(message),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    print("SENT TO DB")
    connection.close()


screen = takeScreenshot("https://www.python.org/")

sendtoDb(screen)
