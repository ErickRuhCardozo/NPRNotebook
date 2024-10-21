import os
import json
import sqlite3
from tkinter import *
from tkinter.ttk import *
from os.path import exists
from threading import Timer
from requests import Session
from datetime import datetime
from functools import partial
from urllib.parse import urlparse
from dataclasses import dataclass
from tkinter.messagebox import showerror


DB_NAME = os.path.expanduser(r'~\closures.db3')


@dataclass
class User:
    name: str
    ssn: str
    password: str


class App(Tk):
    def __init__(self):
        super().__init__()
        Style().configure('TButton', font=('Arial', 12, 'bold'))
        self.title('Caderno Nota Paraná')
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
        if (session := self.login()) == False:
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
    

    def login(self) -> bool | Session:
        session = Session()
        session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        payload = {'attribute': self.selected_user.ssn, 'password': self.selected_user.password}
        attempts = 0
        
        while attempts < 3:
            attempts += 1
            response = session.get('https://notaparana.pr.gov.br/nfprweb/ContaCorrente')
            url = urlparse(response.url) # Get the step param from the system
            response = session.post('https://authz.identidadedigital.pr.gov.br/cidadao_authz/api/v1/authorize', params=url.query, data=payload)

            if response.status_code != 200:
                return False

            if 'Ops!' in response.text:
                session.get('https://notaparana.pr.gov.br/nfprweb/publico/sair')
            elif 'MINHA CONTA CORRENTE' in response.text:
                return session
        
        return False


class CollectorsFrame(Frame):
    def __init__(self, master, command):
        super().__init__(master)
        Label(self, text='Informe o Coletor:', font=('Arial', 14)).pack(pady=5)
        self.btns = []

        for collector in ['Antonio', 'Claudinei', 'Vitor', 'Digitada']:
            self.btns.append(
                Button(
                    self,
                    text=collector,
                    command=partial(command, collector)
                )
            )
        
        [btn.pack(side=LEFT) for btn in self.btns]


class UsersFrame(Frame):
    def __init__(self, master, command):
        super().__init__(master)
        Label(self, text='Informe o Usuário do fechamento:', font=('Arial', 14)).pack(pady=5)
        self.btns = []
        
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        for user in users:
            self.btns.append(
                Button(
                    self,
                    text=f'{user['name']}\n{user['ssn']}',
                    command=partial(command, user)
                )
            )
        
        [btn.pack(side=LEFT, padx=3) for btn in self.btns]


if __name__ == '__main__':
    if not exists(DB_NAME):
       conn = sqlite3.connect(DB_NAME)
       conn.execute('CREATE TABLE closures (id INTEGER PRIMARY KEY, user TEXT, total INTEGER, date TEXT, collector TEXT)')

    App()