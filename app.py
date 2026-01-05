import os
import json
import gradio as gr
import pandas as pd
import plotly.express as px
import time
from dotenv import load_dotenv

from accounts import Account
from database import read_account

load_dotenv(override = True)

TRADER_NAMES = json.loads(os.getenv("TRADER_NAMES"))
INITIAL_DEPOSIT = float(os.getenv("INITIAL_DEPOSIT"))

class TraderView:
    def __init__(self, username: str):
        self.username = username
        self.account = read_account(username) or Account(username, INITIAL_DEPOSIT)
        self.portfolio_history = []
        self._record_portfolio_value()

    def reload(self):
        self.account = read_account(self.username) or self.account

    def _record_portfolio_value(self):
        self.portfolio_history.append(
            {
                "datetime": pd.to_datetime(time.time(), unit = "s"),
                "value": self.account.get_portfolio_value(),
            }
        )

    def get_title(self):
        return f"<div style = 'text-align:center;font-size:28px'>{self.username}</div>"

    def get_portfolio_value_html(self):
        value = self.account.get_portfolio_value()
        pnl = self.account.get_profit_loss()
        color = "green" if pnl >= 0 else "red"
        emoji = "⬆" if pnl >= 0 else "⬇"
        return (
            f"<div style = 'text-align:center;background:{color};padding:6px;'>"
            f"<span style = 'font-size:26px'>${value:,.0f}</span>"
            f"<span style = 'font-size:18px'>&nbsp;{emoji} ${pnl:,.0f}</span>"
            f"</div>"
        )

    def get_portfolio_chart(self, max_points: int = 100):
        if not self.portfolio_history:
            return None
        recent_history = self.portfolio_history
        df = pd.DataFrame(recent_history)
        fig = px.line(df, x = "datetime", y = "value")
        fig.update_layout(
            height = 250,
            margin = dict(l = 30, r = 10, t = 20, b = 30),
            paper_bgcolor = "#bbb",
            plot_bgcolor = "#dde",
        )
        fig.update_xaxes(tickfont = dict(size = 8))
        fig.update_yaxes(tickfont = dict(size = 8), tickformat = ",.0f")
        return fig

    def get_holdings_df(self):
        holdings = self.account.get_holdings()
        return pd.DataFrame(
            [{"Symbol": s, "Quantity": q} for s, q in holdings]
        ) if holdings else pd.DataFrame(columns = ["Symbol", "Quantity"])

    def get_transactions_df(self):
        txs = self.account.list_transactions()
        if not txs:
            return pd.DataFrame(
                columns = ["Type", "Timestamp", "Symbol", "Quantity", "Price", "Amount"]
            )

        rows = []
        for tx in txs:
            rows.append(
                {
                    "Type": tx.tx_type.value.upper(),
                    "Timestamp": pd.to_datetime(tx.timestamp, unit = "s").strftime("%H:%M:%S"),
                    "Symbol": tx.symbol or "",
                    "Quantity": int(tx.quantity or 0),
                    "Price": f"${tx.price_at_transaction:.2f}",
                    "Amount": f"${tx.amount:,.2f}",
                }
            )
        return pd.DataFrame(rows)

    def refresh(self):
        self.reload()
        self._record_portfolio_value()
        return (
            self.get_portfolio_value_html(),
            self.get_portfolio_chart(),
            self.get_holdings_df(),
            self.get_transactions_df(),
        )

def create_ui():
    traders = [TraderView(name) for name in TRADER_NAMES]

    with gr.Blocks(title = "Trading Dashboard", fill_width = True) as ui:
        gr.Markdown("# Autonomous Traders Dashboard")

        with gr.Row():
            for trader in traders:
                with gr.Column(scale = 1):
                    gr.HTML(trader.get_title())

                    portfolio_html = gr.HTML(trader.get_portfolio_value_html)
                    chart = gr.Plot(trader.get_portfolio_chart)
                    holdings = gr.Dataframe(
                        trader.get_holdings_df,
                        headers = ["Symbol", "Quantity"],
                        interactive = False,
                        max_height = 200,
                    )
                    transactions = gr.Dataframe(
                        trader.get_transactions_df,
                        headers = ["Type", "Timestamp", "Symbol", "Quantity", "Price", "Amount"],
                        interactive = False,
                        max_height = 200,
                    )

                    timer = gr.Timer(value = 30)
                    timer.tick(
                        fn = trader.refresh,
                        inputs = [],
                        outputs = [portfolio_html, chart, holdings, transactions],
                        show_progress = False,
                        queue = False,
                    )

    return ui

if __name__ == "__main__":
    ui = create_ui()
    ui.launch(inbrowser = True)