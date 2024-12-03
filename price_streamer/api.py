# price_streamer/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import threading
import logging
from .streamer import PriceStreamer
from .sources.yahoo_finance import YahooFinanceSource
import os

app = FastAPI()
logger = logging.getLogger(__name__)

class StreamConfig(BaseModel):
    symbol: str
    days: int = 3
    speed: float = 1.0

class StreamerState:
    def __init__(self):
        self.current_stream = None
        self.stream_thread = None
        self.config = None
        self.kafka_config = {
            'bootstrap_servers': os.getenv('KAFKA_SERVERS', 'kafka-service:9092').split(',')
        }
        
    def start_streaming(self, config: StreamConfig):
        if self.stream_thread and self.stream_thread.is_alive():
            self.stop_streaming()
            
        self.config = config
        self.current_stream = PriceStreamer(
            data_source=YahooFinanceSource(),
            kafka_config=self.kafka_config
        )
        
        self.stream_thread = threading.Thread(
            target=self.current_stream.stream,
            kwargs={
                'symbol': config.symbol,
                'lookback_days': config.days,
                'replay_speed': config.speed
            }
        )
        self.stream_thread.start()
        
    def stop_streaming(self):
        if self.current_stream:
            self.current_stream.stop_streaming = True
            if self.stream_thread:
                self.stream_thread.join()

state = StreamerState()

@app.get("/status")
async def get_status():
    if state.stream_thread and state.stream_thread.is_alive():
        return {
            "status": "running",
            "config": state.config.dict() if state.config else None
        }
    return {"status": "stopped"}

@app.post("/start")
async def start_stream(config: StreamConfig):
    try:
        state.start_streaming(config)
        return {"message": f"Started streaming {config.symbol}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop")
async def stop_stream():
    state.stop_streaming()
    return {"message": "Stopped streaming"}