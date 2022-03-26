import streamlit as st
from shillelagh.backends.apsw.db import connect


connection = connect(":memory:")
cursor = connection.cursor()

SQL = """
SELECT *
FROM "https://docs.google.com/spreadsheets/d/1uDmTt0ZpltLJfP3xQqlCNOgNHYr9A5rb31PnqcuACnA/edit#gid=0"
"""
for row in cursor.execute(SQL):
    st.write(row)

'''
def run_read_query(query):
    connection = connect(":memory:")
    cursor = connection.cursor()
    rows = cursor.execute(query)
    return rows

sheet_url = st.secrets["public_gsheets_url"]
rows = run_read_query(f'SELECT * FROM "{sheet_url}"')

st.write(rows)

def run_write_query():
    conn = connect()
    query = f'UPDATE "{sheet_url}" SET mark = "1", cathy = "2"'
    rows = conn.execute(query, headers=1)
    conn.close()
    return rows

mState = rows[0].mark
cState = rows[0].cathy


def mChange():
    global mState
    if mState == 'awake':
        mState = 'asleep'
    else:
        mState = 'awake'
    #rows = run_write_query()

def cChange():
    global cState
    if cState == 'awake':
        cState = 'asleep'
    else:
        cState = 'awake'

mButton = st.button("M", on_click=mChange)
cButton = st.button("C", on_click=cChange)

st.write("M: %s    C: %s" % (mState, cState))
'''



