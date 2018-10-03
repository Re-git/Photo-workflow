import datetime
import re
import tkinter as tk
from tkinter import ttk

from tinydb import Query, TinyDB

db = TinyDB('data.json')
query = Query()

def configure_styles(root):
    style = ttk.Style(root)
    style.configure("green.TLabel", foreground="black",
                    background="lawn green", padx=10)
    style.configure("white.TLabel", foreground="black",
                    background="gray89", padx=10)
    style.configure("red.TLabel", foreground="black",
                    background="indian red", padx=10)
    style.configure("system.TButton", foreground="black",
                    background="SystemButtonFace", padx=10)
    style.configure('Treeview', indent=10)


def flip_button_color(value):
    if value.get() == True:
        return "green.TLabel"
    else:
        return "red.TLabel"

def translate_month(date):
    """
    Translate month beween string and int value. 
    >>> translate_month(July)
    7
    >>> translate_month(5)
    May
    """
    months = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
              7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    if type(date) == int:
        return months[date]
    elif type(date) == str:
        for key, value in months.items():
            if date.lower() == value.lower():
                return key
            elif date.isdigit() and int(date) == key:
                return value


def sorted_by_date(iterable):
    return sorted(iterable, key=lambda item: item['date'], reverse=True)


class Date_browser_frame(tk.Frame):
    def __init__(self, paren):
        super().__init__(paren)
        self.columnconfigure(0, weight=1)

    def initUI(self):
        self.rowconfigure(0, weight=1)

        self.years_tree = ttk.Treeview(self)
        self.years_tree.heading('#0', text='Years')
        self.years_tree.column('#0', width=100)
        self.years_tree.bind('<<TreeviewSelect>>',
                             self.display_jobs_filtered_by_date)
        self.years_tree.grid(row=0, column=0, sticky='nsew')

        self.display_dates_list()

        add_job = ttk.Button(self, text='New Job',
                             command=lambda: self.create_empty_job())
        add_job.grid(row=1, column=0, sticky='we')

    def display_dates_list(self):
        dates_of_jobs = [int(item['date'][:4]) for item in sorted_by_date(db.all())]
        date_range = []
        for item in dates_of_jobs:
            if item not in date_range:
                date_range.append(item)
        for year in date_range:
            id = self.years_tree.insert('', tk.END, text=year)
            for month in ('January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December'):
                self.years_tree.insert(id, tk.END, text=month)

    def create_empty_job(self):
        num_of_rows = len(jobs_frame.displayed_jobs)
        current_date = str(datetime.datetime.now().date())
        id = db.insert({'date': current_date, 'client': 'client', 'model': 'model', 'previews': False,
                        'selection': False, 'hd': False, 'sent': False, 'payed': False, 'amount': ''})
        Jobs_frame.create_row(jobs_frame, (num_of_rows + 1), id, current_date,
                              'client', 'model', False, False, False, False, False, '')

    def display_jobs_filtered_by_date(self, lol):
        selected_item = self.years_tree.selection()[0]
        selected_text = str(self.years_tree.item(selected_item)['text'])
        parent_item = self.years_tree.parent(selected_item)
        parent_text = self.years_tree.item(parent_item)['text']

        # loop through displayed jobs and if they match selected text display them in jobs_frame
        for row in jobs_frame.displayed_jobs_vars.values():
            year = row['var_date'].get()[:4]
            month = row['var_date'].get()[5:7]

            if selected_text == translate_month(month) and str(parent_text) == year:
                found_jobs = db.search(query.date.matches(year + '-' + month))
                jobs_frame.display_jobs(sorted_by_date(found_jobs))
                break
            elif selected_text == year:
                found_jobs = db.search(query.date.matches(year))
                jobs_frame.display_jobs(sorted_by_date(found_jobs))
                break
            else:
                jobs_frame.display_jobs([])


