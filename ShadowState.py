import concurrent.futures
import sys
import json
import traceback
import time
import traceback

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    UnauthorizedError,
    QOS,
    PublishToIoTCoreRequest,
    GetThingShadowRequest,
    UpdateThingShadowRequest
)

state = ''
TIMEOUT = 10

#Handler for subscription callback
class SubHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:

        global state
        print("Shadow Event Triggered!!")
        
        try:
            
            # grab the message and load it into our state variable
            message_string = str(event.binary_message.message, "utf-8")
            state = message_string
            print('Shadow state subscriber has updated global state = ' + state)

            # Load message and check values
            #jsonmsg = json.loads(message_string)

            #if jsonmsg['state']['desired']['msg_frequency']:
            #    print("The new msg frequency is:" + str(jsonmsg['state']['desired']['msg_frequency']))
                
            #else:
            #    print("No msg frequency")
                
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        pass



class shadowState():
    def __init__(self, shadowMode='classic', shadowName='', thingName='NathansDevJetson', topic='$aws/things/NathansDevJetson/shadow/update/accepted'):
        self.shadowMode = shadowMode
        self.shadowName = shadowName
        self.thingName = thingName
        self.topic = topic

    def subscribe_to_shadow_update(self):
        try:
            ipc_client = awsiot.greengrasscoreipc.connect()
                
            #subscribe to topic
            request = SubscribeToTopicRequest()
            request.topic = self.topic 
            handler = SubHandler()
            operation = ipc_client.new_subscribe_to_topic(handler) 
            future = operation.activate(request)
            try:
                future.result(TIMEOUT)
                print('Successfully subscribed to topic: ' + self.topic)
            except concurrent.futures.TimeoutError as e:
                print('Timeout occurred while subscribing to topic: ' + self.topic, file=sys.stderr)
                raise e
            except UnauthorizedError as e:
                print('Unauthorized error while subscribing to topic: ' + self.topic, file=sys.stderr)
                raise e
            except Exception as e:
                print('Exception while subscribing to topic: ' + self.topic, file=sys.stderr)
                raise e

        except Exception:
            print('Exception occurred when using IPC.', file=sys.stderr)
            traceback.print_exc()
            exit(1)

    # Get the shadow from the local IPC
    def get_thing_shadow_request(self):
        try:
            # set up IPC client to connect to the IPC server
            ipc_client = awsiot.greengrasscoreipc.connect()
                    
            # create the GetThingShadow request
            get_thing_shadow_request = GetThingShadowRequest()
            get_thing_shadow_request.thing_name = self.thingName
            # set as empty string to request classic shadow
            get_thing_shadow_request.shadow_name = ""
            
            # retrieve the GetThingShadow response after sending the request to the IPC server
            op = ipc_client.new_get_thing_shadow()
            op.activate(get_thing_shadow_request)
            fut = op.get_response()
            
            result = fut.result(TIMEOUT)

            # grab the message and load it into our state variable
            state = result.payload
            print('Get thingShadow request function has updated global state = ' + state)

            # convert string to json object
            #jsonmsg = json.loads(result.payload)

            return result.payload
            
        except Exception as e:
            print("Error get shadow", type(e), e)
            # except ResourceNotFoundError | UnauthorizedError | ServiceError


    # Set the local shadow using the IPC
    def update_thing_shadow_request(self, payload):
        try:
            # set up IPC client to connect to the IPC server
            ipc_client = awsiot.greengrasscoreipc.connect()
                    
            # create the UpdateThingShadow request
            update_thing_shadow_request = UpdateThingShadowRequest()
            update_thing_shadow_request.thing_name = self.thingName
            # send empty string for classic shadow
            update_thing_shadow_request.shadow_name = ""
            update_thing_shadow_request.payload = payload
                            
            # retrieve the UpdateThingShadow response after sending the request to the IPC server
            op = ipc_client.new_update_thing_shadow()
            op.activate(update_thing_shadow_request)
            fut = op.get_response()
            
            result = fut.result(TIMEOUT)
            return result.payload
            
        except Exception as e:
            print("Error update shadow", type(e), e)
            # except ConflictError | UnauthorizedError | ServiceError





def main():
    print('declaring instance of shadowState')
    state = shadowState()
    print('calling subscribe function')
    state.subscribe_to_shadow_update()
        
    # Keep the main thread alive, or the process will exit.
    try:
        print('Keeping subscription alive. ')
        while True:
            time.sleep(10)
    except InterruptedError:
        print('Subscribe interrupted.')
    
if __name__ == "__main__":
    main()