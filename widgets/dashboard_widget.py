import customtkinter as ctk
from widgets.ui_widgets import StatCard, PeriodCard, ReductionCard

class DashboardWidget(ctk.CTkFrame):
    """
    Main dashboard widget displaying financial stats and period summaries.
    Organizes data into sections for cash, tickets, and reductions.
    """

    def __init__(self, master, title, **kwargs):
        """Initializes the dashboard layout and sub-sections."""
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(self, text=title, font=("Arial", 16, "bold"))
        self.title_lbl.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self._create_envelope_section()  # Create the envelope section
        self._create_ticket_section()  # Create the ticket section
        self._create_reduction_section()  # Create the reduction section
        

    def _create_envelope_section(self):
        """
        Builds the cash envelope section (most need info) with summary cards.
        """
        # Create a frame for the envelope section
        self.envelope_section = ctk.CTkFrame(self, border_width=2, border_color="gray", corner_radius=10)
        self.envelope_section.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        for i in range(2):
            self.envelope_section.columnconfigure(i, weight=1)

        # Create a label for the envelope section
        self.envelope_lbl = ctk.CTkLabel(self.envelope_section, text="Espèces à verser", font=("Arial", 12, "bold"))
        self.envelope_lbl.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")

        self.net_cash_amount_card = StatCard(self.envelope_section, title="Montant Espèces Net", amount="0.00")
        self.net_cash_amount_card.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Draw the gross amount cards for the dashboard
        self.gross_amount_card = StatCard(self.envelope_section, title="Montant Brut", amount="0.00")
        self.gross_amount_card.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Draw the net amount cards for the dashboard
        self.net_amount_card = StatCard(self.envelope_section, title="Montant Net", amount="0.00")
        self.net_amount_card.grid(row=2, column=1, padx=5, pady=5, sticky="ew")


    def _create_ticket_section(self):
        """
        Build a section to list all info about the tickets data with cards.
        """
        # Create a frame for the ticket section
        self.ticket_section = ctk.CTkFrame(self, border_width=2, border_color="gray", corner_radius=10)
        self.ticket_section.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        for i in range(2):
            self.ticket_section.columnconfigure(i, weight=1)

        # Create a label for the ticket section
        self.ticket_lbl = ctk.CTkLabel(self.ticket_section, text="Tickets", font=("Arial", 12, "bold"))
        self.ticket_lbl.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")

        # Draw the lunch period card for the dashboard
        self.lunch_period_card = PeriodCard(self.ticket_section,
                                             title="Midi",
                                             ticket_count=0,
                                             ticket_takeaway_count=0,
                                             ticket_amount="0.00")
        self.lunch_period_card.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Draw the evening period card for the dashboard
        self.evening_period_card = PeriodCard(self.ticket_section,
                                              title="Soirée",
                                              ticket_count=0,
                                              ticket_takeaway_count=0,
                                              ticket_amount="0.00")
        self.evening_period_card.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Draw the total period card for the dashboard
        self.total_period_card = PeriodCard(self.ticket_section,
                                            title="Total",
                                            ticket_count=0,
                                            ticket_takeaway_count=0,
                                            ticket_amount="0.00")
        self.total_period_card.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


    def _create_reduction_section(self):
        """
        Builds the reduction section with summary cards.
        """
        # Create a frame for the reduction section
        self.reduction_section = ctk.CTkFrame(self, border_width=2, border_color="gray", corner_radius=10)
        self.reduction_section.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        for i in range(3):
            self.reduction_section.columnconfigure(i, weight=1)

        # Create a label for the reduction section
        self.reduction_lbl = ctk.CTkLabel(self.reduction_section, text="Réductions", font=("Arial", 12, "bold"))
        self.reduction_lbl.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")

        # Draw the reduction cards for the dashboard on row 4 columns 0-5 with 3 cards per row
        values=["Espèces", "Carte", "Recka", "Twint", "Autre"] # TODO: As the reduction widget those values at the end should be set in a config file or in a database, but for now we will hardcode them here 
        self.reduction_cards = []

        for i in range(len(values)):
            col_index = (i % 3)  # 3 cards per row
            row_index = 1 + (i // 3)  # Start from row 5, increment every 3 cards
            print(f"Creating ReductionCard for '{values[i]}' at row {row_index}, column {col_index}")

            self.reduction_cards.append(ReductionCard(self.reduction_section,
                                                      title=values[i],
                                                      reduction_count=0,
                                                      reduction_amount="0.00"))
            self.reduction_cards[-1].grid(row=row_index, column=col_index, padx=5, pady=5, sticky="ew")


    def update_form_dict(self, data):
        """
        Get the data from a dictionary to update the dashboard.

        Args:
            data (dict): A dictionary containing financial metrics 
                         and ticket counts..
        """
        self.net_cash_amount_card.update_value(f"{data['net_cash_amount']:.2f}")
        self.gross_amount_card.update_value(f"{data['gross_amount']:.2f}")
        self.net_amount_card.update_value(f"{data['net_amount']:.2f}")

        self.lunch_period_card.update_values(
            data['lunch_ticket_count'], 
            data['lunch_ticket_takeaway_count'], 
            f"{data['lunch_amount']:.2f}"
        )
        self.evening_period_card.update_values(
            data['evening_ticket_count'], 
            data['evening_ticket_takeaway_count'], 
            f"{data['evening_amount']:.2f}"
        )
        self.total_period_card.update_values(
            data['total_ticket_count'], 
            data['total_ticket_takeaway_count'], 
            f"{data['total_amount']:.2f}"
        )

        for i, method in enumerate(data['methods']):
            self.reduction_cards[i].update_values(
                data['reduction_counts'][method], 
                f"{data['reduction_totals'][method]:.2f}"
            )




