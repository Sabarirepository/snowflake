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

def check_branch():
    """Check if we're on the stage branch"""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    current_branch = result.stdout.strip()
    print(f"🌿 Current branch: {current_branch}")
    
    if current_branch != "stage":
        print("❌ Not on stage branch! This script should only run on the stage branch.")
        return False
    return True

def get_changed_sql_files():
    """Get SQL files changed in the latest commit on stage branch"""
    try:
        # Get the latest commit on stage branch
        result = subprocess.run(
            ["git", "log", "-1", "--name-only", "--format=", "stage"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Error getting files from stage branch: {result.stderr}")
            return []

        # Get list of changed files
        files = result.stdout.strip().split('\n')
        
        # Filter for SQL files
        sql_files = [
            f for f in files 
            if f and f.endswith('.sql') and 
            ('snowflake/sql/' in f or 'sql/' in f or f.startswith('sql/'))
        ]

        # Print all found files for debugging
        print(f"\nAll changed files in latest commit on stage:")
        for f in files:
            if f:
                print(f"  - {f}")
        
        print(f"\nSQL files to process:")
        for f in sql_files:
            print(f"  - {f}")
            
        return sql_files

    except Exception as e:
        print(f"❌ Error getting changed files: {str(e)}")
        return []

def execute_sql_file(file_path, cursor):
    """Execute SQL file with error handling"""
    print(f"\n⚙️ Executing SQL file: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            sql = f.read()
            print(f"📄 SQL content to execute:\n{sql}")
        
        statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
        
        for i, stmt in enumerate(statements, 1):
            print(f"🔹 Running statement {i}/{len(statements)}:\n{stmt}")
            cursor.execute(stmt)
            print(f"✅ Statement {i} executed successfully")
            
    except Exception as e:
        print(f"❌ Error executing {file_path}: {str(e)}")
        raise

def main():
    current_time = datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
    print(f"🚀 Script started at (UTC): {current_time}")
    print(f"👤 Running as user: Sabarirepository")
    
    # First check if we're on stage branch
    if not check_branch():
        return
    
    # Print current working directory and its contents
    print(f"\n📂 Current working directory: {os.getcwd()}")
    print("📂 SQL files in repository:")
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.sql'):
                print(f"  - {os.path.join(root, f)}")

    # Make sure we're on stage branch and get latest changes
    subprocess.run(["git", "checkout", "stage"], capture_output=True, text=True)
    subprocess.run(["git", "pull", "origin", "stage"], capture_output=True, text=True)

    # Get changed SQL files
    sql_files = get_changed_sql_files()
    
    if not sql_files:
        print("\n✅ No SQL files changed in latest commit on stage branch. Exiting.")
        return
    
    print(f"\n📁 Found {len(sql_files)} SQL file(s) to execute:")
    for f in sql_files:
        print(f"   - {f}")
        try:
            with open(f, 'r') as file:
                print(f"   Content of {f}:")
                print(file.read())
        except Exception as e:
            print(f"   ❌ Error reading file {f}: {str(e)}")
    
    print("\n⏳ Waiting 5 seconds before executing...")
    time.sleep(5)
    
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