import concurrent.futures
import sys
import time
import traceback

import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    PublishToTopicRequest,
    PublishToIoTCoreRequest,
    PublishMessage,
    BinaryMessage,
    UnauthorizedError,
    QOS
)


class mqttPublish():
    def __init__(self, timeout=10):
        self.timeout = timeout

    def publish_message(self, topic, payload, mode='edge'):
        try:
            ipc_client = awsiot.greengrasscoreipc.connect()
            qos = QOS.AT_LEAST_ONCE
            message = payload

            if(mode == 'edge'):
                request = PublishToTopicRequest()
                request.topic = topic
                publish_message = PublishMessage()
                publish_message.binary_message = BinaryMessage()
                publish_message.binary_message.message = bytes(message, "utf-8")
                request.publish_message = publish_message
                operation = ipc_client.new_publish_to_topic()
                
            elif(mode == 'cloud'):
                request = PublishToIoTCoreRequest()
                request.topic_name = topic
                request.payload = bytes(message, "utf-8")
                request.qos = qos
                operation = ipc_client.new_publish_to_iot_core()

            operation.activate(request)
            futureResponse = operation.get_response()  

            try:
                futureResponse.result(self.timeout)
                print('Successfully published to topic: ' + topic)
            except concurrent.futures.TimeoutError:
                print('Timeout occurred while publishing to topic: ' + topic, file=sys.stderr)
            except UnauthorizedError as e:
                print('Unauthorized error while publishing to topic: ' + topic, file=sys.stderr)
                raise e
            except Exception as e:
                print('Exception while publishing to topic: ' + topic, file=sys.stderr)
                raise e
            time.sleep(5)
        except InterruptedError:
            print('Publisher interrupted.')
        except Exception:
            print('Exception occurred when using IPC.', file=sys.stderr)
            traceback.print_exc()
            exit(1)


def main():

    publish = mqttPublish()

    # Keep the main thread alive, or the process will exit.
    try:  
        while True:
            publish.publish_message("python/test/topic", "\"message\": \"hello world!\"", "cloud")
            time.sleep(60)
    except InterruptedError:
        print('Process interrupted.')

if __name__ == "__main__":
    main()