class Jobs_frame(tk.Frame):

    displayed_jobs = {}
    displayed_jobs_vars = {}

    def __init__(self, paren):
        super().__init__(paren)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.scrollbar = ttk.Scrollbar(self)
        self.canvas = tk.Canvas(self, yscrollcommand=self.scrollbar.set)
        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.create_window(
            0, 0, anchor='nw', window=self.frame, tags="self.frame")
        self.canvas.bind("<Configure>", self.onCanvasConfigure)
        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.canvas.grid(column=0, row=0, sticky='nsew')
        self.canvas.columnconfigure(0, weight=1)
        self.scrollbar.grid(column=1, row=0, sticky='ns')

        self.frame.columnconfigure(1, weight=5)
        self.frame.columnconfigure(2, weight=5)

        # collect all of the jobs in database and display them
        jobs_sorted_by_date = sorted(
            db.all(), key=lambda item: item['date'], reverse=True)
        self.display_jobs(jobs_sorted_by_date)

    def onCanvasConfigure(self, event):
        # width is tweaked to account for window borders
        width = event.width - 4
        self.canvas.itemconfigure("self.frame", width=width)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def display_jobs(self, list_of_jobs):
        if not self.displayed_jobs:
            for i, e in enumerate(list_of_jobs):
                self.create_row(i, e.doc_id, *e.values())
        else:
            for row in self.displayed_jobs:
                for item in self.displayed_jobs[row].values():
                    try:
                        item.destroy()
                    except Exception:
                        pass
                del row
            for i, e in enumerate(list_of_jobs):
                self.create_row(i+1, e.doc_id, *e.values())

    def change_btn_color(self, id, button):
        # get button text option as string
        btn_name = button.cget('text').lower()
        btn_var = 'var_' + btn_name
        # flip bool Boolvar related to the button
        self.displayed_jobs_vars[id][btn_var].set(
            not self.displayed_jobs_vars[id][btn_var].get())
        db.update(
            {btn_name: self.displayed_jobs_vars[id][btn_var].get()}, doc_ids=[id])
        # change color of button
        self.displayed_jobs[id][btn_name].configure(
            style=flip_button_color(self.displayed_jobs_vars[id][btn_var]))

    def create_row(self, row, id, date, client, model, previews, selection, hd, sent, payed, amount):
        var_date = tk.StringVar(self, date)
        var_client = tk.StringVar(self, client)
        var_model = tk.StringVar(self, model)
        var_previews = tk.BooleanVar(self, previews)
        var_selection = tk.BooleanVar(self, selection)
        var_hd = tk.BooleanVar(self, hd)
        var_sent = tk.BooleanVar(self, sent)
        var_payed = tk.BooleanVar(self, payed)
        var_amount = tk.StringVar(self, amount)

        self.displayed_jobs_vars[id] = {
            'var_date': var_date,
            'var_client': var_client,
            'var_model': var_model,
            'var_previews': var_previews,
            'var_selection': var_selection,
            'var_hd': var_hd,
            'var_sent': var_sent,
            'var_payed': var_payed,
            'var_amount': var_amount
        }

        date = ttk.Entry(self.frame, textvariable=var_date, validate="focusout",
                         validatecommand=lambda: db.update({'date': self.displayed_jobs_vars[id]['var_date'].get()}, doc_ids=[id]))
        date.configure(style="white.TLabel")
        date.grid(column=0, row=row, padx=2, sticky='ew')

        client = ttk.Entry(self.frame, text=var_client, validate="focusout",
                           validatecommand=lambda: db.update({'client': self.displayed_jobs_vars[id]['var_client'].get()}, doc_ids=[id]))
        client.configure(style="white.TLabel")
        client.grid(column=1, row=row, padx=2, sticky='ew')

        model = ttk.Entry(self.frame, textvariable=var_model, validate="focusout",
                          validatecommand=lambda: db.update({'model': self.displayed_jobs_vars[id]['var_model'].get()}, doc_ids=[id]))
        model.configure(style="white.TLabel")
        model.grid(column=2, row=row, padx=2, pady=3, sticky='ew')

        previews = ttk.Button(self.frame, text='Previews')
        previews.configure(style=flip_button_color(
            var_previews), command=lambda: self.change_btn_color(id, previews))
        previews.grid(column=3, row=row, padx=2, sticky='ew')

        selection = ttk.Button(self.frame, text='Selection')
        selection.configure(style=flip_button_color(
            var_selection), command=lambda: self.change_btn_color(id, selection))
        selection.grid(column=4, row=row, padx=2, sticky='ew')

        hd = ttk.Button(self.frame, text='HD')
        hd.configure(style=flip_button_color(var_hd),
                     command=lambda: self.change_btn_color(id, hd))
        hd.grid(column=5, row=row, padx=2, sticky='ew')

        sent = ttk.Button(self.frame, text='Sent')
        sent.configure(style=flip_button_color(var_sent),
                       command=lambda: self.change_btn_color(id, sent))
        sent.grid(column=6, row=row, padx=2, sticky='ew')

        payed = ttk.Button(self.frame, text='Payed')
        payed.configure(style=flip_button_color(var_payed),
                        command=lambda: self.change_btn_color(id, payed))
        payed.grid(column=7, row=row, padx=2, sticky='ew')

        amount = ttk.Entry(self.frame, text=var_amount, validate="focusout",
                           validatecommand=lambda: db.update({'amount': self.displayed_jobs_vars[id]['var_amount'].get()}, doc_ids=[id]))
        amount.configure(style="white.TLabel")
        amount.grid(column=8, row=row, padx=2, sticky='ew')

        remove = ttk.Button(self.frame, text='x', width=1)
        remove.configure(style="system.TLabel",
                         command=lambda: self.remove_row(id))
        remove.grid(column=9, row=row, sticky='ew')

        self.displayed_jobs[id] = {
            'date': date,
            'client': client,
            'model': model,
            'previews': previews,
            'selection': selection,
            'hd': hd,
            'sent': sent,
            'payed': payed,
            'amount': amount,
            'remove': remove
        }

    def remove_row(self, id):
        for i in self.displayed_jobs[id].values():
            try:
                i.destroy()
            except Exception:
                pass
        del self.displayed_jobs[id]
        db.remove(doc_ids=[id])
        # update grid positions of remaining elements
        for r, row in enumerate(self.displayed_jobs.values()):
            for c, item in enumerate(row.values()):
                item.grid(row=r+1, column=c)

        if not self.displayed_jobs:
            num_of_rows = len(jobs_frame.displayed_jobs)
            id = db.insert({'date': 'date', 'client': 'client', 'model': 'model', 'previews': False,
                            'selection': False, 'hd': False, 'sent': False, 'payed': False, 'amount': ''})
            self.create_row((num_of_rows + 1), id, 'date', 'client',
                            'model', False, False, False, False, False, '')


