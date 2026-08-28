import customtkinter as ctk
from widgets.ui_widgets import StatCard, PeriodCard, ReductionCard

class DashboardWidget(ctk.CTkFrame):
    """
    Main dashboard widget displaying financial stats, periods, reductions, and expenses.
    """

    def __init__(self, master, title, **kwargs):
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)

        #self.title_lbl = ctk.CTkLabel(self, text=title, font=("Arial", 18, "bold"))
        #self.title_lbl.grid(row=0, column=0, padx=10, pady=(10, 15), sticky="w")

        self._create_envelope_section()  # Cash drawer & main totals
        self._create_ticket_section()    # Lunch / Evening / Total breakdown
        self._create_expense_section()   # Daily expenses summary
        self._create_reduction_section() # Reductions breakdown by method

    def _create_envelope_section(self):
        """Builds the primary financial summary section."""
        self.envelope_section = ctk.CTkFrame(self, border_width=0, border_color="gray", corner_radius=10)
        self.envelope_section.grid(row=1, column=0, padx=5, pady=8, sticky="ew")

        for i in range(2):
            self.envelope_section.columnconfigure(i, weight=1)

        self.envelope_lbl = ctk.CTkLabel(self.envelope_section, text="Trésorerie & Chiffres Clés", font=("Arial", 14, "bold"))
        self.envelope_lbl.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="ew")

        # Primary highlighted card for physical cash envelope
        self.net_cash_amount_card = StatCard(self.envelope_section, title="Espèces Net (Enveloppe)", amount="0.00")
        self.net_cash_amount_card.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.gross_amount_card = StatCard(self.envelope_section, title="Chiffre d'Affaires Brut", amount="0.00")
        self.gross_amount_card.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.net_amount_card = StatCard(self.envelope_section, title="Chiffre d'Affaires Net", amount="0.00")
        self.net_amount_card.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    def _create_ticket_section(self):
        """Builds the period-by-period ticket breakdown section with full metrics."""
        self.ticket_section = ctk.CTkFrame(self, border_width=0, border_color="gray", corner_radius=10)
        self.ticket_section.grid(row=2, column=0, padx=5, pady=8, sticky="ew")

        for i in range(2):
            self.ticket_section.columnconfigure(i, weight=1)

        self.ticket_lbl = ctk.CTkLabel(self.ticket_section, text="Analyse par Période", font=("Arial", 14, "bold"))
        self.ticket_lbl.grid(row=0, column=0, columnspan=2, pady=(10, 5), sticky="ew")

        self.lunch_period_card = PeriodCard(self.ticket_section, title="Midi")
        self.lunch_period_card.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.evening_period_card = PeriodCard(self.ticket_section, title="Soirée")
        self.evening_period_card.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.total_period_card = PeriodCard(self.ticket_section, title="Total Cumulé")
        self.total_period_card.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    def _create_expense_section(self):
        """Builds the expense totals section."""
        self.expense_section = ctk.CTkFrame(self, border_width=0, border_color="gray", corner_radius=10)
        self.expense_section.grid(row=3, column=0, padx=5, pady=8, sticky="ew")
        self.expense_section.columnconfigure(0, weight=1)

        self.expense_lbl = ctk.CTkLabel(self.expense_section, text="Dépenses du Jour", font=("Arial", 14, "bold"))
        self.expense_lbl.grid(row=0, column=0, pady=(10, 5), sticky="ew")

        self.total_expenses_card = StatCard(self.expense_section, title="Total des Dépenses", amount="0.00")
        self.total_expenses_card.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    def _create_reduction_section(self):
        """Builds the reduction section with dynamic cards per payment method."""
        self.reduction_section = ctk.CTkFrame(self, border_width=0, border_color="gray", corner_radius=10)
        self.reduction_section.grid(row=4, column=0, padx=5, pady=8, sticky="ew")

        for i in range(3):
            self.reduction_section.columnconfigure(i, weight=1)

        self.reduction_lbl = ctk.CTkLabel(self.reduction_section, text="Réductions par Méthode", font=("Arial", 14, "bold"))
        self.reduction_lbl.grid(row=0, column=0, columnspan=3, pady=(10, 5), sticky="ew")

        values = ["cash", "card", "reka", "twint", "other"]  # Mapped to configuration keys
        display_names = ["Espèces", "Carte", "Recka", "Twint", "Autre"]
        self.reduction_cards = []

        for i in range(len(values)):
            col_index = (i % 3)
            row_index = 1 + (i // 3)

            card = ReductionCard(self.reduction_section, title=display_names[i], reduction_count=0, reduction_amount="0.00")
            card.grid(row=row_index, column=col_index, padx=5, pady=5, sticky="ew")
            self.reduction_cards.append(card)

    def update_form_dict(self, data):
        # ... [other updates remain the same] ...

        lunch = data.get('lunch', {})
        evening = data.get('evening', {})
        total = data.get('total', {})

        self.lunch_period_card.update_values(
            lunch.get('ticket_count', 0),
            lunch.get('eat_in_count', 0),
            lunch.get('ticket_takeaway_count', 0),
            lunch.get('delivery_count', 0),
            f"{lunch.get('gross_amount', 0.0):.2f}"
        )
        self.evening_period_card.update_values(
            evening.get('ticket_count', 0),
            evening.get('eat_in_count', 0),
            evening.get('ticket_takeaway_count', 0),
            evening.get('delivery_count', 0),
            f"{evening.get('gross_amount', 0.0):.2f}"
        )
        self.total_period_card.update_values(
            total.get('ticket_count', 0),
            total.get('eat_in_count', 0),
            total.get('ticket_takeaway_count', 0),
            total.get('delivery_count', 0),
            f"{total.get('gross_amount', 0.0):.2f}"
        )