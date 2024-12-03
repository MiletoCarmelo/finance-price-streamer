FROM python:3.9-slim

# Installation des outils de compilation nécessaires
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        python3-dev \
        pkg-config \
        && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY price_streamer/ price_streamer/

RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "price_streamer"]