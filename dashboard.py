
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============================================================
# AIRLINE INTELLIGENCE | EXECUTIVE ANALYTICS
# ============================================================

st.set_page_config(
    page_title="Airline Intelligence | Executive Analytics",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "dashboard_data"

# Premium dark palette — no red
NAVY = "#101A2B"
NAVY_2 = "#17263D"
PANEL = "#172338"
GOLD = "#D6B56D"
IVORY = "#F4F0E6"
MUTED = "#AAB5C5"
TEAL = "#65C3B0"
BLUE = "#7FA6E8"
PURPLE = "#B6A0E8"
COLORS = [GOLD, TEAL, BLUE, PURPLE, "#B7C9D6", "#8CC7A1"]

CHART_TEMPLATE = "plotly_dark"

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

    .stApp {
        background: #101A2B;
        color: #F4F0E6;
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #F4F0E6 !important;
    }

    [data-testid="stSidebar"] {
        background: #17263D;
        border-right: 1px solid #34445A;
    }

    [data-testid="stMetric"] {
        background: #172338;
        border: 1px solid #34445A;
        border-radius: 13px;
        padding: 17px 18px;
        min-height: 112px;
    }

    [data-testid="stMetricLabel"] {
        color: #AAB5C5 !important;
        font-size: 0.85rem;
    }

    [data-testid="stMetricValue"] {
        color: #D6B56D !important;
        font-weight: 700;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.8rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #34445A;
        border-radius: 13px;
    }

    .hero {
        background: linear-gradient(115deg, #17263D, #202F46);
        border: 1px solid #34445A;
        border-radius: 18px;
        padding: 28px 30px;
        margin-bottom: 18px;
    }

    .eyebrow {
        color: #D6B56D;
        letter-spacing: 3px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }

    .hero-title {
        color: #F4F0E6;
        font-family: 'Playfair Display', serif;
        font-size: clamp(28px, 4vw, 43px);
        font-weight: 600;
        margin: 8px 0;
    }

    .hero-copy {
        color: #AAB5C5;
        font-size: 14px;
        line-height: 1.7;
    }

    .section-note {
        color: #AAB5C5;
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 14px;
    }

    .insight-card {
        background: #172338;
        border: 1px solid #34445A;
        border-left: 3px solid #D6B56D;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 10px;
        color: #F4F0E6;
        line-height: 1.65;
        font-size: 13px;
    }

    .insight-label {
        color: #D6B56D;
        font-weight: 700;
        letter-spacing: 1px;
        font-size: 10px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    div[data-testid="stTabs"] button {
        color: #AAB5C5;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #D6B56D;
    }

    hr {
        border-color: #34445A;
    }

    .footer {
        text-align: center;
        color: #AAB5C5;
        font-size: 11px;
        letter-spacing: 1px;
        padding: 24px 0 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LOADING
# ============================================================


@st.cache_data(show_spinner="Loading airline analytics...")
def load_flight_summaries():
    airline = pd.read_csv("airline_summary.csv")
    monthly = pd.read_csv("monthly_summary.csv")
    delays = pd.read_csv("delay_summary.csv")
    routes = pd.read_csv("route_summary.csv")


    # Clean airline summary index column if present
    if "AIRLINE" not in airline.columns:
        first_col = airline.columns[0]
        airline = airline.rename(columns={first_col: "AIRLINE"})

    airline["AIRLINE"] = airline["AIRLINE"].astype(str)

    numeric_airline = [
        "Flights",
        "Cancellation_Rate",
        "Avg_Departure_Delay",
        "Avg_Arrival_Delay"
    ]

    for col in numeric_airline:
        if col in airline.columns:
            airline[col] = pd.to_numeric(airline[col], errors="coerce")

    monthly["Month"] = monthly["Month"].astype(str)
    monthly["Month_Date"] = pd.to_datetime(
        monthly["Month"], format="%Y-%m", errors="coerce"
    )
    monthly = monthly.dropna(subset=["Month_Date"]).sort_values("Month_Date")

    for col in [
        "Flights",
        "Cancellation_Rate",
        "Avg_Departure_Delay",
        "Avg_Arrival_Delay"
    ]:
        if col in monthly.columns:
            monthly[col] = pd.to_numeric(monthly[col], errors="coerce")

    if "Reported Delay Minutes" in delays.columns:
        delays["Reported Delay Minutes"] = pd.to_numeric(
            delays["Reported Delay Minutes"], errors="coerce"
        )

    for col in [
        "Flights", "Avg_Arrival_Delay", "Cancellation_Rate"
    ]:
        if col in routes.columns:
            routes[col] = pd.to_numeric(routes[col], errors="coerce")

    return airline, monthly, delays, routes


@st.cache_data(show_spinner="Loading passenger satisfaction data...")
def load_passengers(train_path, test_path):
    train = pd.read_csv(train_path, low_memory=False)
    test = pd.read_csv(test_path, low_memory=False)

    # Combine both files for descriptive analysis.
    # Remove duplicate passenger IDs if any overlap.
    passengers = pd.concat([train, test], ignore_index=True)
    passengers = passengers.drop(
        columns=["Unnamed: 0"], errors="ignore"
    )

    if "id" in passengers.columns:
        passengers = passengers.drop_duplicates(subset=["id"])

    for col in [
        "Arrival Delay in Minutes",
        "Departure Delay in Minutes",
        "Age",
        "Flight Distance"
    ]:
        if col in passengers.columns:
            passengers[col] = pd.to_numeric(
                passengers[col], errors="coerce"
            )

    if "satisfaction" in passengers.columns:
        passengers["satisfaction"] = (
            passengers["satisfaction"].astype("string").str.strip()
        )

    return passengers


# ============================================================
# FILE CHECKS
# ============================================================

required_files = [
    DATA_DIR / "airline_summary.csv",
    DATA_DIR / "monthly_summary.csv",
    DATA_DIR / "delay_summary.csv",
    DATA_DIR / "route_summary.csv",
    BASE_DIR / "train.csv",
    BASE_DIR / "test.csv",
]

missing_files = [file.name for file in required_files if not file.exists()]

if missing_files:
    st.error(
        "Some project files are missing. Check the file names and locations:"
    )
    for name in missing_files:
        st.write(f"• {name}")
    st.stop()

try:
    airline, monthly, delays, routes = load_flight_summaries(
        str(DATA_DIR)
    )
    passengers = load_passengers(
        str(BASE_DIR / "train.csv"),
        str(BASE_DIR / "test.csv")
    )
except Exception as error:
    st.error("The dashboard could not load its data files.")
    st.code(str(error))
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("## AIRLINE INTELLIGENCE")
st.sidebar.caption("EXECUTIVE CONTROL PANEL")
st.sidebar.markdown("---")

st.sidebar.markdown("### Flight Operations")

airline_options = sorted(airline["AIRLINE"].dropna().unique().tolist())

selected_airlines = st.sidebar.multiselect(
    "Compare airlines",
    options=airline_options,
    default=airline_options,
    help="This filter applies to airline comparison charts and the airline table."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Passenger Experience")

def get_options(column):
    if column not in passengers.columns:
        return ["All"]
    return ["All"] + sorted(
        passengers[column].dropna().astype(str).unique().tolist()
    )

selected_class = st.sidebar.selectbox(
    "Travel class", get_options("Class")
)

selected_travel = st.sidebar.selectbox(
    "Type of travel", get_options("Type of Travel")
)

selected_customer = st.sidebar.selectbox(
    "Customer type", get_options("Customer Type")
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Flight metrics use precomputed summaries from 3 million records. "
    "Passenger analysis combines the supplied train and test files."
)


# ============================================================
# HERO HEADER
# ============================================================

st.markdown("""
<div class="hero">
    <div class="eyebrow">AVIATION • PERFORMANCE • INTELLIGENCE</div>
    <div class="hero-title">Airline Intelligence</div>
    <div class="hero-copy">
        An executive view of flight reliability, delay drivers, airline
        operations and passenger satisfaction — designed to support
        evidence-based operational decisions.
    </div>
</div>
""", unsafe_allow_html=True)

st.caption(
    "FLIGHT OPERATIONS  |  CUSTOMER EXPERIENCE  |  STRATEGIC INSIGHTS"
)


# ============================================================
# EXECUTIVE KPIs
# ============================================================

total_flights = airline["Flights"].sum()

if total_flights > 0:
    overall_cancel_rate = (
        (airline["Flights"] * airline["Cancellation_Rate"]).sum()
        / total_flights
    )
    avg_departure = (
        (airline["Flights"] * airline["Avg_Departure_Delay"]).sum()
        / total_flights
    )
    avg_arrival = (
        (airline["Flights"] * airline["Avg_Arrival_Delay"]).sum()
        / total_flights
    )
else:
    overall_cancel_rate = 0
    avg_departure = 0
    avg_arrival = 0

passenger_count = len(passengers)

satisfied_count = (
    passengers["satisfaction"].str.lower() == "satisfied"
).sum()

satisfaction_rate = (
    satisfied_count / passenger_count * 100
    if passenger_count else 0
)

st.markdown("## Executive Overview")
st.markdown(
    '<div class="section-note">Key performance indicators across the supplied datasets.</div>',
    unsafe_allow_html=True
)

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Flights Analyzed", f"{total_flights:,.0f}")
k2.metric("Cancellation Rate", f"{overall_cancel_rate:.2f}%")
k3.metric("Avg. Departure Delay", f"{avg_departure:.1f} min")
k4.metric("Avg. Arrival Delay", f"{avg_arrival:.1f} min")
k5.metric("Passenger Satisfaction", f"{satisfaction_rate:.1f}%")

st.markdown("---")


# ============================================================
# TABS
# ============================================================

tab_overview, tab_airlines, tab_delays, tab_customers, tab_data = st.tabs([
    "Executive Overview",
    "Airline Performance",
    "Delay Intelligence",
    "Passenger Experience",
    "Data Explorer"
])


# ============================================================
# TAB 1: EXECUTIVE OVERVIEW
# ============================================================

with tab_overview:
    left, right = st.columns([1.25, 1])

    with left:
        st.markdown("### Monthly Flight Activity")
        st.caption("Flight volume over the available date range.")

        fig_monthly = px.line(
            monthly,
            x="Month_Date",
            y="Flights",
            markers=True,
            labels={
                "Month_Date": "Month",
                "Flights": "Number of Flights"
            },
            template=CHART_TEMPLATE
        )

        fig_monthly.update_traces(
            line=dict(color=TEAL, width=3),
            marker=dict(size=5)
        )
        fig_monthly.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=IVORY),
            hovermode="x unified"
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

    with right:
        st.markdown("### Passenger Satisfaction")
        st.caption("Distribution across satisfaction categories.")

        satisfaction_data = (
            passengers["satisfaction"]
            .value_counts(dropna=False)
            .rename_axis("Satisfaction")
            .reset_index(name="Passengers")
        )

        fig_satisfaction = px.pie(
            satisfaction_data,
            names="Satisfaction",
            values="Passengers",
            hole=0.65,
            color="Satisfaction",
            color_discrete_map={
                "satisfied": TEAL,
                "neutral or dissatisfied": GOLD,
                "neutral": BLUE,
                "dissatisfied": PURPLE
            },
            template=CHART_TEMPLATE
        )
        fig_satisfaction.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(line=dict(color=NAVY, width=2))
        )
        fig_satisfaction.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=IVORY),
            legend=dict(orientation="h", y=-0.12)
        )
        st.plotly_chart(fig_satisfaction, use_container_width=True)

    st.markdown("### Executive Signals")

    # These are descriptive findings, not causal conclusions.
    worst_cancel = airline.loc[airline["Cancellation_Rate"].idxmax()]
    best_cancel = airline.loc[airline["Cancellation_Rate"].idxmin()]
    highest_arrival = airline.loc[airline["Avg_Arrival_Delay"].idxmax()]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">Cancellation Watch</div>
            <b>{worst_cancel['AIRLINE']}</b><br>
            Highest cancellation rate in this sample:
            <b>{worst_cancel['Cancellation_Rate']:.2f}%</b>.
            Review flight volumes and operating conditions before
            deciding on corrective action.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">Lower Cancellation Rate</div>
            <b>{best_cancel['AIRLINE']}</b><br>
            Lowest cancellation rate in this sample:
            <b>{best_cancel['Cancellation_Rate']:.2f}%</b>.
            Compare routes, seasons and flight volumes for context.
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">Arrival Delay Review</div>
            <b>{highest_arrival['AIRLINE']}</b><br>
            Highest average arrival delay in this sample:
            <b>{highest_arrival['Avg_Arrival_Delay']:.2f} minutes</b>.
            Investigate route mix and operational constraints.
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# TAB 2: AIRLINE PERFORMANCE
# ============================================================

with tab_airlines:
    st.markdown("### Airline Performance Benchmark")
    st.caption(
        "Select airlines in the sidebar to compare flight volumes, "
        "cancellations and average delays."
    )

    airline_view = airline[
        airline["AIRLINE"].isin(selected_airlines)
    ].copy()

    if airline_view.empty:
        st.info("Select at least one airline from the sidebar.")
    else:
        left, right = st.columns(2)

        with left:
            fig_volume = px.bar(
                airline_view.sort_values("Flights", ascending=True),
                x="Flights",
                y="AIRLINE",
                orientation="h",
                color="Flights",
                color_continuous_scale=["#34445A", GOLD],
                labels={"AIRLINE": "Airline", "Flights": "Flights"},
                template=CHART_TEMPLATE
            )
            fig_volume.update_layout(
                height=500,
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=IVORY)
            )
            st.plotly_chart(fig_volume, use_container_width=True)

        with right:
            fig_cancel = px.bar(
                airline_view.sort_values(
                    "Cancellation_Rate", ascending=True
                ),
                x="Cancellation_Rate",
                y="AIRLINE",
                orientation="h",
                color="Cancellation_Rate",
                color_continuous_scale=["#34445A", GOLD],
                labels={
                    "AIRLINE": "Airline",
                    "Cancellation_Rate": "Cancellation Rate (%)"
                },
                template=CHART_TEMPLATE
            )
            fig_cancel.update_layout(
                height=500,
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=IVORY)
            )
            st.plotly_chart(fig_cancel, use_container_width=True)

        st.markdown("### Delay Comparison")

        delay_compare = airline_view.melt(
            id_vars=["AIRLINE"],
            value_vars=[
                "Avg_Departure_Delay",
                "Avg_Arrival_Delay"
            ],
            var_name="Delay Type",
            value_name="Average Delay (minutes)"
        )

        delay_compare["Delay Type"] = delay_compare["Delay Type"].map({
            "Avg_Departure_Delay": "Departure",
            "Avg_Arrival_Delay": "Arrival"
        })

        fig_delay_compare = px.bar(
            delay_compare,
            x="AIRLINE",
            y="Average Delay (minutes)",
            color="Delay Type",
            barmode="group",
            color_discrete_map={
                "Departure": GOLD,
                "Arrival": TEAL
            },
            template=CHART_TEMPLATE
        )
        fig_delay_compare.update_layout(
            height=440,
            xaxis_tickangle=-35,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=IVORY),
            legend=dict(orientation="h", y=1.08)
        )
        st.plotly_chart(fig_delay_compare, use_container_width=True)

        st.markdown("### Airline Performance Table")

        display_airline = airline_view.rename(columns={
            "AIRLINE": "Airline",
            "Flights": "Flights",
            "Cancellation_Rate": "Cancellation Rate (%)",
            "Avg_Departure_Delay": "Avg Departure Delay (min)",
            "Avg_Arrival_Delay": "Avg Arrival Delay (min)"
        }).sort_values("Flights", ascending=False)

        st.dataframe(
            display_airline.round(2),
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Airline Comparison CSV",
            data=display_airline.to_csv(index=False).encode("utf-8"),
            file_name="airline_performance.csv",
            mime="text/csv"
        )


