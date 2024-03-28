FROM ubuntu:latest

RUN apt-get update -yyqq &&\
    apt-get install -yyqq wget python3-pip &&\
    pip install "watchdog[watchmedo]"
