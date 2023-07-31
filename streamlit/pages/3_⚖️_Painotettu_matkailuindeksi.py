import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import folium_static
from functions.markdown_functions import responsive_to_window_width

st.set_page_config(page_title="Painotettu matkailuindeksi ", 
                   layout="wide", 
                   initial_sidebar_state="expanded")

st.markdown("""
 <div style="display: flex; align-items: center;">
   <h2 style="margin: 0;">Eurovelo 13 – Painotettu matkailuindeksi</h2>
   <img style="margin-left: auto;" src="https://raw.githubusercontent.com/Mponkane/Eurovelo13_analysis/main/streamlit/data/welcome_cyclist.png" width="150" height="150">
 </div>   
Painotetun matkailuindeksin avulla voidaan pisteyttää Eurovelo 13 -reitin päiväsegmenttejä
asettamalla tärkeyden mukaan erilaisia painotuksia palveluille, virkistyskohteille tai maisema-arvoille. Esimerkiksi sen mukaan
miten erilaiset pyörämatkailijat arvottaisivat niitä omalla matkallaan. Täten pyörämatkailureittien palvelutasoa voidaan verrata erilaisista näkökulmista.
Matkailuindeksi saa arvoja väliltä 0-100 sen mukaan, kuinka hyvin painoarvojen mukaiset palvelut ilmenevät reittisegmenteillä. 
<br>
<br><br>
 """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    palvelut = gpd.read_file('streamlit/data/palvelut_ja_virkistyskohteet.geojson')
    eurovelo = gpd.read_file('streamlit/data/eurovelo_buffer.shp')

    # Preprocess data to split rows where 'segmentti' contains multiple segments
    palvelut = palvelut.assign(segmentti=palvelut['segmentti'].str.split(', ')).explode('segmentti')

    return palvelut, eurovelo

# Load and preprocess data using cached function
palvelut, eurovelo = load_data()

# Preprocess data to split rows where 'segmentti' contains multiple segments
palvelut = palvelut.assign(segmentti=palvelut['segmentti'].str.split(', ')).explode('segmentti')

# Create empty DataFrame based on eurovelo data
segments = eurovelo['name'].unique()
segment_counts = pd.DataFrame(index=segments)

# Count number of opportunities for each segment and opportunity type
for opportunity_type in palvelut['type'].unique():
    counts = palvelut[palvelut['type'] == opportunity_type].groupby('segmentti').size()
    segment_counts[opportunity_type] = counts

# Fill missing values with 0
segment_counts = segment_counts.fillna(0)

# Normalize counts to be between 0 and 100
segment_counts = (segment_counts - segment_counts.min()) / (segment_counts.max() - segment_counts.min()) * 100

# User input for weights
total_points = 100

# Initialize weights in session_state
if 'weights' not in st.session_state:
    st.session_state.weights = {}

# Create expander for number inputs
with st.expander('Aseta painotukset'):
    # Create form for weight inputs
    with st.form(key='weights_form'):
        # Split number inputs into two columns within container
        col1, col2 = st.columns(2)

        # Split opportunities into two lists
        opportunities = list(palvelut['type'].unique())
        half = len(opportunities) // 2
        opportunities_col1 = opportunities[:half]
        opportunities_col2 = opportunities[half:]
        
        # Create number inputs for first column
        with col1:
            for opportunity_type in opportunities_col1:
                weight = st.number_input(opportunity_type, min_value=0, max_value=total_points, value=st.session_state.weights.get(opportunity_type, 0))
                st.session_state.weights[opportunity_type] = weight
        
        # Create number inputs for second column
        with col2:
            for opportunity_type in opportunities_col2:
                weight = st.number_input(opportunity_type, min_value=0, max_value=total_points, value=st.session_state.weights.get(opportunity_type, 0))
                st.session_state.weights[opportunity_type] = weight
        
        # Create submit button
        submitted = st.form_submit_button('Valitse asetetut painotukset')
        
        # Create clear button using form_submit_button function with label argument set to 'Clear'
        if st.form_submit_button(label='Tyhjennä painotukset'):
            # Reset weights in session_state
            st.session_state.weights = {}

# Check if form was submitted or cleared
if submitted or 'weights' not in st.session_state:
    # Calculate remaining points
    remaining_points = total_points - sum(st.session_state.weights.values())
    
    # Check if remaining points is negative or positive
    if remaining_points < 0:
        # Display error message for too many points assigned
        st.error(f'Olet asettanut liian paljon pisteitä, vähennä {-remaining_points} pistettä.')
    elif remaining_points > 0:
        # Display warning message for too few points assigned
        st.warning(f'Sijoita painotuksiin vielä {remaining_points} pistettä')
    else:
        # Calculate weighted value for each segment
        segment_counts['weighted'] = 0
        for opportunity_type in palvelut['type'].unique():
            segment_counts['weighted'] += st.session_state.weights[opportunity_type] * (segment_counts[opportunity_type] / 100)

        # Reset index of segment_counts DataFrame
        segment_counts = segment_counts.reset_index()

        initial_coords = [65.5, 26.2]
        zoom_level = 5
        m = folium.Map(location=initial_coords, zoom_start=zoom_level, tiles='cartodbpositron')

        # Merge segment_counts with eurovelo on segment name
        eurovelo = eurovelo.merge(segment_counts, left_on='name', right_on='index')
        # Drop index column from eurovelo
        eurovelo = eurovelo.drop(columns=['index'])

        choropleth = folium.Choropleth(
            geo_data=eurovelo,  # GeoDataFrame with segment geometries
            data=segment_counts,  # DataFrame with weighted values
            columns=['index', 'weighted'],  # Columns containing segment name and weighted value
            key_on='feature.properties.name',  # Property in GeoJSON data containing segment name
            fill_color='Spectral',  # Color scale
            fill_opacity=0.8,
            line_opacity=1,
            line_weight=0.5,
            legend_name='Painotettu matkailuindeksi (max. 100 pistettä)',
        ).add_to(m)

        responsive_to_window_width()
        folium_static(m)

st.markdown("""


#### Menetelmäkuvaus

Indeksiä varten data on esikäsitelty siten, että jokaisen reittisegmentin varrelta löytyvien palvelujen, virkistyskohteiden ja maisema-arvojen lukumäärä
on skaalattu 0-100 välille. Täten reittisegmentti, jonka varrelta löytyy esimerkiksi eniten ruokakauppoja, saa se ruokakauppojen arvoksi 100 pistettä. 
Verkkosivujen käyttäjä voi interaktiivisesti asettaa näille arvoille painotuksia, jonka pohjalta lasketaan painotettu matkailuindeksi.
<br><br>Scripti jolla tämä sivu on tuotettu näet githubista: https://github.com/Mponkane/Eurovelo13_analysis/blob/main/streamlit/pages/3_⚖️_Painotettu_palvelutaso.py        

<br>

 <br>
 <em>App made by Matti Pönkänen | FLOU ltd (2023). Licensed under CC0-1.0.</em>
 
 """, unsafe_allow_html=True)