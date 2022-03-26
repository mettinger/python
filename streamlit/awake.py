import streamlit as st

if 'm' not in st.session_state:
	st.session_state.m = 'awake'

if 'c' not in st.session_state:
	st.session_state.c = 'awake'

mButton = st.button("M")
cButton = st.button("C")

if mButton:
    if st.session_state.m == 'awake':
        st.session_state.m = 'asleep'
    else:
        st.session_state.m = 'awake'

if cButton:
    if st.session_state.c == 'awake':
        st.session_state.c = 'asleep'
    else:
        st.session_state.c = 'awake'
        
st.write("M: %s    C: %s" % (st.session_state.m, st.session_state.c))


