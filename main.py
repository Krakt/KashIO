import customtkinter as ctk
import sqlite3
from widgets.dashboard_widget import DashboardWidget
from widgets.ticket_widget import TicketWidget
from widgets.reduction_widget import ReductionWidget
from widgets.list_manager_widget import ListManager
from widgets.email_widget import EmailManagement
from widgets.date_picker_widget import DatePicker
from widgets.ui_widgets import SummaryChartsFrame, SummaryTableWidget, ClosureModal
from database import init_db, save_closure_to_database, save_ticket_to_database, get_data_between_dates, get_payment_methods_summary, seed_test_data

class MyTabView(ctk.CTkTabview):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, **kwargs)

        self.app_controller = app_controller

        self._daily_tab()
        self._summary_tab()
        self._settings_tab()

    def _daily_tab(self):

        # Create tabs
        tab_daily = self.add("Journalier")
        tab_daily.columnconfigure(0, weight=1, uniform="col_split")
        tab_daily.columnconfigure(1, weight=1, uniform="col_split")

        # Create a ticket section
        self.section1 = TicketWidget(master=tab_daily,
                                     title="Tickets",
                                     on_change=self.app_controller.calculate_all_values,
                                     fg_color="red")
        self.section1.grid(row=0, column=0, padx=10, pady=10, sticky="news")

        self.section2 = ReductionWidget(master=tab_daily, title="Reductions",
                                        on_change=self.app_controller.calculate_all_values, fg_color="blue")
        self.section2.grid(row=1, column=0, padx=10, pady=10, sticky="news")

        self.section3 = DashboardWidget(master=tab_daily, title="Clôture", fg_color="yellow")
        self.section3.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="ew")


        self.save_button = ctk.CTkButton(master=tab_daily, text="Enregistrer la clôture",
                                            command=self.app_controller.save_to_database, fg_color="green")
        self.save_button.grid(row=2, column=0,  columnspan=2)

    def _summary_tab(self):
        summary_tab = self.add("Récapitulatif")

        self.date_picker = DatePicker(master=summary_tab, on_button_click=self.app_controller.generate_summary)
        self.date_picker.grid(row=0, column=0, padx=10, pady=10, sticky="news")

        self.summary_dashboard = DashboardWidget(master=summary_tab, title="Analyse", fg_color="purple")
        self.summary_dashboard.grid(row=1, column=0, rowspan=2, padx=10, pady=10, sticky="news")

        self.summary_charts_frame = SummaryChartsFrame(master=summary_tab)
        self.summary_charts_frame.grid(row=1, column=1, sticky="news")

        self.summary_table_widget = SummaryTableWidget(master=summary_tab)
        self.summary_table_widget.grid(row=2, column=1, stick="news")


    def _settings_tab(self):
        settings_tab = self.add("Paramètre")

        self.method_list_section = ctk.CTkFrame(master=settings_tab)
        self.method_list_section.grid(row=0, column=0)

        self.method_payment = ListManager(self.method_list_section, title="Methode de payement", initial_items=None)
        self.method_payment.grid(row=0, column=0)

        self.email_section = ctk.CTkFrame(master=settings_tab)
        self.email_section.grid(row=0, column=1)

        self.email = EmailManagement(self.email_section, title="Email configuration", initial_items=None)
        self.email.grid(row=0, column=0)