class Search_frame(tk.Frame):
    def __init__(self, paren):
        super().__init__(paren)
        self.initUI()

    def findjobs(self, x):
        dates = db.search(query.date.matches(self.var_search.get()+'.*'))
        models = db.search(query.model.matches(self.var_search.get()+'.*'))
        clients = db.search(query.client.matches(self.var_search.get()+'.*'))
        search_results = dates + models + clients
        search_results_no_duplicates = []
        for i in search_results:
            if i not in search_results_no_duplicates:
                search_results_no_duplicates.append(i)
        jobs_frame.display_jobs(
            sorted_by_date(search_results_no_duplicates))

    def initUI(self):
        self.columnconfigure(1, weight=1)
        self.var_search = tk.StringVar()
        tk.Label(self, text='Search').grid(
            row=0, column=0, sticky='ew', pady=5, padx=5)
        self.search_entry = tk.Entry(self, text=self.var_search)
        self.search_entry.bind('<Return>', self.findjobs)
        self.search_entry.grid(row=0, column=1, sticky='ew', pady=5)


root = tk.Tk()
root.title("Photo assignments")
root.minsize(width=900, height=400)
configure_styles(root)
root.columnconfigure(0, weight=0)
root.columnconfigure(1, weight=3)
root.columnconfigure(2, weight=0)
root.rowconfigure(1, weight=1)
show_all = ttk.Button(root, text='Show all', command=lambda: jobs_frame.display_jobs(
    sorted_by_date(db.all())))
show_all.grid(row=0, column=0, sticky='we')

date_frame = Date_browser_frame(root)
jobs_frame = Jobs_frame(root)
search_frame = Search_frame(root)
date_frame.grid(column=0, row=1, rowspan=2, sticky='nsew')
jobs_frame.grid(column=1, row=1, sticky='nsew')
search_frame.grid(column=1, row=0, sticky='ew')

date_frame.initUI()

def on_exit():
    search_frame.search_entry.focus_set()
    root.after(200, lambda: root.destroy())

# Call this on exit
root.protocol("WM_DELETE_WINDOW", on_exit)

tk.mainloop()
