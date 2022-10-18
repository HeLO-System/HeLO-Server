FROM python:3.9.8-slim-buster

ENV TZ="Europe/Berlin"

WORKDIR /usr/app
COPY . ./

RUN pip install -r requirements.txt

CMD ["gunicorn helo-server:app -b 0.0.0.0:5000"]
