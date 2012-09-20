

import sqlite3
import random

if __name__=='__main__':
    con = sqlite3.connect(':memory:')
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute('CREATE TABLE stuff (A INT, B INT)')
    
    insert_str = 'INSERT INTO stuff (A, B) VALUES (?, ?)'
    values = [(random.randint(0,10),random.randint(0,10)) for i in range(1000000)]
    cur.executemany(insert_str, values)
    print "insert complete"

    cur.execute('SELECT Rowid, * FROM stuff')
    to_update = []
    for d in cur:
        to_update.append((99, d['rowid']))
    cur.executemany('UPDATE stuff SET A=? WHERE Rowid=?', to_update)
    print 'update complete'
    con.close()
