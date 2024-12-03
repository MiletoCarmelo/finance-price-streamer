FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY price_streamer/ price_streamer/

CMD ["python", "-m", "price_streamer.main"]