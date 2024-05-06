import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

path = "C:/Users/cmina/One drive-bentley/OneDrive - Bentley University/year 2/CS230/pythonProject/streamlitproject/"

def side_bar_image():
    image_path = "C:/Users/cmina/One drive-bentley/OneDrive - Bentley University/year 2/CS230/pythonProject/streamlitproject/carcrash.jpg"
    st.sidebar.image(image_path, use_column_width=True)


import random

# [PY3] this function changes the color of the bars in the bar chart and the pie chart at random everytime something new
# is selected. It is called in both the interactive bar chart function and the interactive pie chart function
def generate_random_colors(num_colors):
    return [(random.random(), random.random(), random.random()) for _ in range(num_colors)]

@st.cache_data
def read_data():
    df = pd.read_csv(path + "2017_Crashes_10000_sample.csv")
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


def main():
    side_bar_image()
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


main()