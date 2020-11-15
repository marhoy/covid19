"""Create the footer on every page."""
import dash_core_components as dcc
import dash_html_components as html

footer = html.Div(
    [
        html.H3("Data source"),
        dcc.Markdown(
            """
        COVID-data is downloaded from
        [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19).
    """
        ),
        html.H3("About the author"),
        dcc.Markdown(
            """
        Created by [Martin Høy](mailto:martin@hoy.priv.no),
        March 2020 (updated November 2020).

        Code available on [GitHub](https://github.com/marhoy/covid19).
        Docker image available on [Docker Hub](https://hub.docker.com/r/marhoy/covid).
        """
        ),
    ]
)
