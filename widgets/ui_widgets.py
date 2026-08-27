import customtkinter as ctk
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StatCard(ctk.CTkFrame):
    """
    Build a card to display simple stat card.
    """
    def __init__(self, master, title: str, amount: str, **kwargs):
        """
        Initialize and build the stat card.

        Args:
            master: the parent components.
            title (str): the title of the card to display.
            amount (str): the amount to display (numeric string only).
        """
        super().__init__(master, **kwargs)
        
        # Title
        self.title_lbl = ctk.CTkLabel(self, text=title, font=("Arial", 12, "bold"))
        self.title_lbl.pack(pady=(10, 0))
        
        # amount
        self.amount_lbl = ctk.CTkLabel(self, text=amount, font=("Arial", 20, "bold"))
        self.amount_lbl.pack(pady=(5, 10))

    def update_value(self, new_amount: str):
        """
        Update the value of the stat card.
        
        Args:
            new_amount (str): The new amount to display on the card (numeric string only).
        """
        self.amount_lbl.configure(text=new_amount)


class PeriodCard(ctk.CTkFrame):
    """
    Build a card to display the tickets by time period launch/evening.
    """
    def __init__(self, master, title: str, ticket_count: str, ticket_takeaway_count: str, ticket_amount: str, **kwargs):
        """
        Initialize and build the period card.

        Args:
            master: the parent components.
            title (str): the title of the card to display.
            ticket_count (str): the count of ticket (numeric string only).
            ticket_takeaway_count (str): the count of ticket of takeaways (numeric string only).
            ticket_amount (str): the amount to display (numeric string only).
        """
        super().__init__(master, **kwargs)
        
        # Title
        self.title_lbl = ctk.CTkLabel(self, text=title, font=("Arial", 12, "bold"))
        self.title_lbl.pack(pady=(10, 0))
        
        # Tickets count
        self.number_tickets_lbl = ctk.CTkLabel(self, text=f"Nombre de tickets: {ticket_count}", font=("Arial", 14))
        self.number_tickets_lbl.pack(pady=(5, 0))

        # Takeaway Tickets count
        self.number_tickets_takeaway_lbl = ctk.CTkLabel(self,
                                                        text=f"Nombre d'emporté: {ticket_takeaway_count}",
                                                        font=("Arial", 14))
        self.number_tickets_takeaway_lbl.pack(pady=(5, 0))
        
        # Amount
        self.amount_lbl = ctk.CTkLabel(self, text=f"Montant: {ticket_amount}", font=("Arial", 14))
        self.amount_lbl.pack(pady=(5, 10))

    def update_values(self, new_ticket_count: str, new_ticket_takeaway_count: str, new_ticket_amount: str):
        """
        Update the values of the period card.

        Args:
            new_ticket_count (str): the new count of ticket (numeric string only).
            new_ticket_takeaway_count (str): the new count of ticket of takeaways (numeric string only).
            new_ticket_amount (str): the new amount to display (numeric string only).
        """
        self.number_tickets_lbl.configure(text=f"Nombre de tickets: {new_ticket_count}")
        self.number_tickets_takeaway_lbl.configure(text=f"Nombre d'emporté: {new_ticket_takeaway_count}")
        self.amount_lbl.configure(text=f"Montant: {new_ticket_amount}")


class ReductionCard(ctk.CTkFrame):
    """
    Build a card to display the reduction.
    """
    def __init__(self, master, title: str, reduction_count: str, reduction_amount: str, **kwargs):
        """
        Initialize and build the period card.

        Args:
            master: the parent components.
            title (str): the title of the card to display.
            reduction_count (str): the count of reduction (numeric string only).
            reduction_amount (str): the amount to display (numeric string only).
        """
        super().__init__(master, **kwargs)
        
        # Title
        self.title_lbl = ctk.CTkLabel(self, text=title, font=("Arial", 12, "bold"))
        self.title_lbl.pack(pady=(10, 0))
        
        # Number of Reductions
        self.reduction_count_lbl = ctk.CTkLabel(self, text=f"Nombre de réductions: {reduction_count}", font=("Arial", 14))
        self.reduction_count_lbl.pack(pady=(5, 0))
        
        # Amount
        self.amount_lbl = ctk.CTkLabel(self, text=f"Montant: {reduction_amount}", font=("Arial", 14))
        self.amount_lbl.pack(pady=(5, 10))

    def update_values(self, new_reduction_count: str, new_reduction_amount: str):
        """
        Update the values of the period card.

        Args:
            new_reduction_count (str): the new count of reduction (numeric string only).
            new_reduction_amount (str): the new amount to display (numeric string only).
        """
        self.reduction_count_lbl.configure(text=f"Nombre de réductions: {new_reduction_count}")
        self.amount_lbl.configure(text=f"Montant: {new_reduction_amount}")


class SummaryChartsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Ici tu construis ton interface de droite : 
        # Un label titre, un sous-cadre pour le tableau, et un sous-cadre pour le graphique.
        self.label = ctk.CTkLabel(self, text="Répartition par moyen de paiement", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)
        
        # Frame qui contiendra le graphique Matplotlib
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def update_data(self, payment_data):
        """Méthode appelée quand l'utilisateur clique sur 'Générer' 
        pour rafraîchir le tableau et le camembert avec les nouvelles dates."""
        
        # Nettoyage des anciens widgets graphiques s'il y en a
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        if not payment_data:
            return
            
        labels = [row[0] for row in payment_data] # ex: Espèces, Carte, etc.
        values = [row[1] for row in payment_data] # ex: montants totaux
        
        # Génération du graphique Matplotlib
        fig, ax = plt.subplots(figsize=(5, 4))
        
        # Ajustement des couleurs de fond pour coller au thème CustomTkinter (ex: gris clair)
        fig.patch.set_facecolor('#ebebeb')
        ax.set_facecolor('#ebebeb')
        
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        
        # Intégration dans le frame CTk
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


class SummaryTableWidget(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = ctk.CTkLabel(self, text="Détails financiers", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)
        
        # Le container pour les lignes
        self.data_container = ctk.CTkFrame(self)
        self.data_container.pack(fill="both", expand=True, padx=10, pady=10)

    def update_data(self, payment_data):
        # Nettoyage
        for widget in self.data_container.winfo_children():
            widget.destroy()
            
        # Entête simple
        header = ctk.CTkFrame(self.data_container, fg_color="transparent")
        header.pack(fill="x", pady=5)
        ctk.CTkLabel(header, text="Méthode", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header, text="Montant (CHF)", font=("Arial", 12, "bold")).pack(side="right", padx=10)

        # Lignes de données
        for method, amount in payment_data:
            row = ctk.CTkFrame(self.data_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=method).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"{amount:.2f}").pack(side="right", padx=10)


class ClosureModal(ctk.CTkToplevel):
    def __init__(self, master, on_confirm):
        super().__init__(master)
        self.title("Confirmation de clôture")
        self.geometry("300x250")
        self.on_confirm = on_confirm
        
        # Date par défaut (Aujourd'hui)
        default_date = datetime.now().strftime('%Y-%m-%d')
        
        ctk.CTkLabel(self, text="Date de clôture :").pack(pady=10)
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.insert(0, default_date)
        self.date_entry.pack(pady=5)
        
        # Checkbox Email
        self.send_email_var = ctk.BooleanVar(value=True)
        self.email_checkbox = ctk.CTkCheckBox(self, text="Envoyer par email", variable=self.send_email_var)
        self.email_checkbox.pack(pady=20)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10, fill="x", padx=20)
        
        # Bouton Annuler
        self.cancel_button = ctk.CTkButton(button_frame, text="Annuler", fg_color="gray", command=self.destroy)
        self.cancel_button.pack(side="right", padx=5, expand=True)
        
        # Bouton Valider
        self.validate_button = ctk.CTkButton(button_frame, text="Valider", command=self._confirm)
        self.validate_button.pack(side="left", padx=5, expand=True)
        
    def _confirm(self):
        self.on_confirm(self.date_entry.get(), self.send_email_var.get())
        self.destroy()

################################
### Extended CTK components ####
################################
class ValueSegmentedButton(ctk.CTkSegmentedButton):
    def __init__(self, master, items, current_lang, **kwargs):
        # items: [{"code": "lunch", "text": {"fr": "Midi", "de": "Mittag"}}, ...]
        self.items = items
        self.lang = current_lang
        
        # Build list of display texts for the UI
        display_values = [item["text"][self.lang] for item in items]
        
        super().__init__(master, values=display_values, **kwargs)
        
        # Set default to the first item's text
        if display_values:
            self.set(display_values[0])

    def get_value(self):
        current_text = self.get()
        for item in self.items:
            if item["text"][self.lang] == current_text:
                return item["code"]
        return None


class ValueComboBox(ctk.CTkComboBox):
    def __init__(self, master, items, current_lang, **kwargs):
        self.items = items
        self.lang = current_lang
        
        display_values = [item["text"][self.lang] for item in items]
        
        super().__init__(master, values=display_values, **kwargs)
        
        if display_values:
            self.set(display_values[0])

    def get_value(self):
        current_text = self.get()
        for item in self.items:
            if item["text"][self.lang] == current_text:
                return item["code"]
        return None


class NumericEntry(ctk.CTkEntry):
    def __init__(self, master, allow_float=True, **kwargs):
        super().__init__(master, **kwargs)
        self.allow_float = allow_float
        
        # Register the validation command with Tkinter
        vcmd = (self.register(self._validate_input), '%P')
        self.configure(validate='key', validatecommand=vcmd)

    def _validate_input(self, proposed_value):
        # Allow empty field so the user can backspace everything
        if proposed_value == "":
            return True

        if self.allow_float:
            # Check if it's a valid partial or full float (e.g., "12", "12.", "12.50")
            if proposed_value.count('.') <= 1:
                try:
                    float(proposed_value)
                    return True
                except ValueError:
                    return False
            return False
        else:
            # Integers only
            return proposed_value.isdigit()

    def get_value(self):
        val = self.get().strip()
        if not val:
            return 0.0 if self.allow_float else 0
        try:
            return float(val) if self.allow_float else int(val)
        except ValueError:
            return 0.0 if self.allow_float else 0