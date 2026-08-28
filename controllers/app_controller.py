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
        """Called by UI widgets when data changes; updates form validity and refreshes dashboard."""
        self.check_form_validity()
        
        # Gather individual dataset results
        tickets_summary = self._calculate_tickets()
        reductions_summary = self._calculate_reductions()
        expenses_summary = self._calculate_expenses()
        
        # Combine them for the final dashboard view
        self._update_dashboard(tickets_summary, reductions_summary, expenses_summary)

    def _calculate_tickets(self):
        tickets_data = self.app.tab_view.daily_tab_view.page_tickets.rows
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

            period_key = period if period in periods else "lunch"
            periods[period_key]["ticket_count"] += 1

            if location == "eat_in":
                periods[period_key]["ticket_eatin_count"] += 1
            elif location == "takeaway":
                periods[period_key]["ticket_takeaway_count"] += 1
            else:
                periods[period_key]["ticket_delivery_count"] += 1
            
            periods[period_key]["gross_amount"] += amount

        return {"periods": periods, "totals": t_totals, "counts": t_counts}

    def _calculate_reductions(self):
        reductions_data = self.app.tab_view.daily_tab_view.page_reductions.rows
        methods = ["cash", "card", "reka", "twint", "other"]
        r_totals = {m: 0.0 for m in methods}
        r_counts = {m: 0 for m in methods}
        total_reductions = 0.0

        for reduction in reductions_data:
            reduction_method = reduction["reduction_method"].get() # Update to get_value() if you made it a ValueComboBox
            try:
                count = int(reduction["reduction_count"].get() or 0)
            except ValueError:
                count = 0
            amount = reduction["reduction_amount"].get_value() if hasattr(reduction["reduction_amount"], "get_value") else float(reduction["reduction_amount"].get() or 0.0)

            if count > 0 and reduction_method in r_totals:
                r_totals[reduction_method] += amount
                r_counts[reduction_method] += count

            total_reductions += amount

        return {"totals": r_totals, "counts": r_counts, "total_amount": total_reductions}

    def _calculate_expenses(self):
        expenses_data = self.app.tab_view.daily_tab_view.page_expenses.rows
        total_expenses = 0.0
        expenses_by_method = {}

        for expense in expenses_data:
            amount = expense["amount"].get_value()
            method = expense["method"].get_value()
            
            total_expenses += amount
            # If you want to track cash expenses specifically to deduct from cash drawer:
            if method not in expenses_by_method:
                expenses_by_method[method] = 0.0
            expenses_by_method[method] += amount

        return {"total_amount": total_expenses, "by_method": expenses_by_method}

    def get_live_net_cash(self):
        tickets = self._calculate_tickets()
        reductions = self._calculate_reductions()
        expenses = self._calculate_expenses()

        cash_sales = tickets["totals"].get("cash", 0.0)
        cash_reductions = reductions["totals"].get("cash", 0.0)
        cash_expenses = expenses["by_method"].get("cash", 0.0) # assuming 'cash' code matches your payment methods config

        return cash_sales - cash_reductions - cash_expenses

    def save_to_database(self):
        def on_confirm(closure_date, send_email):
            try:
                save_closure_to_database(
                    self.app.tab_view.daily_tab_view.page_tickets.rows,
                    self.app.tab_view.daily_tab_view.page_reductions.rows,
                    self.app.tab_view.daily_tab_view.page_expenses.rows,
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

    def _process_summary_data(self, raw_data):
        methods = ["cash", "card", "reka", "twint", "other"]
        periods = {
            "lunch": {"ticket_count": 0, "eat_in_count": 0, "ticket_takeaway_count": 0, "delivery_count": 0, "gross_amount": 0.0},
            "evening": {"ticket_count": 0, "eat_in_count": 0, "ticket_takeaway_count": 0, "delivery_count": 0, "gross_amount": 0.0}
        }
        t_totals = {m: 0.0 for m in methods}
        t_counts = {m: 0 for m in methods}

        for row in raw_data["tickets"]:
            is_evening, location_id, method, total_amount, count_tickets = row
            period_key = "evening" if is_evening else "lunch"
            
            periods[period_key]["ticket_count"] += count_tickets
            if location_id == 1:
                periods[period_key]["eat_in_count"] += count_tickets
            elif location_id == 2:
                periods[period_key]["ticket_takeaway_count"] += count_tickets
            elif location_id == 3:
                periods[period_key]["delivery_count"] += count_tickets
                
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

        total_gross_amount = periods["lunch"]["gross_amount"] + periods["evening"]["gross_amount"]
        total_net_amount = total_gross_amount - total_reductions
        total_net_cash = t_totals.get("cash", 0.0) - r_totals.get("cash", 0.0)

        total_combined = {
            "ticket_count": periods["lunch"]["ticket_count"] + periods["evening"]["ticket_count"],
            "eat_in_count": periods["lunch"]["eat_in_count"] + periods["evening"]["eat_in_count"],
            "ticket_takeaway_count": periods["lunch"]["ticket_takeaway_count"] + periods["evening"]["ticket_takeaway_count"],
            "delivery_count": periods["lunch"]["delivery_count"] + periods["evening"]["delivery_count"],
            "gross_amount": total_gross_amount
        }

        return {
            "net_cash_amount": total_net_cash,
            "gross_amount": total_gross_amount,
            "net_amount": total_net_amount,
            "lunch": periods["lunch"],
            "evening": periods["evening"],
            "total": total_combined,
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


    def _update_dashboard(self, tickets_summary, reductions_summary, expenses_summary):
        """Pushes calculated summaries to the dashboard widget display cards."""
        dashboard = self.app.tab_view.daily_tab_view.page_dashboard
        
        # Calculate gross and net
        total_gross = sum(p["gross_amount"] for p in tickets_summary["periods"].values())
        total_reductions = reductions_summary["total_amount"]
        total_net = total_gross - total_reductions
        live_net_cash = self.get_live_net_cash()

        # Update core stat cards using the correct 'update_value' method
        dashboard.net_cash_amount_card.update_value(f"{live_net_cash:.2f}")
        dashboard.gross_amount_card.update_value(f"{total_gross:.2f}")
        dashboard.net_amount_card.update_value(f"{total_net:.2f}")
        dashboard.total_expenses_card.update_value(f"{expenses_summary['total_amount']:.2f}")

        # Update period cards (Lunch, Evening, Total)
        lunch = tickets_summary["periods"]["lunch"]
        evening = tickets_summary["periods"]["evening"]
        
        total_period_data = {
            "ticket_count": lunch["ticket_count"] + evening["ticket_count"],
            "eat_in_count": lunch["ticket_eatin_count"] + evening["ticket_eatin_count"],
            "ticket_takeaway_count": lunch["ticket_takeaway_count"] + evening["ticket_takeaway_count"],
            "delivery_count": lunch["ticket_delivery_count"] + evening["ticket_delivery_count"],
            "gross_amount": total_gross
        }

        dashboard.lunch_period_card.update_values(
            lunch["ticket_count"], lunch["ticket_eatin_count"], lunch["ticket_takeaway_count"], lunch["ticket_delivery_count"], f"{lunch['gross_amount']:.2f}"
        )
        dashboard.evening_period_card.update_values(
            evening["ticket_count"], evening["ticket_eatin_count"], evening["ticket_takeaway_count"], evening["ticket_delivery_count"], f"{evening['gross_amount']:.2f}"
        )
        dashboard.total_period_card.update_values(
            total_period_data["ticket_count"], total_period_data["eat_in_count"], total_period_data["ticket_takeaway_count"], total_period_data["delivery_count"], f"{total_period_data['gross_amount']:.2f}"
        )

        # Update Reduction cards breakdown
        methods = ["cash", "card", "reka", "twint", "other"]
        for i, method in enumerate(methods):
            if i < len(dashboard.reduction_cards):
                count = reductions_summary["counts"].get(method, 0)
                amount = reductions_summary["totals"].get(method, 0.0)
                dashboard.reduction_cards[i].update_values(count, f"{amount:.2f}")