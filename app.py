import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import matplotlib.pyplot as plt

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

# Function for plotting Fare Graphs
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

    row_1 = row.iloc[0, 4:21][::2]  # Line 1: Every second column starting at index 4
    row_2 = row.iloc[0, 5:22][::2]  # Line 2: Every second column starting at index 5

    # Reverse the rows to match the new order
    row_1_reversed = row_1.iloc[::-1]
    row_2_reversed = row_2.iloc[::-1]

    # Calculate the difference (LY - TY)
    difference = row_2_reversed.values - row_1_reversed.values

    # Plot using Plotly for Fare Average graph
    fig1 = go.Figure()

    # Line for "Fare Average - TY"
    fig1.add_trace(go.Scatter(x=xorder, y=row_1_reversed.values, mode='lines+markers', name="Fare Average - TY"))

    # Line for "Fare Average - LY"
    fig1.add_trace(go.Scatter(x=xorder, y=row_2_reversed.values, mode='lines+markers', name="Fare Average - LY"))

    # Plotting the Moving Average (MA) for TY and LY
    fig1.add_trace(go.Scatter(x=xorder, y=row_1_reversed.rolling(window=3).mean(), mode='lines', name="MA - TY", line=dict(dash='dot', color='orange')))
    fig1.add_trace(go.Scatter(x=xorder, y=row_2_reversed.rolling(window=3).mean(), mode='lines', name="MA - LY", line=dict(dash='dot', color='yellow')))

    # Add a horizontal line at the value of the selected row (e.g., index 0, column 3)
    horizontal_value = row.iloc[0, 3]
    fig1.add_hline(y=horizontal_value, line=dict(color='red', dash='dash'), annotation_text=f"Last Year Actual Avg Fare at {horizontal_value}")

    # Update layout for the first figure (Fare averages graph)
    fig1.update_layout(
        title=f"Behavior of Avg Fare - {FROM_CITY} to {TO_CITY}",
        xaxis_title="Snap Dates",
        yaxis_title="Average Fare (USD)",
        template="plotly_dark",
        xaxis=dict(tickvals=xorder),
        hovermode="x unified",
        height=500
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
        template="plotly_dark",
        xaxis=dict(tickvals=xorder),
        hovermode="x unified",
        height=500
    )

    # Display the second graph (Difference graph)
    st.plotly_chart(fig2, use_container_width=True)

    # Display data in an interactive table
    fare_data = pd.DataFrame({
        'Date': xorder,
        'Fare Average - TY': row_1_reversed.values,
        'Fare Average - LY': row_2_reversed.values,
        'Difference (LY - TY)': difference
    })

    st.subheader("Fare Data Table")
    st.dataframe(fare_data)

# Function for plotting Pax Count Graphs
def pax(FROM_CITY, TO_CITY, Month):
    # Load data
    df = pd.read_excel('AVG FARE As at 29Dec Snap.xlsx', sheet_name='AVG_FARE', header=3)

    # Filter the data based on the provided month
    month = df[df["Month"] == Month]

    # Drop unnecessary columns
    Month_Fare = month.drop([
        'SEG KEY', 'SEG KEY LY', 'MonthM_LY', 'Year', 'Month', 'Revenue_USD ',
        "29Dec'24", "29Dec'23", "29Dec'24.", "29Dec'23.", 'Revenue_USD LY'
    ], axis=1)

    first_six_columns = Month_Fare.iloc[:, :6]
    last_eighteen_columns = Month_Fare.iloc[:, -18:]

    # Combine the selected columns
    Month_Fare_combined = pd.concat([first_six_columns, last_eighteen_columns], axis=1)

    # Filter rows based on 'FROM_CITY' and 'TO_CITY'
    if FROM_CITY and TO_CITY:
        row = Month_Fare_combined[(Month_Fare_combined["FROM_CITY"] == FROM_CITY) & (Month_Fare_combined["TO_CITY"] == TO_CITY)]
    else:
        raise ValueError("Both 'FROM_CITY' and 'TO_CITY' must be specified.")

    # If no rows match the filter, raise an error
    if row.empty:
        raise ValueError(f"No data found for the given city pair ('{FROM_CITY}' to '{TO_CITY}').")

    # Select data for the first and second lines from the row
    xorder = ['03-Nov', '10-Nov', '17-Nov', '24-Nov', '01-Dec', '08-Dec', '15-Dec', '22-Dec', '29-Dec']

    row_1 = row.iloc[0, 6:24][::2]  # Line 1: Every second column starting at index 6
    row_2 = row.iloc[0, 7:25][::2]  # Line 2: Every second column starting at index 7

    # Reverse the rows to match the new order
    row_1_reversed = row_1.iloc[::-1]
    row_2_reversed = row_2.iloc[::-1]

    # Plot the time series for Pax count
    plt.figure(figsize=(12, 6))

    # Plot the first line (TY)
    plt.plot(xorder, row_1_reversed.values, marker='o', label="Pax Count - TY")

    # Plot the second line (LY)
    plt.plot(xorder, row_2_reversed.values, marker='s', label="Pax Count - LY")

    # Add a horizontal line at the value of the selected row (e.g., index 0, column 3)
    horizontal_value = row.iloc[0, 3]
    plt.axhline(y=horizontal_value, color='r', linestyle='--', label=f"Last Year Actual Avg Pax count {horizontal_value}")

    # Set the custom X-axis order
    plt.xticks(xorder, rotation=45, ha='right')  # Apply custom order and rotate labels

    # Add labels and title
    plt.xlabel("Snap Dates")
    plt.ylabel("Pax Count")
    plt.title(f"Behavior of Pax Count -  {FROM_CITY} to {TO_CITY}")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()

    # Show the plot
    plt.show()

# Streamlit Interface
st.title("Fare and Pax Count Dashboard")

# Dropdowns for selecting cities and month
FROM_CITY = st.selectbox("Select Departure City", ['City1', 'City2', 'City3'])
TO_CITY = st.selectbox("Select Arrival City", ['City1', 'City2', 'City3'])

Month = st.selectbox("Select Month", ['Nov', 'Dec'])

# Show Fare Chart and Pax Count based on user selection
if st.button("Generate Report"):
    try:
        avg_fare(FROM_CITY, TO_CITY, Month)
        pax(FROM_CITY, TO_CITY, Month)
    except ValueError as e:
        st.error(str(e))
