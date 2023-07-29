import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import folium_static
from functions.markdown_functions import responsive_to_window_width

## ___________________ service level analysis_______________________ 

st.set_page_config(page_title="service level analysis", 
                   layout="wide", 
                   initial_sidebar_state="expanded")


st.markdown("""
            ## **Eurovelo 13 vaihtoehtoisten reittiosuuksien vertailu**

            Osana harvaan asuttujen seutujen matkailuhanketta tarkasteltiin myös Eurovelo 13 -reitin vaihtoehtoisia reittilinjauksia palveluiden näkökulmasta.

            """)


opportunities_VE0 = gpd.read_file('streamlit/data/services_VE0.shp')
opportunities_VE1 = gpd.read_file('streamlit/data/services_VE1.shp')
eurovelo = gpd.read_file('streamlit/data/eurovelo.shp')
ve0 = gpd.read_file('streamlit/data/VE0.shp')
ve1 = gpd.read_file('streamlit/data/VE1.shp')

opportunities_VE0  = opportunities_VE0.to_crs('EPSG:4326')
opportunities_VE1  = opportunities_VE1.to_crs('EPSG:4326')
eurovelo = eurovelo.to_crs('EPSG:4326')
ve0 = ve0.to_crs('EPSG:4326')
ve1 = ve1.to_crs('EPSG:4326')

# Combine the two data frames into a single data frame
opportunities_VE0['route'] = 'Nykyinen reitti (Salla-Savukoski-Pyhä)'
opportunities_VE1['route'] = 'Vaihtoehtoinen reitti (Salla-Kemijärvi-Pyhä)'
combined_data = pd.concat([opportunities_VE0, opportunities_VE1])

opportunity_types = combined_data['type'].unique()
selected_types = st.multiselect('Valitse palvelut ja virkistyskohteet:', opportunity_types, default=opportunity_types)

if not selected_types:
    st.warning('Valitse ainakin yksi palvelu tai virkistyskohde')

else:
    filtered_data = combined_data[combined_data['type'].isin(selected_types)]
    summary_data = filtered_data.groupby(['type', 'route']).size().reset_index(name='count')
    summary_data = summary_data.rename(columns={'type': 'Palvelun tyyppi'})

    # Create a grouped bar chart
    fig = px.bar(
        summary_data,
        x='Palvelun tyyppi',
        y='count',
        color='route',
        text='count',
        barmode='group',
        color_discrete_sequence=['#003346', '#fa9b28']
    )

    # Update the layout of the chart
    fig.update_layout(
        title=f'Palveluiden vertailu nykyisellä ja vaihtoehtoisella reittilinjauksella',
        title_font_size=24,
        xaxis_title=None,
        yaxis_title=None,
        showlegend=True,
        legend_title_text='Reitti',
        legend=dict(
            font=dict(
                size=14
            ),
            title_font_size=16
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    centroid = filtered_data.geometry.unary_union.centroid
    zoom_level = 8

    # Create a new Folium map centered on the centroid of the selected segment's geometry
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=zoom_level, tiles='cartodbpositron')

    # Update the 'add_point_layer' function to use the 'in_both_routes' column to determine the fill color of the CircleMarkers
    def add_point_layer(gdf, color):
        # Add CircleMarkers to the map
        for _, row in gdf.iterrows():
            # Use grey fill color if the point appears in both routes, otherwise use the specified color
            fill_color = '#b3b3b3' if row['in_both_routes'] else color
            
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=5,
                color='white',
                weight=0.8,
                fill=True,
                fill_color=fill_color,
                fill_opacity=1
            ).add_child(folium.Tooltip(row['name'])).add_to(m)

    # Create a new column 'in_both_routes' that is True if the point appears in both routes and False otherwise
    combined_data['in_both_routes'] = combined_data.duplicated(subset=['geometry'], keep=False)

    # Filter the data to only include rows for the selected types
    filtered_data = combined_data[combined_data['type'].isin(selected_types)]

    folium.GeoJson(
        eurovelo,
        style_function=lambda x: {
            'color': 'grey',
            'weight': 3,
            'dashArray': '5, 5'
        }
    ).add_to(m)

    folium.GeoJson(
        ve0,
        style_function=lambda x: {
            'color': 'white',
            'weight': 5
        }
    ).add_to(m)

    folium.GeoJson(
        ve0,
        style_function=lambda x: {
            'color': '#003346',
            'weight': 3
        },
        tooltip=folium.GeoJsonTooltip(fields=['name'])
    ).add_to(m)

    folium.GeoJson(
        ve1,
        style_function=lambda x: {
            'color': 'white',
            'weight': 5
        }
    ).add_to(m)

    folium.GeoJson(
        ve1,
        style_function=lambda x: {
            'color': '#fa9b28',
            'weight': 3
        },
        tooltip=folium.GeoJsonTooltip(fields=['name'])
    ).add_to(m)

    # Add a point layer to the map for each route
    for route, color in zip(['Nykyinen reitti (Salla-Savukoski-Pyhä)', 'Vaihtoehtoinen reitti (Salla-Kemijärvi-Pyhä)'], ['#003346', '#fa9b28']):
        # Filter the data to only include rows for this route
        data = filtered_data[filtered_data['route'] == route]
        
        # Check if the data DataFrame is empty
        if not data.empty:
            # Add a point layer to the map for this route
            add_point_layer(data, color)

    responsive_to_window_width()
    folium_static(m)


