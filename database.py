import sqlite3
import os
import sys
from datetime import datetime, timedelta

# Current application database version
ACTUAL_VERSION = 1
CLOSURES_DIR = "closures"

def get_db_connection():
    return sqlite3.connect('kashio.db')

def check_database_version(db_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create the table for the version of the db if it doesn't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS db_version (version INTEGER PRIMARY KEY)")
    
    # Fetch the version of the db
    cursor.execute("SELECT version FROM db_version")
    row = cursor.fetchone()
    
    if row is None:
        # If the table is empty, initialize to the current version
        cursor.execute("INSERT INTO db_version (version) VALUES (?)", (ACTUAL_VERSION,))
        conn.commit()
    else:
        version_db = row[0]
        if version_db < ACTUAL_VERSION:
            # Call the migration process if the database is outdated
            run_migrations(conn, version_db)
            
    conn.close()

def run_migrations(conn, version_db):
    print(f"Database update required from version {version_db} to {ACTUAL_VERSION}")
    # Add migration logic here as the app grows
    # Example:
    # if version_db < 2:
    #     conn.execute("ALTER TABLE ...")
    
    conn.execute("UPDATE db_version SET version = ?", (ACTUAL_VERSION,))
    conn.commit()

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Use get_resource_path to find the SQL file
    sql_path = get_resource_path('database.sql')
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())
    
    conn.commit()
    conn.close()

def ensure_closures_dir():
    """Create the closures directory if it does not exist."""
    if not os.path.exists(CLOSURES_DIR):
        os.makedirs(CLOSURES_DIR)
        print(f"[INFO] Created directory: {CLOSURES_DIR}")


def get_or_create_shop(cursor, shop_name):
    """Finds a shop by name (case-insensitive) or creates it if it doesn't exist."""
    cleaned_name = shop_name.strip()
    if not cleaned_name:
        cleaned_name = "Inconnu"
        
    cursor.execute("SELECT id FROM shops WHERE LOWER(name) = LOWER(?)", (cleaned_name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    
    cursor.execute("INSERT INTO shops (name) VALUES (?)", (cleaned_name,))
    return cursor.lastrowid


def save_closure_to_database(tickets_data, reductions_data, expenses_data, closure_date, is_email_sent):
    ensure_closures_dir()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO closures (closure_date, is_email_sent) 
                VALUES (?, ?)
            """, (closure_date, 1 if is_email_sent else 0))
            closure_id = cursor.lastrowid

            # Save Tickets using new schema mapping
            for ticket in tickets_data:
                is_evening = 1 if ticket["period"].get_value() == "evening" else 0
                location_val = ticket["location"].get_value()
                location_id = 1 if location_val == "eat_in" else (2 if location_val == "takeaway" else 3)

                cursor.execute("""
                    INSERT INTO tickets (closure_id, is_evening, location_id, method, amount)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    closure_id,
                    is_evening,
                    location_id,
                    ticket["method"].get_value(),
                    float(ticket["amount"].get_value() or 0.0)
                ))

            # Save Reductions
            for reduction in reductions_data:
                count = int(reduction["reduction_count"].get() or 0)
                if count > 0:
                    amount_val = reduction["reduction_amount"].get_value() if hasattr(reduction["reduction_amount"], "get_value") else float(reduction["reduction_amount"].get() or 0.0)
                    cursor.execute("""
                        INSERT INTO reductions (closure_id, count, method, amount)
                        VALUES (?, ?, ?, ?)
                    """, (
                        closure_id,
                        count,
                        reduction["reduction_method"].get(),
                        float(amount_val or 0.0)
                    ))

            # Save Expenses with shop lookup/creation
            for expense in expenses_data:
                shop_name = expense["shop"].get_value()
                shop_id = get_or_create_shop(cursor, shop_name)
                
                cursor.execute("""
                    INSERT INTO expenses (closure_id, shop_id, category_code, method, amount)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    closure_id,
                    shop_id,
                    expense["category"].get_value(),
                    expense["method"].get_value(),
                    float(expense["amount"].get_value() or 0.0)
                ))

            conn.commit()
        except Exception as e:
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
            print(f"An error occurred:\n {e}")
            return None


def get_payment_methods_summary(start_date, end_date):
    """Retrieves the total amounts by payment method for a given period."""
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
    """Generates a 3-week test set (Tuesday to Sunday, no Mondays)"""
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
        
        print("[INFO] Test dataset successfully inserted (excluding Mondays) !")