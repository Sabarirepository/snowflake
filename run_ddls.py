import os
import snowflake.connector
import time

# ❗ WARNING: Do not hardcode credentials in production.
SNOWFLAKE_ACCOUNT = 'cm17072.south-central-us.azure'
SNOWFLAKE_USER = 'SRUTHIMANI173'
SNOWFLAKE_PASSWORD = 'Sachinindia123*'
SNOWFLAKE_ROLE = 'ACCOUNTADMIN'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
SNOWFLAKE_DATABASE = 'DATAPLATFORM'
SNOWFLAKE_SCHEMA = 'STAGE'

SQL_DIRECTORY = './sql'

# 🔍 Find all .sql files under the directory
def get_all_sql_files():
    sql_files = []
    for root, dirs, files in os.walk(SQL_DIRECTORY):
        for file in files:
            if file.endswith('.sql'):
                sql_files.append(os.path.join(root, file))
    return sql_files

# 📜 Read and run SQL
def execute_sql_file(file_path, cursor):
    print(f"\n⚙️ Executing SQL file: {file_path}")
    with open(file_path, 'r') as f:
        sql = f.read()

    statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
    for stmt in statements:
        print(f"🔹 Running: {stmt}")
        cursor.execute(stmt)

# 🚀 Main flow
def main():
    sql_files = get_all_sql_files()

    if not sql_files:
        print("✅ No .sql files found in ./sql. Exiting.")
        return

    print(f"📁 Found {len(sql_files)} SQL file(s). Waiting 30 seconds before executing...")
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
        print("\n✅ All SQL files executed successfully.")
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
