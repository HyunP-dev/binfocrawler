import sqlite3
from sqlite3 import Connection
import sys
sys.path.append(".")

import pandas as pd
import binfocrawler


def init_database():
    con = sqlite3.connect("opinions.db")
    cur = con.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS opinions (
                    bill_id TEXT,
                    opinion_id INTEGER,
                    author TEXT,
                    organization TEXT,
                    date TEXT,
                    title TEXT,
                    content TEXT)""")
    return con

def update_database(connection: Connection, bill_id: str):
    for opinion in binfocrawler.get_opinions(bill_id, -1):
        cur = connection.cursor()
        cur.execute("SELECT 1 FROM opinions WHERE bill_id=? AND opinion_id=?", (bill_id, opinion.id))
        if cur.fetchone() is not None:
            break
        cur.execute("""
                    INSERT INTO opinions(
                        bill_id, opinion_id, author, organization, date,
                        title, content) 
                    values (?, ?, ?, ?, ?, ?, ?)""", (
                        bill_id, opinion.id, opinion.author, opinion.group, opinion.date,
                        opinion.title, opinion.content))
    connection.commit()

def get_counts(connection: Connection, bill_id: str):
    cur = connection.cursor()
    query = """
            SELECT 
                date,
                SUM(CASE WHEN title LIKE '%찬성%' THEN 1 ELSE 0 END) AS agree,
                SUM(CASE WHEN title LIKE '%반대%' THEN 1 ELSE 0 END) AS disagree
            FROM (SELECT * FROM opinions WHERE bill_id=?)
            GROUP BY date
            ORDER BY date;"""
    cur.execute(query, (bill_id, ))
    return pd.DataFrame(cur.fetchall(), columns=["date", "agree", "disagree"])


__all__ = ["init_database", "update_database", "get_counts"]
