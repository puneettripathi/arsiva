import sqlite3

conn = sqlite3.connect('C:\\Users\putripat\\PycharmProjects\\arsiva\\company.db')

c = conn.cursor()
kk = c.execute("select * from TICKER_LOOKUP;")
print(kk.fetchall())
# kk =  c.fetchall()
print([ i[0] for i in c.execute("select ticker from ticker_lookup where upper(COMPANY_NAME) like upper('BLACKROCK%')").fetchall()])