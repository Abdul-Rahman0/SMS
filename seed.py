import psycopg2
import subprocess
import time

# DB config
DB_NAME = "student_user"
DB_USER = "student_user"
DB_PASSWORD = "student_pass"
DB_HOST = "localhost"  # or "db" if running from within Docker container
DB_PORT = 5432

def wait_for_db():
    print("⏳ Waiting for DB to become available...")
    for _ in range(10):
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            conn.close()
            print("✅ DB is ready.")
            return
        except psycopg2.OperationalError:
            time.sleep(1)
    raise Exception("❌ Could not connect to the database.")

def reset_db():
    print(f"🚨 Dropping and recreating database '{DB_NAME}'")
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
    cursor.execute(f"CREATE DATABASE {DB_NAME};")
    conn.close()
    print("✅ Database reset complete.")

if __name__ == "__main__":
    wait_for_db()
    reset_db()

    # Uncomment if you have seed data
    # load_seed_data()
    print("🎉 All done!")
