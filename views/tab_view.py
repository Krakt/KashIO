import customtkinter as ctk
from views.daily_tab import DailyTab
from views.summary_tab import SummaryTab
from views.settings_tab import SettingsTab

class MyTabView(ctk.CTkTabview):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, **kwargs)
        self.app_controller = app_controller

        # Create a tab view container
        tab_daily = self.add("Journalier")
        tab_daily.columnconfigure(0, weight=1)
        tab_daily.rowconfigure(0, weight=1)

        # Instantiate DailyTab inside it
        self.daily_tab_view = DailyTab(master=tab_daily, app_controller=self.app_controller)
        self.daily_tab_view.grid(row=0, column=0, sticky="nsew")

        # Tab 2: Summary
        tab_summary = self.add("Récapitulatif")
        tab_summary.columnconfigure(0, weight=1)
        tab_summary.rowconfigure(0, weight=1)
        self.summary_tab_view = SummaryTab(master=tab_summary, app_controller=self.app_controller)
        self.summary_tab_view.grid(row=0, column=0, sticky="nsew")

        # Tab 3: Settings
        tab_settings = self.add("Paramètre")
        tab_settings.columnconfigure(0, weight=1)
        tab_settings.rowconfigure(0, weight=1)
        self.settings_tab_view = SettingsTab(master=tab_settings, app_controller=self.app_controller)
        self.settings_tab_view.grid(row=0, column=0, sticky="nsew")