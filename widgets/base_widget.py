import customtkinter as ctk

class BaseWidget(ctk.CTkFrame):
    """
    Parent class for the ticket and reduction widget
    """
    def __init__(self, master, title, headers, on_change=None, **kwargs):
        """
        Initialize the base widget and build the template.

        Args:
            title (str): The title of the section.
            on_change: default None. Used for bubbling button event clic.
        """
        super().__init__(master, **kwargs)
        self.on_change = on_change

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=8)
        self.grid_rowconfigure(2, weight=1)

        # Title
        self.title_lbl = ctk.CTkLabel(self, text=title, font=("Arial", 16, "bold"))
        self.title_lbl.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # Scrollable Frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        for i in range(len(headers)):
                    self.scrollable_frame.columnconfigure(i, weight=1)
        
        # Display the headers of the tickets
        for i, text in enumerate(headers):
            lbl = ctk.CTkLabel(self.scrollable_frame, text=text, font=("Arial", 12, "bold"))
            lbl.grid(row=0, column=i, padx=5, pady=5, sticky="news")

        # Add button (calls the child class method)
        self.button = ctk.CTkButton(self, text="Ajouter une ligne", command=self.add_row_and_notify)
        self.button.grid(row=2, column=0, pady=10, sticky="s")
        
        self.rows = []

    def create_new_row(self):
         raise NotImplementedError("Subclasses must implement create_new_row()")

    def add_row_and_notify(self):
        """Add a new row and bubble a notification"""
        self.create_new_row()
        if self.on_change:
            self.on_change()