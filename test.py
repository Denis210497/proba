import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import csv
import shutil

CSV_FILE = 'trades.csv'
COLUMNS = [
    'Entry Date', 'Ticker', 'Setup', 'Buy Price', 'Stop Loss', 'Target Price', 'Shares',
    'Exit Date', 'Sell Price', 'P/L $', 'P/L %', 'R/R Ratio', 'Holding Days', 'Notes'
]
ACCOUNT_FILE = 'account_balance.csv'
ACCOUNT_HISTORY_FILE = 'account_history.csv'

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)

def save_trade(data):
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

def calculate_fields(entry_date, exit_date, buy_price, sell_price, stop_loss, target_price, shares):
    holding_days = (datetime.strptime(exit_date, '%Y-%m-%d') - datetime.strptime(entry_date, '%Y-%m-%d')).days
    pl_dollar = round((sell_price - buy_price) * shares, 2)
    pl_percent = round(((sell_price / buy_price) - 1) * 100, 2)
    risk_per_share = buy_price - stop_loss
    reward_per_share = target_price - buy_price
    rr_ratio = round(reward_per_share / risk_per_share, 2) if risk_per_share != 0 else 'inf'
    return holding_days, pl_dollar, pl_percent, rr_ratio

def show_stats_and_charts():
    if not os.path.exists(CSV_FILE):
        messagebox.showinfo('Info', 'No trades found.')
        return
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        messagebox.showinfo('Info', 'No trades found.')
        return
    total_trades = len(df)
    wins = df[df['P/L $'] > 0]
    losses = df[df['P/L $'] <= 0]
    win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
    avg_gain = wins['P/L $'].mean() if not wins.empty else 0
    avg_loss = losses['P/L $'].mean() if not losses.empty else 0
    expectancy = (win_rate/100 * avg_gain) + ((1 - win_rate/100) * avg_loss)
    profit_factor = wins['P/L $'].sum() / abs(losses['P/L $'].sum()) if losses['P/L $'].sum() != 0 else float('inf')
    cumulative_pl = df['P/L $'].cumsum()
    stats = f"""
Total trades: {total_trades}
Win rate: {win_rate:.2f}%
Average gain: {avg_gain:.2f}
Average loss: {avg_loss:.2f}
Expectancy: {expectancy:.2f}
Profit factor: {profit_factor:.2f}
Cumulative P/L: {df['P/L $'].sum():.2f}
"""
    messagebox.showinfo('Trading Stats', stats)
    # Charts
    plt.figure(figsize=(12, 6))
    plt.subplot(2,2,1)
    plt.plot(cumulative_pl, marker='o')
    plt.title('Cumulative P/L')
    plt.xlabel('Trade #')
    plt.ylabel('Cumulative P/L ($)')
    plt.subplot(2,2,2)
    plt.bar(df.index, df['P/L $'], color=['g' if x > 0 else 'r' for x in df['P/L $']])
    plt.title('P/L per Trade')
    plt.xlabel('Trade #')
    plt.ylabel('P/L ($)')
    plt.subplot(2,2,3)
    plt.pie([len(wins), len(losses)], labels=['Win', 'Loss'], autopct='%1.1f%%', colors=['g','r'])
    plt.title('Win vs Loss')
    plt.tight_layout()
    plt.show()

def refresh_table(tree):
    for row in tree.get_children():
        tree.delete(row)
    if not os.path.exists(CSV_FILE):
        return
    df = pd.read_csv(CSV_FILE)
    for _, row in df.iterrows():
        tree.insert('', 'end', values=list(row))

def submit_trade(entries, tree):
    try:
        entry_date = entries['Entry Date'].get()
        ticker = entries['Ticker'].get().upper()
        setup = entries['Setup'].get()
        buy_price = float(entries['Buy Price'].get())
        stop_loss = float(entries['Stop Loss'].get())
        target_price = float(entries['Target Price'].get())
        shares = int(entries['Shares'].get())
        exit_date = entries['Exit Date'].get()
        sell_price = float(entries['Sell Price'].get())
        notes = entries['Notes'].get()
        holding_days, pl_dollar, pl_percent, rr_ratio = calculate_fields(
            entry_date, exit_date, buy_price, sell_price, stop_loss, target_price, shares)
        row = [
            entry_date, ticker, setup, buy_price, stop_loss, target_price, shares,
            exit_date, sell_price, pl_dollar, pl_percent, rr_ratio, holding_days, notes
        ]
        save_trade(row)
        messagebox.showinfo('Success', 'Trade saved!')
        refresh_table(tree)
    except Exception as e:
        messagebox.showerror('Error', f'Invalid input: {e}')

