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
def plot_histogram(column, series, title, bins=20,description=""):
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
    column.subheader(title)
    column.caption(description)  # Description below the title
    column.bar_chart(hist_df.set_index(title))
    # Plotting in the specified column with whole number labels
    
# Function to calculate KPIs for material data
def calculate_material_kpis(df):
    # Calculate the absolute variation
    df['Absolute Variation'] = df['batched_qty'] - df['required_qty']
    # Calculate the percentage variation based on required quantity
    df['Variation (%)'] = (df['Absolute Variation'] / df['required_qty']) * 100
    
    return df

def plot_material_analytics(df):
    # Plotting comparison of Design, Required, and Batched Quantities
    # We'll consider significant variations for visualization
    
    # Calculate summary statistics
    total_required = df['required_qty'].sum()
    total_batched = df['batched_qty'].sum()
    total_variation = df['Absolute Variation'].sum()
    avg_variation = df['Absolute Variation'].mean()

    # Define the HTML template for the metric display
    metric_template = """
    <div style="padding: 10px; margin: 10px 0; border: 1px solid transparent; border-radius: 5px; text-align: center;">
        <span style="font-size: 0.85em; color: grey;">{label}</span><br>
        <span style="font-size: 2.5em; font-weight: bold;">{value}</span>
    </div>
    """

    # Create two columns for the metrics with custom HTML formatting
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(metric_template.format(label="Total Required Quantity", value=f"{total_required:,.2f}"), unsafe_allow_html=True)
        st.markdown(metric_template.format(label="Total Batched Quantity", value=f"{total_batched:,.2f}"), unsafe_allow_html=True)

    with col2:
        st.markdown(metric_template.format(label="Total Variation", value=f"{total_variation:,.2f}"), unsafe_allow_html=True)
        st.markdown(metric_template.format(label="Average Variation", value=f"{avg_variation:,.2f}"), unsafe_allow_html=True)

    st.divider()

    st.subheader('Significant Discrepancies in Batched vs Required Quantity')
    st.caption("Displays rows where the batched quantity significantly differs from what was required.")  
    significant_variation_df = df[df['Absolute Variation'].abs() > 10]  # adjust the threshold as needed
    
    if not significant_variation_df.empty:
        st.dataframe(significant_variation_df[['material', 'required_qty', 'batched_qty', 'Absolute Variation']])
    else:
        st.write("No significant discrepancies found")
# Streamlit app
# Streamlit app
def main():
    st.set_page_config(layout="wide",page_title="Holicim | Analytics")
   
    # Sidebar - Dataset and Project selection
    st.sidebar.title("Filter")
    dataset_type = st.sidebar.selectbox('Select Dataset Type', options=["Pour Data", "Material Data"])
    project_name = st.sidebar.selectbox('Select Project', options=["421 Park Drive", "BU Data Center - Holcim"])

    # Set title to project name
    st.title(project_name)
    st.divider()
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
            # Add descriptions for each KPI
            descriptions = {
                'Total Loading Time': "This graph shows the frequency of different loading times in minutes.",
                'Total Travel Time to Site': "This graph displays how long it took for trucks to travel to the site.",
                'Onsite Wait Time': "This graph represents the time trucks spent waiting on-site before pouring.",
                'Average Speed of Pour': "This graph indicates the average speed of pouring concrete."
            }
            # Calculate and display pour data KPIs
            kpi_df = calculate_kpis(df)
            kpi_pairs = [
                ('Total Loading Time', 'Total Travel Time to Site'),
                ('Onsite Wait Time', 'Average Speed of Pour')
            ]
            for kpi1, kpi2 in kpi_pairs:
                col1, col2 = st.columns(2)
                with col1:
                    plot_histogram(col1, kpi_df[kpi1], kpi1, description=descriptions[kpi1])
                with col2:
                    plot_histogram(col2, kpi_df[kpi2], kpi2, description=descriptions.get(kpi2, ""))


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