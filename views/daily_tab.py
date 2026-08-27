import customtkinter as ctk
from widgets.dashboard_widget import DashboardWidget
from widgets.expense_widget import ExpenseWidget
from widgets.reduction_widget import ReductionWidget
from widgets.ticket_widget import TicketWidget

class DailyTab(ctk.CTkFrame):
    """
    The daily tab view of the app (inherits from CTkFrame so it can be packed/placed inside the tab view)
    """
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, **kwargs)
        self.app_controller = app_controller

        # Configure this frame to fill the tab space
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)  # Row 1 expands for content

        # --- STEP NAVIGATION HEADER ---
        self.current_step = 0
        self.total_steps = 4
        self.step_titles = [
            "Étape 1/4 : Saisie des Tickets",
            "Étape 2/4 : Réductions",
            "Étape 3/4 : Dépenses",
            "Étape 4/4 : Clôture & Analyse"
        ]

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header_frame.columnconfigure(1, weight=1)

        self.btn_prev = ctk.CTkButton(header_frame, text="◀", width=40, command=self.prev_step)
        self.btn_prev.grid(row=0, column=0, sticky="w")

        self.step_title_lbl = ctk.CTkLabel(header_frame, text=self.step_titles[0], font=("Arial", 16, "bold"))
        self.step_title_lbl.grid(row=0, column=1, sticky="nsew")

        self.btn_next = ctk.CTkButton(header_frame, text="▶", width=40, command=self.next_step)
        self.btn_next.grid(row=0, column=2, sticky="e")

        # --- CONTENT CONTAINER (WIZARD PAGES) ---
        self.wizard_container = ctk.CTkFrame(self, fg_color="transparent")
        self.wizard_container.grid(row=1, column=0, sticky="news", padx=10, pady=10)
        self.wizard_container.columnconfigure(0, weight=1)
        self.wizard_container.rowconfigure(0, weight=1)

        # Page 1: Tickets
        self.page_tickets = TicketWidget(self.wizard_container,
                                         title="Tickets",
                                         on_change=self.app_controller.calculate_all_values,
                                         fg_color="red")
        
        # Page 2: Reductions
        self.page_reductions = ReductionWidget(self.wizard_container,
                                               title="Reductions",
                                               on_change=self.app_controller.calculate_all_values,
                                               fg_color="blue")

        # Page 3: Expenses
        self.page_expenses = ExpenseWidget(self.wizard_container,
                                           title="Dépenses",
                                           on_change=self.app_controller.calculate_all_values,
                                           fg_color="green")
        
        # Page 4: Dashboard & Save Button
        self.page_dashboard_container = ctk.CTkFrame(self.wizard_container, fg_color="transparent")
        self.page_dashboard_container.columnconfigure(0, weight=1)
        self.page_dashboard_container.rowconfigure(0, weight=1)  # Dashboard expands to fill space
        self.page_dashboard_container.rowconfigure(1, weight=0)

        self.dashboard_scrollable_frame = ctk.CTkScrollableFrame(self.page_dashboard_container)
        self.dashboard_scrollable_frame.columnconfigure(0, weight=1)  # Dashboard expands to fill space
        self.dashboard_scrollable_frame.grid(row=0, column=0, sticky="news", padx=5, pady=(5, 10))

        self.page_dashboard = DashboardWidget(self.dashboard_scrollable_frame, title="Clôture", fg_color="yellow")
        self.page_dashboard.grid(row=0, column=0, sticky="news", padx=5, pady=(5, 10))

        self.save_button = ctk.CTkButton(self.page_dashboard_container, text="Enregistrer la clôture",
                                            command=self.app_controller.save_to_database, fg_color="green", height=40)
        self.save_button.grid(row=1, column=0, sticky="ew", padx=5, pady=5)


        # Show the first page initially
        self.show_step(0)

    def show_step(self, step_index):
        """Switch visibility between wizard pages"""
        self.current_step = step_index
        self.step_title_lbl.configure(text=self.step_titles[self.current_step])

        # Hide all pages
        self.page_tickets.grid_forget()
        # self.page_reductions_expenses.grid_forget()
        self.page_reductions.grid_forget()
        self.page_expenses.grid_forget()
        self.page_dashboard_container.grid_forget()

        # Show current page
        if self.current_step == 0:
            self.page_tickets.grid(row=0, column=0, sticky="news")
            self.btn_prev.configure(state="disabled")
        else:
            self.btn_prev.configure(state="normal")

        if self.current_step == 1:
            self.page_reductions.grid(row=0, column=0, sticky="news")

        if self.current_step == 2:
            self.page_expenses.grid(row=0, column=0, sticky="news")

        if self.current_step == 3:
            self.page_dashboard_container.grid(row=0, column=0, sticky="news")
            self.btn_next.configure(state="disabled")
        else:
            self.btn_next.configure(state="normal")

    def next_step(self):
        if self.current_step < self.total_steps - 1:
            self.show_step(self.current_step + 1)

    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)