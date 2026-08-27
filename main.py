import customtkinter as ctk
from config import CONFIG, CURRENT_LANG
from database import init_db
from views.tab_view import MyTabView
from controllers.app_controller import AppController

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KashIO")
        self.geometry("800x600")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize the controller, passing self to it
        self.controller = AppController(self)

        self.tab_view = MyTabView(master=self, app_controller=self.controller)
        self.tab_view.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")


    def on_closing(self):
        """Fermeture propre de l'application et des graphiques"""
        import matplotlib.pyplot as plt
        
        # 1. Fermer toutes les figures Matplotlib
        plt.close('all')
        
        # 2. Détruire l'application Tkinter
        self.destroy()
        
        # 3. Quitter explicitement le processus Python
        import sys
        sys.exit(0)


if __name__ == "__main__":
    app = App()
    app._set_appearance_mode("dark")  # Set the appearance mode to dark
    init_db()  # Initialize the database
    #seed_test_data() # For development purposes only
    
    app.mainloop()