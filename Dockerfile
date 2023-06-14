FROM ubuntu:focal

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y cmake && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    pip3 install numpy && \
    pip3 install opencv-python && \
    apt-get update -y && \
    apt-get install -y ffmpeg libsm6 libxext6 && \
    pip3 install imutils && \
    pip3 install mediapipe && \
    pip3 install protobuf==3.20.3

# run selected files
RUN mkdir /pyfiles
COPY ./FingerCounter.py /pyfiles/FingerCounter.py
COPY ./HandTrackingModule.py /pyfiles/HandTrackingModule.py

EXPOSE 80

CMD ["python3","-u", "/pyfiles/FingerCounter.py"]
