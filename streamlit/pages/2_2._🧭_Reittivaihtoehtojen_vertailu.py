import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static

## ___________________ service level analysis_______________________ 


def set_page():
    st.set_page_config(page_title="Reittivaihtoehtojen vertailu", 
                    layout="wide", 
                    initial_sidebar_state="expanded")

    st.markdown("""
    <div style="display: flex; align-items: center;">
    <h2 style="margin: 0;">Eurovelo 13 – Vaihtoehtoisten reittiosuuksien vertailu</h2>
    <img style="margin-left: auto;" src="https://raw.githubusercontent.com/Mponkane/Eurovelo13_analysis/main/streamlit/data/welcome_cyclist.png" width="150" height="150">
    </div>   
    Osana harvaan asuttujen seutujen matkailuhanketta, tarkasteltiin myös Eurovelo 13 -reitin vaihtoehtoisia reittilinjauksia palveluiden näkökulmasta.
    Nykyinen Eurovelo 13 -reitin linjaus kulkee Sallasta Savukoskelle, jonka kautta se suuntautuu Pyhälle. Osana tätä hanketta, tarkasteltiin myös vaihtoehtoista
    reittiä Kemijärven kautta. Reittivaihtoehdot ovat pituudeltaan samaa luokkaa (150 km), mutta uusi reittilinjaus on palvelutarjonnaltaan runsaampi. 
    Alla olevasta laatikosta pystyt rajaamaan erilaiset palvelut, jotka piirretään näkyviin kuvaajaan sekä karttaan. 
    Kartan harmaat pisteet ovat palveluita, jotka sijoittuvat molempien reittien etapeille.
    <br><br>
    """, unsafe_allow_html=True)


def read_data():
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

    opportunities_VE0['route'] = 'Nykyinen reitti (Salla-Savukoski-Pyhä)'
    opportunities_VE1['route'] = 'Vaihtoehtoinen reitti (Salla-Kemijärvi-Pyhä)'
    combined_data = pd.concat([opportunities_VE0, opportunities_VE1])

    opportunity_types = combined_data['type'].unique()

    return combined_data, opportunity_types, ve0, ve1, eurovelo

def filter_data_and_create_charts(combined_data, opportunity_types, ve0, ve1, eurovelo):
    selected_types = st.multiselect('Valitse palvelut ja virkistyskohteet:', opportunity_types, default=opportunity_types)

    if not selected_types:
        pass

    else:
        # Tämä saatttaa olla väärin
        filtered_data = combined_data[combined_data['type'].isin(selected_types)]
        summary_data = filtered_data.groupby(['type', 'route']).size().reset_index(name='count')
        summary_data = summary_data.rename(columns={'type': 'Palvelun tyyppi'})

        fig = px.bar(
            summary_data,
            x='Palvelun tyyppi',
            y='count',
            color='route',
            text='count',
            barmode='group',
            color_discrete_sequence=['#003346', '#fa9b28']
        )

        fig.update_layout(
            title=f'Palveluiden vertailu nykyisellä ja <br>vaihtoehtoisella reittilinjauksella',
            dragmode=False,
            title_font_size=24,
            xaxis_title=None,
            yaxis_title=None,
            showlegend=True,
            legend_title_text='Reitti',
            legend=dict(
                font=dict(
                    size=14
                ),
                title_font_size=16,
                orientation="h",
                x=0.5,
                y=-0.3,
                xanchor="center",
                yanchor="top"
            )
        )

        
        m = create_map(filtered_data, combined_data, selected_types, eurovelo, ve0, ve1)
        return m, fig

def create_map(filtered_data, combined_data, selected_types, eurovelo, ve0, ve1):
        centroid = filtered_data.geometry.unary_union.centroid
        zoom_level = 8
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=zoom_level, tiles='openstreetmap')

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

        for route, color in zip(['Nykyinen reitti (Salla-Savukoski-Pyhä)', 'Vaihtoehtoinen reitti (Salla-Kemijärvi-Pyhä)'], ['#003346', '#fa9b28']):
            data = filtered_data[filtered_data['route'] == route]
            
            # Check if the data DataFrame is empty
            if not data.empty:
                # Add a point layer to the map for this route
                add_point_layer(data, color, m)

        responsive_to_window_width()
        return m

def responsive_to_window_width():
    making_map_responsive = """
    <style>
    [title~="st.iframe"] { width: 100%}
    </style>
    """
    st.markdown(making_map_responsive, unsafe_allow_html=True)

def add_point_layer(gdf, color, m):
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

def add_description():
    st.markdown("""

    <br>
    <em>App made by Matti Pönkänen | FLOU ltd (2023). Licensed under CC0-1.0.</em>
    
    """, unsafe_allow_html=True)


def main():
    set_page()
    combined_data, opportunity_types, ve0, ve1, eurovelo = read_data()
    result = filter_data_and_create_charts(combined_data, opportunity_types, ve0, ve1, eurovelo)
    if result is None:
        st.warning('Valitse ainakin yksi palvelu tai virkistyskohde')
    else:
        m, fig = result
        config = {'displayModeBar': False}
        st.plotly_chart(fig, use_container_width=True, config=config)
        folium_static(m)
    add_description()


if __name__ == "__main__":
    main()