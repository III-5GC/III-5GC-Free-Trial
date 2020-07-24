FROM ubuntu:18.04
# VOLUME /tmp
# MAINTAINER Chihshin 

#Essential Tool
RUN apt-get update -y && \
 apt-get -f install -y \
 sudo \
 git \
 gawk \
 tmux \
 openssh-server \
 locales \
 net-tools \
 nginx \
 psmisc \
 vim && \
 locale-gen en_US.UTF-8
# snmp snmpd snmp-mibs-downloader 

#init LANG
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8

#init ssh server run environment
RUN mkdir /var/run/sshd
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

#init nginx environment
COPY ./oam/sites-available/default /etc/nginx/sites-available/
COPY ./oam/index.html /var/www/.
RUN nginx -c /etc/nginx/nginx.conf

#Required Lib
RUN apt-get update -y && \
 apt-get -f install -y \
 zsh \
 python3-pip && \
 pip3 install flask libconf

#add user iii
RUN useradd -ms /usr/bin/zsh iii
RUN sudo adduser iii sudo
RUN echo 'iii:iii123@' | sudo chpasswd
# no passwd for iii
RUN echo 'iii ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers 

# boy, dev, copy my zsh to home of iii, (COPY can chown, or owner is root)
COPY --chown=iii ./oh-my-zsh                     /home/iii/.oh-my-zsh
COPY --chown=iii ./zshrc                         /home/iii/.zshrc

#switch path to /home/iii
USER iii
WORKDIR /home/iii
