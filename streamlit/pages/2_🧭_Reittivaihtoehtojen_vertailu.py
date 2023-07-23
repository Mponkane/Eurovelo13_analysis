import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import folium_static
from functions.markdown_functions import responsive_to_window_width
from functions.styling_functions import style_route, style_buffer

## ___________________ service level analysis_______________________ 

st.set_page_config(page_title="service level analysis", 
                   layout="wide", 
                   initial_sidebar_state="expanded")


st.markdown("""
            ## **Eurovelo 13 -reitin palvelutaso**

            Tässä osiossa voit tarkastella Eurovelo 13 -reitin varrelle sijoittuvia palveluita. 10 km puskuri..
            
            """)