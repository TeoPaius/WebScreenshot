from selenium import webdriver
import pika
import sys
import json
import base64
import re


def processUrlName(url):
    return url.strip('\n').replace('/', '_').replace(':', '_').replace('.', '_').replace('-', '_') + '.png'

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

def sendtoDb(data, url):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    # channel.queue_declare(queue='task_queue', durable=True)
    name = processUrlName(url)
    print("SENDING TO BD " + name)
    message = {'name': name, 'data': base64.encodebytes(data).decode('ascii')}
    channel.basic_publish(exchange='',
                          routing_key='task_queue',
                          body=json.dumps(message),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    print("SENT TO DB")
    connection.close()


if len(sys.argv) == 2 :
    screen = takeScreenshot(sys.argv[1])
    sendtoDb(screen, sys.argv[1])

if sys.argv[1] == 'r':
    print("PERFORMING READ on : " + sys.argv[2])

