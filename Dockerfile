FROM debian:latest

MAINTAINER Yang "ygz012@163.com"

ADD sources.list /etc/apt
RUN apt-get update
RUN apt-get install -y vim git-core wget unzip subversion build-essential linux-headers-$(uname -r) libncurses5-dev uuid-dev libjansson-dev libxml2-dev sqlite3 libsqlite3-dev lua5.1 liblua5.1-dev

ADD .vimrc /root
ADD .bashrc /root
RUN apt-get upgrade
WORKDIR /root
