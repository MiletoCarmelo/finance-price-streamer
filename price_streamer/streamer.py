class PriceStreamer:
    def __init__(self, data_source: DataSourceBase, kafka_config: Dict[str, Any]):
        self.data_source = data_source
        self.kafka_config = kafka_config
        self.producer = None
        self.stop_streaming = False
        self.connect_to_kafka()

    def connect_to_kafka(self, max_retries=5, retry_delay=5):
        """Établit la connexion à Kafka avec retry"""
        retries = 0
        while retries < max_retries:
            try:
                logger.info(f"Tentative de connexion à Kafka: {self.kafka_config['bootstrap_servers']}")
                self.producer = KafkaProducer(
                    value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
                    **self.kafka_config
                )
                logger.info("Connexion à Kafka établie avec succès")
                return
            except NoBrokersAvailable:
                retries += 1
                if retries == max_retries:
                    logger.error(f"Impossible de se connecter à Kafka après {max_retries} tentatives")
                    raise
                logger.warning(f"Tentative {retries}/{max_retries} échouée, nouvelle tentative dans {retry_delay}s")
                time.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la connexion à Kafka: {str(e)}")
                raise

    def stream(self, symbol: str, lookback_days: int, replay_speed: float = 1.0, topic: str = 'finance-price-stream'):
        """Stream les données historiques"""
        try:
            self.stop_streaming = False
            data = self.data_source.fetch_historical_data(symbol, lookback_days)
            
            logger.info(f"Starting stream for {symbol} to topic {topic}")
            
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
                
                if not self.producer:
                    logger.error("Pas de connexion Kafka disponible")
                    break

                self.producer.send(topic, message)
                logger.info(f"Streamed to {topic}: {symbol} - Close: {message['data']['close']}")
                
                time.sleep(60 / replay_speed)
                
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            raise