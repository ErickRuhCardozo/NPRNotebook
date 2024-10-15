import json
from auth import User, UserDecoder
from functools import partial
from tkinter import *
from tkinter.ttk import *


class UsersFrame(Frame):
    def __init__(self, master, command):
        super().__init__(master)
        Label(
            self,
            text='Informe o Usuário do fechamento:',
            font=('Arial', 14)
        ).pack(pady=5)
        self.btns = []

        with open('users.json', 'r') as f:
            users = json.load(f, cls=UserDecoder)
        
        for user in users:
            self.btns.append(
                Button(
                    self,
                    text=f'{user.name}\n{user.ssn}',
                    command=partial(command, user)
                )
            )
        
        [btn.pack(side=LEFT, padx=3) for btn in self.btns]


if __name__ == '__main__':
    app = Tk()
    UsersFrame(app, lambda u: print(u.name)).pack()
    app.mainloop()