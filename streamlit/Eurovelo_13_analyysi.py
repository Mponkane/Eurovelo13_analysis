
import streamlit as st


st.set_page_config(page_title="Eurovelo 13 analyysi", 
                   page_icon="🌍", 
                   layout="wide", 
                   initial_sidebar_state="auto")

# info
st.markdown("""
 <div style="display: flex; align-items: center;">
   <h2 style="margin: 0;">Eurovelo 13 -reitin paikkatietoanalyysi</h2>
   <img style="margin-left: auto;" src="https://raw.githubusercontent.com/Mponkane/Eurovelo13_analysis/main/streamlit/data/welcome_cyclist.png" width="150" height="150">
 </div>
            
 Tämä verkkosovellus ja paikkatietoanalyysi on tuotettu osaksi harvaan asuttujen alueiden matkailuhanketta. Hankkeen on tarkoitus pilotoida erilaisia paikkatietomenetelmiä pyörämatkailun suunnitteluun. 
 Verkkosovelluksella pystyt tarkastelemaan ja vertailemaan  Eurovelo 13 -reittisegmenttien palvelutasoa.
##### 👈 Sivupalkista pystyt tarkastelemaan tuotetun analyysin eri osa-alueita.
<br>

 <br><br>
 <em>App made by Matti Pönkänen | FLOU ltd (2023). Licensed under CC-BY.</em>
 
 """, unsafe_allow_html=True)