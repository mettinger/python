import streamlit as st
from streamlit_server_state import server_state, server_state_lock


with server_state_lock["mState"]: 
    if "mState" not in server_state:
        server_state.mState = "awake"

with server_state_lock["mState"]: 
    if "cState" not in server_state:
        server_state.cState = "asleep"


mButton = st.button("Change M")
if mButton:
    with server_state_lock.mState:
        if server_state.mState == 'awake':
            server_state.mState = 'asleep'
        else:
            server_state.mState = 'awake'


cButton = st.button("Change C")
if cButton:
    with server_state_lock.cState:
        if server_state.cState == 'awake':
            server_state.cState = 'asleep'
        else:
            server_state.cState = 'awake'

st.write("M: %s    C: %s" % (server_state.mState, server_state.cState))


