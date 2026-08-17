import customtkinter as ctk
from .base_widget import BaseWidget

class TicketWidget(BaseWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # On définit les colonnes spécifiques à TicketSection
        for i in range(5):
            self.scrollable_frame.columnconfigure(i, weight=1)

        # On dessine les labels spécifiques aux tickets
        headers = ["Libellé", "Soirée", "Emporté", "Méthode", "Montant"]
        for i, text in enumerate(headers):
            ctk.CTkLabel(self.scrollable_frame, text=text, font=("Arial", 12, "bold")).grid(row=0, column=i, padx=5, pady=5, sticky="news")


        self.create_new_row()

    def create_centered_checkbox(self, row_index, column_index, variable, command=None):
        frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        frame.grid(row=row_index, column=column_index, padx=5, pady=5, sticky="ew")
        
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.columnconfigure(2, weight=1)
        
        checkbox = ctk.CTkCheckBox(frame, text="", width=20, variable=variable, command=command)
        # On met la checkbox dans une colonne dédiée, mais on lui pousse un padx à gauche 
        # pour compenser l'espace du label fantôme de CustomTkinter
        checkbox.grid(row=0, column=1, padx=(15, 0))
        
        return variable

    def on_button_click(self):
        # Create a new row in the ticket section when the button is clicked
        self.create_new_row()

    def create_new_row(self):
        row_index = len(self.rows) + 1  # +1 pour sauter l'en-tête
                
        entry_wording = ctk.CTkEntry(self.scrollable_frame, width=120)
        entry_wording.grid(row=row_index, column=0, padx=5, pady=5, sticky="ew")

        var_evening = ctk.IntVar(value=0)  # Default value is 0 (unchecked)
        entry_evening = self.create_centered_checkbox(row_index, 1, var_evening, command=self.on_change)

        var_takeaway = ctk.IntVar(value=0)  # default value is 0 (unchecked)
        entry_takeaway = self.create_centered_checkbox(row_index, 2, var_takeaway, command=self.on_change)

        entry_method = ctk.CTkComboBox(self.scrollable_frame,
                                       width=100,
                                       values=["Espèces", "Carte", "Recka", "Twint", "Autre"],
                                       command=self.on_change)  # Notify on selection change
        
        entry_method.grid(row=row_index, column=3, padx=5, pady=5, sticky="ew")

        entry_amount = ctk.CTkEntry(self.scrollable_frame, width=80)
        entry_amount.grid(row=row_index, column=4, padx=5, pady=5, sticky="ew")
        entry_amount.bind("<KeyRelease>", lambda event: self.on_change())  # Notify on key release

        # store the new row's widgets in the rows list for later retrieval
        self.rows.append({
            "wording": entry_wording,
            "evening": var_evening,
            "takeaway": var_takeaway,
            "method": entry_method,
            "amount": entry_amount
        })