import os
import subprocess
import snowflake.connector
import time  # ⏰ Added to enable sleep

# ❗ WARNING: Do not hardcode credentials in production.
SNOWFLAKE_ACCOUNT = 'cm17072.south-central-us.azure'
SNOWFLAKE_USER = 'SRUTHIMANI173'
SNOWFLAKE_PASSWORD = 'Sachinindia123*'
SNOWFLAKE_ROLE = 'ACCOUNTADMIN'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
SNOWFLAKE_DATABASE = 'DATAPLATFORM'
SNOWFLAKE_SCHEMA = 'STAGE'

# ⛏️ Detect changed .sql files between last commit and current
def get_changed_sql_files():
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.stderr:
        print(f"⚠️ Git error: {result.stderr}")

    changed_files = result.stdout.splitlines()
    print("📁 Changed files:", changed_files)

    sql_files = [f for f in changed_files if f.endswith(".sql") and os.path.exists(f)]
    return sql_files

# 📜 Read and run SQL
def execute_sql_file(file_path, cursor):
    print(f"\n⚙️ Executing SQL file: {file_path}")
    with open(file_path, 'r') as f:
        sql = f.read()

    statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
    for stmt in statements:
        print(f"🔹 Running statement: {stmt}")
        cursor.execute(stmt)

# 🚀 Main flow
def main():
    sql_files = get_changed_sql_files()

    if not sql_files:
        print("✅ No SQL file changes detected. Skipping execution.")
        return

    print("⏳ Waiting 30 seconds before executing SQL...")
    time.sleep(30)

    # Connect to Snowflake
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        role=SNOWFLAKE_ROLE,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
    )
    cursor = conn.cursor()

    try:
        for sql_file in sql_files:
            execute_sql_file(sql_file, cursor)
        print("\n✅ All changed SQL files executed successfully.")
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
