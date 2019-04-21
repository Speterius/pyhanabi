import tkinter


class LoginWindow(tkinter.Tk):
    def __init__(self):
        super().__init__()

        # Widgets
        self.label_username = tkinter.Label(self, text="Username (max 10 char.): ")
        self.label_IP = tkinter.Label(self, text="Server IP: ")
        self.label_port = tkinter.Label(self, text="Server Port: ")
        self.entry_username = tkinter.Entry(self)
        self.entry_IP = tkinter.Entry(self)
        self.entry_port = tkinter.Entry(self)
        self.login_btn = tkinter.Button(self, text='Connect to Server', command=self.connect_clicked)

        # Placement:
        self.label_username.grid(row=0, column=0)
        self.label_IP.grid(row=1, column=0)
        self.label_port.grid(row=2, column=0)

        self.entry_username.grid(row=0, column=1)
        self.entry_IP.grid(row=1, column=1)
        self.entry_port.grid(row=2, column=1)

        self.login_btn.grid(columnspan=2)

    def connect_clicked(self):
        name = self.entry_username.get()
        IP = self.entry_IP.get()
        port = self.entry_port.get()

        print(f'Name: {name}, IP: {IP}, Port: {port}')


root = LoginWindow()
root.mainloop()
