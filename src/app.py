import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import messagebox
from .data_manager import DataManager
from .plotter import Plotter
import datetime

class CalorieApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Счетчик калорий")

        self.root.geometry('800x600')

        self.data_manager = DataManager()
        self.load_data()
        self.create_widgets()

    def load_data(self):
        self.dishes = self.data_manager.load_dishes()
        self.consumption_logs = self.data_manager.load_consumption_logs()

    def save_data(self):
        self.data_manager.save_dishes(self.dishes)
        self.data_manager.save_consumption_logs(self.consumption_logs)

    def create_widgets(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Данные", menu=data_menu)
        data_menu.add_command(label="Очистить все данные", command=self.clear_all_data)

        tabControl = ttk.Notebook(self.root, bootstyle="primary")

        self.tab1 = ttk.Frame(tabControl)
        self.tab2 = ttk.Frame(tabControl)
        self.tab3 = ttk.Frame(tabControl)

        tabControl.add(self.tab1, text='Управление блюдами')
        tabControl.add(self.tab2, text='Логирование потребления')
        tabControl.add(self.tab3, text='Просмотр статистики')

        tabControl.pack(expand=1, fill="both")

        self.create_tab1_widgets()
        self.create_tab2_widgets()
        self.create_tab3_widgets()

    def create_tab1_widgets(self):
        frame = ttk.Labelframe(self.tab1, text='Добавить / Редактировать блюдо', padding=10)
        frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame, text='Название блюда:').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.dish_name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.dish_name_var, bootstyle="info").grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(frame, text='Калорий на 100г:').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.calories_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.calories_var, bootstyle="info").grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text='Добавить / Обновить блюдо', command=self.add_update_dish, bootstyle="success").pack(side='left', padx=5)
        ttk.Button(button_frame, text='Очистить блюда', command=self.clear_dishes, bootstyle="danger").pack(side='left', padx=5)

        frame.columnconfigure(1, weight=1)

        search_frame = ttk.Frame(self.tab1)
        search_frame.pack(padx=10, pady=5, fill='x')
        ttk.Label(search_frame, text='Поиск блюд:').pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.update_dish_listbox)
        ttk.Entry(search_frame, textvariable=self.search_var, bootstyle="info").pack(side='left', padx=5, fill='x', expand=True)

        listbox_frame = ttk.Frame(self.tab1)
        listbox_frame.pack(padx=10, pady=5, fill='both', expand=True)
        self.dish_listbox = tk.Listbox(listbox_frame)
        self.dish_listbox.pack(side='left', fill='both', expand=True)
        self.dish_listbox.bind('<<ListboxSelect>>', self.on_dish_select)

        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.dish_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.dish_listbox.config(yscrollcommand=scrollbar.set)

        self.update_dish_listbox()

    def add_update_dish(self):
        name = self.dish_name_var.get().strip()
        try:
            calories = float(self.calories_var.get().replace(',', '.'))
            if calories <= 0:
                raise ValueError
        except ValueError:
            Messagebox.show_warning("Пожалуйста, введите корректное числовое значение калорийности.", "Ошибка ввода")
            return
        if name:
            self.dishes[name] = calories
            self.save_data()
            self.update_dish_listbox()
            self.update_dish_combobox()  # Обновление значений комбобокса
            Messagebox.show_info(f"Блюдо '{name}' было добавлено/обновлено.", "Успех")
            self.dish_name_var.set('')
            self.calories_var.set('')
        else:
            Messagebox.show_warning("Пожалуйста, введите название блюда.", "Ошибка ввода")

    def update_dish_listbox(self, *args):
        search_text = self.search_var.get().lower()
        self.dish_listbox.delete(0, tk.END)
        for dish in sorted(self.dishes.keys()):
            if search_text in dish.lower():
                self.dish_listbox.insert(tk.END, dish)

    def on_dish_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            dish_name = event.widget.get(index)
            self.dish_name_var.set(dish_name)
            self.calories_var.set(self.dishes[dish_name])

    def clear_dishes(self):
        if Messagebox.yesno("Подтверждение", "Вы уверены, что хотите удалить все блюда? Это действие необратимо."):
            self.dishes.clear()
            self.save_data()
            self.update_dish_listbox()
            self.update_dish_combobox()
            Messagebox.show_info("Все блюда были удалены.", "Успех")

    def create_tab2_widgets(self):
        frame = ttk.Labelframe(self.tab2, text='Логирование потребления', padding=10)
        frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame, text='Выберите блюдо:').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.selected_dish_var = tk.StringVar()
        self.dish_combobox = ttk.Combobox(frame, textvariable=self.selected_dish_var, bootstyle="info")
        self.dish_combobox['values'] = sorted(self.dishes.keys())
        self.dish_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(frame, text='Количество (г):').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.amount_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.amount_var, bootstyle="info").grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text='Залогировать потребление', command=self.log_consumption, bootstyle="success").pack(side='left', padx=5)
        ttk.Button(button_frame, text='Очистить логи потребления', command=self.clear_consumption_logs, bootstyle="danger").pack(side='left', padx=5)

        frame.columnconfigure(1, weight=1)

        listbox_frame = ttk.Frame(self.tab2)
        listbox_frame.pack(padx=10, pady=5, fill='both', expand=True)
        self.consumption_listbox = tk.Listbox(listbox_frame)
        self.consumption_listbox.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.consumption_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.consumption_listbox.config(yscrollcommand=scrollbar.set)

        self.update_consumption_listbox()

    def update_dish_combobox(self):
        self.dish_combobox['values'] = sorted(self.dishes.keys())

    def log_consumption(self):
        dish_name = self.selected_dish_var.get()
        try:
            amount = float(self.amount_var.get().replace(',', '.'))
            if amount <= 0:
                raise ValueError
        except ValueError:
            Messagebox.show_warning("Пожалуйста, введите корректное числовое значение количества.", "Ошибка ввода")
            return
        if dish_name in self.dishes:
            entry = {
                'dish': dish_name,
                'amount': amount,
                'date': datetime.date.today().isoformat()
            }
            self.consumption_logs.append(entry)
            self.save_data()
            self.update_consumption_listbox()
            Messagebox.show_info(f"Потребление {amount}г '{dish_name}' было залогировано.", "Успех")
            self.amount_var.set('')
        else:
            Messagebox.show_warning("Пожалуйста, выберите корректное блюдо.", "Ошибка ввода")

    def update_consumption_listbox(self):
        self.consumption_listbox.delete(0, tk.END)
        for entry in self.consumption_logs:
            line = f"{entry['date']}: {entry['dish']} - {entry['amount']}г"
            self.consumption_listbox.insert(tk.END, line)

    def clear_consumption_logs(self):
        if Messagebox.yesno("Подтверждение", "Вы уверены, что хотите удалить все логи потребления? Это действие необратимо."):
            self.consumption_logs.clear()
            self.save_data()
            self.update_consumption_listbox()
            Messagebox.show_info("Все логи потребления были удалены.", "Успех")

    def create_tab3_widgets(self):
        frame = ttk.Labelframe(self.tab3, text='Выберите диапазон дат', padding=10)
        frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame, text='Начальная дата (ГГГГ-ММ-ДД):').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.start_date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.start_date_var, bootstyle="info").grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(frame, text='Конечная дата (ГГГГ-ММ-ДД):').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.end_date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.end_date_var, bootstyle="info").grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text='Показать статистику', command=self.show_statistics, bootstyle="primary").pack(padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

    def show_statistics(self):
        start_date_str = self.start_date_var.get()
        end_date_str = self.end_date_var.get()
        try:
            start_date = datetime.date.fromisoformat(start_date_str)
            end_date = datetime.date.fromisoformat(end_date_str)
            if start_date > end_date:
                raise ValueError("Начальная дата должна быть до конечной даты.")
        except ValueError as e:
            Messagebox.show_error(str(e), "Ошибка даты")
            return

        filtered_logs = [entry for entry in self.consumption_logs
                         if start_date <= datetime.date.fromisoformat(entry['date']) <= end_date]

        if not filtered_logs:
            Messagebox.show_info("Нет данных о потреблении в выбранном диапазоне дат.", "Нет данных")


        plotter = Plotter(self.root)
        plotter.plot_calories_over_time(start_date, end_date, filtered_logs, self.dishes)

    def clear_all_data(self):
        if Messagebox.yesno("Подтверждение", "Вы уверены, что хотите удалить все данные? Это действие необратимо."):
            self.dishes.clear()
            self.consumption_logs.clear()
            self.save_data()
            self.update_dish_listbox()
            self.update_consumption_listbox()
            self.update_dish_combobox()
            Messagebox.show_info("Все данные были удалены.", "Успех")

    def on_closing(self):
        self.save_data()
        self.root.destroy()
