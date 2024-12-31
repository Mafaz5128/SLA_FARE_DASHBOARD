import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def avg_fare(FROM_CITY, TO_CITY, Month):
    # Load data
    df = pd.read_excel('/content/AVG FARE As at 29Dec Snap.xlsx', sheet_name='AVG_FARE', header=3)
    
    # Filter the data based on the provided month
    month = df[df["Month"] == Month]
    
    # Drop unnecessary columns
    Month_Fare = month.drop([ 
        'SEG KEY', 'SEG KEY LY', 'MonthM_LY', 'Year', 'Month', 'Revenue_USD ', 'PAX_TY', 'PAX LY',
        "29Dec'24", "29Dec'23", "29Dec'24.", "29Dec'23.", 'Revenue_USD LY'
    ], axis=1)

    # Drop columns 22 to 40
    Month_Fare.drop(Month_Fare.columns[22:40], axis=1, inplace=True)
    
    # Filter rows based on 'FROM_CITY' or 'TO_CITY'
    if FROM_CITY:
        row = Month_Fare[Month_Fare["FROM_CITY"] == FROM_CITY]
    elif TO_CITY:
        row = Month_Fare[Month_Fare["TO_CITY"] == TO_CITY]
    else:
        raise ValueError("Either 'FROM_CITY' or 'TO_CITY' must be specified.")
    
    # If no rows match the filter, raise an error
    if row.empty:
        raise ValueError(f"No data found for the given city location. Please check the 'FROM_CITY' or 'TO_CITY'.")

    # Select data for the first and second lines from the row
    xorder = ['03-Nov', '10-Nov', '17-Nov', '24-Nov', '01-Dec', '08-Dec', '15-Dec', '22-Dec', '29-Dec']

    # Select values for plotting
    row_1 = row.iloc[0, 4:21][::2]  # Line 1: Every second column starting at index 4
    row_2 = row.iloc[0, 5:22][::2]  # Line 2: Every second column starting at index 5

    # Reverse the rows to match the new order
    row_1_reversed = row_1.iloc[::-1]  # Reverse the order of the row_1
    row_2_reversed = row_2.iloc[::-1]  # Reverse the order of the row_2

    # Plot the time series
    plt.figure(figsize=(12, 6))

    # Plot the first line
    plt.plot(xorder, row_1_reversed.values, marker='o', label="Fare Average - TY")

    # Plot the second line
    plt.plot(xorder, row_2_reversed.values, marker='s', label="Fare Average - LY")

    # Add a horizontal line at the value of the selected row (e.g., index 0, column 3)
    horizontal_value = row.iloc[0, 3]  # Get the value from the specified cell
    plt.axhline(y=horizontal_value, color='r', linestyle='--', label=f"Last Year Actual Avg Fare at {horizontal_value}")

    # Set the custom X-axis order
    plt.xticks(xorder, rotation=45, ha='right')  # Apply custom order and rotate labels

    # Add labels and title
    plt.xlabel("Snap Dates")
    plt.ylabel("Average Fare (USD)")
    plt.title(f"Behavior of Avg Fare -  {FROM_CITY} to {TO_CITY}")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()

    # Display plot
    st.pyplot(plt)

# Streamlit dashboard code
def main():
    st.title('Average Fare Behavior Dashboard')

    # Load data for dropdowns
    df = pd.read_excel('/content/AVG FARE As at 29Dec Snap.xlsx', sheet_name='AVG_FARE', header=3)

    # Unique values for dropdowns
    from_city_options = df['FROM_CITY'].unique()
    to_city_options = df['TO_CITY'].unique()
    month_options = df['Month'].unique()

    # Streamlit widgets for selecting values
    FROM_CITY = st.selectbox('Select From City:', from_city_options)
    TO_CITY = st.selectbox('Select To City:', to_city_options)
    Month = st.selectbox('Select Month:', month_options)

    # Call the avg_fare function when the user selects options
    if st.button('Generate Fare Graph'):
        avg_fare(FROM_CITY, TO_CITY, Month)

# Run the Streamlit app
if __name__ == '__main__':
    main()
