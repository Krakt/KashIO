import customtkinter as ctk
from config import CONFIG, CURRENT_LANG
from .base_widget import BaseWidget
from .ui_widgets import NumericEntry, ValueComboBox, AutocompleteEntry

class ExpenseWidget(BaseWidget):
    def __init__(self, master, title="", **kwargs):
        
        headers = ["Shop", "Categorie", "Espèce", "Montant"]
        super().__init__(master, headers=headers, title=title, **kwargs)

        self.create_new_row()

    def create_new_row(self):
        row_index = len(self.rows) + 1  # +1 pour sauter l'en-tête

        sug = ["Migro", "Denner", "Coop"]
        # 1. Shop name entry (can later be wired to an autocomplete list)
        entry_shop = AutocompleteEntry(self.scrollable_frame, sug, width=120)
        entry_shop.grid(row=row_index, column=0, padx=5, pady=5, sticky="ew")

        # 2. Category selection (ComboBox with language-agnostic code mapping)
        # Displaying friendly names, but you can map these to your JSON localization codes
        entry_category = ValueComboBox(
            self.scrollable_frame,
            items=CONFIG["lookups"]["expense_categories"],
            current_lang=CURRENT_LANG,
            width=100,
            command=self.on_change
        )
        entry_category.grid(row=row_index, column=1, padx=5, pady=5, sticky="ew")

        # 3. Paid in cash checkbox (default True for petty cash expenses)
        entry_method = ValueComboBox(
            self.scrollable_frame,
            items=CONFIG["lookups"]["payment_methods"],
            current_lang=CURRENT_LANG,
            width=100,
            command=self.on_change
        )
        entry_method.grid(row=row_index, column=2, padx=5, pady=5, sticky="ew")

        # 4. Amount entry
        entry_amount = NumericEntry(self.scrollable_frame, True, width=80)
        entry_amount.grid(row=row_index, column=3, padx=5, pady=5, sticky="ew")
        entry_amount.bind("<KeyRelease>", lambda event: self.on_change() if self.on_change else None)

        # Store widgets in the rows list for saving / validation later
        self.rows.append({
            "shop": entry_shop,
            "category": entry_category,
            "method": entry_method,
            "amount": entry_amount
        })

