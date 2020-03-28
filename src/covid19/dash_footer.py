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
        Plots and model created by [Martin Høy](mailto:martin@hoy.priv.no),
        March 2020.
    """
        ),
    ]
)
