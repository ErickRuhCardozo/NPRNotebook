import re
import requests
import subprocess
from tkinter import *
from tkinter.ttk import *


class App(Tk):
    def __init__(self):
        super().__init__()
        self.title('Caderno Nota Paraná')
        self.geometry('400x450')
        self.notebook = Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)
        session = requests.Session()
        ips = App.get_ips()

        for ip in ips:
            try:
                res = session.get(f'http://{ip}:8000/closures', timeout=1)
            except Exception:
                continue

            if not res.ok or 'empty' in res.text:
                continue

            records = res.json()
            self.setup_tree(ip, records)


        self.mainloop()

    
    def setup_tree(self, ip, records):
        frame = Frame(self.notebook)
        frame.pack(fill=BOTH, expand=True)
        self.notebook.add(frame, text=ip)
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

    

    @staticmethod
    def get_ips():
        pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        output = subprocess.check_output(('arp', '-a'))
        return pattern.findall(output.decode('iso-8859-1'))
    

if __name__ == '__main__':
    App()