FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y gcc
RUN apt-get install -y curl
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0
RUN apt-get install -y libsox-dev

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy only the necessary files and directories
COPY . .

EXPOSE 8000
ENV TF_ENABLE_ONEDNN_OPTS=0

CMD ["python", "main.py"]