
import sqlite3
from pathlib import Path

base_path = Path(__file__).resolve().parents[1]

db_file = (
    base_path / "data" / "processed" / "manufacturing.db"
)

sql_file = (
    base_path / "sql" / "analysis_queries.sql"
)

connection = sqlite3.connect(db_file)

with open(sql_file, "r", encoding="utf-8") as file:
    sql_content = file.read()

# Extract complete SQL statements
statements = []
current_statement = ""

for line in sql_content.splitlines():

    stripped = line.strip()

    if not stripped or stripped.startswith("--"):
        continue

    current_statement += line + "\n"

    if sqlite3.complete_statement(current_statement):
        statements.append(current_statement.strip())
        current_statement = ""

cursor = connection.cursor()

for number, statement in enumerate(statements, start=1):

    print(f"\n{'=' * 55}")
    print(f"SQL QUERY {number}")
    print("=" * 55)

    cursor.execute(statement)

    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    print(" | ".join(columns))
    print("-" * 100)

    for row in rows:
        print(" | ".join(str(value) for value in row))

    print(f"\nRows returned: {len(rows)}")

connection.close()

print("\nALL SQL QUERIES EXECUTED SUCCESSFULLY!")
