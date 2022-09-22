import streamlit as st
import gc


st.write("This is a test page for memory leaking")

st.experimental_singleton.clear()
st.experimental_rerun()