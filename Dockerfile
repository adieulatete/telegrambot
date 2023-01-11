FROM python:3.11

ENV TELEGRAM_API_TOKEN = "5766867317:AAGhhuGI1KoiT2BiCOkzmkse3v3fudsybIs"

WORKDIR /app
RUN pip install --upgrade pip aiogram
COPY *.py ./

ENTRYPOINT ["python", "main.py"]
