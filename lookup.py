import csv
import sqlite3

conn = sqlite3.connect('C:\\Users\putripat\\PycharmProjects\\arsiva\\company.db')

c = conn.cursor()
# c.execute('''drop table if exists TICKER_LOOKUP''')
# c.execute('''CREATE TABLE IF NOT EXISTS TICKER_LOOKUP
#        (TICKER VARCHAR(10)    NOT NULL   ,
#        COMPANY_NAME  VARCHAR(100));''')
#
# with open("lookups\\nasdaq.csv") as filen:
#     file_obj = csv.DictReader(filen)
#     db_insert = [(i['Symbol'],i['Description']) for i in file_obj]


c.executemany("INSERT INTO TICKER_LOOKUP VALUES (?, ?);", [("GOOGL", "Google Inc")])
conn.commit()
# kk = c.fetchall()
# for i in kk[0:10]: print(i)