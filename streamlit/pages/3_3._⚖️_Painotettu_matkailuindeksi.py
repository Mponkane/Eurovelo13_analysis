import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static

def set_page():
    st.set_page_config(page_title="Painotettu matkailuindeksi ", 
                    layout="wide", 
                    initial_sidebar_state="expanded")

    st.markdown("""
    <div style="display: flex; align-items: center;">
    <h2 style="margin: 0;">Eurovelo 13 – Painotettu matkailuindeksi</h2>
    <img style="margin-left: auto;" src="https://raw.githubusercontent.com/Mponkane/Eurovelo13_analysis/main/streamlit/data/welcome_cyclist.png" width="150" height="150">
    </div>   
    Painotetun matkailuindeksin avulla voidaan pisteyttää Eurovelo 13 -reitin päiväetappeja
    asettamalla tärkeyden mukaan erilaisia painotuksia palveluille, virkistyskohteille tai maisema-arvoille. Esimerkiksi sen mukaan
    millaisille erilaisille palveluille erilaiset pyörämatkailijat antaisivat painoarvoa omalla matkallaan. Täten pyörämatkailureittien palvelutasoa voidaan verrata erilaisista näkökulmista.
    <b>Aloita sovelluksen käyttö asettamalla alla olevan pudotusvalikon sisältämille palveluille, virkistyskohteille sekä maisema-arvoille painotus. Käytettävänäsi on 100 pistettä, jonka voit 
    jakaa eri kohteille niiden tärkeyden mukaisesti.</b> Painotuksia käytetään matkailuindeksin laskemiseksi. Indeksi saa arvoja väliltä 0-100 sen mukaan, kuinka hyvin painoarvojen mukaiset 
    palvelut ilmenevät reittietapeilla.
    <br><br>
    """, unsafe_allow_html=True)

# Load and preprocess data using cached function
@st.cache_data
def load_data():
    palvelut = gpd.read_file('streamlit/data/palvelut_ja_virkistyskohteet.geojson')
    eurovelo = gpd.read_file('streamlit/data/eurovelo_buffer.shp')

    # Preprocess data to split rows where 'segmentti' contains multiple segments
    palvelut = palvelut.assign(segmentti=palvelut['segmentti'].str.split(', ')).explode('segmentti')

    return palvelut, eurovelo


def set_weights(palvelut, eurovelo):

    # ------Setting data for weights input-------
    palvelut = palvelut.assign(segmentti=palvelut['segmentti'].str.split(', ')).explode('segmentti')

    segments = eurovelo['name'].unique()
    segment_counts = pd.DataFrame(index=segments)

    for opportunity_type in palvelut['type'].unique():
        counts = palvelut[palvelut['type'] == opportunity_type].groupby('segmentti').size()
        segment_counts[opportunity_type] = counts

    segment_counts = segment_counts.fillna(0)
    segment_counts = (segment_counts - segment_counts.min()) / (segment_counts.max() - segment_counts.min()) * 100

    total_points = 100

    if 'weights' not in st.session_state:
        st.session_state.weights = {}

    temporary_weights = {}  # Store current form values

    with st.expander('Aseta painotukset (yhteensä 100 pistettä)'):
        with st.form(key='weights_form'):
            col1, col2 = st.columns(2)

            opportunities = list(palvelut['type'].unique())
            half = len(opportunities) // 2
            opportunities_col1 = opportunities[:half]
            opportunities_col2 = opportunities[half:]

            with col1:
                for opportunity_type in opportunities_col1:
                    weight = st.number_input(opportunity_type, min_value=0, max_value=total_points, value=st.session_state.weights.get(opportunity_type, 0))
                    temporary_weights[opportunity_type] = weight

            with col2:
                for opportunity_type in opportunities_col2:
                    weight = st.number_input(opportunity_type, min_value=0, max_value=total_points, value=st.session_state.weights.get(opportunity_type, 0))
                    temporary_weights[opportunity_type] = weight

            submitted = st.form_submit_button('Valitse asetetut painotukset')

            if st.form_submit_button(label='Tyhjennä painotukset'):
                st.session_state.weights = {}

    if submitted:
        st.session_state.weights = temporary_weights

    if submitted or 'weights' not in st.session_state:
        remaining_points = total_points - sum(st.session_state.weights.values())
        weights = exception_handling(remaining_points)
        if weights is not None:
            segment_counts['weighted'] = 0
            for opportunity_type in palvelut['type'].unique():
                segment_counts['weighted'] += st.session_state.weights[opportunity_type] * (segment_counts[opportunity_type] / 100)
            segment_counts = segment_counts.reset_index()
            return eurovelo, segment_counts
        else:
            return None, None
    else:
        return None, None

    
