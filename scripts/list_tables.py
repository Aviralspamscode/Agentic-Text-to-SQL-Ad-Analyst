import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)
print(
    con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main' ORDER BY 1"
    ).df()
)
