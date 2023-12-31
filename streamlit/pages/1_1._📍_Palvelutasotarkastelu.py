import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import folium_static
from functions.markdown_functions import responsive_to_window_width
from functions.styling_functions import style_route, style_buffer


def set_page():
    st.set_page_config(page_title="Palvelutasotarkastelu", 
                    layout="wide", 
                    initial_sidebar_state="expanded")

    st.markdown("""
    <div style="display: flex; align-items: center;">
    <h2 style="margin: 0;">Eurovelo 13 -reitin palvelutaso</h2>
    <img style="margin-left: auto;" src="https://raw.githubusercontent.com/Mponkane/Eurovelo13_analysis/main/streamlit/data/welcome_cyclist.png" width="150" height="150">
    </div>   
    Tässä osiossa voit tarkastella Eurovelo 13 -reitin varrelle sijoittuvia palveluita, virkstyskohteita sekä maisema-arvoja. Reittiä voi tarkastella joko kokonaisuutena tai suunniteltujen 
    päiväetappien mukaisesti. Valitse ensin valikosta tarkasteltavat palvelut, virkistyskohteet ja maisemalliset arvot, jonka jälkeen pystyt
    tarkastelemaan miten ne jakaantuvat reitillä tai etapeilla. Päiväetappien palvelutasoa on myös mahdollista verrata koko reitin keskiarvoon, 
    jolloin voidaan vertailla reittiosuuksien laatua palveluiden näkökulmasta. Menetelmäkuvauksen löydät alapuolelta.
    <br><br>
    """, unsafe_allow_html=True)

def read_data():
    merged_opportunities = gpd.read_file('streamlit/data/palvelut_ja_virkistyskohteet.geojson')
    eurovelo = gpd.read_file('streamlit/data/eurovelo.shp')
    buffer = gpd.read_file('streamlit/data/buffer.shp')
    buffer_merged = gpd.read_file('streamlit/data/buffer_merged.shp')

    merged_opportunities = merged_opportunities.to_crs('EPSG:4326')
    eurovelo = eurovelo.to_crs('EPSG:4326')
    buffer = buffer.to_crs('EPSG:4326')
    buffer_merged = buffer_merged.to_crs('EPSG:4326')

    return merged_opportunities, eurovelo, buffer, buffer_merged

def filter_data_and_create_charts(merged_opportunities, eurovelo, buffer, buffer_merged):
    # Hide kansallispuistot and VAMA from the first select box
    opportunity_types = [x for x in merged_opportunities['type'].unique() if x not in ['Kansallispuistot', 'Valtakunnallisesti arvokkaat maisema-alueet']]
    selected_types = st.multiselect('Valitse palvelut ja virkistyskohteet:', opportunity_types)
    landscape_types = ['Kansallispuistot', 'Valtakunnallisesti arvokkaat maisema-alueet']
    selected_landscape_types = st.multiselect('Valitse maisema-arvo:', landscape_types)

    if not selected_types and not selected_landscape_types:
        st.warning('Valitse ainakin yksi palvelu, virkistyskohde tai maisema-arvo')

    else:
        selected_segment = set_segments(merged_opportunities, eurovelo)
        eurovelo_tm35fin = eurovelo.to_crs('EPSG:3067')
        avg_opportunities = merged_opportunities.groupby('type').size() / (eurovelo_tm35fin.geometry.length.sum() / 1000)
        fig1, fig2, m, filtered_data = create_figures(selected_segment, eurovelo, avg_opportunities, merged_opportunities, landscape_types, selected_landscape_types,
                        selected_types, opportunity_types, buffer, buffer_merged)
        if m is not None:
            create_page_elements(selected_segment, filtered_data, landscape_types, eurovelo, fig1, fig2, m)
        

def set_segments(merged_opportunities, eurovelo):

        segments = merged_opportunities['segmentti'].str.split(', ')
        # Flatten the list of lists into a single list of segment values
        segments = [segment for sublist in segments for segment in sublist]
        segments = np.unique(segments)
        gdf = eurovelo.sort_values(by="order")
        # Get the list of segments in the desired order
        segments = gdf["name"].tolist()
        # Add an "Koko reitti" option to the segments list so that data can be looked at nationKoko reittiy
        segments = np.insert(segments, 0, 'Koko reitti')
        # Create a selectbox for different segments
        selected_segment = st.selectbox('Valitse päiväetappi:', segments)

        return selected_segment