def exception_handling(remaining_points):        
    # Check if remaining points is negative or positive
    if remaining_points < 0:
        # Display error message for too many points assigned
        st.error(f'Olet asettanut liian paljon pisteitä, vähennä {-remaining_points} pistettä.')
        return None
    elif remaining_points > 0:
        # Display warning message for too few points assigned
        st.warning(f'Sijoita painotuksiin vielä {remaining_points} pistettä')
        return None
    else:
        weights = 1
        return weights
    
def create_map(eurovelo, segment_counts):
    initial_coords = [65.5, 26.2]
    zoom_level = 5
    m = folium.Map(location=initial_coords, zoom_start=zoom_level, tiles='openstreetmap')

    # Merge segment_counts with eurovelo on segment name
    eurovelo = eurovelo.merge(segment_counts, left_on='name', right_on='index')
    # Drop index column from eurovelo
    eurovelo = eurovelo.drop(columns=['index'])

    _ = folium.Choropleth(
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

    return(m)


def create_table(segment_counts):
    # Sort segments by weighted sum score in descending order
    segment_counts = segment_counts.sort_values(by='weighted', ascending=False)

    # Reset index and rename columns
    segment_counts = segment_counts.reset_index(drop=True)
    segment_counts.index += 1
    segment_counts = segment_counts.rename(columns={'index': 'Päiväetappi', 'weighted': 'Pisteet'})
    

    # Create a table to display the segments
    st.dataframe(segment_counts[['Päiväetappi', 'Pisteet']], width = 1500)

def responsive_to_window_width():
    making_map_responsive = """
    <style>
    [title~="st.iframe"] { width: 100%}
    </style>
    """
    st.markdown(making_map_responsive, unsafe_allow_html=True)

def add_description():
    st.markdown("""


    #### Menetelmäkuvaus

    Indeksiä varten data on esikäsitelty skaalaamalla jokaisen reittietapin varrelta löytyvien palvelujen, virkistyskohteiden ja maisema-arvojen lukumäärä 0-100 välille. 
    Täten reittietappi, jonka varrelta löytyy esimerkiksi eniten ruokakauppoja, saa se ruokakauppojen arvoksi 100 pistettä. 
    Verkkosivujen käyttäjä voi interaktiivisesti asettaa näille arvoille painotuksia, jonka pohjalta lasketaan painotettu summa.
    <br><br>Scriptin jolla sivu on tuotettu, löydät githubista: https://github.com/Mponkane/Eurovelo13_analysis/blob/main/streamlit/pages/3_⚖️_Painotettu_palvelutaso.py        

    <br>

    <br>
    <em>App made by Matti Pönkänen | FLOU ltd (2023). Licensed under CC0-1.0.</em>
    
    """, unsafe_allow_html=True)


def main():
    set_page()
    palvelut, eurovelo = load_data()
    eurovelo, segment_counts = set_weights(palvelut, eurovelo)
    if (segment_counts is not None) or (eurovelo is not None):
        m = create_map(eurovelo, segment_counts)
        responsive_to_window_width()
        folium_static(m)
        create_table(segment_counts)
    add_description()
        
if __name__ == "__main__":
    main()