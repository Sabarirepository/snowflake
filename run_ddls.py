import os
import subprocess
import snowflake.connector
import time
from datetime import datetime
import pytz

# ❗ WARNING: Do not hardcode credentials in production!
SNOWFLAKE_ACCOUNT = 'cm17072.south-central-us.azure'
SNOWFLAKE_USER = 'SRUTHIMANI173'
SNOWFLAKE_PASSWORD = 'Sachinindia123*'
SNOWFLAKE_ROLE = 'ACCOUNTADMIN'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
SNOWFLAKE_DATABASE = 'DATAPLATFORM'
SNOWFLAKE_SCHEMA = 'STAGE'

def get_last_commit_sql_files():
    """
    Returns a list of .sql files changed in the last commit only
    """
    # Get the last commit hash
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ Error getting last commit: {result.stderr}")
        return []
        
    last_commit = result.stdout.strip()
    print(f"🔎 Last commit hash: {last_commit}")

    # Get files changed in the last commit
    diff_result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", last_commit],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if diff_result.returncode != 0:
        print(f"❌ Error getting changed files: {diff_result.stderr}")
        return []

    # Get all changed files
    all_changed_files = diff_result.stdout.splitlines()
    print(f"📄 All changed files in last commit:\n{all_changed_files}")

    # Filter for .sql files only
    sql_files = [
        f for f in all_changed_files
        if f.endswith('.sql') and os.path.exists(f)
    ]
    
    print(f"📁 SQL files in last commit: {sql_files}")
    return sql_files

def execute_sql_file(file_path, cursor):
    """
    Execute SQL file with error handling
    """
    print(f"\n⚙️ Executing SQL file: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            sql = f.read()
        statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
        
        for i, stmt in enumerate(statements, 1):
            print(f"🔹 Running statement {i}/{len(statements)}: {stmt}")
            cursor.execute(stmt)
            print(f"✅ Statement {i} executed successfully")
            
    except Exception as e:
        print(f"❌ Error executing {file_path}: {str(e)}")
        raise

def main():
    current_time = datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
    print(f"🚀 Script started at (UTC): {current_time}")
    print(f"👤 Running as user: Sabarirepository")
    
    # Get SQL files from last commit
    sql_files = get_last_commit_sql_files()
    
    if not sql_files:
        print("✅ No SQL files changed in the last commit. Exiting.")
        return
    
    print(f"📁 Found {len(sql_files)} SQL file(s) to execute:")
    for f in sql_files:
        print(f"   - {f}")
    
    print("\n⏳ Waiting 30 seconds before executing...")
    time.sleep(30)
    
    # Connect to Snowflake
    try:
        print("🔌 Connecting to Snowflake...")
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
        
        # Execute each SQL file
        for sql_file in sql_files:
            execute_sql_file(sql_file, cursor)
        
        print("\n✅ All SQL files executed successfully")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("🔌 Snowflake connection closed")
    
    print(f"🏁 Script completed at (UTC): {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()