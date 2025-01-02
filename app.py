import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Set page configuration to optimize layout
st.set_page_config(layout="wide")

# Custom CSS to reduce sidebar width
st.markdown(
    """
    <style>
        /* Adjust the sidebar width */
        .css-1d391kg {width: 20% !important;}
        .css-1d391kg .sidebar-content {
            width: 100% !important;
        }
        .css-1d391kg .sidebar .sidebar-header {
            padding-top: 20px;
        }

        /* Set the background color of the Streamlit app */
        .main {
            background-color: #001f3d !important;  /* Navy Blue */
        }

        /* Optional: Set background color for sidebar */
        .css-1d391kg {
            background-color: #001f3d !important;  /* Navy Blue */
        }
    </style>
    """, 
    unsafe_allow_html=True
)


# Load data from the Excel file
df = pd.read_excel('AVG FARE As at 29Dec Snap.xlsx', sheet_name='AVG_FARE', header=3)

# Dropdown options
from_city_options = df['FROM_CITY'].unique()
month_options = df['Month'].unique()
monthm_ly_options = df['MonthM_LY'].unique()

# Sidebar for filters
st.sidebar.header('Average Fare Pax Trends')
FROM_CITY = st.sidebar.selectbox('Select From City:', from_city_options)
TO_CITY = st.sidebar.selectbox('Select To City:', df[df['FROM_CITY'] == FROM_CITY]['TO_CITY'].unique())
Month = st.sidebar.selectbox('Select Month:', month_options)
st.sidebar.header('Region Wise Metrics')
MonthM_LY = st.sidebar.selectbox('Select MonthM_LY:', monthm_ly_options)
year_type = st.sidebar.selectbox("Select Year Type", ["ly", "ty"])
snap_date_name = st.sidebar.selectbox("Select Snap Date", ['29-Dec', '22-Dec', '15-Dec', '08-Dec', '01-Dec', '24-Nov', '17-Nov', '10-Nov', '03-Nov'])
month = st.sidebar.selectbox("Select Month", df['Month'].unique())

# Function for Avg Fare Graphs and Table
# Function for Avg Fare Graphs and Table with Bollinger Bands
def avg_fare(FROM_CITY, TO_CITY, Month):
    month = df[df["Month"] == Month]

    # Drop unnecessary columns
    Month_Fare = month.drop(
        [
            'SEG KEY', 'SEG KEY LY', 'MonthM_LY', 'Year', 'Month', 'Revenue_USD ', 'PAX_TY', 'PAX LY',
            "29Dec'24", "29Dec'23", "29Dec'24.", "29Dec'23.", 'Revenue_USD LY'
        ],
        axis=1
    )

    # Filter rows for the selected FROM_CITY and TO_CITY
    row = Month_Fare[(Month_Fare["FROM_CITY"] == FROM_CITY) & (Month_Fare["TO_CITY"] == TO_CITY)]
    if row.empty:
        st.warning(f"No data found for the given city pair ('{FROM_CITY}' to '{TO_CITY}').")
        return

    xorder = ['03-Nov', '10-Nov', '17-Nov', '24-Nov', '01-Dec', '08-Dec', '15-Dec', '22-Dec', '29-Dec']
    row_1 = row.iloc[0, 4:21][::2]
    row_2 = row.iloc[0, 5:22][::2]
    row_1_reversed = row_1.iloc[::-1]
    row_2_reversed = row_2.iloc[::-1]
    difference = row_1_reversed.values - row_2_reversed.values

    # Calculate Bollinger Bands for Fare Average - TY
    rolling_mean = row_1_reversed.rolling(window=3).mean()
    rolling_std = row_1_reversed.rolling(window=3).std()
    upper_band = rolling_mean + (2 * rolling_std)
    lower_band = rolling_mean - (2 * rolling_std)

    # Fare Average Graph with Bollinger Bands
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=xorder, y=row_1_reversed.values, mode='lines+markers', name="Fare Average - TY"))
    fig1.add_trace(go.Scatter(x=xorder, y=row_2_reversed.values, mode='lines+markers', name="Fare Average - LY"))
    fig1.add_trace(go.Scatter(x=xorder, y=rolling_mean, mode='lines', name="MA - TY", line=dict(dash='dot', color='orange')))
    fig1.add_trace(go.Scatter(x=xorder, y=rolling_mean, mode='lines', name="MA - LY", line=dict(dash='dot', color='yellow')))
    fig1.add_trace(go.Scatter(x=xorder, y=upper_band, mode='lines', name="Upper Bollinger Band", line=dict(color='green', dash='dash')))
    fig1.add_trace(go.Scatter(x=xorder, y=lower_band, mode='lines', name="Lower Bollinger Band", line=dict(color='red', dash='dash')))
    horizontal_value = round(row.iloc[0, 3], 2)
    fig1.add_hline(y=horizontal_value, line=dict(color='red', dash='dash'), annotation_text=f"Last Year Avg Fare: {horizontal_value}")
    fig1.update_layout(
        title=f"Behavior of Avg Fare - {FROM_CITY} to {TO_CITY}",
        xaxis_title="Snap Dates",
        yaxis_title="Average Fare (USD)",
        template="plotly_dark",
        xaxis=dict(tickvals=xorder),
        hovermode="x unified",
        height=500
    )

    # Fare Difference Graph
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=xorder, y=difference, mode='lines+markers', name="Difference (TY - LY)", line=dict(dash='dot')))
    fig2.add_hline(y=0, line=dict(color='blue', dash='dash'), annotation_text="Zero Line")
    fig2.update_layout(
        title="Difference (TY - LY)",
        xaxis_title="Snap Dates",
        yaxis_title="Difference in Fare (USD)",
        template="plotly_dark",
        xaxis=dict(tickvals=xorder),
        hovermode="x unified",
        height=500
    )

    # Display the charts side by side
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

    # Fare Data Table
    arrows = ["↑" if diff > 0 else "↓" if diff < 0 else "=" for diff in difference]
    fare_data = pd.DataFrame({
        'Date': xorder,
        'Fare Average - TY': row_1_reversed.values,
        'Fare Average - LY': row_2_reversed.values,
        'Difference (LY - TY)': difference,
        'Trend': arrows
    })

    # Display the Fare Data Table side by side with Pax Data Table
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Fare Data Table")
        st.dataframe(fare_data)

