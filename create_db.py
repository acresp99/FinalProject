import sqlite3
import pandas as pd 

conn = sqlite3.connect('state_pop.db')
cursor = conn.cursor()
df = pd.read_csv('state_pop.csv')
df.to_sql('state_pop',conn, if_exists= 'replace', index = False)
conn.commit()
conn.close()