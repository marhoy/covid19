# covid19
Dash app with current situation and forecast model

# Development

## Requirements
* Python >= 3.8
* poetry
* docker


## Setting up the development environment

```bash
poetry install
poetry run pre-commit install
```

## Running the debug server
```bash
poetry run python app.py
```
The server will then be available on http://localhost:8050


## Running gunicorn locally
```bash
poetry install -E gunicorn
poetry run gunicorn app:server -b :5000
```

# Deploy to Docker
```bash
docker build -t marhoy/covid .
docker run -p 5000:5000 marhoy/covid
docker push marhoy/covid
```
