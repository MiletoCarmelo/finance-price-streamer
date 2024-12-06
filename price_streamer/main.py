# price-streamer/main.py
import argparse
import logging
from .sources.yahoo_finance import YahooFinanceSource
from .streamer import PriceStreamer
import uvicorn
from .api import app
import os
import asyncio
from fastapi import FastAPI
from threading import Thread

app = FastAPI()

@app.get("/health/live")
async def liveness():
    return {"status": "ok"}

@app.get("/health/ready") 
async def readiness():
    return {"status": "ok"}

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_env_or_default(key: str, default: str) -> str:
    return os.getenv(key, default)

def main():
    parser = argparse.ArgumentParser(description='Finance Price Streamer')
    parser.add_argument('--api', action='store_true', help='Lancer en mode API')
    parser.add_argument('--source', type=str, default='yahoo', choices=['yahoo'])
    parser.add_argument('--symbol', type=str)
    parser.add_argument('--days', type=int)
    parser.add_argument('--speed', type=float)
    parser.add_argument(
        '--kafka-servers',
        type=str,
        default=os.getenv('KAFKA_SERVERS', 'localhost:9092'),
        help='Liste des serveurs Kafka (séparés par des virgules)'
    )
    parser.add_argument('--kafka-topic', type=str, default='finance-price-stream')

    args = parser.parse_args()

    # Démarrer le serveur HTTP dans un thread séparé seulement si --api n'est pas utilisé
    if not args.api:
        server_thread = Thread(target=run_server, daemon=True)
        server_thread.start()

    # Si --api est True, on démarre uniquement le serveur HTTP
    if args.api:
        uvicorn.run(app, host="0.0.0.0", port=8000)
        return

    # Utilisation des variables d'environnement ou des arguments
    symbol = args.symbol or get_env_or_default('DEFAULT_SYMBOL', 'JPY')
    days = args.days or int(get_env_or_default('DEFAULT_DAYS', '3'))
    speed = args.speed or float(get_env_or_default('DEFAULT_SPEED', '1.0'))
    kafka_servers = args.kafka_servers or get_env_or_default('KAFKA_SERVERS', 'localhost:9092')

    kafka_config = {
        'bootstrap_servers': kafka_servers.split(',')
    }

    try:
        streamer = PriceStreamer(
            data_source=YahooFinanceSource(),
            kafka_config=kafka_config
        )

        print(f"Using Kafka config: {kafka_config}")  # Pour le debug

        streamer.stream(
            symbol=symbol,
            lookback_days=days,
            replay_speed=speed,
            topic=args.kafka_topic
        )
    except KeyboardInterrupt:
        logger.info("Arrêt du streaming")
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        raise

if __name__ == "__main__":
    main()