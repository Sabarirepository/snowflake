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

def get_changed_sql_files_since_last_merge():
    """
    Returns a list of .sql files changed since the last merge with the 'stage' branch.
    """
    # Find the merge base between HEAD and stage
    result = subprocess.run(
        ["git", "merge-base", "HEAD", "stage"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    merge_base = result.stdout.strip()
    if not merge_base:
        print("❌ Could not find merge base with stage.")
        return []
    print(f"🔎 Merge base commit with stage: {merge_base}")

    # Get changed files since merge base
    diff_result = subprocess.run(
        ["git", "diff", "--name-only", f"{merge_base}..HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    changed_files = [
        f for f in diff_result.stdout.splitlines()
        if f.endswith('.sql') and os.path.exists(f)
    ]
    print(f"📁 Changed .sql files since last merge with stage: {changed_files}")
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
    sql_files = get_changed_sql_files_since_last_merge()
    if not sql_files:
        print("✅ No changed .sql files since last merge with stage. Exiting.")
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
