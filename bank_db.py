import asyncpg


class BankDBConn:
    @classmethod
    async def customer_name(cls, *, query_id: str) -> str | None:
        conn = await asyncpg.connect(user='paradigmx', database='zion')
        row = await conn.fetchrow("SELECT name FROM bank_account WHERE account_number=$1", query_id)
        if row:
            return row["name"].strip()
        else:
            raise ValueError('Customer not found')

    @classmethod
    async def customer_balance(cls, *, query_id: str, include_pending: bool) -> float:
        conn = await asyncpg.connect(user='paradigmx', database='zion')
        row = await conn.fetchrow("SELECT balance, pending FROM bank_account WHERE account_number=$1",
                                  query_id)
        if row:
            balance = row["balance"]
            if include_pending: balance += row["pending"]
            return balance
        else:
            raise ValueError('Customer not found')


if __name__ == "__main__":
    import asyncio
    from rich import print

    query_id = "101"
    customer_name = asyncio.run(BankDBConn.customer_name(query_id=query_id))
    print(customer_name)
    customer_balance = asyncio.run(BankDBConn.customer_balance(query_id=query_id, include_pending=True))
    print(customer_balance)
