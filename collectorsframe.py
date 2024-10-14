from tkinter import *
from tkinter.ttk import *
from functools import partial


COLLECTORS = ['Antonio', 'Claudinei', 'Vitor', 'Digitada']


class CollectorsFrame(Frame):
    def __init__(self, master, command):
        super().__init__(master)
        Label(
            self,
            text='Informe o Coletor:',
            font=('Arial', 14)
        ).pack(pady=5)
        self.btns = []

        for collector in COLLECTORS:
            self.btns.append(
                Button(
                    self,
                    text=collector,
                    command=partial(command, collector)
                )
            )
        
        [btn.pack(side=LEFT) for btn in self.btns]


if __name__ == '__main__':
    app = Tk()
    CollectorsFrame(app, lambda x: print(x)).pack()
    app.mainloop()