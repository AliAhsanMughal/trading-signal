import tkinter as tk
from tkinter import ttk
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import datetime
import threading

def fetch_data(pair):
    df = yf.download(tickers=pair, period='30m', interval='1m')
    df.dropna(inplace=True)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd_df = ta.macd(df['Close'])
    df = pd.concat([df, macd_df], axis=1)
    df.rename(columns={
        "MACD_12_26_9": "MACD",
        "MACDs_12_26_9": "Signal",
        "MACDh_12_26_9": "Hist"
    }, inplace=True)
    return df

def generate_signal(row):
    if row['RSI'] > 50 and row['MACD'] > row['Signal'] and row['Hist'] > 0:
        return "🔼 CALL"
    elif row['RSI'] < 50 and row['MACD'] < row['Signal'] and row['Hist'] < 0:
        return "🔽 PUT"
    else:
        return "⏸ WAIT"

def update_data():
    try:
        pair = pair_entry.get().strip()
        if not pair:
            trade_signal_var.set("Enter a valid pair")
            return
        df = fetch_data(pair)
        latest = df.iloc[-1]
        signal = generate_signal(latest)

        price_var.set(f"{latest['Close']:.5f}")
        rsi_var.set(f"{latest['RSI']:.2f}")
        macd_var.set(f"{latest['MACD']:.5f}")
        signal_line_var.set(f"{latest['Signal']:.5f}")
        hist_var.set(f"{latest['Hist']:.5f}")
        trade_signal_var.set(signal)
        time_var.set(datetime.datetime.now().strftime('%H:%M:%S'))
    except Exception as e:
        trade_signal_var.set("Error fetching data")
        print("Error:", e)
    finally:
        threading.Timer(60, update_data).start()

# GUI setup
app = tk.Tk()
app.title("Trading Signal App")
app.geometry("320x400")
app.resizable(False, False)

tk.Label(app, text="📈 Trading Signal App", font=("Helvetica", 16, "bold")).pack(pady=10)

pair_frame = ttk.Frame(app)
pair_frame.pack(pady=5)
ttk.Label(pair_frame, text="Enter Pair (e.g., EURUSD=X):").pack()
pair_entry = ttk.Entry(pair_frame)
pair_entry.insert(0, "NZDCAD=X")
pair_entry.pack()

frame = ttk.Frame(app)
frame.pack(pady=10)

price_var = tk.StringVar()
rsi_var = tk.StringVar()
macd_var = tk.StringVar()
signal_line_var = tk.StringVar()
hist_var = tk.StringVar()
trade_signal_var = tk.StringVar()
time_var = tk.StringVar()

def make_row(label, var):
    ttk.Label(frame, text=label).pack()
    ttk.Label(frame, textvariable=var, font=("Helvetica", 10)).pack()

make_row("Price:", price_var)
make_row("RSI:", rsi_var)
make_row("MACD:", macd_var)
make_row("Signal Line:", signal_line_var)
make_row("Histogram:", hist_var)

ttk.Label(frame, text="Trade Signal:").pack(pady=(10, 0))
ttk.Label(frame, textvariable=trade_signal_var, font=("Helvetica", 14, "bold")).pack()

ttk.Label(app, textvariable=time_var, font=("Helvetica", 8)).pack(pady=5)

update_data()
app.mainloop()
