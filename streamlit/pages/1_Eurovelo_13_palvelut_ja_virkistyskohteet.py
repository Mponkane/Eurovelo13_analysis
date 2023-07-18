import streamlit as st
import geopandas as gpd
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
            ### 📍**Eurovelo 13 reitin palvelutaso**

            *Kuvaus ja datalähteet tähän*
            
            """)

merged_opportunities = gpd.read_file('streamlit/data/palvelut.shp')

# Reproject the data to Web Mercator
merged_opportunities = merged_opportunities.to_crs('EPSG:4326')

opportunity_types = merged_opportunities['type'].unique()
selected_types = st.multiselect('Valitse palvelut ja virkistyskohteet:', opportunity_types)

if not selected_types:
    st.warning('Valitse ainakin yksi palvelu tai virkistyskohde')

else:
    # Get unique values from the 'municipality' column
    segments = merged_opportunities['segmentti'].unique()

    # Split the values in the 'segmentti' column on the comma character
    segments = merged_opportunities['segmentti'].str.split(', ')

    # Flatten the list of lists into a single list of segment values
    segments = [segment for sublist in segments for segment in sublist]

    # Get the unique segment values
    segments = np.unique(segments)

    # Add an "All" option to the segments list so that data can be looked at nationally
    segments = np.insert(segments, 0, 'All')

    # Create a selectbox for different segments
    selected_segment = st.selectbox('Valitse reittiosuus:', segments)

    # Filter the data based on the selected municipality or All
    if selected_segment == 'All':
        filtered_data = merged_opportunities
        zoom_level = 5
        point_size = 120
    else:
        # Split the values in the 'segmentti' column on the comma character
        segments = merged_opportunities['segmentti'].str.split(', ')
        
        # Create a boolean mask indicating which rows contain the selected segment
        mask = segments.apply(lambda x: selected_segment in x)
        
        # Filter the data using the boolean mask
        filtered_data = merged_opportunities[mask]
        zoom_level = 10
        point_size = 80

    # Filter data by selected opportunity types
    filtered_data = filtered_data[filtered_data['type'].isin(selected_types)]

    #----- CREATING A CHART -----

    # Summarize the number of each opportunity type for the selected municipality or all
    opportunities = filtered_data.groupby(['type', 'color']).size().reset_index(name='count')

    # Rename the opportunity column
    opportunities = opportunities.rename(columns={'type': 'Opportunity type'})

    # Create a bar chart
    fig = px.bar(
        opportunities,
        x='Opportunity type',
        y='count',
        color='Opportunity type',
        text='count',
        color_discrete_sequence=opportunities['color'].unique()
    )

    # Update the layout of the chart
    fig.update_layout(
     title=f'Number of opportunities in {selected_segment}',
     title_font_size=24,
     xaxis_title=None,
     yaxis_title=None,
     showlegend=False
    )

    fig.update_traces(textposition='outside')

    #----- CREATING A MAP ALONGSIDE CHART -----
    if filtered_data.empty:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.warning("Ei palveluita segmentillä, valitse toinen yhteysväli")
    else:  
        # Calculate the centroid of the selected municipality's geometry so that map gets to the location of the points
        centroid = filtered_data.geometry.unary_union.centroid

        # Create a new Folium map centered on the centroid of the selected segment's geometry
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=zoom_level, tiles = "cartodbpositron")

        # Define a function for adding a point layer to the map
        def add_point_layer(gdf, color):
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



        # Add a point layer to the map for each opportunity type
        for opportunity_type in opportunity_types:
            # Filter the data to only include rows for this opportunity type
            data = filtered_data[filtered_data['type'] == opportunity_type]
            
            # Check if the data DataFrame is empty
            if not data.empty:
                # Get the color for this opportunity type from the first row of data
                color = data.iloc[0]['color']
                
                # Add a point layer to the map for this opportunity type
                add_point_layer(data, color)


        col1, col2 = st.columns([1, 1])
        col1.plotly_chart(fig, use_container_width=True)

        responsive_to_window_width()
        # Display the map in Streamlit
        with col2:
            folium_static(m)

