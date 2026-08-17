import customtkinter as ctk


class EmailManagement(ctk.CTkFrame):
    def __init__(self, master, title, initial_items=None, **kwargs):
        super().__init__(master, **kwargs)  # Correction du super()

        # Dictionnaire par défaut si rien n'est fourni
        items = initial_items or {}

        # Initialisation des variables Tkinter (StringVar / BooleanVar)
        self.email_to_var = ctk.StringVar(value=items.get("email_to", ""))
        self.own_smtp_var = ctk.BooleanVar(value=items.get("own_smtp", False))
        self.email_from_var = ctk.StringVar(value=items.get("email_from", ""))
        self.srv_smtp_var = ctk.StringVar(value=items.get("srv_smtp", ""))
        self.port_smtp_var = ctk.StringVar(value=items.get("port_smtp", "465"))
        self.pwd_srv_var = ctk.StringVar(value=items.get("pwd_srv", ""))
        self.smtp_sec_var = ctk.StringVar(value=items.get("smtp_sec", "None"))

        # Titre
        self.title_lbl = ctk.CTkLabel(self, text=title, font=("Arial", 16, "bold"))
        self.title_lbl.pack(fill="x", pady=(10, 20))

        # Destinataire (toujours visible)
        self.create_row("Destinataire", "Destinataire", self.email_to_var)

        # Séparateur / Section SMTP
        self.section1 = ctk.CTkFrame(self, fg_color="transparent")
        self.section1.pack(fill="x", pady=10)

        self.own_smtp_lbl = ctk.CTkLabel(self.section1, text="Propre SMTP")
        self.own_smtp_lbl.pack(side="left")

        # Le switch pilote l'activation des champs SMTP
        self.own_smtp_switch = ctk.CTkSwitch(
            self.section1, text="", variable=self.own_smtp_var, command=self.toggle_smtp_fields
        )
        self.own_smtp_switch.pack(side="right")

        # Champs SMTP (stockés dans une liste pour les activer/désactiver facilement)
        self.smtp_entries = []
        
        self.smtp_entries.append(self.create_row("Envoyeur", "Email de l'envoyeur", self.email_from_var))
        self.smtp_entries.append(self.create_row("Serveur SMTP", "mail.serveur.com", self.srv_smtp_var))
        self.smtp_entries.append(self.create_row("Port SMTP", "Ex: 465 ou 587", self.port_smtp_var))
        self.smtp_entries.append(self.create_row("Password SMTP", "Mot de passe", self.pwd_srv_var, show="*"))

        # Type de sécurité (ComboBox)
        sec_frame = ctk.CTkFrame(self, fg_color="transparent")
        sec_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(sec_frame, text="Type de sécurité", width=150, anchor="w").pack(side="left")
        self.smtp_sec_cb = ctk.CTkComboBox(
            sec_frame, values=["None", "SSL", "STARTTLS"], variable=self.smtp_sec_var
        )
        self.smtp_sec_cb.pack(side="left", expand=True, fill="x")
        self.smtp_entries.append(self.smtp_sec_cb)

        # Bouton Sauver
        self.save_btn = ctk.CTkButton(self, text="Sauver", command=self.save)
        self.save_btn.pack(fill="x", pady=(20, 10))

        # Appliquer l'état initial des champs selon le switch
        self.toggle_smtp_fields()


    def create_row(self, label_text, placeholder, var, show=None):
        """Fonction utilitaire pour créer une ligne propre (Label + Entry)"""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", pady=5)

        lbl = ctk.CTkLabel(frame, text=label_text, width=150, anchor="w")
        lbl.pack(side="left")

        entry_kwargs = {"placeholder_text": placeholder, "textvariable": var}
        if show:
            entry_kwargs["show"] = show

        entry = ctk.CTkEntry(frame, **entry_kwargs)
        entry.pack(side="left", expand=True, fill="x")
        return entry


    def toggle_smtp_fields(self):
        """Active ou désactive les champs SMTP selon l'état du switch"""
        state = "normal" if self.own_smtp_var.get() else "disabled"
        for widget in self.smtp_entries:
            widget.configure(state=state)


    def save(self):
        # Récupération propre des données via les variables
        data = {
            "email_to": self.email_to_var.get(),
            "own_smtp": self.own_smtp_var.get(),
            "email_from": self.email_from_var.get(),
            "srv_smtp": self.srv_smtp_var.get(),
            "port_smtp": self.port_smtp_var.get(),
            "pwd_srv": self.pwd_srv_var.get(),
            "smtp_sec": self.smtp_sec_var.get(),
        }
        print("Données prêtes à être sauvegardées :", data)
        # TODO: Enregistrer dans la DB (avec chiffrement du password si requis)