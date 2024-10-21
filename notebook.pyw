import requests
from tkinter import *
from tkinter.ttk import *


SERVERS = ['desktop-s9rdtak', 'desktop-c0jr8d3', 'localhost']


class App(Tk):
    def __init__(self):
        super().__init__()
        self.title('Caderno Nota Paraná')
        self.geometry('400x450')
        self.notebook = Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.after(1000, self.load_closures)
        self.mainloop()
    

    def load_closures(self):
        session = requests.Session()

        for server in SERVERS:
            try:
                res = session.get(f'http://{server}:8000/closures', timeout=0.5)
            except Exception:
                continue

            if not res.ok or 'empty' in res.text:
                continue

            records = res.json()
            self.setup_tree(server, records)

    
    def setup_tree(self, server, records):
        frame = Frame(self.notebook)
        frame.pack(fill=BOTH, expand=True)
        self.notebook.add(frame, text=server)
        treeview = Treeview(frame, columns=('user', 'total', 'date', 'collector'), show='headings')
        treeview.heading('user', text='Usuário')
        treeview.heading('total', text='Total')
        treeview.heading('date', text='Data')
        treeview.heading('collector', text='Coletor')
        treeview.column('user', width=65)
        treeview.column('total', anchor=CENTER, width=25)
        treeview.column('date', anchor=CENTER, width=25)
        treeview.column('collector', anchor=CENTER, width=25)

        for record in records:
            treeview.insert('', END, values=(record['user'], record['total'], record['date'], record['collector']))

        treeview.pack(fill=BOTH, expand=True)


if __name__ == '__main__':
    App()