def create_figures(selected_segment, eurovelo, avg_opportunities, merged_opportunities, landscape_types, selected_landscape_types, selected_types, opportunity_types,
                   buffer, buffer_merged):
        # Filter the data based on the selected segment or Koko reitti
        if selected_segment == 'Koko reitti':
            filtered_data = merged_opportunities.copy()
            # Reprojecting for length properties
            eurovelo_tm35fin = eurovelo.to_crs('EPSG:3067')
            # Calculate the length of the entire route in kilometers
            segment_length = eurovelo_tm35fin.geometry.length.sum() / 1000
            avg_opportunities_segment = avg_opportunities
            zoom_level = 5
        else:
            eurovelo_tm35fin = eurovelo.to_crs('EPSG:3067')
            segment_length = eurovelo_tm35fin[eurovelo_tm35fin['name'] == selected_segment].geometry.length.sum() / 1000

            # Filter the data to only include rows for the selected segment
            mask = merged_opportunities['segmentti'].apply(lambda x: selected_segment in x)
            filtered_data = merged_opportunities[mask]

            # Calculate the average number of opportunities per kilometer for each Palvelun tyyppi
            avg_opportunities_segment = filtered_data.groupby('type').size() / segment_length
            
            # Filter the data using the boolean mask
            filtered_data = merged_opportunities[mask]
            zoom_level = 8

        # Filter data by selected Palvelun tyyppi
        filtered_data = filtered_data[filtered_data['type'].isin(selected_types + selected_landscape_types)]
        # Add a checkbox to show or hide the buffer
        col1, col2 = st.columns([1, 1])
        with col1:
            # Add a checkbox to show or hide the comparison chart
            if selected_segment != 'Koko reitti':
                show_comparison = st.checkbox('Vertaa palvelujen määrää koko reitin keskiarvoon (palvelut per kilometri)', value=False)
            else:
                show_comparison = False
        with col2:
            show_buffer = st.checkbox('Näytä 10 km etäisyysvyöhyke reitistä', value=False)

        # Summarize the number of each Palvelun tyyppi for the selected municipality or Koko reitti
        opportunities = filtered_data.groupby(['type', 'color']).size().reset_index(name='count')

        # Rename the opportunity column
        opportunities = opportunities.rename(columns={'type': 'Palvelun tyyppi'})

        fig1 = opportunity_chart(opportunities, selected_segment, segment_length)

        if show_comparison is not False:
            fig2 = create_comparison_chart(selected_segment, filtered_data, avg_opportunities, avg_opportunities_segment)
            fig2.update_traces(textposition='outside')
            
        else:
            fig2 = None

        m = create_map(filtered_data, zoom_level, show_buffer, selected_segment, buffer, buffer_merged, eurovelo, landscape_types, opportunity_types)

        return fig1, fig2, m, filtered_data

def opportunity_chart(opportunities, selected_segment, segment_length):
    # Create a bar chart
    fig1 = px.bar(
        opportunities,
        x='Palvelun tyyppi',
        y='count',
        color='Palvelun tyyppi',
        text='count',
        color_discrete_sequence=opportunities['color'].unique()
    )

    # Update the layout of the chart
    fig1.update_layout(
        dragmode=False,
        title=f'Palvelut etapilla:<br>{selected_segment} ({segment_length:.0f} km)',
        title_font_size=24,
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False
    )
    return fig1

#function for creating a comparison chart
def create_comparison_chart(selected_segment, filtered_data, avg_opportunities, avg_opportunities_segment):
    # Get the selected Palvelun tyyppit from the filtered_data DataFrame
    selected_opportunity_types = filtered_data['type'].unique()

    # Reindex the avg_opportunities and avg_opportunities_segment Series objects
    avg_opportunities = avg_opportunities.reindex(selected_opportunity_types, fill_value=0)
    avg_opportunities_segment = avg_opportunities_segment.reindex(selected_opportunity_types, fill_value=0)

    # Create a DataFrame with columns for Palvelun tyyppi, etappi, and average opportunities per kilometer
    data = pd.DataFrame({
        'Palvelun tyyppi': np.tile(selected_opportunity_types, 2),
        'Etappi': np.repeat([selected_segment, 'Koko reitti'], len(selected_opportunity_types)),
        'Palveluiden määrä kilometriä kohden': np.concatenate([avg_opportunities_segment.values, avg_opportunities.values])
    })

    # Create a bar chart
    fig2 = px.bar(
        data,
        x='Palvelun tyyppi',
        y='Palveluiden määrä kilometriä kohden',
        color='Etappi',
        barmode='group',
        color_discrete_map={selected_segment: '#fa9b28', 'Koko reitti': '#003346'}
    )

    # Update the layout of the chart
    fig2.update_layout(
        dragmode=False,
        title='Palveluiden määrä <br>kilometriä kohden',
        title_font_size=24,
        xaxis_title=None,
        yaxis_title=None,
        height=450,
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.1,
            xanchor="center",
            yanchor="top"
        )
    )
    
    return fig2


