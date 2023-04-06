from  rabbitMq.ClassModelV4 import RabbitMqProducer,RabbitMqConsumer
from settings.config import *
import time
for i in range(10000):
    RabbitMqProducer(user=mqUser, pwd=mqPassword,
                     host=mqHost, port=mqConnectPort,
                     virtual_host=mqVirtualHost,
                     exchange=mqExchange).send(queueName=detectPhotoQueueName,routingKey=detectPhotoQueueKey,body={
                         'id':'1',
                         "checkType":"head",
                         "path":"rtsp://admin:123456@122.227.52.190:55554/cam/realmonitor?channel=5&subtype=0"
                     })
    RabbitMqProducer(user=mqUser, pwd=mqPassword,
                     host=mqHost, port=mqConnectPort,
                     virtual_host=mqVirtualHost,
                     exchange=mqExchange).send(queueName=detectPhotoQueueName,routingKey=detectPhotoQueueKey,body={
                         'id':'2',
                         "checkType":"smoke",
                         "path":"rtsp://122.226.50.38:55550/stream2"
                     })
    
    RabbitMqProducer(user=mqUser, pwd=mqPassword,
                     host=mqHost, port=mqConnectPort,
                     virtual_host=mqVirtualHost,
                     exchange=mqExchange).send(queueName=detectPhotoQueueName,routingKey=detectPhotoQueueKey,body={
                         'id':'2',
                         "checkType":"smoke",
                         "path":"rtsp://122.226.50.38:55550/stream2"
                     })
                     
    RabbitMqProducer(user=mqUser, pwd=mqPassword,
                     host=mqHost, port=mqConnectPort,
                     virtual_host=mqVirtualHost,
                     exchange=mqExchange).send(queueName=detectPhotoQueueName,routingKey=detectPhotoQueueKey,body={
                         'id':'3',
                         "checkType":"head",
                         "path":"rtsp://122.226.50.38:55550/stream2"
                     })
    time.sleep(0.2)