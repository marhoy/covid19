"""Make the app available for gunicorn."""
from covid19.dash_main import app

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
