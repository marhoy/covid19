FROM python:3.8-slim

# Install poetry in the system python
RUN pip install --upgrade pip && pip install poetry

# Run everything from here as a non-privileged user
ENV USERNAME flask
RUN useradd -m $USERNAME
# If using an alpine image
# RUN addgroup -S $USERNAME && adduser -S $USERNAME -G $USERNAME

# Set a workdir
WORKDIR /home/$USERNAME/app
RUN chown $USERNAME.$USERNAME .

# Run as a non-privileged used
USER $USERNAME

# Copy the lock file. If it hasn't changed, we won't reinstall packages
COPY --chown=$USERNAME:$USERNAME poetry.lock pyproject.toml ./

# Install required packages, and the optional gunicorn
RUN poetry install --no-dev -E gunicorn

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
