# test_connection.py
import MySQLdb

try:
    conn = MySQLdb.connect(
        host='localhost',
        user='aiagent',
        password='aiagent_password',
        database='aiagent',
        port=3308
    )
    print("连接成功!")
    conn.close()
except Exception as e:
    print(f"连接失败: {e}")