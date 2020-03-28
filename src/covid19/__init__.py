"""Make the app available from the outside."""
from covid19.dash_main import server as app

__all__ = ["app"]
