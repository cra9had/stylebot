FROM python:3.12-slim

# Create app directory
WORKDIR /app

# Install app dependencies
COPY ./requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

# Bundle app source
COPY ./ /app

CMD ["python", "./main.py"]