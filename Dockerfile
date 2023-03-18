FROM ubuntu:focal

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y cmake && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    #pip3 install numpy && \
    pip3 install awsiotsdk 

# run selected files
RUN mkdir /pyfiles
COPY ./dummy_sensor.py /pyfiles/dummy_sensor.py
COPY ./example_publisher.py /pyfiles/example_publisher.py

EXPOSE 80

CMD ["python3","-u", "/pyfiles/example_publisher.py"]
