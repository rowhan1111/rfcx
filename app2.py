import streamlit as st
from sqlalchemy import text
import time

conn = st.connection('pets_db', type='sql')
store_data = []
alert = st.empty()
while True:
    pet_owners = conn.query("select * from pet_owners")
    alert.empty()
    if(pet_owners.values[0][1] > 40):
        alert = st.warning("Wood cutting sound detected")
    st.cache_data.clear()
    time.sleep(2)