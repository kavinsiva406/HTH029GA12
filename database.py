import sqlite3

DB_NAME = "onboardai.db"

def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection

def init_database():
    connection = get_connection()
    connection.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)""")
    connection.execute("""CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT, content TEXT)""")
    connection.execute("""CREATE TABLE IF NOT EXISTS progress (
        user_id INTEGER, topic_id INTEGER, score INTEGER DEFAULT 0, attempts INTEGER DEFAULT 0,
        PRIMARY KEY(user_id, topic_id))""")
    connection.commit(); connection.close()

def seed_database():
    connection = get_connection()
    connection.execute("INSERT OR IGNORE INTO users (id,name,email,password) VALUES (1,?,?,?)",
                       ("Kavin", "kavin@demo.com", "123456"))
    topics = [
        (1,"Company Introduction","Learn about company culture and values.","This module introduces employees to the company, its culture, mission and values."),
        (2,"HR Policies","Understand important employee policies.","Employees should understand attendance, leave, workplace behaviour and HR procedures."),
        (3,"Cybersecurity","Learn cybersecurity best practices.","Employees must protect company systems, passwords and confidential information. Security incidents should be reported immediately."),
        (4,"Data Privacy","Learn how company information should be protected.","Employees must protect sensitive information and only access data required for their work.")]
    for topic in topics:
        connection.execute("INSERT OR IGNORE INTO topics (id,title,description,content) VALUES (?,?,?,?)", topic)
    connection.commit(); connection.close()
