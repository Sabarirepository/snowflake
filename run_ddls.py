import os
import subprocess
import snowflake.connector
import time

# ❗ WARNING: Do not hardcode credentials in production!
SNOWFLAKE_ACCOUNT = 'cm17072.south-central-us.azure'
SNOWFLAKE_USER = 'SRUTHIMANI173'
SNOWFLAKE_PASSWORD = 'Sachinindia123*'
SNOWFLAKE_ROLE = 'ACCOUNTADMIN'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
SNOWFLAKE_DATABASE = 'DATAPLATFORM'
SNOWFLAKE_SCHEMA = 'STAGE'

def get_last_committed_sql_files():
    """
    Returns a list of .sql files changed in the last commit.
    """
    # Get the hash of the last commit
    result = subprocess.run(
        ["git", "log", "-n", "1", "--pretty=format:%H"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    last_commit_hash = result.stdout.strip()

    if not last_commit_hash:
        print("❌ No commits found.")
        return []

    print(f"🔎 Last commit hash: {last_commit_hash}")

    # Get the list of files changed in the last commit
    diff_result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", last_commit_hash],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    changed_files = [
        f for f in diff_result.stdout.splitlines()
        if f.endswith('.sql') and os.path.exists(f)
    ]

    print(f"📁 .sql files in last commit: {changed_files}")
    return changed_files

def execute_sql_file(file_path, cursor):
    print(f"\n⚙️ Executing SQL file: {file_path}")
    with open(file_path, 'r') as f:
        sql = f.read()
    statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
    for stmt in statements:
        print(f"🔹 Running: {stmt}")
        cursor.execute(stmt)

def main():
    sql_files = get_last_committed_sql_files()
    if not sql_files:
        print("✅ No changed .sql files in the last commit. Exiting.")
        return
    print(f"📁 Found {len(sql_files)} changed SQL file(s). Waiting 30 seconds before executing...")
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