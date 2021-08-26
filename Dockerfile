FROM almalinux:8

RUN mkdir -p /code && yum update -y && yum install python3-virtualenv -y
COPY requirements.txt /tmp/requirements.txt
RUN cd /code && virtualenv -p python3.6 env && source env/bin/activate \
    && pip3 install -r /tmp/requirements.txt && deactivate && rm -f /tmp/requirements.txt
COPY gitea_listener /code/gitea_listener
WORKDIR /code
