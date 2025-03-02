import streamlit as st
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_file_path = os.path.join(os.getcwd(), "amazing-city.json")
creds = ServiceAccountCredentials.from_json_keyfile_name(json_file_path, scope)
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Streamlit app title and intro
st.title("TACOS & Profitability Dashboard")
st.write("""
Welcome to your advanced analytics dashboard! This app pulls data from your Google Sheet, analyzes profitability across scenarios, 
and even predicts TACOS using machine learning. Explore the tabs below for insights, graphs, and predictions!
""")

# --- Connect to Google Sheet ---
try:
    client = gspread.authorize(creds)
    sheet = client.open("DT project").sheet1
    data = sheet.get_all_values()
except Exception as e:
    logging.error("Error connecting to Google Sheets: %s", e)

# Convert to DataFrame
df = pd.DataFrame(data[1:], columns=data[0])

# Clean the data
def clean_numeric(value):
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '')
        try:
            return float(value)
        except ValueError:
            return np.nan
    return value

numeric_cols = ['Selling Price per Unit', 'Units Sold', 'Fixed Costs', 'Loan Interest', 
                'Revenue', 'TACOS', 'Profit Before Tax', 'Profit After Tax']
for col in df.columns[1:]:
    df[col] = df[col].apply(clean_numeric)

df.loc[df['Parameter'] == 'Tax Rate', df.columns[1:]] = (
    df.loc[df['Parameter'] == 'Tax Rate', df.columns[1:]].astype(float) * 100
)

# Transpose for scenario-based analysis
df_t = df.set_index('Parameter').T.reset_index()
df_t.columns.name = None
df_t = df_t.rename(columns={'index': 'Scenario'})
df_t['TACOS'] = df_t['TACOS'].fillna(0)

# Calculate additional metrics
df_t['Profit Margin (%)'] = (df_t['Profit Before Tax'] / df_t['Revenue']) * 100
df_t['TACOS Percentage'] = (df_t['TACOS'] / df_t['Revenue']) * 100
df_t['Break Even Units'] = (df_t['Fixed Costs'] + df_t['Loan Interest'] + df_t['TACOS']) / df_t['Selling Price per Unit']

# --- Tabs for Different Views ---
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Graphs", "Sensitivity Analysis", "ML Prediction"])

# --- Tab 1: Overview ---
with tab1:
    st.header("Scenario Overview")
    st.write("""
    This table shows key financial metrics across all scenarios. 
    - **Revenue**: Total sales income.
    - **TACOS**: Total Advertising Cost of Sales (max allowed for breakeven).
    - **Profit Before Tax (PBT)**: Revenue minus all costs.
    - **Profit Margin**: PBT as a percentage of Revenue.
    - **TACOS Percentage**: TACOS as a percentage of Revenue.
    """)
    st.dataframe(df_t[['Scenario', 'Revenue', 'TACOS', 'Profit Before Tax', 'Profit After Tax', 
                       'Profit Margin (%)', 'TACOS Percentage']], use_container_width=True)

    st.subheader("Key Insights")
    optimal = df_t[df_t['Profit Before Tax'] >= 0].sort_values(by='Revenue', ascending=False).iloc[0]
    st.write(f"**Best Scenario**: {optimal['Scenario']} with Revenue = ${optimal['Revenue']:,.2f} and TACOS = ${optimal['TACOS']:,.2f}")

# --- Tab 2: Graphs ---
with tab2:
    st.header("Visual Insights")
    st.write("Explore how TACOS and profitability vary across scenarios.")

    # Bar plot for TACOS and Revenue
    fig1 = px.bar(df_t, x='Scenario', y=['TACOS', 'Revenue'], barmode='group', 
                  title="TACOS vs Revenue Across Scenarios",
                  labels={'value': 'Amount ($)', 'variable': 'Metric'})
    st.plotly_chart(fig1)

    # Line plot for Profit Margin and TACOS Percentage
    fig2 = px.line(df_t, x='Scenario', y=['Profit Margin (%)', 'TACOS Percentage'], 
                   title="Profit Margin vs TACOS Percentage",
                   labels={'value': 'Percentage (%)', 'variable': 'Metric'})
    st.plotly_chart(fig2)

# --- Tab 3: Sensitivity Analysis ---
with tab3:
    st.header("Sensitivity Analysis")
    st.write("""
    Adjust Selling Price or Units Sold to see how TACOS and profitability change in the Base Case.
    """)
    
    price_slider = st.slider("Selling Price per Unit", 1.0, 50.0, 5.50, step=0.5)
    units_slider = st.slider("Units Sold", 1000, 10000, 5000, step=100)

    # Recalculate for Base Case
    base_case = df_t[df_t['Scenario'] == 'Base Case'].copy()
    base_case['Selling Price per Unit'] = price_slider
    base_case['Units Sold'] = units_slider
    base_case['Revenue'] = base_case['Selling Price per Unit'] * base_case['Units Sold']
    base_case['Profit Before Tax'] = (base_case['Revenue'] - base_case['Fixed Costs'] - 
                                      base_case['Loan Interest'] - base_case['TACOS'])
    base_case['Profit After Tax'] = base_case['Profit Before Tax'] * (1 - base_case['Tax Rate'] / 100)
    base_case['Profit Margin (%)'] = (base_case['Profit Before Tax'] / base_case['Revenue']) * 100

    st.write("Adjusted Base Case:")
    st.dataframe(base_case[['Scenario', 'Revenue', 'TACOS', 'Profit Before Tax', 'Profit After Tax', 
                            'Profit Margin (%)']])

# --- Tab 4: ML Prediction ---
with tab4:
    st.header("TACOS Prediction with Machine Learning")
    st.write("""
    Using Linear Regression, we predict TACOS based on Units Sold, Selling Price, and Fixed Costs.
    """)
    
    # Prepare data for ML
    X = df_t[['Units Sold', 'Selling Price per Unit', 'Fixed Costs']].astype(float)
    y = df_t['TACOS'].astype(float)
    
    # Split and train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Predict and evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    st.write(f"Model Mean Squared Error: {mse:,.2f}")

    # User input for prediction
    st.subheader("Predict TACOS")
    pred_units = st.number_input("Units Sold", 1000, 10000, 5000)
    pred_price = st.number_input("Selling Price per Unit", 1.0, 50.0, 5.50)
    pred_fixed = st.number_input("Fixed Costs", 5000, 20000, 10000)
    
    pred_input = np.array([[pred_units, pred_price, pred_fixed]])
    pred_tacos = model.predict(pred_input)[0]
    st.write(f"Predicted TACOS: ${pred_tacos:,.2f}")

    # Plot actual vs predicted
    fig3 = px.scatter(x=y_test, y=y_pred, labels={'x': 'Actual TACOS', 'y': 'Predicted TACOS'},
                      title="Actual vs Predicted TACOS")
    fig3.add_shape(type="line", x0=min(y_test), y0=min(y_test), x1=max(y_test), y1=max(y_test), 
                   line=dict(color="Red", dash="dash"))
    st.plotly_chart(fig3)

# Run instructions
st.sidebar.write("To run locally: `streamlit run app.py`")
