import os
import subprocess
import snowflake.connector
import time
from datetime import datetime
import pytz
import shutil

# Snowflake credentials
SNOWFLAKE_ACCOUNT = 'cm17072.south-central-us.azure'
SNOWFLAKE_USER = 'SRUTHIMANI173'
SNOWFLAKE_PASSWORD = 'Sachinindia123*'
SNOWFLAKE_ROLE = 'ACCOUNTADMIN'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
SNOWFLAKE_DATABASE = 'DATAPLATFORM'
SNOWFLAKE_SCHEMA = 'STAGE'

# Constants
SQL_DIR = "snowflake/sql"
ARCHIVE_DIR = "snowflake/sql/archive"

def log_message(message):
    """Print message with timestamp"""
    current_time = datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}] {message}")

def check_branch():
    """Check if we're on the stage branch"""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    current_branch = result.stdout.strip()
    log_message(f"🌿 Current branch: {current_branch}")
    
    if current_branch != "stage":
        log_message("❌ Not on stage branch! This script should only run on the stage branch.")
        return False
    return True

def get_sql_files():
    """Get all SQL files from snowflake/sql directory (excluding archive)"""
    sql_files = []
    
    if not os.path.exists(SQL_DIR):
        log_message(f"❌ Directory {SQL_DIR} not found!")
        return []
        
    # Get all .sql files directly from snowflake/sql/ (not subdirectories)
    for file in os.listdir(SQL_DIR):
        if file.endswith('.sql') and os.path.isfile(os.path.join(SQL_DIR, file)):
            full_path = os.path.join(SQL_DIR, file)
            sql_files.append(full_path)
            log_message(f"Found SQL file: {full_path}")
    
    return sorted(sql_files)

def move_to_archive(file_path):
    """Move executed SQL file to archive directory with timestamp"""
    try:
        # Create archive directory if it doesn't exist
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        
        # Get timestamp for file name
        timestamp = datetime.now(pytz.UTC).strftime('%Y_%m_%d_%H_%M_%S')
        
        # Construct new file name with timestamp
        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file_name)
        new_name = f"{base_name}_{timestamp}{ext}"
        archive_path = os.path.join(ARCHIVE_DIR, new_name)
        
        # Move file to archive
        shutil.move(file_path, archive_path)
        log_message(f"✅ Moved {file_path} to {archive_path}")
        
    except Exception as e:
        log_message(f"❌ Error moving file to archive: {str(e)}")
        raise

def execute_sql_file(file_path, cursor):
    """Execute SQL file with error handling"""
    log_message(f"\n⚙️ Executing SQL file: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            sql = f.read()
            log_message(f"📄 SQL content to execute:\n{sql}")
        
        statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
        
        for i, stmt in enumerate(statements, 1):
            log_message(f"🔹 Running statement {i}/{len(statements)}:\n{stmt}")
            cursor.execute(stmt)
            log_message(f"✅ Statement {i} executed successfully")
            
        return True
            
    except Exception as e:
        log_message(f"❌ Error executing {file_path}: {str(e)}")
        raise

def main():
    log_message("=== Script Started ===")
    log_message(f"👤 Running as user: Sabarirepository")
    
    # First check if we're on stage branch
    if not check_branch():
        return
    
    # Print current working directory
    log_message(f"📂 Current working directory: {os.getcwd()}")
    
    # Get all SQL files from snowflake/sql (excluding archive)
    sql_files = get_sql_files()
    
    if not sql_files:
        log_message("✅ No SQL files found in snowflake/sql/. Exiting.")
        return
    
    log_message(f"📁 Found {len(sql_files)} SQL file(s) to execute:")
    for f in sql_files:
        log_message(f"   - {f}")
        try:
            with open(f, 'r') as file:
                log_message(f"   Content of {f}:")
                log_message(file.read())
        except Exception as e:
            log_message(f"   ❌ Error reading file {f}: {str(e)}")
    
    log_message("\n⏳ Waiting 5 seconds before executing...")
    time.sleep(5)
    
    # Connect to Snowflake
    try:
        log_message("🔌 Connecting to Snowflake...")
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
            if execute_sql_file(sql_file, cursor):
                move_to_archive(sql_file)
        
        log_message("✅ All SQL files executed successfully and moved to archive")
        
    except Exception as e:
        log_message(f"❌ Error: {str(e)}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            log_message("🔌 Snowflake connection closed")
    
    log_message("=== Script Completed ===")

if __name__ == "__main__":
    main()