# Function for Pax Graphs and Table
def pax(FROM_CITY, TO_CITY, Month):
    month = df[df["Month"] == Month]

    # Drop unnecessary columns
    Month_Fare = month.drop(
        [
            'SEG KEY', 'SEG KEY LY', 'MonthM_LY', 'Year', 'Month', 'Revenue_USD ',
            "29Dec'24", "29Dec'23", "29Dec'24.", "29Dec'23.", 'Revenue_USD LY'
        ],
        axis=1
    )

    # Filter rows for the selected FROM_CITY and TO_CITY
    row = Month_Fare[(Month_Fare["FROM_CITY"] == FROM_CITY) & (Month_Fare["TO_CITY"] == TO_CITY)]
    if row.empty:
        st.warning(f"No data found for the given city pair ('{FROM_CITY}' to '{TO_CITY}').")
        return

    xorder = ['03-Nov', '10-Nov', '17-Nov', '24-Nov', '01-Dec', '08-Dec', '15-Dec', '22-Dec', '29-Dec']
    row_2 = row.iloc[0, 25:43][::2]
    row_1 = row.iloc[0, 24:43][::2]
    row_1_reversed = row_1.iloc[::-1]
    row_2_reversed = row_2.iloc[::-1]
    difference = row_1_reversed.values - row_2_reversed.values

    # Pax Graph
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=xorder, y=row_1_reversed.values, mode='lines+markers', name="Pax - TY"))
    fig3.add_trace(go.Scatter(x=xorder, y=row_2_reversed.values, mode='lines+markers', name="Pax - LY"))
    fig3.add_trace(go.Scatter(x=xorder, y=row_1_reversed.rolling(window=3).mean(), mode='lines', name="MA - TY", line=dict(dash='dot', color='orange')))
    fig3.add_trace(go.Scatter(x=xorder, y=row_2_reversed.rolling(window=3).mean(), mode='lines', name="MA - LY", line=dict(dash='dot', color='yellow')))
    horizontal_value = round(row.iloc[0, 4], 2)
    fig3.add_hline(y=horizontal_value, line=dict(color='red', dash='dash'), annotation_text=f"Last Year Pax Count: {horizontal_value}")
    fig3.update_layout(
        title=f"Behavior of Pax - {FROM_CITY} to {TO_CITY}",
        xaxis_title="Snap Dates",
        yaxis_title="Pax",
        template="plotly_dark",
        xaxis=dict(tickvals=xorder),
        hovermode="x unified",
        height=500
    )

    # Pax Difference Graph
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=xorder, y=difference, mode='lines+markers', name="Difference (TY - LY)", line=dict(dash='dot')))
    fig4.add_hline(y=0, line=dict(color='blue', dash='dash'), annotation_text="Zero Line")
    fig4.update_layout(
        title="Difference (TY - LY)",
        xaxis_title="Snap Dates",
        yaxis_title="Difference in Pax",
        template="plotly_dark",
        xaxis=dict(tickvals=xorder),
        hovermode="x unified",
        height=500
    )

    # Display the charts side by side
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        st.plotly_chart(fig4, use_container_width=True)

    # Pax Data Table
    arrows = ["↑" if diff > 0 else "↓" if diff < 0 else "=" for diff in difference]
    pax_data = pd.DataFrame({
        'Date': xorder,
        'Pax - TY': row_1_reversed.values,
        'Pax - LY': row_2_reversed.values,
        'Difference (LY - TY)': difference,
        'Trend': arrows
    })

    # Display the Pax Data Table side by side with Fare Data Table
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pax Data Table")
        st.dataframe(pax_data)

