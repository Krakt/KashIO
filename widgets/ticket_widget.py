import customtkinter as ctk
from config import CONFIG, CURRENT_LANG
from .base_widget import BaseWidget
from .ui_widgets import ValueComboBox, ValueSegmentedButton, NumericEntry

class TicketWidget(BaseWidget):
    def __init__(self, master, title, **kwargs):
        
        # Define the labels for the tickets
        headers = ["Période", "Emplacement", "Méthode", "Montant"]
        super().__init__(master, headers=headers, title=title, **kwargs)


        self.create_new_row()

    def on_button_click(self):
        # Create a new row in the ticket section when the button is clicked
        self.create_new_row()

    def create_new_row(self):
        row_index = len(self.rows) + 1  # +1 to jump header

        period_selector = ValueSegmentedButton(self.scrollable_frame,
                                               items=CONFIG["lookups"]["periods"],
                                               current_lang=CURRENT_LANG,
                                               command=self.on_change)
        period_selector.set(CONFIG["lookups"]["periods"][0]["text"][CURRENT_LANG])
        period_selector.grid(row=row_index, column=0, padx=5, pady=5, sticky="ew")


        location_selector = ValueSegmentedButton(self.scrollable_frame,
                                                 items=CONFIG["lookups"]["locations"],
                                                 current_lang=CURRENT_LANG,
                                                 command=self.on_change)
        
        location_selector.set(CONFIG["lookups"]["locations"][0]["text"][CURRENT_LANG])
        location_selector.grid(row=row_index, column=1, padx=5, pady=5, sticky="ew")

        
        entry_method = ValueComboBox(self.scrollable_frame,
                                     items=CONFIG["lookups"]["payment_methods"],
                                     current_lang=CURRENT_LANG,
                                     width=100,
                                     command=self.on_change)
        entry_method.grid(row=row_index, column=2, padx=5, pady=5, sticky="ew")


        entry_amount = NumericEntry(self.scrollable_frame, True, width=80)
        entry_amount.grid(row=row_index, column=3, padx=5, pady=5, sticky="ew")
        entry_amount.bind("<KeyRelease>", lambda event: self.on_change())  # Notify on key release

        # store the new row's widgets in the rows list for later retrieval
        self.rows.append({
            "period": period_selector,
            "location": location_selector,
            "method": entry_method,
            "amount": entry_amount
        })