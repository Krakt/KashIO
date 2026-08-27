import customtkinter as ctk
from widgets.list_manager_widget import ListManager
from widgets.email_widget import EmailManagement

class SettingsTab(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, **kwargs)
        self.app_controller = app_controller

        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self.method_list_section = ctk.CTkFrame(master=self)
        self.method_list_section.grid(row=0, column=0, padx=10, pady=10, sticky="news")

        self.method_payment = ListManager(self.method_list_section, title="Methode de payement", initial_items=None)
        self.method_payment.grid(row=0, column=0, padx=10, pady=10, sticky="news")

        self.email_section = ctk.CTkFrame(master=self)
        self.email_section.grid(row=0, column=1, padx=10, pady=10, sticky="news")

        self.email = EmailManagement(self.email_section, title="Email configuration", initial_items=None)
        self.email.grid(row=0, column=0, padx=10, pady=10, sticky="news")