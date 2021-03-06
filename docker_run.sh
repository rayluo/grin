# Usage: docker_run [Dockerfile.alpine | Dockerfile.slim]
DOCKERFILE=${1-Dockerfile.alpine}
echo "Building with $DOCKERFILE"

# See also https://stackoverflow.com/questions/45141402/build-and-run-dockerfile-with-one-command#comment116261404_51314059
IMAGE_NAME=tk_cn_sg

# Build the image with context because we'd need the ./requirements.txt
docker build -t $IMAGE_NAME -f $DOCKERFILE .

# Permits the root user on the local machine to connect to X windows display.
# (It feels more secure than "xhost +" which disables all access control.)
xhost local:root

# NOTE: https://stackoverflow.com/a/65756710/728675
docker run -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY \
    -v $PWD:/app -w /app \
    --user $(id -u):$(id -g) \
    --rm \
    $IMAGE_NAME \
    python desktop.py