def save_account_balance(start_balance):
    with open(ACCOUNT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Start Balance'])
        writer.writerow([start_balance])

def load_account_balance():
    if not os.path.exists(ACCOUNT_FILE):
        return None
    with open(ACCOUNT_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            try:
                return float(row[0])
            except:
                return None
    return None

def show_account_status(start_entry, current_entry, result_label):
    try:
        start = float(start_entry.get())
        current = float(current_entry.get())
        save_account_balance(start)
        diff = current - start
        percent = (current / start - 1) * 100 if start != 0 else 0
        result_label.config(text=f"Promjena: {diff:.2f} $  ({percent:.2f}%)")
    except Exception as e:
        result_label.config(text=f"Greška u unosu: {e}")

def save_account_history(date, balance):
    new_file = not os.path.exists(ACCOUNT_HISTORY_FILE)
    with open(ACCOUNT_HISTORY_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(['Date', 'Balance'])
        writer.writerow([date, balance])

def load_account_history():
    if not os.path.exists(ACCOUNT_HISTORY_FILE):
        return pd.DataFrame(columns=['Date', 'Balance'])
    df = pd.read_csv(ACCOUNT_HISTORY_FILE)
    return df

def refresh_account_history_table(tree, df=None):
    for row in tree.get_children():
        tree.delete(row)
    if df is None:
        df = load_account_history()
    if isinstance(df, pd.DataFrame):
        for _, row in df.iterrows():
            tree.insert('', 'end', values=(row['Date'], row['Balance']))

def sort_history(tree, col, reverse, df):
    df_sorted = df.sort_values(col, ascending=not reverse)
    refresh_account_history_table(tree, df_sorted)
    tree.heading(col, command=lambda: sort_history(tree, col, not reverse, df_sorted))

def filter_history_by_year_month(year_var, month_var, tree, stats_label):
    df = load_account_history()
    if isinstance(df, pd.DataFrame) and not df.empty:
        if year_var.get():
            df = df[pd.to_datetime(df['Date']).dt.year == int(year_var.get())]
        if month_var.get():
            df = df[pd.to_datetime(df['Date']).dt.month == int(month_var.get())]
        refresh_account_history_table(tree, df)
        show_account_stats(df, stats_label)
    else:
        refresh_account_history_table(tree)
        stats_label.config(text='')

def show_account_stats(df, stats_label):
    if df.empty:
        stats_label.config(text='')
        return
    avg = df['Balance'].mean()
    minv = df['Balance'].min()
    maxv = df['Balance'].max()
    std = df['Balance'].std()
    # Drawdown
    cummax = df['Balance'].cummax()
    drawdown = (df['Balance'] - cummax).min()
    # Broj mjeseci u plusu/minusu
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M')
    monthly = df.groupby('Month')['Balance'].last().diff().fillna(0)
    plus = (monthly > 0).sum()
    minus = (monthly < 0).sum()
    stats_label.config(text=f"Prosjek: {avg:.2f}  Min: {minv:.2f}  Max: {maxv:.2f}  Std: {std:.2f}\nNajveći drawdown: {drawdown:.2f}\nMjeseci u plusu: {plus}  Mjeseci u minusu: {minus}")

def export_filtered_to_excel(tree):
    rows = [tree.item(child)['values'] for child in tree.get_children()]
    if not rows:
        messagebox.showinfo('Izvoz', 'Nema podataka za izvoz.')
        return
    df = pd.DataFrame(rows, columns=['Date', 'Balance'])
    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel files', '*.xlsx')])
    if file_path:
        df.to_excel(file_path, index=False)
        messagebox.showinfo('Izvoz', f'Podaci izvezeni u {file_path}')

def save_chart_as_png(fig):
    file_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG files', '*.png')])
    if file_path:
        fig.savefig(file_path)
        messagebox.showinfo('Izvoz', f'Graf spremljen kao {file_path}')

def show_account_history_chart(tree):
    rows = [tree.item(child)['values'] for child in tree.get_children()]
    if not rows:
        messagebox.showinfo('Info', 'Nema povijesti stanja računa.')
        return
    df = pd.DataFrame(rows, columns=['Date', 'Balance'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Balance'] = df['Balance'].astype(float)
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(df['Date'], df['Balance'], marker='o')
    ax.set_title('Promjena stanja računa kroz vrijeme')
    ax.set_xlabel('Datum')
    ax.set_ylabel('Stanje ($)')
    ax.grid(True)
    plt.tight_layout()
    plt.show()
    save_chart_as_png(fig)

def show_monthly_change_chart(tree):
    rows = [tree.item(child)['values'] for child in tree.get_children()]
    if not rows:
        messagebox.showinfo('Info', 'Nema povijesti stanja računa.')
        return
    df = pd.DataFrame(rows, columns=['Date', 'Balance'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Balance'] = df['Balance'].astype(float)
    df = df.sort_values('Date')
    df['Month'] = df['Date'].dt.to_period('M')
    monthly = df.groupby('Month')['Balance'].last().diff().fillna(0)
    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(monthly.index.astype(str), monthly.values)
    ax.set_title('Mjesečna promjena stanja računa')
    ax.set_xlabel('Mjesec')
    ax.set_ylabel('Promjena ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    save_chart_as_png(fig)

def delete_selected_history(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showinfo('Brisanje', 'Odaberi zapis za brisanje.')
        return
    if not messagebox.askyesno('Potvrda', 'Jeste li sigurni da želite obrisati zapis?'):
        return
    df = load_account_history()
    values = tree.item(selected[0])['values']
    df = df[~((df['Date'] == values[0]) & (df['Balance'] == float(values[1])))]
    df.to_csv(ACCOUNT_HISTORY_FILE, index=False)
    refresh_account_history_table(tree)

def edit_selected_history(tree, date_entry, balance_entry, edit_btn, add_btn):
    selected = tree.selection()
    if not selected:
        messagebox.showinfo('Uređivanje', 'Odaberi zapis za uređivanje.')
        return
    values = tree.item(selected[0])['values']
    date_entry.delete(0, tk.END)
    date_entry.insert(0, values[0])
    balance_entry.delete(0, tk.END)
    balance_entry.insert(0, values[1])
    edit_btn.config(state='normal')
    add_btn.config(state='disabled')

def save_edited_history(tree, date_entry, balance_entry, edit_btn, add_btn):
    selected = tree.selection()
    if not selected:
        return
    try:
        new_date = date_entry.get()
        new_balance = float(balance_entry.get())
        datetime.strptime(new_date, '%Y-%m-%d')
        df = load_account_history()
        values = tree.item(selected[0])['values']
        idx = df[(df['Date'] == values[0]) & (df['Balance'] == float(values[1]))].index
        if not idx.empty:
            df.at[idx[0], 'Date'] = new_date
            df.at[idx[0], 'Balance'] = new_balance
            df.to_csv(ACCOUNT_HISTORY_FILE, index=False)
            refresh_account_history_table(tree)
            date_entry.delete(0, tk.END)
            balance_entry.delete(0, tk.END)
            edit_btn.config(state='disabled')
            add_btn.config(state='normal')
    except Exception as e:
        messagebox.showerror('Greška', f'Greška u uređivanju: {e}')

def add_account_history(date_entry, balance_entry, tree):
    date = date_entry.get()
    balance = balance_entry.get()
    try:
        datetime.strptime(date, '%Y-%m-%d')
        balance = float(balance)
        save_account_history(date, balance)
        refresh_account_history_table(tree)
    except Exception as e:
        messagebox.showerror('Error', f'Greška u unosu: {e}')

def main():
    init_csv()
    root = tk.Tk()
    root.title('Trading Journal')
    tab_control = ttk.Notebook(root)
    # --- Tab 1: Add Trade ---
    tab1 = ttk.Frame(tab_control)
    entries = {}
    fields = ['Entry Date', 'Ticker', 'Setup', 'Buy Price', 'Stop Loss', 'Target Price', 'Shares',
              'Exit Date', 'Sell Price', 'Notes']
    for i, field in enumerate(fields):
        lbl = ttk.Label(tab1, text=field)
        lbl.grid(row=i, column=0, padx=5, pady=5, sticky='e')
        ent = ttk.Entry(tab1)
        ent.grid(row=i, column=1, padx=5, pady=5)
        entries[field] = ent
    submit_btn = ttk.Button(tab1, text='Save Trade', command=lambda: submit_trade(entries, tree))
    submit_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)
    # --- Tab 2: All Trades ---
    tab2 = ttk.Frame(tab_control)
    tree = ttk.Treeview(tab2, columns=COLUMNS, show='headings', height=15)
    for col in COLUMNS:
        tree.heading(col, text=col)
        tree.column(col, width=90, anchor='center')
    tree.pack(expand=True, fill='both')
    refresh_table(tree)
    # --- Tab 3: Stats & Charts ---
    tab3 = ttk.Frame(tab_control)
    stats_btn = ttk.Button(tab3, text='Show Stats & Charts', command=show_stats_and_charts)
    stats_btn.pack(pady=30)
    # --- Tab 4: Account Status ---
    tab4 = ttk.Frame(tab_control)
    ttk.Label(tab4, text='Početno stanje računa ($):').grid(row=0, column=0, padx=5, pady=5, sticky='e')
    start_entry = ttk.Entry(tab4)
    start_entry.grid(row=0, column=1, padx=5, pady=5)
    start_balance = load_account_balance()
    if start_balance is not None:
        start_entry.insert(0, str(start_balance))
    ttk.Label(tab4, text='Trenutno stanje računa ($):').grid(row=1, column=0, padx=5, pady=5, sticky='e')
    current_entry = ttk.Entry(tab4)
    current_entry.grid(row=1, column=1, padx=5, pady=5)
    result_label = ttk.Label(tab4, text='')
    result_label.grid(row=3, column=0, columnspan=2, pady=10)
    calc_btn = ttk.Button(tab4, text='Izračunaj', command=lambda: show_account_status(start_entry, current_entry, result_label))
    calc_btn.grid(row=2, column=0, columnspan=2, pady=10)
    # Povijest stanja
    ttk.Label(tab4, text='Dodaj u povijest (datum YYYY-MM-DD, stanje $):').grid(row=4, column=0, columnspan=2, pady=(20,5))
    date_entry = ttk.Entry(tab4)
    date_entry.grid(row=5, column=0, padx=5, pady=5)
    balance_entry = ttk.Entry(tab4)
    balance_entry.grid(row=5, column=1, padx=5, pady=5)
    # Tablica povijesti
    history_tree = ttk.Treeview(tab4, columns=['Date', 'Balance'], show='headings', height=7)
    for col in ['Date', 'Balance']:
        history_tree.heading(col, text=col)
        history_tree.column(col, width=100, anchor='center')
    history_tree.grid(row=6, column=0, columnspan=6, padx=5, pady=5)
    refresh_account_history_table(history_tree)
    add_btn = ttk.Button(tab4, text='Dodaj zapis', command=lambda: add_account_history(date_entry, balance_entry, history_tree))
    add_btn.grid(row=5, column=2, padx=5, pady=5)
    edit_btn = ttk.Button(tab4, text='Spremi izmjene', state='disabled', command=lambda: save_edited_history(history_tree, date_entry, balance_entry, edit_btn, add_btn))
    edit_btn.grid(row=5, column=3, padx=5, pady=5)
    del_btn = ttk.Button(tab4, text='Obriši zapis', command=lambda: delete_selected_history(history_tree))
    del_btn.grid(row=7, column=1, pady=10)
    edit_select_btn = ttk.Button(tab4, text='Uredi zapis', command=lambda: edit_selected_history(history_tree, date_entry, balance_entry, edit_btn, add_btn))
    edit_select_btn.grid(row=7, column=0, pady=10)
    # Sortiranje i filtriranje
    year_var = tk.StringVar()
    month_var = tk.StringVar()
    ttk.Label(tab4, text='Godina:').grid(row=8, column=0, sticky='e')
    year_entry = ttk.Entry(tab4, textvariable=year_var, width=6)
    year_entry.grid(row=8, column=1, sticky='w')
    ttk.Label(tab4, text='Mjesec:').grid(row=8, column=2, sticky='e')
    month_entry = ttk.Entry(tab4, textvariable=month_var, width=4)
    month_entry.grid(row=8, column=3, sticky='w')
    filter_btn = ttk.Button(tab4, text='Filtriraj', command=lambda: filter_history_by_year_month(year_var, month_var, history_tree, stats_label))
    filter_btn.grid(row=8, column=4, padx=5)
    # Statistika
    stats_label = ttk.Label(tab4, text='', justify='left')
    stats_label.grid(row=9, column=0, columnspan=6, sticky='w', padx=5, pady=5)
    # Izvoz
    chart_btn = ttk.Button(tab4, text='Prikaži graf', command=lambda: show_account_history_chart(history_tree))
    chart_btn.grid(row=10, column=0, pady=10)
    monthly_chart_btn = ttk.Button(tab4, text='Mjesečna promjena', command=lambda: show_monthly_change_chart(history_tree))
    monthly_chart_btn.grid(row=10, column=1, pady=10)
    export_btn = ttk.Button(tab4, text='Izvezi prikazano u Excel', command=lambda: export_filtered_to_excel(history_tree))
    export_btn.grid(row=10, column=2, pady=10)
    # Sortiranje po klikovima na zaglavlja
    df = load_account_history()
    for col in ['Date', 'Balance']:
        history_tree.heading(col, command=lambda c=col: sort_history(history_tree, c, False, df))
    # Prikaz statistike za sve
    show_account_stats(df, stats_label)
    # --- Add tabs ---
    tab_control.add(tab1, text='Add Trade')
    tab_control.add(tab2, text='All Trades')
    tab_control.add(tab3, text='Stats & Charts')
    tab_control.add(tab4, text='Account Status')
    tab_control.pack(expand=1, fill='both')
    root.mainloop()

if __name__ == '__main__':
    main() 