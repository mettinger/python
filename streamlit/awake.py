import streamlit as st
import os

stateFile = os.path.dirname(__file__) + '/state.txt'

with open(stateFile, 'r') as fp:
    mState, cState = fp.readlines()

def mChange():
    global mState, cState

    if mState == 'awake':
        mState = 'asleep'
    else:
        mState = 'awake'
    with open(stateFile, 'w') as fp:
        fp.write(mState + '\n' + cState)

def cChange():
    global mState, cState

    if cState == 'awake':
        cState = 'asleep'
    else:
        cState = 'awake'
    with open(stateFile, 'w') as fp:
        fp.write(mState + '\n' + cState)

mButton = st.button("M", on_click=mChange)
cButton = st.button("C", on_click=cChange)

st.write("M: %s    C: %s" % (mState, cState))


