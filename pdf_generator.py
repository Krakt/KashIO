from fpdf import FPDF
from datetime import datetime

class ClosurePDF(FPDF):
    def header(self):
        # Titre du document
        self.set_font("helvetica", "B", 16)
        self.cell(0, 10, "KashIO - Rapport de Clôture", align="center", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 10)
        self.cell(0, 5, f"Généré le {datetime.now().strftime('%d.%m.%Y à %H:%M')}", align="center", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        # Pied de page
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="center")

def generate_closure_pdf(closure_date, tickets_data, reductions_data, filename="cloture.pdf"):
    pdf = ClosurePDF()
    pdf.add_page()
    
    # Date de clôture concernée
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, f"Date de clôture : {closure_date}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Section Tickets
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "1. Détails des Tickets", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    for ticket in tickets_data:
        wording = ticket["wording"].get() or "Sans libellé"
        method = ticket["method"].get()
        amount = ticket["amount"].get() or "0.00"
        pdf.cell(0, 6, f" - {wording} ({method}) : {amount} CHF", new_x="LMARGIN", new_y="NEXT")
        
    pdf.ln(5)
    
    # Section Réductions
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "2. Réductions", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    for reduction in reductions_data:
        count = reduction["reduction_count"].get() or "0"
        method = reduction["reduction_method"].get()
        amount = reduction["reduction_amount"].get() or "0.00"
        if int(count) > 0:
            pdf.cell(0, 6, f" - {method} : {count} réductions pour un total de {amount} CHF", new_x="LMARGIN", new_y="NEXT")

    pdf.output(filename)
    print(f"[INFO] PDF généré avec succès : {filename}")