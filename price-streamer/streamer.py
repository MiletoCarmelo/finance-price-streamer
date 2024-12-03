# price_streamer/streamer.py
from kafka import KafkaProducer
import json
import time
import logging
from typing import Dict, Any
from .sources.base import DataSourceBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceStreamer:
    def __init__(self, data_source: DataSourceBase, kafka_config: Dict[str, Any]):
        self.data_source = data_source
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_config['bootstrap_servers'],
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8')
        )
        self.stop_streaming = False

    def stream(self, symbol: str, lookback_days: int, replay_speed: float = 1.0):
        """Stream les données historiques"""
        try:
            self.stop_streaming = False
            data = self.data_source.fetch_historical_data(symbol, lookback_days)
            
            logger.info(f"Starting stream for {symbol}")
            
            for timestamp, row in data.iterrows():
                if self.stop_streaming:
                    logger.info("Stopping stream on request")
                    break
                    
                message = {
                    'symbol': symbol,
                    'source': self.data_source.get_source_name(),
                    'timestamp': str(timestamp),
                    'data': {
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': float(row.get('Volume', 0))
                    }
                }
                
                self.producer.send('finance-price-stream', message)
                logger.info(f"Streamed: {symbol} - Close: {message['data']['close']}")
                
                time.sleep(60 / replay_speed)
                
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            raise