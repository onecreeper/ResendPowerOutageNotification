FROM python:3.9-slim

RUN pip install resend

WORKDIR /app

COPY ./app /app

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
