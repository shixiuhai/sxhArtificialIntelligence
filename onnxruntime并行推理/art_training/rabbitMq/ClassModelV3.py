# RabbitMq生产者
import sys
sys.path.append('..') 
from retry import retry
import pika
from log.ClassModel import Log
import json
# 实例化一个log对象
log=Log(__name__, 'rabbitMqV3.log').Logger
class RabbitMqProducer:
    def __init__(self, user, pwd, host, port,virtual_host,exchange):
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
        # 设置消费分发模式，以及交换机的持久化
        self.channel.exchange_declare(exchange = self.exchange,durable = True, exchange_type='direct')
        # 监听开启
        # Thread(target=self.restartProducer,args=()).start()
        # log.info("生产者监听方法开启成功")
    
    def send(self,queueName:str,routingKey:str, body:dict):
        # 这里不需要声明持久化，前面交换机已经声明过了
        # self.channel.queue_declare(queue=queueName)
        # if self.connection.is_open and self.channel.is_open: # 这个判断没有必要做，会增加开销
        try:
            ## 设置需要发送的消息
            body = json.dumps(body,ensure_ascii=False)
            # 推送消息delivery_mode = 2表示该消息是持久化消息
            self.channel.basic_publish(exchange=self.exchange, routing_key=routingKey, body=body,properties=pika.BasicProperties(delivery_mode = 2))    
        # 发送消息出现异常
        except Exception as error:
            # tcp连接断开或者信道断开
            if self.connection.is_closed or self.channel.is_closed:
                # 先关闭可能存在的rabbitMq相关连接
                self.close()
                self.__init__(self.user, self.pwd, self.host, self.port,self.virtual_host,self.exchange)
                log.info("触发了生产者重新初始化,原因是生产者长时间没有发送信息与服务端建立的连接中断或异常中断")
                # 调用回调的方法重新发送消息
                try:
                    # 重新发送消息
                    self.channel.basic_publish(exchange=self.exchange, routing_key=routingKey, body=body,properties=pika.BasicProperties(delivery_mode = 2))    
                    # self.send(queueName,routingKey, body),这里不可以使用回调方法，不然body会被dumps两层
                    log.info("消息重发成功")
                except:
                    log.error("消息重发失败")
            # 触发了其他异常
            else:
                # 先关闭rabbitMq相关连接
                self.close()
                self.__init__(self.user, self.pwd, self.host, self.port,self.virtual_host,self.exchange)
                log.info("生产者发送消息出现其他异常,异常错误是%s"%error)
                # 调用回调的方法重新发送消息
                try:
                    # 重新发送消息
                    self.channel.basic_publish(exchange=self.exchange, routing_key=routingKey, body=body,properties=pika.BasicProperties(delivery_mode = 2))
                except:
                    log.error("消息重发失败")

    # 定义一个关闭已存在信道或者连接的方法
    def close(self):
        if self.connection.is_open:
            self.connection.close()
        if self.channel.is_open:
            self.channel.close()
    

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