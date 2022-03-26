import streamlit as st

from streamlit_server_state import server_state, server_state_lock

st.title("Global Counter Example")

with server_state_lock["count"]:  # Lock the "count" state for thread-safety
    if "count" not in server_state:
        server_state.count = 0

increment = st.button("Increment")
if increment:
    with server_state_lock.count:
        server_state.count += 1

decrement = st.button("Decrement")
if decrement:
    with server_state_lock.count:
        server_state.count -= 1

st.write("Count = ", server_state.count)


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



