# Goagent Dockerfile
#
# https://github.com/goagent/goagent/Dockerfile
#

# Pull base image.
FROM centos:latest

# ENV
ENV GAE_APPIDS=your_appid
ENV GAE_EMAIL=your_email
ENV GAE_PASSWORD=your_password
ENV USE_DOCKER=true

# Set locale
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Expose port
EXPOSE 8087 8086

# Define working directory
WORKDIR /root

# Download goagent and install dependencies
RUN \
  yum install -y python openssl-devel pyOpenSSL python-gevent python-crypto wget unzip && \
  mkdir -p /root/.pki/nssdb && \
  certutil -d /root/.pki/nssdb -N && \
  wget -O goagent.zip https://github.com/goagent/goagent/archive/3.0.zip && \
  unzip goagent.zip && \
  rm -f goagent.zip && \
  mv goagent-3.0 goagent

# Change working directory to goagent
WORKDIR goagent

# Upload goagent server part
RUN \
  python server/uploader.py && \
  sed -i.bak s/appid\ =\ goagent/appid\ =\ ${GAE_APPIDS}/g local/proxy.ini && \
  sed -i.bak s/ip\ =\ 127.0.0.1/ip\ =\ 0.0.0.0/g local/proxy.ini

# Start goagent
CMD python local/proxy.py
