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

def log_message(message):
    """Print message with timestamp"""
    current_time = datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}] {message}")

def get_sql_files():
    """Get all SQL files from sql directory (excluding archive)"""
    sql_dir = "sql"
    sql_files = []
    
    if not os.path.exists(sql_dir):
        log_message(f"❌ Directory {sql_dir} not found!")
        return []
    
    # Get all .sql files directly from sql directory (not subdirectories)
    for file in os.listdir(sql_dir):
        if file.endswith('.sql') and os.path.isfile(os.path.join(sql_dir, file)):
            if 'archive' not in file:
                full_path = os.path.join(sql_dir, file)
                sql_files.append(full_path)
                log_message(f"Found SQL file: {full_path}")
    
    return sorted(sql_files)

def move_to_archive(file_path):
    """Move executed SQL file to archive directory with timestamp"""
    try:
        # Create archive directory if it doesn't exist
        archive_dir = os.path.join('sql', 'archive')
        os.makedirs(archive_dir, exist_ok=True)
        
        # Get timestamp for file name
        timestamp = datetime.now(pytz.UTC).strftime('%Y_%m_%d_%H_%M_%S')
        
        # Construct new file name with timestamp
        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file_name)
        new_name = f"{base_name}_{timestamp}{ext}"
        archive_path = os.path.join(archive_dir, new_name)
        
        # Move file to archive
        shutil.move(file_path, archive_path)
        log_message(f"✅ Moved {file_path} to {archive_path}")
        
        return archive_path
        
    except Exception as e:
        log_message(f"❌ Error moving file to archive: {str(e)}")
        raise

def commit_changes(archived_files):
    """Commit archived files with [skip ci] tag to prevent workflow trigger"""
    try:
        # Configure git
        subprocess.run(["git", "config", "user.name", "Sabarirepository"], check=True)
        subprocess.run(["git", "config", "user.email", "sabarirepository@users.noreply.github.com"], check=True)
        
        # Stage all changes (archived files and removed originals)
        subprocess.run(["git", "add", "sql/"], check=True)
        
        # Create commit message with [skip ci] tag
        timestamp = datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
        commit_message = f"[skip ci] Archived SQL files after successful execution at {timestamp}"
        
        # Commit changes
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push changes
        subprocess.run(["git", "push", "origin", "stage"], check=True)
        
        log_message("✅ Successfully committed and pushed changes to repository")
        
    except Exception as e:
        log_message(f"❌ Error committing changes: {str(e)}")
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
    log_message(f"Current Date and Time (UTC): {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')}")
    log_message(f"Current User's Login: Sabarirepository")
    
    # Initialize list to track archived files
    archived_files = []
    
    # Get SQL files
    sql_files = get_sql_files()
    
    if not sql_files:
        log_message("✅ No SQL files found to process. Exiting.")
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
        
        # Execute each SQL file and move to archive immediately
        for sql_file in sql_files:
            if execute_sql_file(sql_file, cursor):
                archived_path = move_to_archive(sql_file)
                archived_files.append(archived_path)
        
        log_message("✅ All SQL files executed successfully and moved to archive")
        
        # Commit changes with [skip ci] tag
        if archived_files:
            commit_changes(archived_files)
        
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