# Function for Pax Table Monthly LY
def pax_table_monthly(MonthM_LY):
    # Filter the dataframe by MonthM_LY
    filtered_df = df[df['MonthM_LY'] == MonthM_LY]
    
    if filtered_df.empty:
        st.warning(f"No data found for the selected MonthM_LY: {MonthM_LY}.")
    else:
        # Group and calculate metrics for the filtered data
        sum_pax = filtered_df.groupby(['Region_AI'])['PAX LY'].sum().reset_index(name='Pax')
        sum_revenue = (
            filtered_df.groupby(['Region_AI'])['Revenue_USD LY']
            .sum()
            .round(0)
            .astype(int)
            .reset_index(name='Revenue(USD)')
        )
        avg_fare = filtered_df.groupby(['Region_AI'])['LY Act Avg Fare'].mean().reset_index(name='AvgFare')

        # Merge the grouped data on Region_AI
        merged_df = sum_pax.merge(sum_revenue, on='Region_AI').merge(avg_fare, on='Region_AI')

        # Reshape the data to keep `Region_AI` as rows and metrics as columns
        final_table = merged_df

        # Display the final table below the Pax and Fare tables
        st.subheader(f"Region-wise Metrics for MonthM_LY: {MonthM_LY}")
        st.dataframe(final_table)

def generate_table_by_snap_date(year_type, snap_date_name, month):
    # Assuming fare data is between columns 18 to 34 and pax data is from column 35 onwards
    fare_columns = df.columns[17:35]  # Fare columns from 18 to 34
    pax_columns = df.columns[35:]  # Pax columns starting from 35
    # Mapping fare and pax columns to snap_dates
    snap_dates = ['29-Dec', '22-Dec', '15-Dec', '08-Dec', '01-Dec', '24-Nov', '17-Nov', '10-Nov', '03-Nov']

    # Ensure the number of fare and pax columns matches the number of snap dates
    if len(fare_columns) != len(snap_dates) * 2 or len(pax_columns) != len(snap_dates) * 2:
        st.warning("Mismatch between number of fare/pax columns and snap dates.")
        return

    # Split fare and pax columns based on the year_type ('ly' or 'ty')
    if year_type == 'ly':
        ly_fare_columns = fare_columns[::2]  # Last year fares (every other column starting from 0)
        ly_pax_columns = pax_columns[::2]  # Last year pax (every other column starting from 0)
        columns = list(zip(snap_dates, ly_fare_columns, ly_pax_columns))  # Mapping to snap_dates for LY
    elif year_type == 'ty':
        ty_fare_columns = fare_columns[1::2]  # This year fares (every other column starting from 1)
        ty_pax_columns = pax_columns[1::2]  # This year pax (every other column starting from 1)
        columns = list(zip(snap_dates, ty_fare_columns, ty_pax_columns))  # Mapping to snap_dates for TY
    else:
        st.warning("Invalid year_type. It should be 'ly' or 'ty'.")
        return

    # Ensure the snap_date_name exists in the snap_dates
    if snap_date_name not in snap_dates:
        st.warning(f"Invalid snap_date_name: {snap_date_name}. Valid options are: {', '.join(snap_dates)}.")
        return

    # Ensure the month exists
    if month not in df['Month'].unique():
        st.warning(f"Invalid month: {month}. Valid options are: {', '.join(df['Month'].unique())}.")
        return

    # Get the corresponding columns for the snap_date_name
    snap_date_index = snap_dates.index(snap_date_name)

    # Select the appropriate fare and pax columns based on snap_date_name
    selected_fare_column = columns[snap_date_index][1]  # Fare column for the selected snap date
    selected_pax_column = columns[snap_date_index][2]  # Pax column for the selected snap date

    # Filter the data for the selected month
    month_filtered_df = df[df['Month'] == month]

    # Group by 'Region_AI' and 'Month' and aggregate the data for the selected columns
    try:
        sum_pax = month_filtered_df.groupby(['Region_AI', 'Month'])[selected_pax_column].sum().reset_index(name='SumPax')
        avg_fare = month_filtered_df.groupby(['Region_AI', 'Month'])[selected_fare_column].mean().reset_index(name='AvgFare')
    except KeyError as e:
        st.warning(f"Column not found in df: {e}")
        return

    # Merge the aggregated data on 'Region_AI' and 'Month'
    result_table = sum_pax.merge(avg_fare, on=['Region_AI', 'Month'], how='left')

    # Display the final table in Streamlit
    st.write(f"Region-wise Metrics for Snap Date: {snap_date_name} and Month: {month}")
    st.dataframe(result_table)


# Handle button click to generate insights
if st.sidebar.button('Generate Insights-1'):
    try:
        # Print selected filter values for debugging
        st.write(f"FROM_CITY: {FROM_CITY}, TO_CITY: {TO_CITY}, Month: {Month}")
        
        # Generate Fare and Pax insights
        avg_fare(FROM_CITY, TO_CITY, Month)  # Generate Fare and Pax Graphs
        pax(FROM_CITY, TO_CITY, Month)       # Generate Pax Graphs and Table
if st.sidebar.button('Generate Insights-2'):
    try:
        pax_table_monthly(MonthM_LY)         # Generate Pax Table for Monthly LY
        generate_table_by_snap_date(year_type, snap_date_name, month)
    except Exception as e:
        st.error(f"Error while generating insights: {e}")
