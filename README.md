# Real Time Object Detection and Communication

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