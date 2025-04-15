
# REST Crypto Converter

An **asynchronous REST service** for real-time cryptocurrency conversion built as a test task for a Python developer. This project demonstrates modern Python web development practices using FastAPI, Pydantic for data validation, and Redis for caching.

## Core Features

- **Async REST Endpoint**
  A single endpoint (`/api/v1/convert`) is provided to perform cryptocurrency conversions. The service is fully asynchronous, enabling efficient handling of I/O-bound tasks such as network requests.

- **Supported Exchanges**
  The service supports multiple cryptocurrency exchanges:
  - **Binance**
  - **KuCoin**
  It dynamically iterates through the supported exchanges to find a valid conversion rate if a specific exchange is not requested.

- **Flexible Request Schema**
  The conversion request accepts the following JSON format:
  ```json
  {
      "currency_from": "USDT",
      "currency_to": "TRX",
      "exchange": null,
      "amount": 100,
      "cache_max_seconds": 1000
  }
  ```
  - If `exchange` is set to `null`, the service tries each supported exchange until a valid rate is found.
  - `cache_max_seconds` controls how long conversion rates are cached.

- **Response Schema**
  The service returns conversion details with the following JSON structure:
  ```json
  {
      "currency_from": "USDT",
      "currency_to": "TRX",
      "exchange": "binance",
      "rate": "8.21",
      "result": "821",
      "updated_at": 1714304596
  }
  ```

- **Dynamic Exchange Handling**
  - If no specific exchange is provided, the service iterates through the supported exchanges in a predetermined order until the desired currency pair is found.
  - If the currency pair is unavailable across all exchanges, an informative error message is returned.

- **Caching Mechanism**
  - Conversion rates are cached in Redis to improve performance and reduce unnecessary external API calls.
  - If a `cache_max_seconds` value is specified and the cached data is fresh, the service returns the cached result.
  - If `cache_max_seconds` is null, the latest rate is always fetched.

- **Indirect Currency Conversion**
  - In cases where a direct conversion rate for the requested currency pair is not available, the service attempts an indirect conversion using an intermediary currency (such as USDT).

- **Robust Network Handling**
  - The service is designed to handle network errors or exchange unavailability gracefully by attempting the next available exchange.
  - If all exchanges fail to provide a valid conversion, the service returns an appropriate error message.

## Folder Structure

The project is organized to separate business logic from external integrations:

```
src/
├── adapters/        # Contains external API adapters (Binance, KuCoin, etc.) using the adapter pattern.
├── services/        # Contains business logic for cryptocurrency conversion (ConversionService).
├── tests/           # Contains unit and integration tests.
├── api.py           # FastAPI routes and dependency injection for the conversion endpoint.
├── config.py        # Application configuration.
├── di.py            # Dependency injection helpers.
├── main.py          # Application entry point.
├── schemas.py       # Pydantic models for request/response validation.
```

## Running the Project

1. **Install Dependencies:**

   ```bash
   poetry install
   ```

2. **Adjust the configuration:**

   Copy .env.example and .redis.conf.example to .env and .redis.conf, respectively. Consider adjusting the configurations inside if needed.

3. **Start the Application:**

   Run the app locally using poetry:
   ```bash
   poetry run uvicorn src.main:app --reload
   ```

   Alternatively, run using docker compose:
   ```bash
   docker-compose up
   ```

Your service is ready, now go and see generated docs [here](http://localhost:8000/docs) and [here](http://localhost:8000/redoc)


### Testing

   Execute the test suite using pytest:
   ```bash
   poetry run pytest
   ```
