
# Airline Operations & Customer Experience Analytics

## Project Overview
An interactive business intelligence project analyzing airline operational performance, flight delays, cancellations, diversions, and passenger satisfaction using Python and Streamlit.

## Business Problem
Airlines need to improve schedule reliability and customer satisfaction while identifying operational issues that contribute to delays and cancellations.

## Objectives
- Analyze flight volume and operational performance.
- Compare cancellation rates and delays across airlines.
- Investigate reported causes of flight delays.
- Explore passenger satisfaction and service ratings.
- Present actionable business recommendations through an interactive dashboard.

## Dataset Sources
- [Flight Delay and Cancellation Dataset (2019–2023)](https://www.kaggle.com/datasets/patrickzel/flight-delay-and-cancellation-dataset-2019-2023)
- [Airline Passenger Satisfaction Dataset](https://www.kaggle.com/datasets/teejmahal20/airline-passenger-satisfaction)

## Tools & Technologies
- Python
- Pandas
- Plotly
- Streamlit
- CSV data analysis

## Key Findings
Analysis of the 3-million-record flight sample identified:
- 18 airlines and 7,785 routes.
- 2.64% overall cancellation rate.
- 0.24% diversion rate.
- 10.12-minute average departure delay.
- 4.26-minute average arrival delay.

## Dashboard Features
- Executive Overview
- Airline Performance Comparison
- Delay Cause Analysis
- Passenger Experience and Satisfaction
- Interactive filters and data exploration

## Project Structure
- `dashboard.py` — interactive Streamlit dashboard
- `flight_analysis.py` — flight analysis and summary generation
- `requirements.txt` — required Python libraries
- `dashboard_data/` — summarized flight data used by the dashboard
- `train.csv` and `test.csv` — passenger satisfaction data, if included
- `screenshots/` — dashboard screenshots
- `Airline_Business_Intelligence_Report.docx` — business intelligence report, if included

## How to Run Locally
Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Launch the dashboard:

```bash
python -m streamlit run dashboard.py
```

## Business Recommendations
- Investigate recurring late-aircraft and carrier-related delays.
- Monitor cancellation and delay trends by airline, route, and month.
- Improve disruption communication and passenger support.
- Use service-rating insights to prioritize customer experience improvements.

## Limitations
The flight operations and passenger satisfaction datasets are separate sources and are not directly linked at individual-flight or passenger level. Results are descriptive and do not establish causation.

## Author
Data Analytics Portfolio Project
