import customtkinter as ctk

class ListManager(ctk.CTkFrame):
    def __init__(self, master, title, initial_items=None, **kwargs):
        super().__init__(master, **kwargs)

        # Create an array to store the items
        self.items = initial_items or []

        self.title_lbl = ctk.CTkLabel(self, text=title, font=("Arial", 14, "bold"))
        self.title_lbl.pack(pady=5, anchor="w")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=5)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Nouvelle methode de paiement")
        self.entry.pack(side="left", expand=True, fill="x", padx=(0,5))

        self.add_button = ctk.CTkButton(self.input_frame, text="Ajouter", command=self.add_item)
        self.add_button.pack(side="right")

        self.list_container = ctk.CTkScrollableFrame(self, height=150)
        self.list_container.pack(fill="both", expand=True, pady=5)

        for item in self.items:
            self.create_item_row(item)


    def add_item(self):
        val = self.entry.get().strip()
        if val and val not in self.items:
            self.items.append(val)
            self.create_item_row(val)
            self.entry.delete(0, "end")


    def create_item_row(self, val):
        row_frame = ctk.CTkFrame(self.list_container)
        row_frame.pack(fill="x", pady=2)

        lbl = ctk.CTkLabel(row_frame, text=val)
        lbl.pack(side="left", padx=10, pady=5)

        del_btn = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", hover_color="darkred",
                                command=lambda: self.remove_item(val, row_frame))
        del_btn.pack(side="right", padx=5, pady=5)


    def remove_item(self, val, row_frame):
        if val in self.items:
            confirmation_windows = ctk.CTkInputDialog(text=f"Voulez-vous vraiment supprimer: {val}? \n Taper le nom de la methode", title="Confirmation supression valeur payement")
            response = confirmation_windows.get_input()

            if response and str.lower(response) == str.lower(val):
                self.items.remove(val)
                row_frame.destroy()
