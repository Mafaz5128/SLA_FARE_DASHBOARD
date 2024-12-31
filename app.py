import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Apply custom CSS to adjust the layout
st.markdown(
    """
    <style>
    .reportview-container {
        width: 100%;
        max-width: 100%;
        margin: 0;
    }
    .block-container {
        padding: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def avg_fare(FROM_CITY, TO_CITY, Month):
    # Load data
    df = pd.read_excel('AVG FARE As at 29Dec Snap.xlsx', sheet_name='AVG_FARE', header=3)
    
    # Filter the data based on the provided month
    month = df[df["Month"] == Month]
    
    # Drop unnecessary columns
    Month_Fare = month.drop([ 
        'SEG KEY', 'SEG KEY LY', 'MonthM_LY', 'Year', 'Month', 'Revenue_USD ', 'PAX_TY', 'PAX LY',
        "29Dec'24", "29Dec'23", "29Dec'24.", "29Dec'23.", 'Revenue_USD LY'
    ], axis=1)

    # Drop columns 22 to 40
    Month_Fare.drop(Month_Fare.columns[22:40], axis=1, inplace=True)
    
    # Filter rows based on both 'FROM_CITY' and 'TO_CITY'
    if FROM_CITY and TO_CITY:
        row = Month_Fare[(Month_Fare["FROM_CITY"] == FROM_CITY) & (Month_Fare["TO_CITY"] == TO_CITY)]
    else:
        raise ValueError("Both 'FROM_CITY' and 'TO_CITY' must be specified.")
    
    # If no rows match the filter, raise an error
    if row.empty:
        raise ValueError(f"No data found for the given city pair ('{FROM_CITY}' to '{TO_CITY}'). Please check the cities.")

    # Select data for the first and second lines from the row
    xorder = ['03-Nov', '10-Nov', '17-Nov', '24-Nov', '01-Dec', '08-Dec', '15-Dec', '22-Dec', '29-Dec']

    # Select values for plotting
    row_1 = row.iloc[0, 4:21][::2]  # Line 1: Every second column starting at index 4
    row_2 = row.iloc[0, 5:22][::2]  # Line 2: Every second column starting at index 5

    # Reverse the rows to match the new order
    row_1_reversed = row_1.iloc[::-1]  # Reverse the order of the row_1
    row_2_reversed = row_2.iloc[::-1]  # Reverse the order of the row_2

    # Calculate the difference (LY - TY)
    difference = row_2_reversed.values - row_1_reversed.values

    # Determine the indicator (up or down)
    indicator = ['⬆️' if diff > 0 else '⬇️' for diff in difference]

    # Moving Average (3-point moving average)
    ma_window = 3
    row_1_ma = row_1_reversed.rolling(window=ma_window).mean()
    row_2_ma = row_2_reversed.rolling(window=ma_window).mean()

    # Plot using Plotly for Fare Average graph
    fig1 = go.Figure()

    # Line for "Fare Average - TY"
    fig1.add_trace(go.Scatter(x=xorder, y=row_1_reversed.values, mode='lines+markers', name="Fare Average - TY"))

    # Line for "Fare Average - LY"
    fig1.add_trace(go.Scatter(x=xorder, y=row_2_reversed.values, mode='lines+markers', name="Fare Average - LY"))

    # Plotting the Moving Average (MA) for TY and LY
    fig1.add_trace(go.Scatter(x=xorder, y=row_1_ma, mode='lines', name="MA - TY", line=dict(dash='dot', color='orange')))
    fig1.add_trace(go.Scatter(x=xorder, y=row_2_ma, mode='lines', name="MA - LY", line=dict(dash='dot', color='yellow')))

    # Add a horizontal line at the value of the selected row (e.g., index 0, column 3)
    horizontal_value = row.iloc[0, 3]  # Get the value from the specified cell
    fig1.add_hline(y=horizontal_value, line=dict(color='red', dash='dash'), annotation_text=f"Last Year Actual Avg Fare at {horizontal_value}")

    # Update layout for the first figure (Fare averages graph)
    fig1.update_layout(
        title=f"Behavior of Avg Fare - {FROM_CITY} to {TO_CITY}",
        xaxis_title="Snap Dates",
        yaxis_title="Average Fare (USD)",
        legend_title="Legend",
        template="plotly_dark",
        xaxis=dict(tickvals=xorder),
        hovermode="x unified",
        height=500,  # Height remains the same
        width=None   # Let Streamlit handle the width automatically
    )

    # Display the first graph (Fare Average graph)
    st.plotly_chart(fig1, use_container_width=True)

    # Plot the difference graph (LY - TY) separately
    fig2 = go.Figure()

    # Add a line for the difference (LY - TY)
    fig2.add_trace(go.Scatter(x=xorder, y=difference, mode='lines+markers', name="Difference (LY - TY)", line=dict(dash='dot')))

    # Add a horizontal line at y=0 to indicate the zero baseline
    fig2.add_hline(y=0, line=dict(color='blue', dash='dash'), annotation_text="Zero Line", line_width=2)

    # Update layout for the second figure (Difference graph)
    fig2.update_layout(
        title="Difference (LY - TY)",
        xaxis_title="Snap Dates",
        yaxis_title="Difference in Fare (USD)",
        legend_title="Legend",
        template="plotly_dark",
        xaxis=dict(tickvals=xorder),
        hovermode="x unified",
        height=500,  # Height remains the same
        width=None   # Let Streamlit handle the width automatically
    )

    # Display the second graph (Difference graph)
    st.plotly_chart(fig2, use_container_width=True)

    # Display data in an interactive table
    st.subheader("Fare Data Table")
    fare_data = pd.DataFrame({
        'Date': xorder,
        'Fare Average - TY': row_1_reversed.values,
        'Fare Average - LY': row_2_reversed.values,
        'Difference (LY - TY)': difference,
        'Indicator': indicator
    })
    
    # Display the dataframe in an interactive table
    st.dataframe(fare_data)

# Streamlit dashboard code
def main():
    st.title('Average Fare Behavior Dashboard')

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

    # Call the avg_fare function when the user selects options
    if st.button('Generate Fare Graph'):
        avg_fare(FROM_CITY, TO_CITY, Month)

# Run the Streamlit app
if __name__ == '__main__':
    main()
