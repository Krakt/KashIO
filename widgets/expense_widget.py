import customtkinter as ctk
from .base_widget import BaseWidget
from .ui_widgets import NumericEntry

class ExpenseWidget(BaseWidget):
    def __init__(self, master, title, **kwargs):
        
        headers = ["Shop", "Categorie", "Espèce", "Montant"]
        super().__init__(master, title, headers=headers, **kwargs)

        self.create_new_row()

    def create_new_row(self):
        row_index = len(self.rows) + 1  # +1 pour sauter l'en-tête

        # 1. Shop name entry (can later be wired to an autocomplete list)
        entry_shop = ctk.CTkEntry(self.scrollable_frame, width=120)
        entry_shop.grid(row=row_index, column=0, padx=5, pady=5, sticky="ew")

        # 2. Category selection (ComboBox with language-agnostic code mapping)
        # Displaying friendly names, but you can map these to your JSON localization codes
        entry_category = ctk.CTkComboBox(
            self.scrollable_frame,
            width=110,
            values=["Nourriture", "Boissons", "Essence", "Autre"],
            command=lambda value: self.on_change() if self.on_change else None
        )
        entry_category.grid(row=row_index, column=1, padx=5, pady=5, sticky="ew")

        # 3. Paid in cash checkbox (default True for petty cash expenses)
        var_cash = ctk.BooleanVar(value=True)
        checkbox_cash = ctk.CTkCheckBox(
            self.scrollable_frame,
            text="",
            variable=var_cash,
            width=30,
            command=lambda: self.on_change() if self.on_change else None
        )
        checkbox_cash.grid(row=row_index, column=2, padx=5, pady=5, sticky="n")

        # 4. Amount entry
        entry_amount = NumericEntry(self.scrollable_frame, True, width=80)
        entry_amount.grid(row=row_index, column=3, padx=5, pady=5, sticky="ew")
        entry_amount.bind("<KeyRelease>", lambda event: self.on_change() if self.on_change else None)

        # Store widgets in the rows list for saving / validation later
        self.rows.append({
            "shop": entry_shop,
            "category": entry_category,
            "paid_in_cash": var_cash,
            "amount": entry_amount
        })

