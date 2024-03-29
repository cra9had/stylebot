FROM python:3.11-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache -r /app/requirements.txt
COPY bot /app/bot
CMD ["python", "-m", "bot"]