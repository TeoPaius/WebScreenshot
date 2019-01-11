import pika
import json
import base64
import os

basePath = "screenshots/"

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
channel.queue_declare(queue='read_queue', durable=True)
print(' [*] Waiting for screens. To exit press CTRL+C')


def saveImgtoDb(data):
    filename = json.loads(data)['name']
    content = base64.b64decode(json.loads(data)['data'])

    # filename = url.replace(['/', ':', '.'], '_') + ".png"
    with open(basePath + filename, "wb") as file:
        file.write(content)
    print("[-DB-] WROTE TO FILE " + filename)

def taskCallback(ch, method, properties, body):
    print("[-DB-] RECEIVED SCREEEN")

    saveImgtoDb(body)

    ch.basic_ack(delivery_tag = method.delivery_tag)
    print("[-DB-] DB acknowledged")

def findById(fileName):
    if fileName == '*.png':
        return '\n'.join([file for file in os.listdir('D:\\faculta an3\\detectify\\db\\screenshots')])[:-1]
    if fileName not in os.listdir('D:\\faculta an3\\detectify\\db\\screenshots'):
        return 'invalid file name'
    return fileName


def readCallback(ch, method, properties, body):
    name = body.decode("ascii")

    response = findById(name)

    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id= properties.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(taskCallback,
                      queue='task_queue')
channel.basic_consume(readCallback, queue='read_queue')

channel.start_consuming()