# ============================================================
# TAB 3: DELAY INTELLIGENCE
# ============================================================

with tab_delays:
    st.markdown("### Understanding Delay Drivers")
    st.caption(
        "Reported delay minutes by cause and performance trends over time."
    )

    left, right = st.columns([1.05, 1])

    with left:
        delay_view = delays.dropna(
            subset=["Reported Delay Minutes"]
        ).sort_values("Reported Delay Minutes", ascending=True)

        fig_causes = px.bar(
            delay_view,
            x="Reported Delay Minutes",
            y="Delay Cause",
            orientation="h",
            color="Reported Delay Minutes",
            color_continuous_scale=["#34445A", GOLD],
            labels={
                "Reported Delay Minutes": "Reported Delay Minutes",
                "Delay Cause": "Delay Cause"
            },
            template=CHART_TEMPLATE
        )
        fig_causes.update_layout(
            height=400,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=IVORY)
        )
        st.plotly_chart(fig_causes, use_container_width=True)

    with right:
        fig_delay_trend = px.line(
            monthly,
            x="Month_Date",
            y=["Avg_Departure_Delay", "Avg_Arrival_Delay"],
            markers=True,
            labels={
                "Month_Date": "Month",
                "value": "Average Delay (minutes)",
                "variable": "Delay Type"
            },
            color_discrete_map={
                "Avg_Departure_Delay": GOLD,
                "Avg_Arrival_Delay": TEAL
            },
            template=CHART_TEMPLATE
        )
        fig_delay_trend.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=IVORY),
            legend=dict(orientation="h", y=1.08)
        )
        st.plotly_chart(fig_delay_trend, use_container_width=True)

    st.markdown("### Busiest Routes")

    route_view = routes.copy()
    route_view["Route"] = (
        route_view["ORIGIN"].astype(str)
        + " → "
        + route_view["DEST"].astype(str)
    )

    top_n = st.slider(
        "Number of routes to display",
        min_value=5,
        max_value=min(30, max(5, len(route_view))),
        value=min(10, max(5, len(route_view)))
    )

    top_routes = route_view.nlargest(top_n, "Flights").sort_values("Flights")

    fig_routes = px.bar(
        top_routes,
        x="Flights",
        y="Route",
        orientation="h",
        color="Avg_Arrival_Delay",
        color_continuous_scale=["#65C3B0", "#D6B56D"],
        labels={
            "Flights": "Flights",
            "Route": "Route",
            "Avg_Arrival_Delay": "Avg Arrival Delay (min)"
        },
        template=CHART_TEMPLATE
    )
    fig_routes.update_layout(
        height=max(400, top_n * 30),
        coloraxis_colorbar_title="Avg Delay",
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=IVORY)
    )
    st.plotly_chart(fig_routes, use_container_width=True)

    st.caption(
        "Route data shows the 100 most frequent routes exported during "
        "preprocessing, not every route in the original flight dataset."
    )


