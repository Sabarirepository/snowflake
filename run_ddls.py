import os
import subprocess
import snowflake.connector

# Snowflake credentials
SNOWFLAKE_ACCOUNT = 'cm17072.south-central-us.azure'
SNOWFLAKE_USER = 'SRUTHIMANI173'
SNOWFLAKE_PASSWORD = 'Sachinindia123*'
SNOWFLAKE_ROLE = 'ACCOUNTADMIN'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
SNOWFLAKE_DATABASE = 'DATAPLATFORM'
SNOWFLAKE_SCHEMA = 'STAGE'

# Directory with SQL files
SQL_DIR = './sql'

# Get list of changed .sql files using Git
def get_changed_sql_files():
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    changed_files = result.stdout.splitlines()
    return [f for f in changed_files if f.endswith(".sql") and os.path.exists(f)]

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

# Run SQL file
def execute_sql_file(file_path):
    print(f"\n⚙️ Running: {file_path}")
    with open(file_path, 'r') as f:
        sql = f.read()
        for stmt in sql.split(';'):
            stmt = stmt.strip()
            if stmt:
                print(f"🔹 Executing: {stmt}")
                cursor.execute(stmt)

# Run changed files
changed_files = get_changed_sql_files()
if not changed_files:
    print("✅ No SQL file changes detected. Skipping.")
else:
    for file in changed_files:
        execute_sql_file(file)

cursor.close()
conn.close()
