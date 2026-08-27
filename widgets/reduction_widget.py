import customtkinter as ctk
from config import CONFIG, CURRENT_LANG
from .base_widget import BaseWidget
from .ui_widgets import ValueComboBox, NumericEntry

class ReductionWidget(BaseWidget):
    """
    Widget component to manage and calculate customer reduction entries.
    Handles dynamic row creation, validation, and total amount calculation.
    """

    def __init__(self, master, title, **kwargs):
        """Initializes the ReductionWidget and sets up the user interface."""
        
        # Define the reduction section columns
        headers = ["Nombre", "Méthode", "Montant"]
        super().__init__(master, title, headers=headers, **kwargs)


        self.warning_lbl = ctk.CTkLabel(
            self,
            text="🔒 En attente d'un ticket valide pour activer les réductions",
            font=("Arial", 10, "bold"),
            text_color="red")
        self.warning_lbl.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")

        self.create_new_row()


    def set_state(self, state):
        """
        Updates the enabled/disabled state of all widgets in the section.
        
        Args:
            state (str): The state to apply ('normal' or 'disabled').
        """
        # Set the state of the entire reduction section (enabled/disabled)
        for row in self.rows:
            row["reduction_count"].configure(state=state)
            row["reduction_method"].configure(state=state)
            # The amount label does not have a state, so we skip it

        if state == "disabled":
            self.warning_lbl.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        else:
            self.warning_lbl.grid_remove()

        # Also set the state of the add button
        self.button.configure(state=state)


    def on_button_click(self):
        """Handle the button clic to create a new row"""
        # Create a new row in the reduction section when the button is clicked
        self.create_new_row()


    def create_new_row(self):
        """Create a new reduction row"""
        row_index = len(self.rows) + 1  # +1 pour sauter l'en-tête

        var_reduction_count = ctk.StringVar(value="0")  # Default value is 0
        var_reduction_unit_amount = ctk.StringVar(value="18.00")  # Default value is 18.00
        var_reduction_amount = ctk.StringVar(value="0.00")  # Default value is 0.00

        def update_amount(*args):
            """Calculate the amount of the reduction"""
            try:
                # Calculate the sum based on the number of reductions and the reduction amount
                reduction_count = int(var_reduction_count.get())
                reduction_unit_amount = float(var_reduction_unit_amount.get())
                total_sum = reduction_count * reduction_unit_amount
                var_reduction_amount.set(f"{total_sum:.2f}")
            except ValueError:
                var_reduction_amount.set("0.00")

            if self.on_change:
                self.on_change()

        # Trace changes to the number of reductions and the reduction amount
        var_reduction_count.trace_add("write", update_amount)
        var_reduction_count.trace_add("write", update_amount)


        reduction_count_entry = NumericEntry(self.scrollable_frame, False, textvariable=var_reduction_count, width=120)
        reduction_count_entry.grid(row=row_index, column=0, padx=5, pady=5, sticky="ew")


        reduction_method_cb = ValueComboBox(self.scrollable_frame,
                                            items=CONFIG["lookups"]["payment_methods"],
                                            current_lang=CURRENT_LANG,
                                            width=100,
                                            command=self.on_change)
        reduction_method_cb.grid(row=row_index, column=1, padx=5, pady=5, sticky="ew")


        reduction_amount_entry = ctk.CTkLabel(self.scrollable_frame,
                                              textvariable=var_reduction_amount,
                                              font=("Arial", 12, "bold"))
        reduction_amount_entry.grid(row=row_index, column=2, padx=5, pady=5, sticky="ew")

        # Store the new row's widgets in the rows list for later retrieval
        self.rows.append({
            "reduction_count": reduction_count_entry,
            "reduction_amount": var_reduction_amount,
            "reduction_method": reduction_method_cb
        })


    def form_data_validation(self):
        """
        Control and validate the data from the form.
        
        Return:
            Boolean: True if the data are validated False otherwise
            str: An alert message
        """
        reduction_method_used = [row["reduction_method"].get() for row in self.rows if row["reduction_method"].get()]
        # Validate the form data for the reduction section
        for row in self.rows:
            reduction_count = row["reduction_count"].get()
            reduction_amount = row["reduction_amount"].get()
            reduction_method = row["reduction_method"].get()

            if not reduction_count.isdigit() or int(reduction_count) < 0:
                return False, "Le nombre de réductions doit être un entier positif."
            if not reduction_amount.replace('.', '', 1).isdigit() or float(reduction_amount) < 0:
                return False, "Le montant doit être un nombre positif."
            if reduction_method not in ["Espèces", "Carte", "Recka", "Twint", "Autre"]:
                return False, "La méthode de paiement est invalide."

        if len(reduction_method_used) != len(set(reduction_method_used)):
            return False, "Chaque type de réduction ne peut être utilisé qu'une seule fois."

        return True, ""