# ============================================================
# TAB 4: PASSENGER EXPERIENCE
# ============================================================

with tab_customers:
    st.markdown("### Passenger Experience Intelligence")
    st.caption(
        "Explore satisfaction and service ratings across passenger groups."
    )

    passenger_view = passengers.copy()

    if selected_class != "All":
        passenger_view = passenger_view[
            passenger_view["Class"].astype(str) == selected_class
        ]

    if selected_travel != "All":
        passenger_view = passenger_view[
            passenger_view["Type of Travel"].astype(str) == selected_travel
        ]

    if selected_customer != "All":
        passenger_view = passenger_view[
            passenger_view["Customer Type"].astype(str) == selected_customer
        ]

    if passenger_view.empty:
        st.warning("No passenger records match these filters.")
    else:
        total_filtered = len(passenger_view)

        filtered_satisfied = (
            passenger_view["satisfaction"].str.lower() == "satisfied"
        ).sum()

        filtered_rate = (
            filtered_satisfied / total_filtered * 100
            if total_filtered else 0
        )

        p1, p2, p3 = st.columns(3)

        p1.metric("Filtered Passengers", f"{total_filtered:,}")
        p2.metric("Satisfaction Rate", f"{filtered_rate:.1f}%")
        p3.metric(
            "Average Flight Distance",
            f"{passenger_view['Flight Distance'].mean():,.0f}"
            if "Flight Distance" in passenger_view.columns else "N/A"
        )

        left, right = st.columns(2)

        with left:
            group_data = (
                passenger_view.groupby(
                    ["Class", "satisfaction"], dropna=False
                )
                .size()
                .reset_index(name="Passengers")
            )

            fig_class = px.bar(
                group_data,
                x="Class",
                y="Passengers",
                color="satisfaction",
                barmode="group",
                color_discrete_map={
                    "satisfied": TEAL,
                    "neutral or dissatisfied": GOLD
                },
                labels={
                    "Class": "Travel Class",
                    "Passengers": "Passenger Records",
                    "satisfaction": "Satisfaction"
                },
                template=CHART_TEMPLATE
            )
            fig_class.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=IVORY)
            )
            st.plotly_chart(fig_class, use_container_width=True)

        with right:
            travel_data = (
                passenger_view.groupby(
                    ["Type of Travel", "satisfaction"], dropna=False
                )
                .size()
                .reset_index(name="Passengers")
            )

            fig_travel = px.bar(
                travel_data,
                x="Type of Travel",
                y="Passengers",
                color="satisfaction",
                barmode="group",
                color_discrete_map={
                    "satisfied": TEAL,
                    "neutral or dissatisfied": GOLD
                },
                labels={
                    "Type of Travel": "Type of Travel",
                    "Passengers": "Passenger Records",
                    "satisfaction": "Satisfaction"
                },
                template=CHART_TEMPLATE
            )
            fig_travel.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=IVORY)
            )
            st.plotly_chart(fig_travel, use_container_width=True)

        st.markdown("### Service Rating Benchmark")

        rating_columns = [
            "Inflight wifi service",
            "Departure/Arrival time convenient",
            "Ease of Online booking",
            "Gate location",
            "Food and drink",
            "Online boarding",
            "Seat comfort",
            "Inflight entertainment",
            "On-board service",
            "Leg room service",
            "Baggage handling",
            "Checkin service",
            "Inflight service",
            "Cleanliness"
        ]

        available_ratings = [
            column for column in rating_columns
            if column in passenger_view.columns
        ]

        if available_ratings:
            rating_data = (
                passenger_view[available_ratings]
                .mean()
                .sort_values()
                .rename_axis("Service")
                .reset_index(name="Average Rating")
            )

            fig_ratings = px.bar(
                rating_data,
                x="Average Rating",
                y="Service",
                orientation="h",
                color="Average Rating",
                color_continuous_scale=["#34445A", GOLD],
                labels={
                    "Average Rating": "Mean Rating",
                    "Service": "Service Dimension"
                },
                template=CHART_TEMPLATE
            )
            fig_ratings.update_layout(
                height=540,
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=IVORY)
            )
            st.plotly_chart(fig_ratings, use_container_width=True)

        st.markdown("### Satisfaction by Arrival Delay")

        if "Arrival Delay in Minutes" in passenger_view.columns:
            delay_passengers = passenger_view.dropna(
                subset=["Arrival Delay in Minutes"]
            ).copy()

            delay_passengers["Arrival Delay Band"] = pd.cut(
                delay_passengers["Arrival Delay in Minutes"].clip(lower=0),
                bins=[-0.01, 0, 15, 60, float("inf")],
                labels=[
                    "On time",
                    "1–15 min",
                    "16–60 min",
                    "Over 60 min"
                ]
            )

            delay_satisfaction = (
                delay_passengers.groupby(
                    ["Arrival Delay Band", "satisfaction"],
                    observed=False
                )
                .size()
                .reset_index(name="Passengers")
            )

            delay_satisfaction = delay_satisfaction[
                delay_satisfaction["Passengers"] > 0
            ]

            fig_delay_satisfaction = px.bar(
                delay_satisfaction,
                x="Arrival Delay Band",
                y="Passengers",
                color="satisfaction",
                barmode="group",
                color_discrete_map={
                    "satisfied": TEAL,
                    "neutral or dissatisfied": GOLD
                },
                template=CHART_TEMPLATE,
                labels={
                    "Arrival Delay Band": "Arrival Delay",
                    "Passengers": "Passenger Records",
                    "satisfaction": "Satisfaction"
                }
            )
            fig_delay_satisfaction.update_layout(
                height=390,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=IVORY)
            )
            st.plotly_chart(
                fig_delay_satisfaction,
                use_container_width=True
            )

        st.download_button(
            "Download Filtered Passenger Data",
            data=passenger_view.to_csv(index=False).encode("utf-8"),
            file_name="filtered_passenger_experience.csv",
            mime="text/csv"
        )


