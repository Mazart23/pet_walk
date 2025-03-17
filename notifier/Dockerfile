FROM python:3.12-slim

WORKDIR /notifier

RUN apt-get update && \
    apt-get install -y gcc  && \
    apt-get -q -y install --no-install-recommends \
    build-essential \
    python3-dev

RUN python -m pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5003

COPY . .

CMD ["python3", "app.py"]