class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KashIO")
        self.geometry("800x600")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = MyTabView(master=self, app_controller=self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        self.check_form_validity()  # Initial check to set the button state

    def check_form_validity(self):
        has_valid_tickets = False

        # Check if there is at least one ticket with a non-empty wording and a valid amount
        for ticket in self.tab_view.section1.rows:
            try:
                amount = float(ticket["amount"].get() or 0.0)
                if amount > 0.0:
                    has_valid_tickets = True
                    break
            except ValueError:
                pass  # Ignore invalid amounts for now

        if has_valid_tickets:
            self.tab_view.save_button.configure(state="normal")
            self.tab_view.section2.set_state("normal")  # Enable the reduction section
        else:
            self.tab_view.save_button.configure(state="disabled")
            self.tab_view.section2.set_state("disabled")  # Disable the reduction section

    def calculate_all_values(self, *args):

        # Remove error but print something in the console if it's happen
        if args:
            print(f"[DEBUG] calculate_all_values got some inexpected values : {args}")

        self.check_form_validity()  # Check form validity whenever values change

        tickets_data = self.tab_view.section1.rows
        reductions_data = self.tab_view.section2.rows

        periods = {
            "Launch": {"ticket_count": 0, "ticket_takeaway_count": 0, "gross_amount": 0.0},
            "Evening": {"ticket_count": 0, "ticket_takeaway_count": 0, "gross_amount": 0.0}
        }

        methods = ["Espèces", "Carte", "Recka", "Twint", "Autre"]
        t_totals = {method: 0.0 for method in methods}
        t_counts = {method: 0 for method in methods}

        for ticket in tickets_data:
            method = ticket["method"].get()
            is_evening = ticket["evening"].get()
            is_takeaway = ticket["takeaway"].get()

            try:
                amount = float(ticket["amount"].get() or 0.0)
            except ValueError:
                amount = 0.0

            if method in t_totals:
                t_totals[method] += amount
                t_counts[method] += 1

            period_key = "Evening" if is_evening else "Launch"
            periods[period_key]["ticket_count"] += 1
            if is_takeaway:
                periods[period_key]["ticket_takeaway_count"] += 1
            periods[period_key]["gross_amount"] += amount

        r_totals = {reduction_method: 0.0 for reduction_method in methods}
        r_counts = {reduction_method: 0 for reduction_method in methods}
        total_reductions = 0.0

        for reduction in reductions_data:
            reduction_method = reduction["reduction_method"].get()

            try:
                count = int(reduction["reduction_count"].get() or 0)
            except ValueError:
                count = 0

            try:
                amount = float(reduction["reduction_amount"].get() or 0.0)
            except ValueError:
                amount = 0.0

            if count > 0 and reduction_method in r_totals:
                r_totals[reduction_method] += amount
                r_counts[reduction_method] += count

            total_reductions += amount

        total_gross_amount = periods["Launch"]["gross_amount"] + periods["Evening"]["gross_amount"]
        total_net_amount = total_gross_amount - total_reductions
        total_net_cash = t_totals["Espèces"] - r_totals["Espèces"]

        self.tab_view.section3.net_cash_amount_card.update_value(f"{total_net_cash:.2f}")

        # Update the dashboard section with the calculated values
        self.tab_view.section3.gross_amount_card.update_value(f"{total_gross_amount:.2f}")
        self.tab_view.section3.net_amount_card.update_value(f"{total_net_amount:.2f}")


        self.tab_view.section3.launch_period_card.update_values(periods["Launch"]["ticket_count"],
                                                       periods["Launch"]["ticket_takeaway_count"],
                                                       f"{periods['Launch']['gross_amount']:.2f}")
        self.tab_view.section3.evening_period_card.update_values(periods["Evening"]["ticket_count"],
                                                        periods["Evening"]["ticket_takeaway_count"],
                                                        f"{periods['Evening']['gross_amount']:.2f}")
        self.tab_view.section3.total_period_card.update_values(periods["Launch"]["ticket_count"] + periods["Evening"]["ticket_count"],
                                                      periods["Launch"]["ticket_takeaway_count"] + periods["Evening"]["ticket_takeaway_count"],
                                                      f"{total_gross_amount:.2f}")

        for i, method in enumerate(methods):
            self.tab_view.section3.reduction_cards[i].update_values(r_counts[method], f"{r_totals[method]:.2f}")

    def save_to_database(self):
        def on_confirm(closure_date, send_email):
            try:
                # 1. Sauvegarde en DB
                save_closure_to_database(self.tab_view.section1.rows,
                                         self.tab_view.section2.rows,
                                         closure_date,
                                         send_email)
                
                # 2. Génération du PDF en parallèle
                from pdf_generator import generate_closure_pdf
                filename = f"cloture_{closure_date}.pdf"
                generate_closure_pdf(closure_date, self.tab_view.section1.rows, self.tab_view.section2.rows, filename)
                
                print(f"[INFO] Clôture et PDF enregistrés pour le {closure_date}")
                
            except Exception as e:
                print(f"[ERREUR] Échec de la clôture : {e}")
            
        self.modal = ClosureModal(self, on_confirm)
        self.modal.grab_set()

    def _process_summary_data(self, raw_data):
        """
        Processes raw SQL data from get_data_between_dates and structures it
        into a dictionary compatible with DashboardWidget.update_form_dict.
        """
        methods = ["Espèces", "Carte", "Recka", "Twint", "Autre"]
        
        periods = {
            "Launch": {"ticket_count": 0, "takeaway_ticket_count": 0, "gross_amount": 0.0},
            "Evening": {"ticket_count": 0, "takeaway_ticket_count": 0, "gross_amount": 0.0}
        }

        t_totals = {method: 0.0 for method in methods}
        t_counts = {method: 0 for method in methods}

        # Traitement des tickets bruts de la DB
        # Format du fetchall: (is_evening, is_takeaway, method, total_amount, count_tickets)
        for row in raw_data["tickets"]:
            is_evening, is_takeaway, method, total_amount, count_tickets = row
            
            period_key = "Evening" if is_evening else "Launch"
            periods[period_key]["ticket_count"] += count_tickets
            if is_takeaway:
                # Note: Ajuste selon si ton SQL sépare les emportés ou non, 
                # ici on cumule le compte d'emportés
                periods[period_key]["takeaway_ticket_count"] += count_tickets if is_takeaway else 0
            periods[period_key]["gross_amount"] += total_amount

            if method in t_totals:
                t_totals[method] += total_amount
                t_counts[method] += count_tickets

        r_totals = {method: 0.0 for method in methods}
        r_counts = {method: 0 for method in methods}
        total_reductions = 0.0

        # Traitement des réductions brutes de la DB
        # Format du fetchall: (method, total_number, total_amount)
        for row in raw_data["reductions"]:
            method, total_number, total_amount = row
            if method in r_totals:
                r_totals[method] += total_amount
                r_counts[method] += total_number
            total_reductions += total_amount

        total_gross_amount = periods["Launch"]["gross_amount"] + periods["Evening"]["gross_amount"]
        total_net_amount = total_gross_amount - total_reductions
        total_net_cash = t_totals["Espèces"] - r_totals["Espèces"]

        # Construction du dictionnaire final attendu par le Dashboard
        summary_dict = {
            "net_cash_amount": total_net_cash,
            "gross_amount": total_gross_amount,
            "net_amount": total_net_amount,
            "launch_ticket_count": periods["Launch"]["ticket_count"],
            "launch_ticket_takeaway_count": periods["Launch"]["takeaway_ticket_count"],
            "launch_amount": periods["Launch"]["gross_amount"],
            "evening_ticket_count": periods["Evening"]["ticket_count"],
            "evening_ticket_takeaway_count": periods["Evening"]["takeaway_ticket_count"],
            "evening_amount": periods["Evening"]["gross_amount"],
            "total_ticket_count": periods["Launch"]["ticket_count"] + periods["Evening"]["ticket_count"],
            "total_ticket_takeaway_count": periods["Launch"]["takeaway_ticket_count"] + periods["Evening"]["takeaway_ticket_count"],
            "total_amount": total_gross_amount,
            "methods": methods,
            "reduction_counts": r_counts,
            "reduction_totals": r_totals
        }

        return summary_dict

    def generate_summary(self, start, end):
        """
        Generates and displays the summary dashboard between two dates.
        """
        raw_data = get_data_between_dates(start, end)
        if not raw_data:
            print("[WARNING] No data found for this date range.")
            return

        processed_data = self._process_summary_data(raw_data)
        self.tab_view.summary_dashboard.update_form_dict(processed_data)

        payment_data = get_payment_methods_summary(start, end)

        print(f"raw payment data:\n {payment_data}")
        # Utilisation du bon nom défini dans _summary_tab
        self.tab_view.summary_charts_frame.update_data(payment_data)
        self.tab_view.summary_table_widget.update_data(payment_data)

    def on_closing(self):
        """Fermeture propre de l'application et des graphiques"""
        import matplotlib.pyplot as plt
        
        # 1. Fermer toutes les figures Matplotlib
        plt.close('all')
        
        # 2. Détruire l'application Tkinter
        self.destroy()
        
        # 3. Quitter explicitement le processus Python
        import sys
        sys.exit(0)


if __name__ == "__main__":
    app = App()
    app._set_appearance_mode("dark")  # Set the appearance mode to dark
    init_db()  # Initialize the database
    seed_test_data()
    app.mainloop()