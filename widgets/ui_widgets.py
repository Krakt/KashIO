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
    Card displaying ticket counts (total, eat-in, takeaway, delivery) and total gross amount for a period.
    """
    def __init__(self, master, title, ticket_count=0, eat_in_count=0, takeaway_count=0, delivery_count=0, amount="0.00", **kwargs):
        super().__init__(master, **kwargs)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Period Title
        self.title_lbl = ctk.CTkLabel(self, text=title, font=("Arial", 12, "bold"))
        self.title_lbl.grid(row=0, column=0, columnspan=3, pady=(5, 2), sticky="ew")

        # Gross Amount (Highlighted)
        self.amount_lbl = ctk.CTkLabel(self, text=f"{amount} CHF", font=("Arial", 14, "bold"))
        self.amount_lbl.grid(row=1, column=0, columnspan=3, pady=(0, 5), sticky="ew")

        # Detailed breakdown labels
        self.total_tickets_lbl = ctk.CTkLabel(self, text=f"Total Tickets: {ticket_count}", font=("Arial", 11))
        self.total_tickets_lbl.grid(row=2, column=0, sticky="w", padx=10)

        self.eat_in_lbl = ctk.CTkLabel(self, text=f"Sur place: {eat_in_count}", font=("Arial", 10))
        self.eat_in_lbl.grid(row=3, column=0, sticky="w", padx=10)

        self.takeaway_lbl = ctk.CTkLabel(self, text=f"À emporter: {takeaway_count}", font=("Arial", 10))
        self.takeaway_lbl.grid(row=2, column=1, sticky="w", padx=10)

        self.delivery_lbl = ctk.CTkLabel(self, text=f"Livraison: {delivery_count}", font=("Arial", 10))
        self.delivery_lbl.grid(row=3, column=1, sticky="w", padx=10)

        self.just_eat_lbl = ctk.CTkLabel(self, text=f"Just Eat: {delivery_count}", font=("Arial", 10))
        self.just_eat_lbl.grid(row=2, column=2, sticky="w", padx=10)

    def update_values(self, ticket_count, eat_in_count, takeaway_count, delivery_count, just_eat_count, amount):
        """Refreshes all counts and the monetary total for the period card."""
        self.total_tickets_lbl.configure(text=f"Total Tickets: {ticket_count}")
        self.eat_in_lbl.configure(text=f"Sur place: {eat_in_count}")
        self.takeaway_lbl.configure(text=f"À emporter: {takeaway_count}")
        self.delivery_lbl.configure(text=f"Livraison: {delivery_count}")
        self.just_eat_lbl.configure(text=f"Just Eat: {just_eat_count}")
        self.amount_lbl.configure(text=f"{amount} CHF")


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

import customtkinter as ctk

class AutocompleteEntry(ctk.CTkFrame):
    """
    A CustomTkinter entry field with a floating Toplevel dropdown for autocomplete suggestions.
    """
    def __init__(self, master, suggestions=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.suggestions = suggestions or []
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Main text entry
        self.entry = ctk.CTkEntry(self)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<KeyRelease>", self._on_keyrelease)
        self.entry.bind("<FocusOut>", self._delayed_hide) # Hide when clicking away

        self.suggestion_win = None

    def get_value(self):
        return self.entry.get().strip()

    def set_value(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

    def _on_keyrelease(self, event):
        term = self.entry.get().lower()
        
        if not term:
            self._hide_suggestions()
            return

        matches = [s for s in self.suggestions if term in s.lower() and s.lower() != term]
        
        if matches:
            self._show_suggestions(matches)
        else:
            self._hide_suggestions()

    def _show_suggestions(self, matches):
        self._hide_suggestions()

        # Get absolute screen coordinates of the entry box
        self.update_idletasks()
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        width = self.entry.winfo_width()

        # Create a borderless floating Toplevel window for the dropdown
        self.suggestion_win = ctk.CTkToplevel(self)
        self.suggestion_win.wm_overrideredirect(True)
        self.suggestion_win.geometry(f"{width}x{min(len(matches), 5) * 30}+{x}+{y}")
        self.suggestion_win.attributes("-topmost", True)

        # Frame inside the popup
        frame = ctk.CTkFrame(self.suggestion_win, border_width=1, border_color="gray")
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)

        for i, match in enumerate(matches[:5]):
            btn = ctk.CTkButton(
                frame, 
                text=match, 
                fg_color="transparent", 
                text_color=("black", "white"),
                hover_color=("gray80", "gray30"),
                anchor="w",
                height=25,
                command=lambda m=match: self._select_suggestion(m)
            )
            btn.grid(row=i, column=0, sticky="ew", padx=2, pady=1)

    def _select_suggestion(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
        self._hide_suggestions()

    def _delayed_hide(self, event):
        # Small delay to allow click event on suggestion buttons to register first
        self.after(200, self._hide_suggestions)

    def _hide_suggestions(self):
        if self.suggestion_win:
            try:
                self.suggestion_win.destroy()
            except Exception:
                pass
            self.suggestion_win = None

    def update_suggestions(self, new_suggestions):
        self.suggestions = new_suggestions