import streamlit as st
import pandas as pd


def side_bar_image():
    image_path = "C:/Users/cmina/One drive-bentley/OneDrive - Bentley University/year 2/CS230/pythonProject/streamlitproject/carcrash.jpg"
    st.sidebar.image(image_path, use_column_width=True)

@st.cache_data
def load_data():
    path = "C:/Users/cmina/One drive-bentley/OneDrive - Bentley University/year 2/CS230/pythonProject/streamlitproject/"
    df = pd.read_csv(path + "2017_Crashes_10000_sample.csv")
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

def main():
    side_bar_image()
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

main()