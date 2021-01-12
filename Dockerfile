# Currently use python:2-slim as base, because it has the needed tix-dev package.
# Eventually, we will remove the tix dependency,
# and then switch to python:2-alpine, and do "apk add python2-tkinter"
FROM python:2-slim

RUN apt update && apt install -y \
    python-tk \
    tix-dev \
    \
    # Install one of the Chinese fonts from https://packages.debian.org/stable/fonts/
    fonts-arphic-ukai \
    \
    && rm -rf /var/lib/apt/lists/*

## Currently decides to keep this image as a stable Tkinter+Tix+ChineseFont environment
##      rather than shipping the volatile main app inside this image
# COPY . /home
# WORKDIR /home
# ENTRYPOINT my_main_program

## Use the accompanied docker_run.sh to specify latest application at run-time.

# This is the default Tkinter demo
CMD ["python", "-m", "Tkinter"]

