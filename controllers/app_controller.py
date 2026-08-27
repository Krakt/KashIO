# controllers/app_controller.py
from database import save_closure_to_database, get_data_between_dates, get_payment_methods_summary
from widgets.ui_widgets import ClosureModal

class AppController:
    def __init__(self, main_app):
        self.app = main_app

    def check_form_validity(self):
        has_valid_tickets = False
        for ticket in self.app.tab_view.daily_tab_view.page_tickets.rows:
            try:
                amount = float(ticket["amount"].get() or 0.0)
                if amount > 0.0:
                    has_valid_tickets = True
                    break
            except ValueError:
                pass  

        if has_valid_tickets:
            self.app.tab_view.daily_tab_view.page_reductions.set_state("normal")
        else:
            self.app.tab_view.daily_tab_view.page_reductions.set_state("disabled")

    def calculate_all_values(self, *args):
        if args:
            print(f"[DEBUG] calculate_all_values got some unexpected values: {args}")

        self.check_form_validity()

        tickets_data = self.app.tab_view.daily_tab_view.page_tickets.rows
        reductions_data = self.app.tab_view.daily_tab_view.page_reductions.rows
        expenses_data = self.app.tab_view.daily_tab_view.page_expenses.rows

        periods = {
            "lunch": {"ticket_count": 0, "ticket_eatin_count": 0, "ticket_takeaway_count": 0, "ticket_delivery_count": 0, "gross_amount": 0.0},
            "evening": {"ticket_count": 0, "ticket_eatin_count": 0, "ticket_takeaway_count": 0, "ticket_delivery_count": 0, "gross_amount": 0.0}
        }

        methods = ["cash", "card", "reka", "twint", "other"]
        t_totals = {method: 0.0 for method in methods}
        t_counts = {method: 0 for method in methods}

        for ticket in tickets_data:
            method = ticket["method"].get_value()
            period = ticket["period"].get_value()
            location = ticket["location"].get_value()
            amount = ticket["amount"].get_value()

            if method in t_totals:
                t_totals[method] += amount
                t_counts[method] += 1

            period_key = period
            periods[period_key]["ticket_count"] += 1

            if location == "eat_in":
                periods[period_key]["ticket_eatin_count"] += 1
            elif location == "takeaway":
                periods[period_key]["ticket_takeaway_count"] += 1
            else:
                periods[period_key]["ticket_delivery_count"] += 1
            
            periods[period_key]["gross_amount"] += amount

        r_totals = {m: 0.0 for m in methods}
        r_counts = {m: 0 for m in methods}
        total_reductions = 0.0

        for reduction in reductions_data:
            reduction_method = reduction["reduction_method"].get_value()
            count = reduction["reduction_count"].get_value()

            try:
                amount = float(reduction["reduction_amount"].get() or 0.0)
            except ValueError:
                amount = 0.0

            if count > 0 and reduction_method in r_totals:
                r_totals[reduction_method] += amount
                r_counts[reduction_method] += count

            total_reductions += amount

        total_expenses = 0.0
        for expense in expenses_data:
            # If your expenses have a value/code selector or payment method:
            # method = expense["method"].get_value()
            amount = expense["amount"].get_value()
            total_expenses += amount

        total_gross_amount = periods["lunch"]["gross_amount"] + periods["evening"]["gross_amount"]
        total_net_amount = total_gross_amount - total_reductions
        total_net_cash = t_totals["cash"] - r_totals["cash"]

        dashboard = self.app.tab_view.daily_tab_view.page_dashboard
        dashboard.net_cash_amount_card.update_value(f"{total_net_cash:.2f}")
        dashboard.gross_amount_card.update_value(f"{total_gross_amount:.2f}")
        dashboard.net_amount_card.update_value(f"{total_net_amount:.2f}")

        dashboard.lunch_period_card.update_values(
            periods["lunch"]["ticket_count"],
            periods["lunch"]["ticket_takeaway_count"],
            f"{periods['lunch']['gross_amount']:.2f}"
        )
        dashboard.evening_period_card.update_values(
            periods["evening"]["ticket_count"],
            periods["evening"]["ticket_takeaway_count"],
            f"{periods['evening']['gross_amount']:.2f}"
        )
        dashboard.total_period_card.update_values(
            periods["lunch"]["ticket_count"] + periods["evening"]["ticket_count"],
            periods["lunch"]["ticket_takeaway_count"] + periods["evening"]["ticket_takeaway_count"],
            f"{total_gross_amount:.2f}"
        )

        for i, method in enumerate(methods):
            dashboard.reduction_cards[i].update_values(r_counts[method], f"{r_totals[method]:.2f}")

    # TODO: Need to add the expense rows so they are saved too
    def save_to_database(self):
        def on_confirm(closure_date, send_email):
            try:
                save_closure_to_database(
                    self.app.tab_view.daily_tab_view.page_tickets.rows,
                    self.app.tab_view.daily_tab_view.page_reductions.rows,
                    closure_date,
                    send_email
                )
                generate_pdf(closure_date)
                print(f"[INFO] Clôture et PDF enregistrés pour le {closure_date}")
            except Exception as e:
                print(f"[ERREUR] Échec de la clôture : {e}")
            
        self.modal = ClosureModal(self.app, on_confirm)
        self.modal.grab_set()

        def generate_pdf(closure_date):
            from pdf_generator import generate_closure_pdf
            filename = f"cloture_{closure_date}.pdf"
            generate_closure_pdf(
                closure_date,
                self.app.tab_view.daily_tab_view.section1.rows,
                self.app.tab_view.daily_tab_view.section2.rows,
                filename
            )

    # TODO: has to be redo with all the modification
    def _process_summary_data(self, raw_data):
        methods = ["Espèces", "Carte", "Reka", "Twint", "Autre"]
        periods = {
            "Lunch": {"ticket_count": 0, "takeaway_ticket_count": 0, "gross_amount": 0.0},
            "Evening": {"ticket_count": 0, "takeaway_ticket_count": 0, "gross_amount": 0.0}
        }
        t_totals = {m: 0.0 for m in methods}
        t_counts = {m: 0 for m in methods}

        for row in raw_data["tickets"]:
            is_evening, is_takeaway, method, total_amount, count_tickets = row
            period_key = "Evening" if is_evening else "Lunch"
            periods[period_key]["ticket_count"] += count_tickets
            if is_takeaway:
                periods[period_key]["takeaway_ticket_count"] += count_tickets
            periods[period_key]["gross_amount"] += total_amount

            if method in t_totals:
                t_totals[method] += total_amount
                t_counts[method] += count_tickets

        r_totals = {m: 0.0 for m in methods}
        r_counts = {m: 0 for m in methods}
        total_reductions = 0.0

        for row in raw_data["reductions"]:
            method, total_number, total_amount = row
            if method in r_totals:
                r_totals[method] += total_amount
                r_counts[method] += total_number
            total_reductions += total_amount

        total_gross_amount = periods["Lunch"]["gross_amount"] + periods["Evening"]["gross_amount"]
        total_net_amount = total_gross_amount - total_reductions
        total_net_cash = t_totals["Espèces"] - r_totals["Espèces"]

        return {
            "net_cash_amount": total_net_cash,
            "gross_amount": total_gross_amount,
            "net_amount": total_net_amount,
            "lunch_ticket_count": periods["lunch"]["ticket_count"],
            "lunch_ticket_takeaway_count": periods["lunch"]["takeaway_ticket_count"],
            "lunch_amount": periods["lunch"]["gross_amount"],
            "evening_ticket_count": periods["evening"]["ticket_count"],
            "evening_ticket_takeaway_count": periods["evening"]["takeaway_ticket_count"],
            "evening_amount": periods["evening"]["gross_amount"],
            "total_ticket_count": periods["lunch"]["ticket_count"] + periods["Evening"]["ticket_count"],
            "total_ticket_takeaway_count": periods["lunch"]["takeaway_ticket_count"] + periods["evening"]["takeaway_ticket_count"],
            "total_amount": total_gross_amount,
            "methods": methods,
            "reduction_counts": r_counts,
            "reduction_totals": r_totals
        }

    def generate_summary(self, start, end):
        raw_data = get_data_between_dates(start, end)
        if not raw_data:
            print("[WARNING] No data found for this date range.")
            return

        processed_data = self._process_summary_data(raw_data)
        self.app.tab_view.summary_tab_view.summary_dashboard.update_form_dict(processed_data)

        payment_data = get_payment_methods_summary(start, end)
        self.app.tab_view.summary_tab_view.summary_charts_frame.update_data(payment_data)
        self.app.tab_view.summary_tab_view.summary_table_widget.update_data(payment_data)