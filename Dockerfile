FROM ubuntu:16.04

#MAINTANER Your Name "youremail@domain.tld"

ENV MAIL_USERNAME=yourmail@test.com
ENV MAIL_PASSWORD=testpass
ENV SECRET_KEY=SuperRandomStringToBeUsedForEncryption

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev
RUN apt-get install -y ruby-dev
RUN gem install foreman
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt


RUN apt-get install -y redis-server
WORKDIR /app
RUN apt-get install -y build-essential libpq-dev
RUN pip3 install -r requirements.txt
ENV PYTHONIOENCODING=UTF-8
RUN pip3 install sqlalchemy_utils flask_dance flask_caching python-gitlab
COPY . /app
RUN python3 manage.py recreate_db && python3 manage.py setup_dev && python3 manage.py add_fake_data

CMD ["foreman", "start" ,"-f", "Local"]

