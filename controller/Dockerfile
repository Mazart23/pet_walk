FROM python:3.12-slim

WORKDIR /redirecter

RUN apt-get update && \
    apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    build-essential \
    python3-dev \
    pkg-config \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

COPY . .

CMD ["python3", "app.py"]