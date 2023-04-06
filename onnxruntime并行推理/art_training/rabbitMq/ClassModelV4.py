# RabbitMq生产者,多信道模式解决多线程不安全因素
# 该版本不是V3的升级版本！！！
# V4 版本适合多个线程使用生产者，缺点效率低
# 建议方法通过队列实现单例生产者消息发送
import sys
sys.path.append('..') 
from retry import retry
import pika
from log.ClassModel import Log
import json
# 实例化一个log对象
log=Log(__name__, 'rabbitMqV4.log').Logger
class RabbitMqProducer:
    def __init__(self, user, pwd, host, port,virtual_host,exchange):
        self.user = user
        self.pwd = pwd
        self.host=host
        self.port=port
        self.virtual_host=virtual_host
        self.exchange=exchange
        
    def send(self,queueName:str,routingKey:str, body:dict):
        try:
            ## 设置需要发送的消息
            body = json.dumps(body,ensure_ascii=False)
            
            # 设置rabbitmq用户名和密码相关
            credentials = pika.PlainCredentials(self.user, self.pwd)  # mq用户名和密码
            # 建立连接对象
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.virtual_host, credentials=credentials)
            )
            # 建立信道连接
            channel=connection.channel()
            # 设置消费分发模式，以及交换机的持久化
            channel.exchange_declare(exchange = self.exchange,durable = True, exchange_type='direct')
            # 推送消息delivery_mode = 2表示该消息是持久化消息
            channel.basic_publish(exchange=self.exchange, routing_key=routingKey, body=body,properties=pika.BasicProperties(delivery_mode = 2))    
            # 发送完成消息后关闭信道和连接
            channel.close()
            connection.close()
            
        # 发送消息出现异常
        except Exception as error:
            log.info("发送消息失败，准备重发消息")
            # 调用回调的方法重新发送消息
            try:
                # 重新发送消息
                # 设置rabbitmq用户名和密码相关
                credentials = pika.PlainCredentials(self.user, self.pwd)  # mq用户名和密码
                # 建立连接对象
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.virtual_host, credentials=credentials)
                )
                # 建立信道连接
                channel=connection.channel()
                # 设置消费分发模式，以及交换机的持久化
                channel.exchange_declare(exchange = self.exchange,durable = True, exchange_type='direct')
                # 推送消息delivery_mode = 2表示该消息是持久化消息
                channel.basic_publish(exchange=self.exchange, routing_key=routingKey, body=body,properties=pika.BasicProperties(delivery_mode = 2))    
                # 发送完成消息后关闭信道和连接
                channel.close()
                connection.close()
                # self.send(queueName,routingKey, body),这里不可以使用回调方法，不然body会被dumps两层
                log.info("消息重发成功")
            except:
                # log.error("消息重发失败,没有发送的消息是%s"%(body))
                log.error("消息重发失败")
       

 

# RabbitMq消费者

class RabbitMqConsumer:
    @retry(delay=5)
    def __init__(self, user, pwd, host, port,virtual_host,exchange,prefetch_count=50):
        self.user = user
        self.pwd = pwd
        self.host=host
        self.port=port
        self.virtual_host=virtual_host
        self.exchange=exchange
        # 设置rabbitmq用户名和密码相关
        self.credentials = pika.PlainCredentials(self.user, self.pwd)  # mq用户名和密码
        # 建立连接对象
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.virtual_host, credentials=self.credentials)
        )
        # 建立信道连接
        self.channel=self.connection.channel()
        # 设置消费分发模式和交换机持久化
        self.channel.exchange_declare(exchange = self.exchange,durable = True, exchange_type='direct')
        # 设置最多一次性接收多少条消息缓冲
        self.channel.basic_qos(prefetch_count=prefetch_count)
       
    # 消费者开始接收消息
    @retry(delay=5)
    def receive(self, queueName,routingKey,fun):
        # receive开启接收前，先判断一下连接或者信道是否存在
        if self.connection.is_closed or self.channel.is_closed:
            # 先关闭可能存在的rabbitMq相关连接
            self.close()
            self.__init__(self.user, self.pwd, self.host, self.port,self.virtual_host,self.exchange)
            log.info("触发了消费者重新初始化,原因是消费者和服务器因为不知名原因断开了连接")
        # 队列和key绑定，这里的因为在服务器上手动绑定了队列，所以不是必须的
        # self.channel.queue_bind(exchange = self.exchange,queue=queueName,routing_key=routingKey)
        # 指明需要消费的队列是哪个
        self.channel.basic_consume(queueName, fun, auto_ack=False)
        try:
            # 开启消息接收
            self.startConsumer()
        except pika.exceptions.ConnectionClosedByBroker:
            pass
        
    def startConsumer(self):
        # 开始阻塞消费
        self.channel.start_consuming()
    # 定义一个关闭方法
    def close(self):
        if self.connection.is_open:
            self.connection.close()
        if self.channel.is_open:
            self.channel.close()