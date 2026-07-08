import pandas as pd
import plotly.express as px

from dash import Dash, dcc, html
from dash.dependencies import Input, Output


salary_df = pd.read_csv(
    r"datasets\cleaned\dataset 1\training dataset.csv"
)
transactions_df = pd.read_csv(
    r"datasets\cleaned\dataset 2\training dataset.csv"
)
cost_df = pd.read_csv(
    r"datasets\cleaned\dataset 3\training dataset.csv"
)
inflation_df = pd.read_csv(
    r"datasets\cleaned\dataset 4\training dataset.csv"
)


def get_df(name):
    if name == "salary":
        return salary_df
    elif name == "transactions":
        return transactions_df
    elif name == "cost":
        return cost_df
    elif name == "inflation":
        return inflation_df
    return salary_df


def create_dashboard(server):

    dash_app = Dash(
        __name__,
        server=server,
        url_base_pathname="/analytics-dashboard/"
    )

    dash_app.layout = html.Div(

        [

            html.H2(
                "EDA Explorer Dashboard",
                style={
                    "textAlign": "center",
                    "marginBottom": "20px"
                },
            ),

            html.Div(

                [

                    html.Div(

                        [

                            dcc.Dropdown(
                                id="dataset",
                                options=[
                                    {
                                        "label": "Salary",
                                        "value": "salary"
                                    },
                                    {
                                        "label": "Transactions",
                                        "value": "transactions"
                                    },
                                    {
                                        "label": "Cost",
                                        "value": "cost"
                                    },
                                    {
                                        "label": "Inflation",
                                        "value": "inflation"
                                    },
                                ],
                                value="salary",
                                style={
                                    "marginBottom": "10px"
                                },
                            ),

                            dcc.Dropdown(
                                id="x",
                                placeholder="Select X column",
                                style={
                                    "marginBottom": "10px"
                                },
                            ),

                            dcc.Dropdown(
                                id="y",
                                placeholder="Select Y column",
                                style={
                                    "marginBottom": "10px"
                                },
                            ),

                            dcc.Dropdown(
                                id="color",
                                placeholder="Color (optional)",
                                style={
                                    "marginBottom": "10px"
                                },
                            ),

                            dcc.Checklist(
                                id="options",
                                options=[
                                    {
                                        "label": "Trendline",
                                        "value": "trend"
                                    },
                                    {
                                        "label": "Log Scale",
                                        "value": "log"
                                    },
                                    {
                                        "label": "Histogram",
                                        "value": "hist"
                                    },
                                    {
                                        "label": "Box",
                                        "value": "box"
                                    },
                                    {
                                        "label": "Violin",
                                        "value": "violin"
                                    },
                                    {
                                        "label": "Heatmap",
                                        "value": "heat"
                                    },
                                ],
                                value=["hist", "heat"],
                                style={
                                    "marginBottom": "15px"
                                },
                            ),

                            dcc.Dropdown(
                                id="filter-col",
                                placeholder="Filter column",
                                style={
                                    "marginBottom": "10px"
                                },
                            ),

                            dcc.Dropdown(
                                id="filter-val",
                                placeholder="Filter value",
                            ),

                        ],

                        style={
                            "width": "25%",
                            "padding": "20px",
                            "backgroundColor": "#f4f6f8",
                            "borderRadius": "10px",
                            "boxShadow": "0px 0px 10px rgba(0,0,0,0.05)",
                        },
                    ),

                    html.Div(

                        [
                            html.Div(id="graphs")
                        ],

                        style={
                            "width": "75%",
                            "padding": "20px",
                        },
                    ),

                ],

                style={
                    "display": "flex",
                    "gap": "20px",
                },

            ),

        ],

        style={
            "padding": "20px",
            "backgroundColor": "#ffffff",
        },

    )

    @dash_app.callback(
        Output("x", "options"),
        Output("y", "options"),
        Output("color", "options"),
        Output("filter-col", "options"),
        Input("dataset", "value"),
    )
    def update_columns(dataset):
        df = get_df(dataset)
        cols = [{"label": c, "value": c} for c in df.columns]
        return cols, cols, cols, cols
    

    @dash_app.callback(
        Output("filter-val", "options"),
        Input("filter-col", "value"),
        Input("dataset", "value")
    )
    def update_filter_vals(col, dataset):
        df = get_df(dataset)

        if col:
            return [
                {"label": str(v), "value": v}
                for v in df[col].dropna().unique()
            ]

        return []


    @dash_app.callback(
        Output("graphs", "children"),
        Input("dataset", "value"),
        Input("x", "value"),
        Input("y", "value"),
        Input("color", "value"),
        Input("options", "value"),
        Input("filter-col", "value"),
        Input("filter-val", "value"),
    )
    def update_graphs(
        dataset,
        x,
        y,
        color,
        opts,
        fcol,
        fval,
    ):

        df = get_df(dataset).copy()

        opts = opts or []

        if fcol and fval:
            df = df[df[fcol] == fval]

        num_cols = df.select_dtypes(
            include="number"
        ).columns.tolist()

        if not x and len(df.columns) > 0:
            x = df.columns[0]

        if not y and len(num_cols) > 0:
            y = num_cols[0]

        graphs = []
        if x and y:

            if x in num_cols and y in num_cols:

                if "trend" in opts:

                    fig = px.scatter(
                        df,
                        x=x,
                        y=y,
                        color=color,
                        trendline="ols"
                    )

                else:

                    fig = px.scatter(
                        df,
                        x=x,
                        y=y,
                        color=color
                    )

            else:

                fig = px.strip(
                    df,
                    x=x,
                    y=y,
                    color=color
                )

            if "log" in opts:
                fig.update_yaxes(type="log")

            graphs.append(
                dcc.Graph(
                    figure=fig
                )
            )

        if x and "hist" in opts:

            fig = px.histogram(
                df,
                x=x,
                color=color
            )

            if "log" in opts:
                fig.update_yaxes(type="log")

            graphs.append(
                dcc.Graph(
                    figure=fig
                )
            )

        if x and y and "box" in opts:

            graphs.append(

                dcc.Graph(

                    figure=px.box(
                        df,
                        x=x,
                        y=y,
                        color=color
                    )

                )

            )

        if x and y and "violin" in opts:

            graphs.append(

                dcc.Graph(

                    figure=px.violin(
                        df,
                        x=x,
                        y=y,
                        color=color
                    )

                )

            )

        if "heat" in opts and len(num_cols) > 1:

            corr = df[num_cols].corr()

            graphs.append(

                dcc.Graph(

                    figure=px.imshow(
                        corr,
                        text_auto=True,
                        aspect="auto"
                    )

                )

            )

        if not graphs and len(num_cols) > 0:

            graphs.append(

                dcc.Graph(

                    figure=px.histogram(
                        df,
                        x=num_cols[0]
                    )

                )

            )

        return graphs

    return dash_app