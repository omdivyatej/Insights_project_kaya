import streamlit as st
import pandas as pd
import numpy as np

# Function to calculate time differences for KPIs
def calculate_kpis(df):
    # Convert timestamps into datetime objects and calculate durations
    time_columns = [
        'payload_event_batch_start_time', 'payload_event_batch_end_time',
        'payload_event_departure_time', 'payload_event_arrival_time',
        'payload_event_pouring_start_time', 'payload_event_pouring_finish_time'
    ]
    for col in time_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Calculate KPIs
    df['Total Loading Time'] = (df['payload_event_batch_end_time'] - df['payload_event_batch_start_time']).dt.total_seconds() / 60
    df['Total Travel Time to Site'] = (df['payload_event_arrival_time'] - df['payload_event_departure_time']).dt.total_seconds() / 60
    df['Onsite Wait Time'] = (df['payload_event_pouring_start_time'] - df['payload_event_arrival_time']).dt.total_seconds() / 60
    df['Total Pour Time'] = (df['payload_event_pouring_finish_time'] - df['payload_event_pouring_start_time']).dt.total_seconds() / 60
    
    # Assuming that pour time is not available if 'payload_event_pouring_finish_time' is NaT
    df['Average Speed of Pour'] = np.where(df['Total Pour Time'] > 0, df['quantity'] / df['Total Pour Time'], 0)
    
    return df

# Function to plot a histogram in a given column
def plot_histogram(column, series, title, bins=20):
    # Create histogram data with rounded bins and counts
    count, bin_edges = np.histogram(series.dropna(), bins=bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_centers = np.round(bin_centers).astype(int)
    count = np.round(count).astype(int)
    
    # Create a DataFrame with rounded data
    hist_df = pd.DataFrame({
        title: bin_centers,
        'Count': count
    })
    
    # Plotting in the specified column with whole number labels
    column.bar_chart(hist_df.set_index(title))

# Streamlit app
def main():
    # Set wide mode layout
    st.set_page_config(layout="wide")

    

    # Sidebar - Project selection
    st.sidebar.title("Filter")
    project_name = st.sidebar.selectbox('Select Project', options=["421 Park Drive", "BU Data Center - Holcim"])
    st.title(project_name)
    # Project-specific year options
    if project_name == "421 Park Drive":
        selected_year = st.sidebar.selectbox('Select Year', options=[2023])
    else:  # BU data center
        selected_year = st.sidebar.selectbox('Select Year', options=[2020, 2021, 2022, 2023])

    load_button = st.sidebar.button('Load Data')

    # Main - Load and display data
    if load_button:
        if project_name == "421 Park view":
            csv_file = 'pour data_2023.csv'  # Assuming there is only one file for "421 Park view"
        else:
            csv_file = f'BU Data/pour {selected_year}.csv'  # Assuming files are named like 'BU_data_center_2020.csv', etc.

        # Load data
        df = pd.read_csv(csv_file)
        
        # Calculate KPIs
        kpi_df = calculate_kpis(df)
        
        # Define KPIs to plot
        kpi_pairs = [
            ('Total Loading Time', 'Total Travel Time to Site'),
            ('Onsite Wait Time', 'Average Speed of Pour')
        ]
        
        # Display histograms using Streamlit's native chart functions
        for kpi1, kpi2 in kpi_pairs:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f'{kpi1} (minutes)')
                plot_histogram(col1, kpi_df[kpi1], kpi1)
            with col2:
                st.subheader(f'{kpi2} (minutes/quantity)' if 'Pour' in kpi2 else f'{kpi2} (minutes)')
                plot_histogram(col2, kpi_df[kpi2], kpi2)

if __name__ == "__main__":
    main()
