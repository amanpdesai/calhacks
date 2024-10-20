import pymysql

# Establish connection to the database
connection = pymysql.connect(
    host='svc-f90325a9-8b27-495d-a436-7cb5c7764c62-dml.aws-oregon-3.svc.singlestore.com',
    user='admin',
    password='Flj3M3k6N1of0CXLuR73YiPRMkf9JiTj',
    database='instructions',
    port=3306
)

try:
    # Ensure cursor is created and managed properly
    with connection.cursor() as cursor:
        # Query to get all the tables in the database
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
        else:
            # Loop through and drop each table
            for table in tables:
                table_name = table[0]  # Extract table name from tuple
                drop_query = f"DROP TABLE IF EXISTS {table_name}"
                cursor.execute(drop_query)
                print(f"Dropped table: {table_name}")
            
            # Commit the changes to the database
            connection.commit()

except pymysql.MySQLError as e:
    print(f"Error: {e}")
finally:
    # Close the database connection
    connection.close()
    print("All tables dropped and connection closed.")
