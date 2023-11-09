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

def calculate_material_kpis(df):
    # Perform calculations for material data KPIs here
    # Example: df['Variation'] = calculate_variation(df)
    return df

# Placeholder function to plot material data analytics
# Implement the actual plotting of material data analytics
def plot_material_analytics(df):
    # Plot analytics for material data here
    # Example: st.bar_chart(df['Variation'])
    pass
# Streamlit app
# Streamlit app
def main():
    st.set_page_config(layout="wide")
    st.set_page_config(page_title="Holcim | Analytics")
    # Sidebar - Dataset and Project selection
    st.sidebar.title("Filter")
    dataset_type = st.sidebar.selectbox('Select Dataset Type', options=["Pour Data", "Material Data"])
    project_name = st.sidebar.selectbox('Select Project', options=["421 Park Drive", "BU Data Center - Holcim"])

    # Set title to project name
    st.title(project_name)

    # Determine the available year options based on project name
    if project_name == "421 Park Drive":
        selected_year = st.sidebar.selectbox('Select Year', options=[2023])
    else:
        selected_year = st.sidebar.selectbox('Select Year', options=[2020, 2021, 2022, 2023])

    load_button = st.sidebar.button('Load Data')

    # Main - Load and display data
    if load_button:
        # Determine the CSV file based on dataset type and project name
        if dataset_type == "Pour Data":
            if project_name == "421 Park Drive":
                csv_file = 'pour data_2023.csv'  # Assuming there is only one file for "421 Park Drive"
            else:
                csv_file = f'BU Data/pour {selected_year}.csv'  # Adjust the path as needed
            
            # Load pour data
            df = pd.read_csv(csv_file)
            
            # Calculate and display pour data KPIs
            kpi_df = calculate_kpis(df)
            kpi_pairs = [
                ('Total Loading Time', 'Total Travel Time to Site'),
                ('Onsite Wait Time', 'Average Speed of Pour')
            ]
            for kpi1, kpi2 in kpi_pairs:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f'{kpi1} (minutes)')
                    plot_histogram(col1, kpi_df[kpi1], kpi1)
                with col2:
                    st.subheader(f'{kpi2} (minutes/quantity)' if 'Pour' in kpi2 else f'{kpi2} (minutes)')
                    plot_histogram(col2, kpi_df[kpi2], kpi2)

        elif dataset_type == "Material Data":
            # Assuming material data files follow a similar naming convention
            if project_name == "421 Park Drive":
                csv_file = 'materials_data_2023.csv'  # Update with actual file path
            else:
                csv_file = f'BU Data/materials{selected_year}.csv'  # Update with actual file path
            
            # Load material data
            df = pd.read_csv(csv_file)
            
            # Calculate and display material data KPIs
            material_kpi_df = calculate_material_kpis(df)
            # Implement the function to display material data analytics
            plot_material_analytics(material_kpi_df)

if __name__ == "__main__":
    main()