import streamlit as st
import streamlit.components.v1 as components
import json

# Define the custom component
def pydeck_map(data, on_click):
    # Create the component HTML
    html = f"""
    <div id="map"></div>
    <script src="https://unpkg.com/deck.gl@latest"></script>
    <script>
        const map = new deck.DeckGL({{
            container: 'map',
            mapStyle: 'https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json',
            initialViewState: {{
                longitude: -122.4,
                latitude: 37.76,
                zoom: 11,
                pitch: 50
            }},
            controller: true,
            layers: [
                new deck.ScatterplotLayer({{
                    data: {data},
                    getPosition: d => [d.longitude, d.latitude],
                    getRadius: d => 100,
                    getFillColor: d => [255, 0, 0],
                    onClick: info => {{
                        if (info.object) {{
                            window.parent.postMessage({{
                                type: 'streamlit:setComponentValue',
                                value: info.object
                            }}, '*');
                        }}
                    }}
                }})
            ]
        }});
    </script>
    """

    # Display the component in Streamlit
    components.html(html, height=500)

    # Handle click events
    value = st.session_state.get('value')
    if value:
        on_click(value)

# Define some data for the map
data = [
    {'longitude': -122.4, 'latitude': 37.76},
    {'longitude': -122.5, 'latitude': 37.76},
    {'longitude': -122.6, 'latitude': 37.76}
]

# Display the map in Streamlit
pydeck_map(data, on_click=lambda x: st.write(json.dumps(x)))
