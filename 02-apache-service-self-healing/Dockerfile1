FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir "boto3>=1.35,<2" "docker>=7,<8"

COPY agenttask2.py .

CMD ["python", "-u", "agenttask2.py"]
