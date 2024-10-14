from tkinter import *
from tkinter.ttk import *
from usersframe import UsersFrame
from collectorsframe import CollectorsFrame
from datetime import datetime
from auth import User, login
from functools import partial
from tkinter.messagebox import showerror
from threading import Timer
from os.path import exists
import sqlite3
import os


DB_NAME = os.path.expanduser(r'~\closures.db3')


class App(Tk):
    def __init__(self):
        super().__init__()
        Style().configure('TButton', font=('Arial', 12, 'bold'))
        self.title('Caderno Nota Paraná')
        # self.geometry('800x100')
        self.selected_user: User = None
        self.selected_collector: str = None
        self.usersframe = UsersFrame(self, partial(self.on_user_selected))
        self.collectorsframe = CollectorsFrame(self, partial(self.on_collector_selected))
        self.waitlbl = Label(self, text='Realizando fechamento, aguarde...', font=('Arial', 16, 'bold'))
        self.usersframe.pack(expand=True)
        self.mainloop()
    

    def on_user_selected(self, user: User):
        self.selected_user = user
        self.usersframe.pack_forget()
        self.collectorsframe.pack(expand=True)
    

    def on_collector_selected(self, collector: str):
        self.selected_collector = collector
        self.collectorsframe.pack_forget()
        self.waitlbl.pack(expand=True)
        self.config(cursor='watch')
        Timer(0.5, partial(self.make_closure)).start()
    

    def make_closure(self):
        if (session := login(self.selected_user)) == False:
            showerror('Erro', f'Não foi possível logar o usuário {self.selected_user.name}.\nFeche o programa e tente novamente')
            self.waitlbl.config(text='Feche o programa e tente novamente')
            self.config(cursor='arrow')
            return
        
        res = session.get(f'https://notaparana.pr.gov.br/nfprweb/app/v1/datatable/documentoFiscalDoado/?mes={datetime.now().month}&ano={datetime.now().year}&draw=1&start=0&length=1&_=1728757253261')
        res = res.json()
        conn = sqlite3.connect(DB_NAME)
        conn.execute(
            'INSERT INTO closures (user, total, date, collector) VALUES (?, ?, ?, ?)',
            (self.selected_user.name, res['recordsTotal'], datetime.now().strftime('%d/%m/%Y'), self.selected_collector)
        )
        conn.commit()
        self.waitlbl.config(text='Fechamento Realizado Com Sucesso!')
        self.config(cursor='arrow')


def create_database():
    conn = sqlite3.connect(DB_NAME)
    conn.execute('CREATE TABLE closures (id INTEGER PRIMARY KEY, user TEXT, total INTEGER, date TEXT, collector TEXT)')


if __name__ == '__main__':
    if not exists(DB_NAME):
        create_database()

    App()