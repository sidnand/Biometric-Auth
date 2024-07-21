FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update -q && \
    apt-get install -yq \
    build-essential \
    gcc \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsox-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000
ENV TF_ENABLE_ONEDNN_OPTS=0

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]