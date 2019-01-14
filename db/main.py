# this module acts like a database server
# it gets messages using rabbitmq for saving a certain screenshot or retreiving the name/bytes of an image
# it uses 2 queues:   one for saving the image( as array of bytes)
#                     one for handling read requests from the main client

import pika
import json
import base64
import os

basePath = "screenshots/"

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
channel.queue_declare(queue='read_queue', durable=True)
print('[-DB-] Waiting for screens. To exit press CTRL+C')


def saveImgtoDb(data):
    # data is of tipe {url: string, img: bytearray}

    # the main reason i used b64 encoding is that  arrays of bytes are not serializable in the json
    # so  i needed something to turn them in strings and back
    filename = json.loads(data)['name']
    content = base64.b64decode(json.loads(data)['data'])

    with open(basePath + filename, "wb") as file:
        file.write(content)
    print("[-DB-] WROTE TO FILE " + filename)

def taskCallback(ch, method, properties, body):
    # callback used when this layer gets an image
    print("[-DB-] RECEIVED SCREEEN")

    saveImgtoDb(body)

    ch.basic_ack(delivery_tag = method.delivery_tag)
    print("[-DB-] DB acknowledged")

def findById(fileName):
    # this part can be adapted according to what we need from the db
    # now i returned only the modified name of the chosen file or all files if they exist
    if fileName == '*.png':
        return '\n'.join([file for file in os.listdir('..\\db\\screenshots')])[:-1], b'0'
    if fileName not in os.listdir('..\\db\\screenshots'):
        return 'invalid file name', b'0'
    with open(basePath + fileName, "rb") as file:
        data = file.read()
    return fileName,data


def readCallback(ch, method, properties, body):
    # callback used when receiving read request
    name = body.decode("ascii")
    result = findById(name)
    response = {"filename": result[0], "data": base64.encodebytes(result[1]).decode('ascii')}
    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id= properties.correlation_id),
                     body=json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)



# this is an idependent module (well i tried to make all of them to be as independent as possible)
# to be able to easily replace parts
channel.basic_qos(prefetch_count=1)
channel.basic_consume(taskCallback,
                      queue='task_queue')
channel.basic_consume(readCallback, queue='read_queue')
channel.start_consuming()