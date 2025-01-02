import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Load data
df = pd.read_excel('AVG FARE As at 29Dec Snap.xlsx', sheet_name='AVG_FARE', header=3)

# Unique values for dropdowns
from_city_options = df['FROM_CITY'].unique()
month_options = df['Month'].unique()
month_mly_options = df['MonthM_LY'].unique()  # For filtering Pax Data Table

# Streamlit widget for filtering
FROM_CITY = st.selectbox('Select From City:', from_city_options)
TO_CITY = st.selectbox('Select To City:', df[df['FROM_CITY'] == FROM_CITY]['TO_CITY'].unique())
Month = st.selectbox('Select Month:', month_options)
MonthM_LY = st.selectbox('Select MonthM_LY for Pax Table:', month_mly_options)

# Function for Avg Fare Graphs
def avg_fare(FROM_CITY, TO_CITY, Month):
    # Filter data
    month = df[df["Month"] == Month]

    # Drop unnecessary columns
    Month_Fare = month.drop(
        [
            'SEG KEY', 'SEG KEY LY', 'MonthM_LY', 'Year', 'Month', 'Revenue_USD ', 'PAX_TY', 'PAX LY',
            "29Dec'24", "29Dec'23", "29Dec'24.", "29Dec'23.", 'Revenue_USD LY'
        ],
        axis=1
    )

    # Filter rows
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

    # Fare Average Graph
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=xorder, y=row_1_reversed.values, mode='lines+markers', name="Fare Average - TY"))
    fig1.add_trace(go.Scatter(x=xorder, y=row_2_reversed.values, mode='lines+markers', name="Fare Average - LY"))
    fig1.add_trace(go.Scatter(x=xorder, y=row_1_reversed.rolling(window=3).mean(), mode='lines', name="MA - TY", line=dict(dash='dot', color='orange')))
    fig1.add_trace(go.Scatter(x=xorder, y=row_2_reversed.rolling(window=3).mean(), mode='lines', name="MA - LY", line=dict(dash='dot', color='yellow')))
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
    st.plotly_chart(fig1, use_container_width=True)

# Function for Pax Graphs and Data Table
def pax(FROM_CITY, TO_CITY, MonthM_LY):
    filtered_df = df[df["MonthM_LY"] == MonthM_LY]
    sum_pax = filtered_df.groupby(['Region_AI'])['PAX LY'].sum().reset_index(name='Pax')
    sum_revenue = (
        filtered_df.groupby(['Region_AI'])['Revenue_USD LY']
        .sum()
        .round(0)
        .astype(int)
        .reset_index(name='Revenue(USD)')
    )
    avg_fare = filtered_df.groupby(['Region_AI'])['LY Act Avg Fare'].mean().reset_index(name='AvgFare')

    # Merge the grouped data
    pax_data = sum_pax.merge(sum_revenue, on='Region_AI').merge(avg_fare, on='Region_AI')

    st.subheader("Interactive Pax Data Table")
    st.dataframe(pax_data)

# Streamlit button to trigger both functions
if st.button('Generate Graphs and Tables'):
    avg_fare(FROM_CITY, TO_CITY, Month)
    pax(FROM_CITY, TO_CITY, MonthM_LY)
