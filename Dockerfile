# We might switch to python:3-alpine, which would hopefully result in smaller image.
##FROM python:3-alpine
##RUN apk update && apk add \
##    # python3-tkinter
##    tk
##    # font-isas-misc
FROM python:3-slim

RUN apt update && apt install -y \
    python3-tk \
    \
    # Install one of the Chinese fonts from https://packages.debian.org/stable/fonts/
    fonts-arphic-ukai \
    \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

## Decides to keep this image as a stable tkinter+ChineseFont+dependency environment
##      rather than shipping the volatile main app inside this image
# COPY . /home
# WORKDIR /home
# ENTRYPOINT my_main_program

## Use the accompanied docker_run.sh to specify latest application at run-time.

# This is the default tkinter demo
CMD ["python", "-m", "tkinter"]

