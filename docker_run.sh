# NOTE:
# Derived from https://stackoverflow.com/a/57040181
# It may also need a one-time `xhost +` to disable access control
docker run -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY \
    -v $PWD:/app -w /app \
    --rm \
    $(docker build -q - < Dockerfile) \
    python grin.py

