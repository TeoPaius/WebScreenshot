import pika
import time
import json
import base64

basePath = "screenshots/"

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for screens. To exit press CTRL+C')


def saveImgtoDb(data):
    filename = json.loads(data)['name']
    content = base64.b64decode(json.loads(data)['data'])

    # filename = url.replace(['/', ':', '.'], '_') + ".png"
    with open(basePath + filename, "wb") as file:
        file.write(content)

def callback(ch, method, properties, body):
    print("RECEIVED SCREEEN")

    saveImgtoDb(body)

    print("WROTE TO FILE")
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='task_queue')

channel.start_consuming()