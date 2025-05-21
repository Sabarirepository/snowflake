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

def get_current_commit_hash():
    """Get the current commit hash"""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout.strip()

def get_last_processed_commit():
    """Get the last processed commit from a tracking file"""
    try:
        if os.path.exists('.last_processed_commit'):
            with open('.last_processed_commit', 'r') as f:
                return f.read().strip()
    except:
        pass
    return None

def save_current_commit():
    """Save the current commit as processed"""
    current_commit = get_current_commit_hash()
    with open('.last_processed_commit', 'w') as f:
        f.write(current_commit)

def get_changed_sql_files():
    """
    Returns SQL files changed between the last processed commit and current commit
    """
    current_commit = get_current_commit_hash()
    last_processed = get_last_processed_commit()
    
    print(f"🔎 Current commit: {current_commit}")
    print(f"🔎 Last processed commit: {last_processed or 'None (first run)'}")

    if not last_processed:
        # If first run, only get files in current commit
        diff_command = ["git", "diff-tree", "-r", "--no-commit-id", "--name-only", "HEAD"]
    else:
        # Get files changed since last processed commit
        diff_command = ["git", "diff", "--name-only", f"{last_processed}", "HEAD"]

    result = subprocess.run(
        diff_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Error getting changed files: {result.stderr}")
        return []

    # Filter for SQL files in specific directories
    changed_files = [
        f for f in result.stdout.splitlines()
        if f.endswith('.sql') and 
        ('snowflake/sql/' in f or 'sql/' in f) and 
        os.path.exists(f)
    ]
    
    print(f"📁 Changed SQL files:\n{changed_files}")
    return changed_files

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
    
    # Get changed SQL files
    sql_files = get_changed_sql_files()
    
    if not sql_files:
        print("✅ No new SQL files to process. Exiting.")
        return
    
    print(f"📁 Found {len(sql_files)} SQL file(s) to execute:")
    for f in sql_files:
        print(f"   - {f}")
        if os.path.exists(f):
            with open(f, 'r') as file:
                print(f"   Content of {f}:")
                print(file.read())
        else:
            print(f"   ❌ File does not exist: {f}")
    
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
        
        # Save the current commit as processed
        save_current_commit()
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