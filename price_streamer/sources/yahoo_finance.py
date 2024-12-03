from .base import DataSourceBase
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class YahooFinanceSource(DataSourceBase):
    def validate_symbol(self, symbol: str) -> str:
        """Ajoute =X pour les paires forex si nécessaire"""
        return f"{symbol}=X" if not "=" in symbol else symbol

    def get_source_name(self) -> str:
        return "yahoo_finance"

    def fetch_historical_data(self, symbol: str, lookback_days: int) -> pd.DataFrame:
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            symbol = self.validate_symbol(symbol)
            logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval='1m'
            )
            
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
                
            logger.info(f"Retrieved {len(data)} data points")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise