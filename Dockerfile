FROM python:3.11

ENV TELEGRAM_API_TOKEN = ""

WORKDIR /app
RUN pip install --upgrade pip aiogram
COPY *.py ./

ENTRYPOINT ["python", "main.py"]
