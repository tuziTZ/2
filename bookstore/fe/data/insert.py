import sqlite3
import psycopg2

# SQLite连接和游标
sqlite_conn = sqlite3.connect('book.db')
sqlite_cursor = sqlite_conn.cursor()

# PostgreSQL连接和游标
postgres_conn = psycopg2.connect(
    database='bookstore',
    user='postgres',
    password='123456',
    host='127.0.0.1',
    port='5432'
)
postgres_cursor = postgres_conn.cursor()

# 1. 导出SQLite表结构
sqlite_cursor.execute("PRAGMA table_info(table_name)")
table_structure = sqlite_cursor.fetchall()
table_name = "book"  # 替换为实际的表名

# 构建PostgreSQL的CREATE TABLE语句
create_table_sql = f"CREATE TABLE {table_name} ("
for column_info in table_structure:
    column_name = column_info[1]
    column_type = column_info[2]
    create_table_sql += f"{column_name} {column_type}, "
print(create_table_sql)
create_table_sql = create_table_sql.rstrip(', ') + ");"

# 2. 在PostgreSQL中创建表
# postgres_cursor.execute(create_table_sql)
postgres_conn.commit()

# 3. 导出SQLite数据
sqlite_cursor.execute(f"SELECT * FROM {table_name}")
table_data = sqlite_cursor.fetchall()

# 4. 插入数据到PostgreSQL
for row in table_data:
    placeholders = ', '.join(['%s' for _ in row])
    insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
    print(f"Insert SQL: {insert_sql}")
    print(f"Row data: {row}")
    postgres_cursor.execute(insert_sql, row)

postgres_conn.commit()

# 关闭连接
sqlite_conn.close()
postgres_conn.close()
