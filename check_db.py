import sqlite3
conn = sqlite3.connect('c:/aribot/backend/yuna_chats.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM messages WHERE content LIKE '%Arjun Dayal%';")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()
