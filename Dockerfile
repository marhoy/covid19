FROM python:3.9-slim

# Define some environment variables
ENV PIP_NO_CACHE_DIR=true \
    DEBIAN_FRONTEND=noninteractive

# Install dependencies needed to get/build packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends apt-utils \
    && apt-get install -y --no-install-recommends \
    curl

# Install poetry in the system python
RUN pip install --upgrade pip setuptools

# Run everything from here as a non-privileged user
ENV USERNAME app
ENV PATH="$PATH:/home/$USERNAME/.poetry/bin:/home/$USERNAME/.local/bin"

# Add user
RUN useradd -m $USERNAME
# If using an alpine image
# RUN addgroup -S $USERNAME && adduser -S $USERNAME -G $USERNAME

# Set a workdir
WORKDIR /home/$USERNAME/app
RUN chown $USERNAME.$USERNAME .

# Run as a non-privileged used
USER $USERNAME

# Install a specific version of poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - --version 1.1.4

# Copy the lock file. If it hasn't changed, we won't reinstall packages
COPY --chown=$USERNAME:$USERNAME poetry.lock pyproject.toml ./

# Install required packages, and the optional gunicorn
RUN poetry install --no-dev

# Copy necessary files to container
COPY --chown=$USERNAME:$USERNAME src ./src
COPY --chown=$USERNAME:$USERNAME app.py .

# Install this package as well
RUN poetry install --no-dev

# Expose port 5000
EXPOSE 5000

# Run gunicorn
ENTRYPOINT ["poetry", "run"]
CMD ["gunicorn", "-c", "src/gunicorn_config.py", "app:server"]
