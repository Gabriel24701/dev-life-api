import sqlite3

def create_tables():
    with sqlite3.connect("database/devlife.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                status INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                goal_type TEXT NOT NULL,
                target INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                completed_dates TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                platform TEXT NOT NULL,
                progress INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                completed INTEGER NOT NULL
            );
        """)
        conn.commit()

if __name__ == "__main__":
    create_tables()
    print("Tabelas criadas com sucesso!")