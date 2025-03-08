import psycopg


class BankDBConn:
    @classmethod
    async def customer_name(cls, *, query_id: str) -> str | None:
        with psycopg.connect("dbname=zion user=paradigmx") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM bank_account WHERE account_number=%s", (query_id,))
                row = cur.fetchone()
                if row:
                    return row[0].strip() # type: ignore
                else:
                    raise ValueError('Customer not found')

    @classmethod
    async def customer_balance(cls, *, query_id: str, include_pending: bool) -> float:
        with psycopg.connect("dbname=zion user=paradigmx") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT balance, pending FROM bank_account WHERE account_number=%s", (query_id,))
                row = cur.fetchone()
                if row:
                    balance = row[0]
                    if include_pending: balance += row[1]
                    return balance
                else:
                    raise ValueError('Customer not found')


if __name__ == "__main__":
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
