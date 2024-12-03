from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd

class DataSourceBase(ABC):
    @abstractmethod
    def fetch_historical_data(self, symbol: str, lookback_days: int) -> pd.DataFrame:
        """
        Récupère les données historiques depuis la source
        
        Args:
            symbol: Symbole de trading
            lookback_days: Nombre de jours d'historique
            
        Returns:
            DataFrame avec colonnes: [open, high, low, close, volume]
        """
        pass

    @abstractmethod
    def validate_symbol(self, symbol: str) -> str:
        """
        Valide et formate le symbole selon la source
        
        Args:
            symbol: Symbole à valider
            
        Returns:
            Symbole formaté
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Retourne le nom de la source"""
        pass