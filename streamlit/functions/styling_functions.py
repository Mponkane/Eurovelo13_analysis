import streamlit as st
import folium
from streamlit_folium import folium_static

def style_buffer(m, selected_segment, buffer, buffer_merged):
    # Add the Eurovelo route to the map
    if selected_segment == 'EV13':
        # Add the merged buffer to the map
        folium.GeoJson(
            buffer_merged,
            style_function=lambda x: {
                'color': '#034716',
                'weight': 1,
                'fillColor': '#034716',
                'fillOpacity': 0.1
            }
        ).add_to(m)

    else:
        # Filter the buffer data to only include the selected segment
        buffer_selected = buffer[buffer['name'] == selected_segment]

        # Add the selected buffer to the map
        folium.GeoJson(
            buffer_selected,
            style_function=lambda x: {
                'color': '#034716',
                'weight': 1,
                'fillColor': '#034716',
                'fillOpacity': 0.2
            }
        ).add_to(m)

def style_route(m, selected_segment, eurovelo):
    # Add the Eurovelo route to the map
    if selected_segment == 'EV13':

        # Add a white border around the entire route
        folium.GeoJson(
            eurovelo,
            style_function=lambda x: {
                'color': 'white',
                'weight': 3
            }
        ).add_to(m)

        # Add the entire route to the map
        folium.GeoJson(
            eurovelo,
            style_function=lambda x: {
                'color': '#fa9b28',
                'weight': 2
            }
        ).add_to(m)
    else:
        # Add the non-selected segments of the route to the map as a grey dashed line
        folium.GeoJson(
            eurovelo,
            style_function=lambda x: {
                'color': 'grey',
                'weight': 3,
                'dashArray': '5, 5'
            }
        ).add_to(m)

        # Filter the Eurovelo data to only include the selected segment
        eurovelo_selected = eurovelo[eurovelo['name'] == selected_segment]

        # Add a white border around the selected segment
        folium.GeoJson(
            eurovelo_selected,
            style_function=lambda x: {
                'color': 'white',
                'weight': 8
            }
        ).add_to(m)

        # Add the selected segment to the map
        folium.GeoJson(
            eurovelo_selected,
            style_function=lambda x: {
                'color': '#fa9b28',
                'weight': 4
            }
        ).add_to(m)
