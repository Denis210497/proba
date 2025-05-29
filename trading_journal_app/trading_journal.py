import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk
import pandas as pd
from datetime import datetime
import json
import os
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry  # Add calendar widget

class TradingJournalApp:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Trading Journal")
        self.root.geometry("1200x800")
        
        # Set up seaborn style
        sns.set_style("whitegrid")
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        
        # Available chart styles
        self.chart_styles = {
            "Default": "default",
            "Dark": "dark_background",
            "Classic": "classic",
            "Minimal": "bmh"
        }
        
        # Initialize settings variables
        self.theme_var = tk.StringVar(value="arc")
        self.profit_color = tk.StringVar(value="#22bb33")
        self.loss_color = tk.StringVar(value="#bb2124")
        self.chart_style = tk.StringVar(value="Default")  # Changed to match dictionary key
        
        # Initialize data storage
        self.data_file = "trades.csv"
        self.config_file = "trading_config.json"
        self.trades_df = self.load_trades()
        self.account_balance = self.load_account_balance()
        
        # Define trading instruments
        self.forex_pairs = [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'USD/CAD', 
            'AUD/USD', 'NZD/USD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY'
        ]
        
        self.indices = [
            'NASDAQ', 'S&P 500', 'DOW 30', 'FTSE 100', 'DAX',
            'NIKKEI 225', 'HANG SENG', 'ASX 200'
        ]
        
        self.commodities = [
            'GOLD', 'SILVER', 'CRUDE OIL', 'NATURAL GAS', 'COPPER'
        ]
        
        # Define setup types
        self.setup_types = [
            # SMC (Smart Money Concepts) Setups
            'SMC - 4H Fair Value Gap',
            'SMC - 4H Breaker Block',
            'SMC - 4H Order Block',
            'SMC - 4H Mitigation Block',
            'SMC - 15min Fair Value Gap',
            'SMC - 15min Breaker Block',
            'SMC - 15min Order Block',
            'SMC - 15min Mitigation Block',
            # Fibonacci Setups
            'FIB - 4H 0.618 Retracement',
            'FIB - 4H 0.786 Retracement',
            'FIB - 4H Extension 1.618',
            'FIB - 15min 0.618 Retracement',
            'FIB - 15min 0.786 Retracement',
            'FIB - 15min Extension 1.618',
            # Traditional Setups
            'Support/Resistance',
            'Moving Average',
            'Trend Line Break',
            'Pattern Trade',
            'Gap Fill',
            'Momentum',
            'Other'
        ]
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_trade_entry_tab()
        self.create_trade_list_tab()
        self.create_statistics_tab()
        self.create_account_settings_tab()
        
        # Load saved settings after UI is created
        self.load_saved_settings()

    def create_pl_chart(self):
        try:
            # Create figure with single plot
            fig = plt.figure(figsize=(12, 6))
            plt.clf()
            
            # Set style to a clean, minimal look
            plt.style.use('seaborn-v0_8-whitegrid')
            plt.rcParams['axes.facecolor'] = 'white'
            plt.rcParams['figure.facecolor'] = 'white'
            plt.rcParams['grid.color'] = '#E5E5E5'
            plt.rcParams['grid.linestyle'] = '-'
            plt.rcParams['grid.linewidth'] = 0.5
            plt.rcParams['axes.grid'] = True
            plt.rcParams['axes.edgecolor'] = '#CCCCCC'
            plt.rcParams['axes.linewidth'] = 1
            
            if len(self.trades_df) == 0:
                # If no trades, show empty chart with message
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'No trades to display', 
                       horizontalalignment='center',
                       verticalalignment='center',
                       transform=ax.transAxes,
                       fontsize=12)
                ax.set_axis_off()
            else:
                ax = fig.add_subplot(111)
                
                # Calculate cumulative P&L
                pl_series = self.trades_df['P/L ($)'].astype(float)
                cumulative_pl = pl_series.cumsum()
                
                # Create x-axis as simple index
                x_values = range(len(cumulative_pl))
                
                # Plot line
                line = ax.plot(x_values, cumulative_pl, 
                             color='#0066CC',  # Blue color similar to example
                             linewidth=1.5,
                             solid_capstyle='round')[0]
                
                # Set title and labels
                ax.set_title('Realized PnL', fontsize=12, pad=20)
                ax.set_ylabel('', fontsize=10)  # Remove y-axis label
                ax.set_xlabel('', fontsize=10)  # Remove x-axis label
                
                # Format y-axis with clean number format (no dollar signs)
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
                
                # Remove top and right spines
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                # Adjust grid to match example
                ax.grid(True, axis='y', alpha=0.3)
                ax.grid(False, axis='x')  # Remove vertical gridlines
                
                # Set y-axis limits to start from 0
                ax.set_ylim(bottom=0)
                
                # Remove x-axis labels
                ax.set_xticks([])
                
                # Add some padding to the right to match example
                ax.margins(x=0.02)
            
            # Adjust layout
            plt.tight_layout()
            
            # Clear any existing widgets in charts_frame
            if hasattr(self, 'charts_frame'):
                for widget in self.charts_frame.winfo_children():
                    widget.destroy()
                
                # Create and configure canvas
                canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
                canvas.draw()
                
                # Use grid instead of pack
                canvas_widget = canvas.get_tk_widget()
                canvas_widget.grid(row=0, column=0, sticky='nsew')
                
                # Configure grid weights for the canvas
                self.charts_frame.grid_columnconfigure(0, weight=1)
                self.charts_frame.grid_rowconfigure(0, weight=1)
        except Exception as e:
            print(f"Error creating P/L chart: {str(e)}")
            # Create an empty frame if there's an error
            if hasattr(self, 'charts_frame'):
                for widget in self.charts_frame.winfo_children():
                    widget.destroy()
                ttk.Label(self.charts_frame, text="Error creating chart").grid(row=0, column=0)

    def load_saved_settings(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.theme_var.set(config.get('theme', 'arc'))
                self.profit_color.set(config.get('profit_color', '#22bb33'))
                self.loss_color.set(config.get('loss_color', '#bb2124'))
                # Ensure we load a valid chart style
                saved_style = config.get('chart_style', 'Default')
                if saved_style not in self.chart_styles:
                    saved_style = 'Default'
                self.chart_style.set(saved_style)
                self.update_theme()
    
    def load_trades(self):
        if os.path.exists(self.data_file):
            return pd.read_csv(self.data_file)
        return pd.DataFrame(columns=[
            'Date', 'Ticker', 'Setup Type', 'Position', 'Entry Price',
            'Stop Loss', 'Position Size', 'Target', 'Exit Price',
            'P/L ($)', 'P/L (%)', 'Screenshot Path', 'Notes'
        ])
    
    def save_trades(self):
        self.trades_df.to_csv(self.data_file, index=False)
    
    def load_account_balance(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return float(config.get('account_balance', 0))
        return 0.0

    def save_account_balance(self):
        config = {
            'account_balance': self.account_balance,
            'theme': self.theme_var.get(),
            'profit_color': self.profit_color.get(),
            'loss_color': self.loss_color.get(),
            'chart_style': self.chart_style.get()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
    
    def choose_color(self, color_type):
        from tkinter import colorchooser
        color = colorchooser.askcolor(title=f"Choose {color_type} color")[1]
        if color:
            if color_type == 'profit':
                self.profit_color.set(color)
            else:
                self.loss_color.set(color)
            self.update_trade_list()
            self.update_statistics()

    def update_theme(self, event=None):
        self.root.set_theme(self.theme_var.get())

    def update_statistics(self):
        if len(self.trades_df) == 0:
            return
        
        # Calculate statistics
        stats = {
            'Initial Balance': f"${self.account_balance:.2f}",
            'Current Balance': f"${self.calculate_current_balance():.2f}",
            'Total Trades': len(self.trades_df),
            'Winning Trades': len(self.trades_df[self.trades_df['P/L ($)'].astype(float) > 0]),
            'Losing Trades': len(self.trades_df[self.trades_df['P/L ($)'].astype(float) < 0]),
        }
        
        stats['Win Rate (%)'] = (stats['Winning Trades'] / stats['Total Trades']) * 100
        
        pl_series = self.trades_df['P/L ($)'].astype(float)
        stats['Total P/L ($)'] = pl_series.sum()
        stats['Average Trade ($)'] = pl_series.mean()
        stats['Largest Win ($)'] = pl_series.max()
        stats['Largest Loss ($)'] = pl_series.min()
        
        # Calculate additional metrics
        if len(pl_series) > 0:
            winning_trades = pl_series[pl_series > 0]
            losing_trades = pl_series[pl_series < 0]
            
            if len(winning_trades) > 0 and len(losing_trades) > 0:
                avg_win = winning_trades.mean()
                avg_loss = abs(losing_trades.mean())
                stats['Risk-Reward Ratio'] = avg_win / avg_loss if avg_loss != 0 else 0
                
                # Calculate max drawdown
                cumulative = pl_series.cumsum()
                rolling_max = cumulative.expanding().max()
                drawdowns = (cumulative - rolling_max)
                stats['Max Drawdown ($)'] = abs(drawdowns.min())
        
        # Update statistics tree
        self.stats_tree.delete(*self.stats_tree.get_children())
        for metric, value in stats.items():
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            self.stats_tree.insert('', tk.END, values=[metric, formatted_value])
        
        # Create P/L chart
        self.create_pl_chart()

    def calculate_current_balance(self):
        if len(self.trades_df) == 0:
            return self.account_balance
        
        pl_series = self.trades_df['P/L ($)'].astype(float)
        return self.account_balance + pl_series.sum()

    def browse_screenshot(self, entry_widget):
        filename = filedialog.askopenfilename(
            title="Select Screenshot",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
    
    def save_trade(self):
        # Collect data from form
        trade_data = {}
        for label, entry in self.entries.items():
            if isinstance(entry, tk.Text):
                trade_data[label] = entry.get("1.0", tk.END).strip()
            elif isinstance(entry, DateEntry):
                trade_data[label] = entry.get_date().strftime('%Y-%m-%d')
            else:
                trade_data[label] = entry.get()
        
        # Validate required fields
        required_fields = ['Date', 'Ticker', 'Setup Type', 'Position', 'Entry Price', 'Position Size']
        missing_fields = [field for field in required_fields if not trade_data.get(field)]
        
        if missing_fields:
            messagebox.showerror("Error", f"Please fill in the following required fields:\n{', '.join(missing_fields)}")
            return
        
        # Calculate P/L
        try:
            entry_price = float(trade_data['Entry Price'])
            exit_price = float(trade_data['Exit Price']) if trade_data['Exit Price'] else 0
            position_size = float(trade_data['Position Size'])
            
            if exit_price > 0:
                if trade_data['Position'] == 'Long':
                    pl_dollar = (exit_price - entry_price) * position_size
                else:  # Short
                    pl_dollar = (entry_price - exit_price) * position_size
                
                pl_percent = (pl_dollar / (entry_price * position_size)) * 100
                
                trade_data['P/L ($)'] = f"{pl_dollar:.2f}"
                trade_data['P/L (%)'] = f"{pl_percent:.2f}"
        except ValueError:
            trade_data['P/L ($)'] = ""
            trade_data['P/L (%)'] = ""
        
        # Add to dataframe
        self.trades_df = pd.concat([self.trades_df, pd.DataFrame([trade_data])],
                                 ignore_index=True)
        self.save_trades()
        
        # Update displays
        self.update_trade_list()
        self.update_statistics()
        
        # Clear form
        for label, entry in self.entries.items():
            if isinstance(entry, tk.Text):
                entry.delete("1.0", tk.END)
            elif isinstance(entry, DateEntry):
                entry.set_date(datetime.now())
            else:
                entry.set("")
        
        messagebox.showinfo("Success", "Trade saved successfully!")
    
    def update_trade_list(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add trades to treeview
        for idx, trade in self.trades_df.iterrows():
            values = [trade[col] for col in self.tree['columns'][:-1]]  # Exclude Balance Impact
            
            # Calculate balance impact
            if pd.notna(trade['P/L ($)']):
                pl = float(trade['P/L ($)'])
                balance_impact = f"{(pl / self.account_balance * 100):.2f}%" if self.account_balance > 0 else "N/A"
            else:
                balance_impact = "N/A"
            
            values.append(balance_impact)
            
            # Add row with color based on P/L
            if pd.notna(trade['P/L ($)']):
                pl = float(trade['P/L ($)'])
                tag = 'profit' if pl > 0 else 'loss'
                self.tree.insert('', tk.END, values=values, tags=(tag,))
            else:
                self.tree.insert('', tk.END, values=values)
        
        # Configure row colors
        self.tree.tag_configure('profit', foreground='green')
        self.tree.tag_configure('loss', foreground='red')
    
    def view_trade_details(self, event):
        if event is not None:
            item = self.tree.selection()[0]
        else:
            item = self.tree.selection()[0]
        
        trade_values = self.tree.item(item)['values']
        trade_data = self.trades_df.iloc[self.tree.index(item)]
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Trade Details")
        popup.geometry("800x900")
        
        # Create main container with scrollbar
        main_canvas = tk.Canvas(popup)
        scrollbar = ttk.Scrollbar(popup, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Trade Information Section
        info_frame = ttk.LabelFrame(scrollable_frame, text="Trade Information")
        info_frame.pack(fill=tk.X, padx=10, pady=5, ipadx=5, ipady=5)
        
        # Create two columns for trade details
        left_frame = ttk.Frame(info_frame)
        right_frame = ttk.Frame(info_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Distribute fields between columns
        columns = list(self.trades_df.columns)
        mid_point = len(columns) // 2
        
        for i, col in enumerate(columns):
            frame = left_frame if i < mid_point else right_frame
            field_frame = ttk.Frame(frame)
            field_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(field_frame, text=f"{col}:", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)
            value_label = ttk.Label(field_frame, text=str(trade_data[col]))
            value_label.pack(side=tk.LEFT, padx=5)
            
            # Color P/L values
            if col in ['P/L ($)', 'P/L (%)'] and trade_data[col]:
                try:
                    value = float(trade_data[col])
                    color = 'green' if value > 0 else 'red'
                    value_label.configure(foreground=color)
                except ValueError:
                    pass
        
        # Screenshots Section
        screenshots_frame = ttk.LabelFrame(scrollable_frame, text="Trade Screenshots")
        screenshots_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        screenshot_path = trade_data['Screenshot Path']
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                # Create image viewer with zoom capabilities
                img = Image.open(screenshot_path)
                # Calculate aspect ratio
                aspect_ratio = img.width / img.height
                
                # Set maximum dimensions while maintaining aspect ratio
                max_width = 700
                max_height = 500
                
                if img.width > max_width or img.height > max_height:
                    if aspect_ratio > 1:
                        new_width = max_width
                        new_height = int(max_width / aspect_ratio)
                    else:
                        new_height = max_height
                        new_width = int(max_height * aspect_ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img)
                
                # Create canvas for image
                img_canvas = tk.Canvas(screenshots_frame, width=max_width, height=max_height)
                img_canvas.pack(pady=5)
                
                # Add image to canvas
                img_canvas.create_image(max_width//2, max_height//2, image=photo, anchor=tk.CENTER)
                img_canvas.image = photo  # Keep a reference
                
                # Add zoom buttons
                zoom_frame = ttk.Frame(screenshots_frame)
                zoom_frame.pack(pady=5)
                
                def zoom(factor):
                    nonlocal img, photo
                    new_width = int(img.width * factor)
                    new_height = int(img.height * factor)
                    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(resized)
                    img_canvas.delete("all")
                    img_canvas.create_image(max_width//2, max_height//2, image=photo, anchor=tk.CENTER)
                    img_canvas.image = photo
                
                ttk.Button(zoom_frame, text="Zoom In", command=lambda: zoom(1.2)).pack(side=tk.LEFT, padx=5)
                ttk.Button(zoom_frame, text="Zoom Out", command=lambda: zoom(0.8)).pack(side=tk.LEFT, padx=5)
                ttk.Button(zoom_frame, text="Reset", command=lambda: zoom(1.0)).pack(side=tk.LEFT, padx=5)
                
            except Exception as e:
                ttk.Label(screenshots_frame, text=f"Error loading image: {str(e)}").pack(pady=10)
        else:
            ttk.Label(screenshots_frame, text="No screenshot available").pack(pady=10)
        
        # Pack main container and scrollbar
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add close button
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
    
    def update_account_balance(self):
        try:
            new_balance = float(self.balance_var.get())
            self.account_balance = new_balance
            self.save_account_balance()
            messagebox.showinfo("Success", "Account balance updated successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for account balance.")

    def show_context_menu(self, event):
        if self.tree.selection():
            self.context_menu.post(event.x_root, event.y_root)

    def delete_selected_trade(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a trade to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected trade(s)?"):
            for item in selected_items:
                index = self.tree.index(item)
                self.trades_df = self.trades_df.drop(index)
            
            self.save_trades()
            self.update_trade_list()
            self.update_statistics()
            messagebox.showinfo("Success", "Trade(s) deleted successfully!")

    def create_trade_entry_tab(self):
        entry_frame = ttk.Frame(self.notebook)
        self.notebook.add(entry_frame, text="New Trade")
        
        # Create form fields
        fields = [
            ('Date', None),  # Will be replaced with DateEntry
            ('Ticker', ''),
            ('Setup Type', self.setup_types),
            ('Position', ['Long', 'Short']),
            ('Entry Price', ''),
            ('Stop Loss', ''),
            ('Position Size', ''),
            ('Target', ''),
            ('Exit Price', ''),
            ('Screenshot Path', ''),
            ('Notes', '')
        ]
        
        self.entries = {}
        for i, (label, default) in enumerate(fields):
            ttk.Label(entry_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            
            if label == 'Date':
                # Create date picker
                entry = DateEntry(entry_frame, width=20, background='darkblue',
                                foreground='white', borderwidth=2,
                                date_pattern='yyyy-mm-dd')
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
                self.entries[label] = entry
                
            elif label == 'Ticker':
                # Create frame for ticker selection
                ticker_frame = ttk.Frame(entry_frame)
                ticker_frame.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
                
                # Create combobox for instrument type
                instrument_var = tk.StringVar()
                instrument_combo = ttk.Combobox(ticker_frame, textvariable=instrument_var,
                                              values=['Forex', 'Indices', 'Commodities'])
                instrument_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Create combobox for specific ticker
                ticker_var = tk.StringVar()
                ticker_combo = ttk.Combobox(ticker_frame, textvariable=ticker_var)
                ticker_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
                
                def update_tickers(*args):
                    if instrument_var.get() == 'Forex':
                        ticker_combo['values'] = self.forex_pairs
                    elif instrument_var.get() == 'Indices':
                        ticker_combo['values'] = self.indices
                    elif instrument_var.get() == 'Commodities':
                        ticker_combo['values'] = self.commodities
                    ticker_combo.set('')
                
                instrument_combo.bind('<<ComboboxSelected>>', update_tickers)
                self.entries[label] = ticker_var
                
            elif isinstance(default, list):
                # Create dropdown for lists
                var = tk.StringVar()
                entry = ttk.Combobox(entry_frame, textvariable=var, values=default)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
                self.entries[label] = var
            elif label == 'Notes':
                # Create text area for notes
                entry = tk.Text(entry_frame, height=4, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
                self.entries[label] = entry
            elif label == 'Screenshot Path':
                # Create frame for screenshot path and browse button
                path_frame = ttk.Frame(entry_frame)
                path_frame.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
                
                entry = ttk.Entry(path_frame)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                browse_btn = ttk.Button(path_frame, text="Browse",
                                      command=lambda e=entry: self.browse_screenshot(e))
                browse_btn.pack(side=tk.RIGHT, padx=5)
                
                self.entries[label] = entry
            else:
                # Create regular entry
                var = tk.StringVar(value=default)
                entry = ttk.Entry(entry_frame, textvariable=var)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
                self.entries[label] = var
        
        # Add save button
        save_btn = ttk.Button(entry_frame, text="Save Trade",
                             command=self.save_trade)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        # Configure grid
        entry_frame.columnconfigure(1, weight=1)

    def create_trade_list_tab(self):
        list_frame = ttk.Frame(self.notebook)
        self.notebook.add(list_frame, text="Trade List")
        
        # Create buttons frame
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        delete_btn = ttk.Button(buttons_frame, text="Delete Selected Trade",
                               command=self.delete_selected_trade)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(buttons_frame, text="Refresh List",
                               command=self.update_trade_list)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ['Date', 'Ticker', 'Setup Type', 'Position', 'Entry Price',
                  'Exit Price', 'P/L ($)', 'P/L (%)', 'Balance Impact']
        
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Add headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Pack elements
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click event and right-click menu
        self.tree.bind('<Double-1>', self.view_trade_details)
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Create right-click menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="View Details", command=lambda: self.view_trade_details(None))
        self.context_menu.add_command(label="Delete Trade", command=self.delete_selected_trade)
        
        # Load existing trades
        self.update_trade_list()

    def create_statistics_tab(self):
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        
        # Create main container with grid
        main_container = ttk.Frame(stats_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create statistics display
        self.stats_tree = ttk.Treeview(main_container, columns=['Metric', 'Value'],
                                      show='headings', height=10)
        self.stats_tree.heading('Metric', text='Metric')
        self.stats_tree.heading('Value', text='Value')
        
        self.stats_tree.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        
        # Create frame for charts
        self.charts_frame = ttk.Frame(main_container)
        self.charts_frame.grid(row=1, column=0, sticky='nsew')
        
        # Add update button
        update_btn = ttk.Button(main_container, text="Update Statistics",
                               command=self.update_statistics)
        update_btn.grid(row=2, column=0, pady=10)
        
        # Configure grid weights
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        self.update_statistics()

    def create_account_settings_tab(self):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Account Settings")
        
        # Account Balance Frame
        balance_frame = ttk.LabelFrame(settings_frame, text="Account Balance")
        balance_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(balance_frame, text="Current Balance: $").pack(side=tk.LEFT, padx=5)
        self.balance_var = tk.StringVar(value=f"{self.account_balance:.2f}")
        balance_entry = ttk.Entry(balance_frame, textvariable=self.balance_var)
        balance_entry.pack(side=tk.LEFT, padx=5)
        
        update_balance_btn = ttk.Button(balance_frame, text="Update Balance",
                                      command=self.update_account_balance)
        update_balance_btn.pack(side=tk.LEFT, padx=5)

        # Appearance Settings Frame
        appearance_frame = ttk.LabelFrame(settings_frame, text="Appearance Settings")
        appearance_frame.pack(fill=tk.X, padx=10, pady=10)

        # Theme selection
        ttk.Label(appearance_frame, text="Theme:").pack(side=tk.LEFT, padx=5)
        theme_combo = ttk.Combobox(appearance_frame, textvariable=self.theme_var,
                                 values=["arc", "clam", "alt", "default", "classic"])
        theme_combo.pack(side=tk.LEFT, padx=5)
        theme_combo.bind('<<ComboboxSelected>>', self.update_theme)

        # Color scheme selection
        colors_frame = ttk.Frame(appearance_frame)
        colors_frame.pack(fill=tk.X, padx=5, pady=5)

        # Profit color
        ttk.Label(colors_frame, text="Profit Color:").pack(side=tk.LEFT, padx=5)
        profit_color_btn = ttk.Button(colors_frame, text="Choose",
                                    command=lambda: self.choose_color('profit'))
        profit_color_btn.pack(side=tk.LEFT, padx=5)

        # Loss color
        ttk.Label(colors_frame, text="Loss Color:").pack(side=tk.LEFT, padx=5)
        loss_color_btn = ttk.Button(colors_frame, text="Choose",
                                  command=lambda: self.choose_color('loss'))
        loss_color_btn.pack(side=tk.LEFT, padx=5)

        # Chart Settings Frame
        chart_frame = ttk.LabelFrame(settings_frame, text="Chart Settings")
        chart_frame.pack(fill=tk.X, padx=10, pady=10)

        # Chart style
        ttk.Label(chart_frame, text="Chart Style:").pack(side=tk.LEFT, padx=5)
        chart_style_combo = ttk.Combobox(chart_frame, textvariable=self.chart_style,
                                       values=list(self.chart_styles.keys()))
        chart_style_combo.pack(side=tk.LEFT, padx=5)
        chart_style_combo.bind('<<ComboboxSelected>>', lambda e: self.update_statistics())

if __name__ == "__main__":
    app = TradingJournalApp()
    app.root.mainloop() 