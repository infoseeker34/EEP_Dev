import cv2
import imutils
from imutils.video import VideoStream
from imutils.video import FileVideoStream
import HandTrackingModule as htm
import time
import StateManager as sm


rtsp_url = 'rtsp://admin1:password@192.168.1.48:554/h264Preview_01_main'

detector = htm.handDetector()
tipIds = [4, 8, 12, 16, 20]
pTime = 0
print('declaring instance of shadowState')
config = sm.shadowState()
config.get_thing_shadow_request()
config.subscribe_to_shadow_update()
print('shadowState initialized')
rtsp_url = ""


while True:
    
    rtsp_url = config.get_currentstate()

    if (rtsp_url):

        #if(rtsp_url == 'demo'):
        video_stream = FileVideoStream('/home/ubuntu/EEP_Dev/fingerCounting.MOV').start()
        #else:
        #    video_stream = VideoStream(rtsp_url).start()

        while config.get_currentstate() == rtsp_url:      

            frame = video_stream.read()
            if frame is None:
                continue

            frame = imutils.resize(frame,width=1200)

            img = detector.findHands(frame)
            lmList = detector.findPosition(img, draw=False)
                    
            if len(lmList) != 0:
                fingers = []
                # Thumb
                if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
                # 4 Fingers
                for id in range(1, 5):
                    if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                # print(fingers)
                totalFingers = fingers.count(1)
                print(totalFingers)
        
                cv2.rectangle(img, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, str(totalFingers), (45, 375), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 25)
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
            #cv2.imshow("show camera", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
print('RTSP URL has not yet been received!')
# sleep for 10 seconds and try again
time.sleep(10)

cv2.destroyAllWindows()
video_stream.stop()