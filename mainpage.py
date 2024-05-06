"""
Name:       Colin Minarik
CS230:      Section 5
Data:       Which data set you used
URL:

Description:

"""
import streamlit as st
def main_page():
    # [ST4] image for the sidebar, this function is on every file in my code
    def side_bar_image():
        image_path = "C:/Users/cmina/One drive-bentley/OneDrive - Bentley University/year 2/CS230/pythonProject/streamlitproject/carcrash.jpg"
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

def main():
    load_data_source_page()
    side_bar_image()
    # Sidebar navigation
    st.sidebar.title("Navigation")
    # Create a dictionary of your pages
    pages_dict = {
        "Home": main_page,
        "Data Source": Data_Source_Page,
        "Data Overview": data_Overview_Page
    }
    # Radio button for page selection
    selected_page = st.sidebar.radio("Select a page:", list(pages_dict.keys()))

    # Call the app function based on selection
    pages_dict[selected_page]()

main()
