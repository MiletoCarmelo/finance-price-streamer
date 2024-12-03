import pytest
from price_streamer.sources.base import DataSourceBase
from price_streamer.streamer import PriceStreamer
import pandas as pd
from datetime import datetime, timedelta

class MockDataSource(DataSourceBase):
    def validate_symbol(self, symbol: str) -> str:
        return symbol

    def get_source_name(self) -> str:
        return "mock"

    def fetch_historical_data(self, symbol: str, lookback_days: int) -> pd.DataFrame:
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=lookback_days),
            end=datetime.now(),
            freq='1min'
        )
        
        data = {
            'Open': [100.0] * len(dates),
            'High': [101.0] * len(dates),
            'Low': [99.0] * len(dates),
            'Close': [100.5] * len(dates),
            'Volume': [1000] * len(dates)
        }
        
        return pd.DataFrame(data, index=dates)

def test_streamer_initialization():
    kafka_config = {'bootstrap_servers': ['localhost:9092']}
    source = MockDataSource()
    streamer = PriceStreamer(source, kafka_config)
    assert streamer.data_source == source

def test_mock_data_source():
    source = MockDataSource()
    data = source.fetch_historical_data("TEST", 1)
    assert not data.empty
    assert 'Open' in data.columns
    assert 'Close' in data.columns