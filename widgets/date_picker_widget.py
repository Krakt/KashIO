import customtkinter as ctk

class DatePicker(ctk.CTkFrame):  # Hérite d'un Frame et non d'une Window (CTk)
    def __init__(self, master, on_button_click=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_button_click = on_button_click

        # Configuration de la disposition (par exemple en ligne)
        self.columnconfigure((0, 1, 2), weight=1)

        self.start_date_entry = ctk.CTkEntry(self, placeholder_text="Début (YYYY-MM-DD)")
        self.start_date_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.end_date_entry = ctk.CTkEntry(self, placeholder_text="Fin (YYYY-MM-DD)")
        self.end_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.search_btn = ctk.CTkButton(self, text="Générer", command=self.date_selected)
        self.search_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    def date_selected(self):
        if self.on_button_click:
            start = self.start_date_entry.get()
            end = self.end_date_entry.get()
            self.on_button_click(start, end)