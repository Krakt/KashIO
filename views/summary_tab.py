import customtkinter as ctk
from widgets.dashboard_widget import DashboardWidget
from widgets.date_picker_widget import DatePicker
from widgets.ui_widgets import SummaryChartsFrame, SummaryTableWidget

class SummaryTab(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, **kwargs)
        self.app_controller = app_controller

        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.date_picker = DatePicker(master=self, on_button_click=self.app_controller.generate_summary)
        self.date_picker.grid(row=0, column=0, padx=10, pady=10, sticky="news")

        self.summary_dashboard = DashboardWidget(master=self, title="Analyse", fg_color="purple")
        self.summary_dashboard.grid(row=1, column=0, rowspan=2, padx=10, pady=10, sticky="news")

        self.summary_charts_frame = SummaryChartsFrame(master=self)
        self.summary_charts_frame.grid(row=1, column=1, sticky="news", padx=10, pady=10)

        self.summary_table_widget = SummaryTableWidget(master=self)
        self.summary_table_widget.grid(row=2, column=1, sticky="news", padx=10, pady=10)