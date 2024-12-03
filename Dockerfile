# Selection basis
FROM python:3.11.9

# Set working directory
WORKDIR /app

# Copy dependency files and source code
# COPY ./pyproject.toml ./poetry.lock* ./
COPY ./pyproject.toml ./
COPY . .

# Update pip and install Poetry
RUN pip install --upgrade pip && \
 pip install poetry

# Install dependencies
RUN poetry config virtualenvs.create false && \
 poetry install --no-interaction --no-ansi
 

COPY price_streamer/ price_streamer/


CMD ["python", "-m", "price_streamer"]