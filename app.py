import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Load data for dropdowns
df = pd.read_excel('AVG FARE As at 29Dec Snap.xlsx', sheet_name='AVG_FARE', header=3)

# Unique values for dropdowns
from_city_options = df['FROM_CITY'].unique()
month_options = df['Month'].unique()

# Streamlit widget for selecting 'From City'
FROM_CITY = st.selectbox('Select From City:', from_city_options)

# Filter 'TO_CITY' options based on 'FROM_CITY'
to_city_options = df[df['FROM_CITY'] == FROM_CITY]['TO_CITY'].unique()

# Streamlit widget for selecting 'To City'
TO_CITY = st.selectbox('Select To City:', to_city_options)

# Streamlit widget for selecting the month
Month = st.selectbox('Select Month:', month_options)

def add_trend_indicators(dataframe, diff_column):
    """Add a trend indicator (arrow) for a given difference column."""
    dataframe['Trend'] = dataframe[diff_column].apply(
        lambda x: '⬆️' if x > 0 else ('⬇️' if x < 0 else '➡️')
    )
    dataframe[diff_column] = dataframe[diff_column].astype(str) + " " + dataframe['Trend']
    return dataframe.drop(columns=['Trend'])

def avg_fare(FROM_CITY, TO_CITY, Month):
    # Filter data based on the provided month
    month = df[df["Month"] == Month]
    
    # Drop unnecessary columns
    Month_Fare = month.drop([ 
        'SEG KEY', 'SEG KEY LY', 'MonthM_LY', 'Year', 'Month', 'Revenue_USD ', 'PAX_TY', 'PAX LY',
        "29Dec'24", "29Dec'23", "29Dec'24.", "29Dec'23.", 'Revenue_USD LY'
    ], axis=1)

    # Filter rows based on both 'FROM_CITY' and 'TO_CITY'
    row = Month_Fare[(Month_Fare["FROM_CITY"] == FROM_CITY) & (Month_Fare["TO_CITY"] == TO_CITY)]

    if row.empty:
        st.warning(f"No data found for the given city pair ('{FROM_CITY}' to '{TO_CITY}'). Please check the cities.")
        return

    # Select data for plotting
    xorder = ['03-Nov', '10-Nov', '17-Nov', '24-Nov', '01-Dec', '08-Dec', '15-Dec', '22-Dec', '29-Dec']
    row_1 = row.iloc[0, 4:21][::2]  # Line 1: Every second column starting at index 4
    row_2 = row.iloc[0, 5:22][::2]  # Line 2: Every second column starting at index 5

    # Reverse the rows to match the new order
    row_1_reversed = row_1.iloc[::-1]  # Reverse the order of the row_1
    row_2_reversed = row_2.iloc[::-1]  # Reverse the order of the row_2

    # Calculate the difference (LY - TY)
    difference = row_2_reversed.values - row_1_reversed.values

    # Plot using Plotly for Fare Average graph
    fig1 = go.Figure()

    # Line for "Fare Average - TY"
    fig1.add_trace(go.Scatter(x=xorder, y=row_1_reversed.values, mode='lines+markers', name="Fare Average - TY"))

    # Line for "Fare Average - LY"
    fig1.add_trace(go.Scatter(x=xorder, y=row_2_reversed.values, mode='lines+markers', name="Fare Average - LY"))

    # Add horizontal line for LY Actual Avg Fare
    fig1.add_hline(y=row.iloc[0, 3], line=dict(color='red', dash='dash'), annotation_text="Last Year Avg Fare")

    # Update layout for the first figure
    fig1.update_layout(
        title=f"Behavior of Avg Fare - {FROM_CITY} to {TO_CITY}",
        xaxis_title="Snap Dates",
        yaxis_title="Average Fare (USD)",
        template="plotly_dark",
        hovermode="x unified"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # Plot the difference graph
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=xorder, y=difference, mode='lines+markers', name="Difference (LY - TY)", line=dict(dash='dot')))
    fig2.add_hline(y=0, line=dict(color='blue', dash='dash'), annotation_text="Zero Line")
    fig2.update_layout(
        title="Difference (LY - TY)",
        xaxis_title="Snap Dates",
        yaxis_title="Difference in Fare (USD)",
        template="plotly_dark",
        hovermode="x unified"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Fare Data Table with trend indicators
    fare_data = pd.DataFrame({
        'Date': xorder,
        'Fare Average - TY': row_1_reversed.values,
        'Fare Average - LY': row_2_reversed.values,
        'Difference (LY - TY)': difference
    })
    fare_data = add_trend_indicators(fare_data, 'Difference (LY - TY)')
    st.subheader("Fare Data Table")
    st.dataframe(fare_data)

def pax(FROM_CITY, TO_CITY, Month):
    # Similar logic for Pax data...
    # Add indicators as needed for the Pax table.

    st.warning("Pax function implementation follows a similar logic.")

# Trigger functions
if st.button('Generate Fare and Pax Graphs'):
    avg_fare(FROM_CITY, TO_CITY, Month)
    pax(FROM_CITY, TO_CITY, Month)
