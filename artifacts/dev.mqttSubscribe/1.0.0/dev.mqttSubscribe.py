import concurrent.futures
import sys
import time
import traceback

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    UnauthorizedError,
    QOS,
    PublishToIoTCoreRequest
)

topic = "test/topic/python"
qos = QOS.AT_LEAST_ONCE
TIMEOUT = 10

                    
class StreamHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            message = str(event.binary_message.message, "utf-8")
            print("Received new message: " + message)

        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        print("Received a stream error.", file=sys.stderr)
        traceback.print_exc()
        return False  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        print('Subscribe to topic stream closed.')


class mqttSubscribe():
    def __init__(self, timeout=10):
        self.timeout = timeout

    def subscribe_to_topic(self, topic, mode='edge'):
        try:
            ipc_client = awsiot.greengrasscoreipc.connect()

            request = SubscribeToTopicRequest()
            request.topic = topic
            handler = StreamHandler()
            operation = ipc_client.new_subscribe_to_topic(handler)
            future = operation.activate(request)
            
            try:
                future.result(TIMEOUT)
                print('Successfully subscribed to topic: ' + topic)
            except concurrent.futures.TimeoutError as e:
                print('Timeout occurred while subscribing to topic: ' + topic, file=sys.stderr)
                raise e
            except UnauthorizedError as e:
                print('Unauthorized error while subscribing to topic: ' + topic, file=sys.stderr)
                raise e
            except Exception as e:
                print('Exception while subscribing to topic: ' + topic, file=sys.stderr)
                raise e
        except InterruptedError:
            print('Publisher interrupted.')
        except Exception:
            print('Exception occurred when using IPC.', file=sys.stderr)
            traceback.print_exc()
            exit(1)

def main():

    subscribe = mqttSubscribe()

    # Keep the main thread alive, or the process will exit.
    try:  
        while True:
            subscribe.subscribe_to_topic("python/test/topic")
            time.sleep(60)
    except InterruptedError:
        print('Process interrupted.')

if __name__ == "__main__":
    main()