def create_map(filtered_data, zoom_level, show_buffer, selected_segment, buffer, buffer_merged, eurovelo, landscape_types, opportunity_types):
        #----- CREATING A MAP ALONGSIDE CHART -----
        if filtered_data.empty:
            col1, _ = st.columns([1, 1])
            with col1:
                st.warning("Ei palveluita etapilla, valitse toinen yhteysväli")
            return None
        
        else:  
            # Calculate the centroid of the selected segment geometry so that map gets to the location of the points
            centroid = filtered_data.geometry.unary_union.centroid

            # Create a new Folium map centered on the centroid of the selected segment's geometry
            m = folium.Map(location=[centroid.y, centroid.x], zoom_start=zoom_level, tiles = 'openstreetmap')

            # Add the buffer and route to the map
            if show_buffer:
                style_buffer(m, selected_segment, buffer, buffer_merged)
            style_route(m, selected_segment, eurovelo)


            # Add a polygon layer to the map for each landscape type
            for landscape_type in landscape_types:
                # Filter the data to only include rows for this landscape type
                data = filtered_data[filtered_data['type'] == landscape_type]
                
                # Check if the data DataFrame is empty
                if not data.empty:
                    # Get the fill color for this landscape type from the first row of data
                    color = data.iloc[0]['color']
                    
                    # Add a polygon layer to the map for this landscape type
                    add_polygon_layer(data, m)

            # Add a point layer to the map for each opportunity type
            for opportunity_type in opportunity_types:
                # Filter the data to only include rows for this opportunity type
                data = filtered_data[filtered_data['type'] == opportunity_type]
                
                # Check if the data DataFrame is empty
                if not data.empty:
                    # Get the color for this opportunity type from the first row of data
                    color = data.iloc[0]['color']
                    
                    # Add a point layer to the map for this opportunity type
                    add_point_layer(data, color, m)

            return(m)
        
# Function for adding polygons
def add_polygon_layer(gdf, m):
    # Add GeoJson polygons to the map
    for _, row in gdf.iterrows():
        folium.GeoJson(
            row.geometry,
            style_function=lambda x: {
                'color': row['stroke'],
                'weight': 1,
                'fillColor': row['color'],
                'fillOpacity': 0.5
            }
        ).add_child(folium.Tooltip(row['name'])).add_to(m)


# Define a function for adding a point layer to the map
def add_point_layer(gdf, color, m):
    # Add CircleMarkers to the map
    for _, row in gdf.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5,
            color='white',
            weight=0.8,
            fill=True,
            fill_color=color,
            fill_opacity=1
        ).add_child(folium.Tooltip(row['name'])).add_to(m)


def create_page_elements(selected_segment, filtered_data, landscape_types, eurovelo, fig1, fig2, m):
        col1, col2 = st.columns([1, 1])
        config = {'displayModeBar': False}
        col1.plotly_chart(fig1, use_container_width=True, config=config)
        responsive_to_window_width()
        if fig2 is not None:
            col2.plotly_chart(fig2, use_container_width=True, config=config)
            folium_static(m)
        else:
            with col2:
                folium_static(m)
        if selected_segment == 'Koko reitti':
            # Adding a table to compare the different segments
            filtered_data['segmentti'] = filtered_data['segmentti'].str.split(', ')
            filtered_data = filtered_data.explode('segmentti')
            segment_counts = filtered_data.groupby('segmentti').size().reset_index(name='Valittujen palveluiden ja maisema-alueiden lukumäärä etapilla')
            segment_counts = segment_counts[~segment_counts['segmentti'].isin(landscape_types)]
            segment_counts = segment_counts.rename(columns={'segmentti': 'Päiväetappi'})
            eurovelo_tm35fin = eurovelo_tm35fin = eurovelo.to_crs('EPSG:3067')
            segment_lengths = eurovelo_tm35fin.groupby('name').geometry.apply(lambda x: x.length.sum()) / 1000
            segment_counts['Etapin pituus (km)'] = segment_counts['Päiväetappi'].map(segment_lengths)
            st.dataframe(segment_counts, width = 1500)

def set_description():
    st.markdown("""


    #### Menetelmäkuvaus

    Analyysin paikkatietoaineistot on kerätty erilaisista tietolähteistä, jotka löydät verkkosivun kohdasta <b>4. Datalähteet</b>. 
    Palvelutasoanalyysi on tuotettu, jakamalla Eurovelon GPX-jälki 31 päiväetappiin. Analyysissä, jokaiselle päiväetapille on ajettu 10 km puskurivyöhyke, joiden sisälle jäävät palvelut on kiinnitetty arvottamaan eri päiväetappeja. 
    Data on alustettu erilaisilla paikkatieto-ohjelmistoilla, jonka jälkeen se on viety Pythonin Streamlit kirjaston avulla verkkoon, interaktiiviseen muotoon. 
    <br><br>Scriptin jolla sivu on tuotettu, löydät githubista: https://github.com/Mponkane/Eurovelo13_analysis/blob/main/streamlit/pages/1_📍_Palvelut_ja_virkistyskohteet.py         

    <br>

    <br>
    <em>App made by Matti Pönkänen | FLOU ltd (2023). Licensed under CC0-1.0.</em>
    
    """, unsafe_allow_html=True)

def main():
    set_page()
    merged_opportunities, eurovelo, buffer, buffer_merged = read_data()
    filter_data_and_create_charts(merged_opportunities, eurovelo, buffer, buffer_merged)
    set_description()

if __name__ == "__main__":
    main()