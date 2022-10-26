FROM python:3.11.0

ENV TZ="Europe/Berlin"

WORKDIR /usr/app
COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["./gunicorn.sh"]
