import os
import subprocess
import snowflake.connector

# ❗ WARNING: It's insecure to hardcode passwords in source files.
# Use environment variables or a secret manager in real use.
SNOWFLAKE_ACCOUNT = 'cm17072.south-central-us.azure'
SNOWFLAKE_USER = 'SRUTHIMANI173'
SNOWFLAKE_PASSWORD = 'Sachinindia123*'
SNOWFLAKE_ROLE = 'ACCOUNTADMIN'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
SNOWFLAKE_DATABASE = 'DATAPLATFORM'
SNOWFLAKE_SCHEMA = 'STAGE'

# Get list of changed .sql files using Git
def get_changed_sql_files():
    # Ensure we fetch latest from origin/stage
    subprocess.run(["git", "fetch", "origin", "stage"], check=True)

    # Get changed files
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/stage..HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.stderr:
        print(f"⚠️ Git error: {result.stderr}")

    changed_files = result.stdout.splitlines()
    print("📁 Changed files:", changed_files)

    return [
        f for f in changed_files
        if f.endswith(".sql") and os.path.exists(f)
    ]

# Run SQL file
def execute_sql_file(file_path, cursor):
    print(f"\n⚙️ Running SQL file: {file_path}")
    with open(file_path, 'r') as f:
        sql = f.read()
        statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
        for stmt in statements:
            print(f"🔹 Executing: {stmt}")
            cursor.execute(stmt)

# Main execution
def main():
    changed_sql_files = get_changed_sql_files()

    if not changed_sql_files:
        print("✅ No SQL file changes detected. Skipping execution.")
        return

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
        for sql_file in changed_sql_files:
            execute_sql_file(sql_file, cursor)
        print("✅ All SQL changes applied successfully.")
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
