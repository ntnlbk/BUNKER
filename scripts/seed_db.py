import os
import psycopg2
from psycopg2 import sql

# Database connection details for Docker environment
DB_CONFIG = {
    "dbname": "bunker_db",
    "user": "root",
    "password": "root",
    "host": "postgres_db",
    "port": 5432
}

def seed_database():
    data_dir = "scripts/data"
    
    # Check if the data directory exists
    if not os.path.exists(data_dir):
        print(f"Error: The directory '{data_dir}' does not exist.")
        return

    conn = None
    cursor = None
    try:
        # 1. Connect to the database
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connected successfully!\n")

        # 2. Find all .txt files in the data folder
        txt_files = [f for f in os.listdir(data_dir) if f.endswith(".txt")]

        if not txt_files:
            print("No .txt files found in the 'data' directory.")
            return

        print(f"Found {len(txt_files)} text file(s) to process.\n")

        # 3. Loop through each file
        for filename in txt_files:
            # Extract table name from filename (e.g., "secrets.txt" -> "secrets")
            table_name = os.path.splitext(filename)[0].lower().strip()
            file_path = os.path.join(data_dir, filename)

            print(f"Processing '{filename}' -> Table: [{table_name}]")

            # 4. Create the table dynamically
            create_table_query = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    value TEXT
                );
            """).format(sql.Identifier(table_name))
            
            cursor.execute(create_table_query)

            # 5. Read file line by line (New Format Handler)
            inserted_count = 0
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    item = line.strip()
                    
                    # Skip empty lines or commented lines
                    if not item or item.startswith("#"):
                        continue

                    # 6. Insert each line into the table
                    insert_query = sql.SQL("""
                        INSERT INTO {} (value) 
                        VALUES (%s);
                    """).format(sql.Identifier(table_name))
                    
                    cursor.execute(insert_query, (item,))
                    inserted_count += 1

            print(f"   ✔ Inserted {inserted_count} rows into table '{table_name}'.")

        # 7. Commit all changes to the database
        conn.commit()
        print("\nAll files have been successfully seeded into their respective tables!")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        if conn:
            conn.rollback()
            print("Transaction rolled back.")
            
    finally:
        # 8. Close connections
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    seed_database()