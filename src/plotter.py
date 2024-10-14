import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import matplotlib.dates as mdates
from scipy.interpolate import interp1d
import datetime
from ttkbootstrap.dialogs import Messagebox

class Plotter:
    def __init__(self, root):
        self.root = root

    def plot_calories_over_time(self, start_date, end_date, consumption_logs, dishes):
        calories_per_day = {}
        for entry in consumption_logs:
            date = entry['date']
            calories = dishes[entry['dish']] * (entry['amount'] / 100)
            calories_per_day.setdefault(date, 0)
            calories_per_day[date] += calories

        total_days = (end_date - start_date).days + 1
        dates = [start_date + datetime.timedelta(days=i) for i in range(total_days)]
        dates_str = [date.strftime('%Y-%m-%d') for date in dates]
        calories_list = [calories_per_day.get(date_str, 0) for date_str in dates_str]

        graph_window = tk.Toplevel(self.root)
        graph_window.title("Потребленные калории с течением времени")
        graph_window.geometry('800x600')

        fig = Figure(figsize=(8, 4), facecolor='white')
        ax = fig.add_subplot(111)
        line, = ax.plot(dates, calories_list, marker='o', linestyle='-', color='#1f77b4')
        ax.set_title('Потребленные калории с течением времени')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Калории')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_facecolor('#f0f0f0')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        dates_num = mdates.date2num(dates)
        calories_array = np.array(calories_list)

        if len(dates_num) < 2:
            Messagebox.show_info("Недостаточно данных для отображения интерактивного графика.", "Информация")
            return

        interp_func = interp1d(dates_num, calories_array, kind='linear', fill_value="extrapolate")

        def format_tooltip_text(xdata, ydata):
            date = mdates.num2date(xdata)
            date_str = date.strftime('%Y-%m-%d')
            return f"Дата: {date_str}\nКалории: {ydata:.2f}"

        annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def on_motion(event):
            if event.inaxes == ax:
                xdata = event.xdata
                if xdata is None:
                    return
                y_interp = interp_func(xdata)
                annot.xy = (xdata, y_interp)
                text = format_tooltip_text(xdata, y_interp)
                annot.set_text(text)
                annot.get_bbox_patch().set_alpha(0.8)
                annot.set_visible(True)
                canvas.draw_idle()
            else:
                annot.set_visible(False)
                canvas.draw_idle()

        canvas.mpl_connect("motion_notify_event", on_motion)
