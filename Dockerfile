# Selection basis
FROM python:3.11.9

# Set working directory
WORKDIR /app

# Update pip and install Poetry
RUN pip install --upgrade pip && \
 pip install poetry

# Copier les fichiers de configuration poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copier le code source
COPY price_streamer/ price_streamer/
 
# Exposer le port 8000
EXPOSE 8000

# Commande de démarrage
# CMD ["python", "-m", "price_streamer"]
CMD ["poetry", "run", "python", "-m", "price_streamer"]