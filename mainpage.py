"""
Name:       Colin Minarik
CS230:      Section 5
Data:       Which data set you used
URL:

Description: This stream lit site breaks down the data from the car crashes of 2017 data set. I have created various pivot tables, some being interactive and showing certain totals.
Also it includes various interactive charts and graphs to display the data differently. There are also drop down, text, and check boxes. There is also an interactive 
map that allows you to select certain towns to view where the crashes were reported and has a legend that tells you how many cars were involved in the car. Also, when you 
hover over it, it tells you the severity of the crash. 

"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
def main_page():
    # [ST4] image for the sidebar, this function is on every file in my code
    def side_bar_image():
        image_path = "carcrash.jpg"
        st.sidebar.image(image_path, use_column_width=True)

    def load_data_source_page():
        st.title("Car Crashes in Massachusetts in 2017")
        st.header("Dataset Overview")
        st.markdown("""
        **Title:** Car Crashes  
        **Type:** Geospatial: In Massachusetts  
        **Description:** This dataset includes comprehensive information about car crashes in Massachusetts, with 
        the types of crashes, location, and result of the crash.
        """)
        st.header("About the Dataset")
        st.markdown("""
        The "Car Crash" dataset provides geospatial data on car crashes across the state. 
        This information helps visualize where most crashes take place and outcomes of these crashes.
        """)

def page2():
    @st.cache_data
    def load_data():
        path = "C:/Users/cmina/One drive-bentley/OneDrive - Bentley University/year 2/CS230/pythonProject/streamlitproject/"
        df = pd.read_csv("2017_Crashes_10000_sample.csv")
        df['POLC_AGNCY_TYPE_DESCR'] = df['POLC_AGNCY_TYPE_DESCR'].str.lower()
        if df.empty:
            st.error("Loaded data is empty.")
        return df
    
    
    # [ST3] a text box that allows you to enter state or local police, no matter what case the letter is
    # that then returns a tabel showing the total amount of responses.
    def Police_text_box():
        st.title('Police Agency Response Analysis')
        df = load_data()
        agency_type = st.text_input("Enter agency type (e.g., local police, state police):").lower().strip()
        if agency_type:
            count = df[df['POLC_AGNCY_TYPE_DESCR'] == agency_type].shape[0]
            results_df = pd.DataFrame({
                'Agency Type': [agency_type.capitalize()],
                'Total Count': [count]
            })
            st.write("### Total Responses for the Entered Agency Type")
            st.table(results_df)
        else:
            st.write("Please enter an agency type above.")
    
    
    # [PY2] This function return two values, the total amount of conditions reported for each category and the percentage of them
    def calculate_road_conditions():
        df = load_data()
        if 'ROAD_SURF_COND_DESCR' not in df.columns:
            st.error("The expected column 'ROAD_SURF_COND_DESCR' is not found in the dataset.")
            return None, None  # Return None for both counts and percentages if column is missing
        conditions = ["Dry", "Ice", "Snow", "Wet", "Slush", "Not reported", "Unknown"]
        df = df[df['ROAD_SURF_COND_DESCR'].isin(conditions)]
        condition_counts = df['ROAD_SURF_COND_DESCR'].value_counts()
        total = condition_counts.sum()
        condition_percentages = (condition_counts / total * 100).round(2).astype(str) + '%'
        results_df = pd.DataFrame({
            'Condition': condition_counts.index,
            'Total Count': condition_counts.values,
            'Percentage': condition_percentages.values
        })
    
        return results_df, total
    
    def display_road_conditions():
        results_df, total = calculate_road_conditions()
        if results_df is not None and total is not None:
            st.write('<style>thead th {text-align: center;} tbody td {text-align: left;} th, td {font-size: 18px;}</style>', unsafe_allow_html=True)
            st.write("### Road Surface Condition Analysis")
            st.write(f"Total recorded conditions: {total}")
            st.dataframe(results_df)
        elif results_df is None:
            st.write("No data to display.")
    
    # [Py1] this function has two parameters, the dataset and the certain column, it filters through those and creates a
    # a table to show the totals of whether it was a hit and run or not.
    def summarize_hit_run(data, column_name="HIT_RUN_DESCR"):
        if column_name not in data.columns:
            st.error(f"The column '{column_name}' does not exist in the dataset.")
            return None
        hit_run_counts = data[column_name].value_counts()
        results_df = pd.DataFrame({
            'Category': hit_run_counts.index,
            'Total Count': hit_run_counts.values
        })
        expected_categories = ["Yes, hit and run", "No hit and run"]
        for category in expected_categories:
            if category not in results_df['Category'].tolist():
                results_df = results_df.append({'Category': category, 'Total Count': 0}, ignore_index=True)
        st.table(results_df)
    
    # [DA4] filters the data shown in ascending or descending order, it also displays the amount of cars involved in the
    # crash that are selected.
    # [DA6] Interactive pivot tables.
    def interactive_pivot_table(data):
        unique_vehicle_counts = sorted(data['NUMB_VEHC'].dropna().unique())
        selected_vehicle_counts = []
        st.write("Select number of vehicles involved:")
        for index, vehicle_count in enumerate(unique_vehicle_counts):
            if st.checkbox(f"{vehicle_count} vehicles", key=f"vehicle_{index}"):
                selected_vehicle_counts.append(vehicle_count)
    
        filtered_data = data[data['NUMB_VEHC'].isin(selected_vehicle_counts)]
        sort_order = st.radio("Select sort order for vehicle data:", ("Ascending", "Descending"), key='sort_vehicle')
    
        if not filtered_data.empty:
            pivot_table = pd.pivot_table(filtered_data, values='CRASH_NUMB', index='NUMB_VEHC', aggfunc='count')
            pivot_table.rename(columns={'CRASH_NUMB': 'Total Crashes'}, inplace=True)
            pivot_table = pivot_table.sort_values(by='Total Crashes', ascending=(sort_order == "Ascending"))
            st.write("### Pivot Table Showing the Number of Crashes for Each Vehicle Count")
            st.dataframe(pivot_table)
        else:
            st.write("No data available for the selected numbers of vehicles.")
    
    # [DA5] filters the data you want shown by towns selected and either in ascending or descending order in total amount
    # of crashes that took place within the town.
    def interactive_pivot_table2(data):
        towns = st.multiselect('Select Towns:', data['CITY_TOWN_NAME'].unique())
        sort_order = st.radio("Select sort order for town data:", ("Ascending", "Descending"), key='sort_town')
    
        if towns:
            filtered_data = data[data['CITY_TOWN_NAME'].isin(towns)]
            town_crash_data = filtered_data.groupby('CITY_TOWN_NAME').size().reset_index(name='Total Crashes')
            total_crashes = town_crash_data['Total Crashes'].sum()
            town_crash_data['Percentage of Total Crashes'] = (town_crash_data['Total Crashes'] / total_crashes * 100).round(2)
            town_crash_data = town_crash_data.sort_values(by='Total Crashes', ascending=(sort_order == "Ascending"))
            st.write("### Pivot Table Showing Total Crashes and Percentages")
            st.dataframe(town_crash_data.set_index('CITY_TOWN_NAME'))
        else:
            st.warning('Please select at least one town.')
    
    # [DA3] shows the largest and smallest values by date for amount of crashes within the dataset
    def display_crash_analysis(data):
        # Converts 'CRASH_DATE_TEXT' to datetime to ensure the correct aggregation
        data['CRASH_DATE_TEXT'] = pd.to_datetime(data['CRASH_DATE_TEXT'])
    
        # [PY5] dictionary that stores each date and later in the code it sums it up to display the total amount of crashes
        # on the date.
        date_crash_counts = {}
        # [DA8] Uses iterrows() to iterate through each row of the dataframe and pull each date
        for index, row in data.iterrows():
            crash_date = row['CRASH_DATE_TEXT'].date()
            if crash_date in date_crash_counts:
                date_crash_counts[crash_date] += 1
            else:
                date_crash_counts[crash_date] = 1
        # Converts the dictionary into a DataFrame
        date_counts_df = pd.DataFrame(list(date_crash_counts.items()), columns=['Date', 'Number of Crashes'])
        date_counts_df.set_index('Date', inplace=True)
        top_dates = date_counts_df.nlargest(5, 'Number of Crashes')
        bottom_dates = date_counts_df.nsmallest(5, 'Number of Crashes')
        st.write("## Dates with Most and Least Crashes")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 5 Dates with Most Crashes")
            st.dataframe(top_dates)
        with col2:
            st.subheader("Top 5 Dates with Least Crashes")
            st.dataframe(bottom_dates)
    
    def run():
        Police_text_box()
        st.title('Road Surface Condition Analysis')
        display_road_conditions()
        st.title('Hit and Run Summary')
        # Call the function with the dataset
        summarize_hit_run(data=load_data())
        interactive_pivot_table(data=load_data())
        st.title('Interactive Crash Data Analysis')
        interactive_pivot_table2(data=load_data())
        display_crash_analysis(data=load_data())
    
    run()

def page3():
    path = "C:/Users/cmina/One drive-bentley/OneDrive - Bentley University/year 2/CS230/pythonProject/streamlitproject/"
    
    @st.cache(allow_output_mutation=True)
    def read_data():
        df = pd.read_csv("2017_Crashes_10000_sample.csv")
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
    
    def run2():
        data = read_data()
        st.title('Crash Map Viewer')
        show_crash_map(data)
       
    
    run2()

def page4():
    import random
    
    # [PY3] this function changes the color of the bars in the bar chart and the pie chart at random everytime something new
    # is selected. It is called in both the interactive bar chart function and the interactive pie chart function
    def generate_random_colors(num_colors):
        return [(random.random(), random.random(), random.random()) for _ in range(num_colors)]
    
    @st.cache_data
    def read_data():
        df = pd.read_csv("2017_Crashes_10000_sample.csv")
        return df
    
    
    # [DA1] cleaning and sorting data into a bar chart
    # [VIZ1] an interactive bar chart with titles, and axis labels
    def interactive_bar_chart(data):
        # [ST1] a drop down box that lets you select each twon from the data set to display the amount of crashes in the town on the bar chart
        towns = st.multiselect('Select Towns:', data['CITY_TOWN_NAME'].unique())
        # [ST2] an interval slider that changes the values on the y-axis scale
        scale_factor = st.slider('Y-axis Scale Factor:', min_value=1, max_value=10, step=1, value=1)
        if not towns:
            st.warning('Please select at least one town.')
            return
        filtered_data = data[data['CITY_TOWN_NAME'].isin(towns)]
        total_crashes = filtered_data.groupby('CITY_TOWN_NAME').size().reset_index(name='Number of Crashes')
        st.subheader('Total Crashes in Selected Towns')
        st.markdown("### Select Towns and Interval:")
        st.sidebar.write('---')
        if not total_crashes.empty:
            fig, ax = plt.subplots()
            colors = generate_random_colors(len(total_crashes))
            ax.bar(total_crashes['CITY_TOWN_NAME'], total_crashes['Number of Crashes'], color=colors)
            ax.set_ylabel('Number of Crashes (scaled)')
            ax.set_xlabel('Towns')
            ax.set_title('Total Crashes by Selected Town(s)')
            ax.set_xticks(range(len(total_crashes)))
            ax.set_xticklabels(total_crashes['CITY_TOWN_NAME'], rotation=45, ha='right')
            ax.set_ylim(0, total_crashes['Number of Crashes'].max() * scale_factor)
            tick_vals = ax.get_yticks()
            ax.set_yticklabels([int(y / scale_factor) for y in tick_vals])
            st.pyplot(fig)
        else:
            st.write("No data available for the selected towns.")
    
        if not total_crashes.empty:
            st.write("### Detailed Data Table")
            # [DA6] creates an interactive pivot tabel that changes based on what towns are selected to show the totals
            st.dataframe(total_crashes.set_index('CITY_TOWN_NAME'))
        else:
            st.write("No data to display in the table.")
    
    # [VIZ2] an interactive pie chart with a title and labels
    def interactive_pie_chart(data):
        unique_vehicle_counts = sorted(data['NUMB_VEHC'].dropna().unique())
        selected_vehicle_counts = []
        # EXTRA CREDIT: creates a checkbox to select the amount of cars involved in crashes you want to display in the pie chart
        st.write("Select number of vehicles involved:")
        for vehicle_count in unique_vehicle_counts:
            if st.checkbox(f"{vehicle_count} vehicles", key=vehicle_count):
                selected_vehicle_counts.append(vehicle_count)
        filtered_data = data[data['NUMB_VEHC'].isin(selected_vehicle_counts)]
        crashes_per_vehicle_count = filtered_data['NUMB_VEHC'].value_counts().sort_index()
        if not crashes_per_vehicle_count.empty:
            fig, ax = plt.subplots()
            colors = generate_random_colors(len(crashes_per_vehicle_count))
            ax.pie(crashes_per_vehicle_count, labels=crashes_per_vehicle_count.index, autopct='%1.1f%%', startangle=90,
                   colors=colors)
            ax.set_title('Percentage of Crashes by Selected Numbers of Vehicles Involved')
            st.pyplot(fig)
        else:
            st.write("No data available for the selected numbers of vehicles.")
    
    def plot_sequential_bar_chart(data):
        # [DA2] sorting the data in descending order for the sequential bar chart
        crashes_per_vehicle_count_sorted = data['NUMB_VEHC'].value_counts().sort_values(ascending=False)
        fig, ax = plt.subplots()
        ax.bar(crashes_per_vehicle_count_sorted.index.astype(str), crashes_per_vehicle_count_sorted.values, color='skyblue')
        ax.set_xlabel('Number of Vehicles Involved')
        ax.set_ylabel('Total Number of Crashes')
        ax.set_title('Crashes with Amount of Cars')
        st.pyplot(fig)
        # [DA6] creates a pivot table that shows the total amount of crashes with a certain amount of cars
        pivot_table = crashes_per_vehicle_count_sorted.reset_index()
        pivot_table.columns = ['Number of Vehicles Involved', 'Total Number of Crashes']
        total_crashes = pivot_table['Total Number of Crashes'].sum()
        pivot_table['Percentage of Total Crashes'] = (pivot_table['Total Number of Crashes'] / total_crashes) * 100
        st.write("### Pivot Table Showing the Sum of Crashes for Each Vehicle Count")
        st.dataframe(pivot_table.style.format({'Percentage of Total Crashes': "{:.2f}%"}))
    
    # [VIZ3] third chart, a line chart that displays the total number of crashes on certain dates throughout 2017
    def plot_line_chart(data):
        data['Datetime'] = pd.to_datetime(data['CRASH_DATE_TEXT'] + ' ' + data['CRASH_TIME'])
        data = data.set_index('Datetime')
        daily_data = data.resample('D').count()
        plt.figure(figsize=(10, 5))
        plt.plot(daily_data.index, daily_data['CRASH_DATE_TEXT'], marker='o', linestyle='-')  # Assuming any column to count
        plt.title('Daily Trends in Crashes')
        plt.xlabel('Date')
        plt.ylabel('Number of Crashes')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)
    
    
    def run3():
        data = read_data()
        st.subheader('Interactive Analysis of Total Crashes in Certain Towns')
        interactive_bar_chart(data)
        st.write("\n")
        st.subheader('Interactive Analysis of Vehicle Crashes')
        interactive_pie_chart(data)
        st.write("\n")
        st.subheader('Analysis of Vehicle Crashes')
        st.write("## Sequential Bar Chart of Crashes by Vehicle Count")
        plot_sequential_bar_chart(data)
        st.write("\n")
        st.title('Crash Data Analysis Over Time')
    #   EXTRA CREDIT: a button that when clicked displays the line chart
        if st.button('Show Trend'):
            plot_line_chart(data.copy())
    
    
    run3()

def main():
    load_data_source_page()
    side_bar_image()
    # Sidebar navigation
    st.sidebar.title("Navigation")
    # Create a dictionary of your pages
    pages_dict = {
        "Home": main_page,
        "Queries and Pivot Tables": page2,
        "Data Map": page3,
        "Data Information": page4
    }
    # Radio button for page selection
    selected_page = st.sidebar.radio("Select a page:", list(pages_dict.keys()))

    # Call the app function based on selection
    pages_dict[selected_page]()

main()