# ============================================================
# TAB 5: DATA EXPLORER
# ============================================================

with tab_data:
    st.markdown("### Data Explorer")
    st.caption(
        "Inspect the processed flight summaries and passenger records."
    )

    data_choice = st.selectbox(
        "Choose a dataset",
        [
            "Airline Summary",
            "Monthly Summary",
            "Delay Causes",
            "Top 100 Routes",
            "Passenger Records"
        ]
    )

    data_map = {
        "Airline Summary": airline,
        "Monthly Summary": monthly.drop(
            columns=["Month_Date"], errors="ignore"
        ),
        "Delay Causes": delays,
        "Top 100 Routes": routes,
        "Passenger Records": passengers
    }

    chosen_data = data_map[data_choice]

    st.write(f"**Rows:** {len(chosen_data):,}")
    st.dataframe(
        chosen_data.head(1000),
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Selected Dataset as CSV",
        data=chosen_data.to_csv(index=False).encode("utf-8"),
        file_name=data_choice.lower().replace(" ", "_") + ".csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div class="footer">
AIRLINE INTELLIGENCE &nbsp; • &nbsp;
OPERATIONS ANALYTICS &nbsp; • &nbsp;
CUSTOMER EXPERIENCE
<br><br>
Prepared for strategic performance review using the supplied datasets.
</div>
""", unsafe_allow_html=True)
