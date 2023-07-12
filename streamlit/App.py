
import streamlit as st


## ___________________ APP _______________________ 

st.set_page_config(page_title="Eurovelo cycling analysis", 
                   page_icon="🌍", 
                   layout="centered", 
                   initial_sidebar_state="auto")

# info
st.markdown("""
 <div style="display: flex; align-items: center;">
   <h2 style="margin: 0;">Eurovelo 13 - service level analysis</h2>
   <img style="margin-left: auto;" src="xxx" width="100" height="110">
 </div>
            
 This web app was developed as part of the Tourism Development Project for Sparsely Populated Areas to showcase service levels of different Eurovelo 13 segments.  
 
 ###### 👈 ***From the sidebar you can explore different components of the service level analysis***
 
 *Streamlit app made by Matti Pönkänen | FLOU ltd (2023). Licensed under CC-BY.*
 
 """, unsafe_allow_html=True)