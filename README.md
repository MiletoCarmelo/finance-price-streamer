
# Finance Price Streamer

Application Python qui simule un flux de données financières en temps réel à partir de données historiques.

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python -m price_streamer.main --symbol JPY --days 3 --speed 1.0
```

Arguments disponibles :
- `--source`: Source des données (défaut: yahoo)
- `--symbol`: Symbole à streamer
- `--days`: Nombre de jours d'historique
- `--speed`: Vitesse de replay
- `--kafka-servers`: Serveurs Kafka
- `--kafka-topic`: Topic de destination

## Tests

```bash
pytest tests/
```

## Docker

```bash
docker build -t finance-price-streamer .
docker run finance-price-streamer --symbol JPY --days 3
```
```