from database import get_db, engine
import sqlalchemy

def inspect():
    try:
        with engine.connect() as connection:
            print("\n--- TABLE: operadoras (Limit 1) ---")
            res_op = connection.execute(sqlalchemy.text("SELECT * FROM operadoras LIMIT 1")).mappings().first()
            print(dict(res_op) if res_op else "Table appears empty")

            print("\n--- TABLE: despesas_consolidadas (Limit 1) ---")
            res_desp = connection.execute(sqlalchemy.text("SELECT * FROM despesas_consolidadas LIMIT 1")).mappings().first()
            print(dict(res_desp) if res_desp else "Table appears empty")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
