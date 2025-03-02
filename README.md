
# TACOS & Profitability Dashboard

Welcome to the TACOS & Profitability Dashboard! This advanced analytics dashboard pulls data from a Google Sheet, analyzes profitability across scenarios, and predicts TACOS using machine learning.

## Features

- **Overview Tab**: Displays key financial metrics across all scenarios.
- **Graphs Tab**: Visual insights into TACOS and profitability variations.
- **Sensitivity Analysis Tab**: Adjust selling price or units sold to see changes in TACOS and profitability.
- **ML Prediction Tab**: Predict TACOS using Linear Regression based on units sold, selling price, and fixed costs.

## Setup Instructions

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/tacos-profitability-dashboard.git
    cd tacos-profitability-dashboard
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Add your Google Sheets API credentials**:
    - Place your `amazing-city1.json` file in the root directory of the project.

4. **Run the Streamlit app**:
    ```sh
    streamlit run sheetanalysis.py
    ```

## Usage

- Open the Streamlit app in your browser.
- Navigate through the tabs to explore different views and insights.
- Use the sliders in the Sensitivity Analysis tab to adjust parameters and see real-time changes.
- Use the ML Prediction tab to predict TACOS based on user inputs.

## Screenshots

### Overview Tab
![Overview Tab](images/1.png)

### Graphs Tab
![Graphs Tab](images/2.png)
![Graphs Tab](images/3.png)

### Sensitivity Analysis Tab
![Sensitivity Analysis Tab](images/4.png)

### ML Prediction Tab
![ML Prediction Tab](images/5.png)

## Contributing

Feel free to submit issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.

