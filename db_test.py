import psycopg
from rich import print


with psycopg.connect("dbname=zion user=paradigmx") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM bank_account")
        for record in cur:
            print(record)

        query_id = "101"
        cur.execute("SELECT name FROM bank_account WHERE account_number=%s", (query_id,))
        print(cur.fetchone()[0].strip()) # type: ignore

        cur.execute("SELECT balance FROM bank_account WHERE account_number=%s", (query_id,))
        print(cur.fetchone()[0]) # type: ignore

        conn.commit()
