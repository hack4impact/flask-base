FROM python:3.8-alpine


# Packages required for psycopg2
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

#MAINTANER Your Name "youremail@domain.tld"
ENV MAIL_USERNAME=yourmail@test.com
ENV MAIL_PASSWORD=testpass
ENV SECRET_KEY=SuperRandomStringToBeUsedForEncryption
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip3 install -r requirements.txt 
ENV PYTHONIOENCODING=UTF-8
RUN pip3 install sqlalchemy_utils flask_dance flask_caching python-gitlab

COPY . /app

ENTRYPOINT ["python3", "-u" ,"manage.py", "run_worker"]

