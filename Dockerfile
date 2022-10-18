FROM python:3.9.8-slim-buster

ENV TZ="Europe/Berlin"

WORKDIR /usr/app
COPY . ./

RUN pip install -r requirements.txt

CMD ["python","helo-server.py"]
