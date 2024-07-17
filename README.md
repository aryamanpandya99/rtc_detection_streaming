# Real Time Object Detection and Communication

This project implements real-time object detection and communication using WebRTC. The system consists of a client and a server that communicate with each other to perform object detection on video frames captured from a webcam. The client then asynchronously processes the video frames using a pre-trained YOLOv5 model and displays the video of the frames with and without the bounding boxes.


## Project Structure

The project is organized as follows:

- `client.py`: Client-side code for real-time object detection and WebRTC communication.

- `server.py`: Server-side code for processing detected coordinates from the client.

- `rtc_signal_handlers.py`: Signaling handlers for WebRTC communication.

- `requirements.txt`: Project dependencies.

- `Dockerfile_client`: Dockerfile for the client-side image.

- `Dockerfile_server`: Dockerfile for the server-side image.


## Run using python 
```sh
python server.py --signaling tcp-socket
```
And in another terminal on the same machine:

```sh
python client.py --signaling tcp-socket
```

### Building Docker Images

To build the Docker images for both server and client, run the following commands in the project directory:

```sh
docker build -f Dockerfile_server -t webcam_server .
docker build -f Dockerfile_client -t webcam_client .
```