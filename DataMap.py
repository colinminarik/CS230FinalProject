import streamlit as st
import pandas as pd
import pydeck as pdk


def side_bar_image():
    image_path = "C:/Users/cmina/One drive-bentley/OneDrive - Bentley University/year 2/CS230/pythonProject/streamlitproject/carcrash.jpg"
    st.sidebar.image(image_path, use_column_width=True)

path = "C:/Users/cmina/One drive-bentley/OneDrive - Bentley University/year 2/CS230/pythonProject/streamlitproject/"

@st.cache(allow_output_mutation=True)
def read_data():
    df = pd.read_csv(path + "2017_Crashes_10000_sample.csv")
    df.dropna(subset=['LON', 'LAT', 'CITY_TOWN_NAME', 'NUMB_VEHC', 'MAX_INJR_SVRTY_CL'], inplace=True)
    return df

def get_color_map(unique_vehc_counts):
    colors = [
        [255, 0, 0, 160], [0, 255, 0, 160], [0, 0, 255, 160], [255, 255, 0, 160],
        [255, 0, 255, 160], [0, 255, 255, 160], [128, 0, 0, 160], [128, 128, 0, 160],
        [0, 128, 0, 160], [128, 0, 128, 160], [0, 128, 128, 160], [0, 0, 128, 160],
    ]
    # [PY4] List comprehension that correlates the number of crashes with the correct color
    color_map = {vehc: colors[i % len(colors)] for i, vehc in enumerate(unique_vehc_counts)}
    return color_map

# [VIZ4] Scatter plot map that lets you select the town you want to view and shows all the crashes that occured in that town
# it also displays each crash in a different color depending on how many cars were involved in the crash
# also when you hover over the data point it displays the overall severity of the crash
def show_crash_map(data):
    towns = data['CITY_TOWN_NAME'].unique()
    selected_town = st.selectbox("Select a town to display crashes:", towns)
    filtered_data = data[data['CITY_TOWN_NAME'] == selected_town]

    if not filtered_data.empty:
        unique_vehicle_counts = sorted(filtered_data['NUMB_VEHC'].unique())
        color_map = get_color_map(unique_vehicle_counts)
        filtered_data['color'] = filtered_data['NUMB_VEHC'].apply(lambda x: color_map[x])

        view_state = pdk.ViewState(
            latitude=filtered_data['LAT'].mean(),
            longitude=filtered_data['LON'].mean(),
            zoom=11,
            pitch=50,
        )
        # creates the box with info when you hover over a data point
        tooltip={"html": "<b>Town:</b> {CITY_TOWN_NAME}<br><b>Max Injury Severity:</b> {MAX_INJR_SVRTY_CL}",
                 "style": {"backgroundColor": "steelblue", "color": "white"}}

        scatterplot_layer = pdk.Layer(
            "ScatterplotLayer",
            filtered_data,
            get_position="[LON, LAT]",
            get_color="color",
            get_radius=100,
            pickable=True,  # Enable tooltips
        )

        deck = pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=view_state,
            layers=[scatterplot_layer],
            tooltip=tooltip
        )
        st.pydeck_chart(deck)
        st.markdown("### Color Legend for Number of Vehicles Involved")
        for vehc, color in color_map.items():
            color_hex = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
            st.markdown(f"<span style='color:{color_hex};'>●</span> {vehc} vehicles", unsafe_allow_html=True)
    else:
        st.error("No data available for the selected town.")

def main():
    data = read_data()
    st.title('Crash Map Viewer')
    show_crash_map(data)
    side_bar_image()

main()