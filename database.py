import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('kashio.db')
    cursor = conn.cursor()
    
    # Execute the SQL statements to create tables
    with open('database.sql', 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())
    
    conn.commit()
    conn.close()


def save_closure_to_database(tickets_data, reductions_data, closure_date, is_email_sent):
        # Save the current state of tickets and reductions to the database
    with open_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # 1. Créer la clôture du jour
            cursor.execute("""
                INSERT INTO closures (closure_date, is_email_sent) 
                VALUES (?, ?)
            """, (closure_date, 1 if is_email_sent else 0))
            closure_id = cursor.lastrowid

            # 2. Insérer les tickets
            for ticket in tickets_data:
                cursor.execute("""
                    INSERT INTO tickets (closure_id, wording, is_evening, is_takeaway, method, amount)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    closure_id,
                    ticket["wording"].get(),
                    1 if ticket["evening"].get() else 0,
                    1 if ticket["takeaway"].get() else 0,
                    ticket["method"].get(),
                    float(ticket["amount"].get() or 0)
                ))

            # 3. Insérer les réductions
            for reduction in reductions_data:
                cursor.execute("""
                    INSERT INTO reductions (closure_id, count, method, amount)
                    VALUES (?, ?, ?, ?)
                """, (
                    closure_id,
                    int(reduction["reduction_count"].get() or 0),
                    reduction["reduction_method"].get(),
                    float(reduction["reduction_amount"].get() or 0)
                ))

            # Si on arrive ici sans erreur, le 'with' valide (commit) tout d'un coup.
            conn.commit()
            
        except Exception as e:
            # En cas de pépin, SQLite annule tout (rollback)
            conn.rollback()
            raise e


def save_ticket_to_database(ticket_data):
    with open_database_connection() as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO tickets (closure_id, wording, evening, takeaway, method, amount)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                ticket_data['closure_id'],
                ticket_data['wording'],
                ticket_data['evening'],
                ticket_data['takeaway'],
                ticket_data['method'],
                ticket_data['amount']
            ))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e


def save_reduction_to_database(reduction_data):
    with open_database_connection() as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO reductions (closure_id, number, method, amount)
                VALUES (?, ?, ?, ?)
            """, (
                reduction_data['closure_id'],
                reduction_data['count'],
                reduction_data['method'],
                reduction_data['amount']
            ))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e


def open_database_connection():
    return sqlite3.connect('kashio.db')


def delete_ticket_from_database(ticket_id):
    with open_database_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e


def get_data_between_dates(start_date, end_date):
    with open_database_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT t.is_evening, t.is_takeaway, t.method,
                       SUM(t.amount) as total_amount,
                       COUNT(t.id) as count_tickets
                FROM tickets t
                JOIN closures c ON t.closure_id = c.id
                WHERE c.closure_date BETWEEN ? AND ?
                GROUP BY t.is_evening, t.is_takeaway, t.method;
            """, (start_date, end_date))
            tickets_data = cursor.fetchall()

            cursor.execute("""
                SELECT r.method,
                       SUM(r.count) as total_count,
                       SUM(r.amount) as total_amount
                FROM reductions r
                JOIN closures c ON r.closure_id = c.id
                WHERE c.closure_date BETWEEN ? AND ?
                GROUP BY r.method;
            """, (start_date, end_date))
            reductions_data = cursor.fetchall()

            return {
                "tickets": tickets_data,
                "reductions": reductions_data
            }
        
        except Exception as e:
            print(f"Une erreur est survenue:\n {e}")
            return None


def get_payment_methods_summary(start_date, end_date):
    """Récupère le total des montants par moyen de paiement sur une période donnée"""
    with open_database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT T.method, SUM(T.amount) as total_amount
            FROM tickets T
            JOIN closures C ON T.closure_id = C.id
            WHERE C.closure_date BETWEEN ? AND ?
            GROUP BY T.method
        """, (start_date, end_date))
        return cursor.fetchall()


def seed_test_data():
    """Génère un jeu de test de 3 semaines (mardi au dimanche, pas de lundi)"""
    import random
    
    with open_database_connection() as conn:
        cursor = conn.cursor()
        
        # Vérifie si la table closures a déjà des données pour éviter les doublons à chaque lancement
        cursor.execute("SELECT COUNT(*) FROM closures")
        if cursor.fetchone()[0] > 0:
            return  # La base a déjà des données, on ne fait rien
        
        # On part d'une date de début (par exemple un mardi, il y a 3 semaines)
        # On utilise le contexte temporel actuel ou une date fixe de référence
        start_date = datetime(2026, 6, 2) # Un mardi de référence
        
        methods = ['Espèces', 'Carte', 'Recka', 'Twint', 'Autre']
        reduction_methods = ['Espèces', 'Carte', 'Recka']
        
        # Générer sur 21 jours (environ 3 semaines)
        for i in range(25):
            current_date = start_date + timedelta(days=i)
            
            # Exclusion du lundi (weekday() == 0 en Python)
            if current_date.weekday() == 0:
                continue
                
            date_str = current_date.strftime('%Y-%m-%d')
            
            try:
                # 1. Créer la clôture
                cursor.execute("""
                    INSERT INTO closures (closure_date, is_email_sent) 
                    VALUES (?, ?)
                """, (date_str, random.choice([0, 1])))
                closure_id = cursor.lastrowid
                
                # 2. Insérer quelques tickets pour cette journée (ex: 5 à 10 tickets)
                for _ in range(random.randint(5, 10)):
                    cursor.execute("""
                        INSERT INTO tickets (closure_id, wording, is_evening, is_takeaway, method, amount)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        closure_id,
                        random.choice(['Menu du jour', 'Plat A', 'Plat B', 'Boisson', 'Dessert']),
                        random.choice([0, 1]),
                        random.choice([0, 1]),
                        random.choice(methods),
                        round(random.uniform(15.0, 120.0), 2)
                    ))
                
                # 3. Insérer quelques réductions (0 à 3 par jour)
                for _ in range(random.randint(0, 3)):
                    cursor.execute("""
                        INSERT INTO reductions (closure_id, count, method, amount)
                        VALUES (?, ?, ?, ?)
                    """, (
                        closure_id,
                        random.randint(1, 4),
                        random.choice(reduction_methods),
                        round(random.uniform(10.0, 50.0), 2)
                    ))
                    
                conn.commit()
            except Exception as e:
                # Si la date existe déjà, on ignore pour le test
                continue
        
        print("[INFO] Jeu de données de test inséré avec succès (sans les lundis) !")