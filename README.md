# covid19
Dash app displaying the current situation of Covid-19.

A deployed version of this repository is available at https://covid.hoy.priv.no/


# Development

## Requirements
* Python >= 3.8
* pyenv (recommended for virtual environment management)
* poetry
* docker


## Setting up the development environment

```bash
# Create and activate a dedicated virtual environment
pyenv virtualenv 3.9.0 covid-19
pyenv local covid-19

# Install project dependencies
poetry install
pre-commit install
```

## Running the debug server
During development, you can just keep this server running: It will automatically refresh
when you change some of the project files.

```bash
python app.py
```
The debug server will then be available on http://localhost:8050


## Running gunicorn locally
The production server uses gunicorn. If you want to run that locally, have a look at at `CMD` in the `Dockerfile`, which runs:
```bash
gunicorn -c src/gunicorn_config.py app:server
```
The production server will then be available on http://localhost:5000


# Deploy to Docker container
You can use Docker to deploy the production server.
```bash
# Build docker image
docker build -t marhoy/covid .

# Run docker image and forward port 5000 to host port 5001
docker run -p 5001:5000 marhoy/covid

# Push docker image to docker hub
docker push marhoy/covid
```
The production server running inside the Docker container will be available on
http://localhost:5001
