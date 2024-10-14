import requests
from tkinter import *
from tkinter.ttk import *


SERVERS = ['localhost:8000']


class App(Tk):
    def __init__(self):
        super().__init__()
        self.title('Caderno Nota Paraná')
        self.geometry('800x450')
        self.notebook = Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)

        for server in SERVERS:
            res = requests.get(f'http://{server}/closures')

            if not res.ok or 'empty' in res.text:
                continue

            res = res.json()
            frame = Frame(self.notebook)
            frame.pack(fill=BOTH, expand=True)
            self.notebook.add(frame, text=server)
            treeview = Treeview(frame, columns=('user', 'total', 'date', 'collector'), show='headings')
            treeview.heading('user', text='Usuário')
            treeview.heading('total', text='Total')
            treeview.heading('date', text='Data')
            treeview.heading('collector', text='Coletor')
            treeview.column('total', anchor=E)
            treeview.column('date', anchor=CENTER)
            treeview.column('collector', anchor=CENTER)

            for record in res:
                treeview.insert('', END, values=(
                    record['user'],
                    record['total'],
                    record['date'],
                    record['collector'],
                ))

            treeview.pack(fill=BOTH, expand=True)

        self.mainloop()
    

if __name__ == '__main__':
    App()