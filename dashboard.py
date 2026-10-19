
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE CONFIGURATION & DESIGN
# ============================================================

st.set_page_config(
    page_title="Airline Intelligence | Executive Control Panel",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#101A2B"
PANEL = "#17263D"
GOLD = "#D6B56D"
IVORY = "#F4F0E6"
MUTED = "#AAB5C5"
TEAL = "#65C3B0"
BLUE = "#7FA6E8"
PURPLE = "#B6A0E8"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {NAVY};
        color: {IVORY};
    }}
    [data-testid="stSidebar"] {{
        background-color: {PANEL};
    }}
    h1, h2, h3 {{
        color: {IVORY} !important;
    }}
    p, label, .stCaption {{
        color: {MUTED};
    }}
    [data-testid="stMetric"] {{
        background-color: {PANEL};
        border: 1px solid #30415A;
        padding: 18px;
        border-radius: 12px;
    }}
    [data-testid="stMetricLabel"] {{
        color: {MUTED} !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {GOLD} !important;
    }}
    div[data-testid="stDataFrame"] {{
        border: 1px solid #30415A;
        border-radius: 8px;
    }}
    .section-note {{
        color: {MUTED};
        font-size: 0.92rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FILE LOCATIONS
# Supports summary CSVs in dashboard_data OR repository root
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "dashboard_data"


def find_file(filename):
    candidates = [
        DATA_DIR / filename,
        BASE_DIR / filename,
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def read_csv_safely(path):
    if path is None:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception:
        try:
            return pd.read_csv(path, encoding="latin1", low_memory=False)
        except Exception:
            return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_flight_summaries():
    airline = read_csv_safely(find_file("airline_summary.csv"))
    monthly = read_csv_safely(find_file("monthly_summary.csv"))
    delay = read_csv_safely(find_file("delay_summary.csv"))
    routes = read_csv_safely(find_file("route_summary.csv"))
    return airline, monthly, delay, routes


@st.cache_data(show_spinner="Loading passenger datasets...")
def load_passengers():
    frames = []
    for filename in ["train.csv", "test.csv"]:
        path = BASE_DIR / filename
        if path.exists():
            df = read_csv_safely(path)
            if not df.empty:
                frames.append(df)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined.columns = combined.columns.astype(str).str.strip()
    return combined


def numeric_series(df, column):
    if column not in df.columns:
        return pd.Series(dtype="float64")
    return pd.to_numeric(df[column], errors="coerce")


def find_column(df, candidates):
    if df.empty:
        return None

    normalized = {
        str(col).strip().lower().replace("_", " ").replace("-", " "): col
        for col in df.columns
    }

    for candidate in candidates:
        key = candidate.strip().lower().replace("_", " ").replace("-", " ")
        if key in normalized:
            return normalized[key]

    for candidate in candidates:
        key = candidate.strip().lower().replace("_", " ").replace("-", " ")
        for normalized_name, original in normalized.items():
            if key in normalized_name:
                return original

    return None


def numeric_column(df, candidates):
    col = find_column(df, candidates)
    if col is None:
        return None
    converted = pd.to_numeric(df[col], errors="coerce")
    if converted.notna().any():
        return col
    return None


def display_metric(label, value, help_text=None):
    st.metric(label=label, value=value, help=help_text)


def chart_layout(fig, title=None, height=380):
    fig.update_layout(
        title=title,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=IVORY, family="Arial"),
        title_font=dict(size=17, color=IVORY),
        margin=dict(l=20, r=20, t=55, b=35),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=IVORY),
        ),
        xaxis=dict(
            gridcolor="#30415A",
            linecolor="#30415A",
            tickfont=dict(color=MUTED),
            title_font=dict(color=MUTED),
        ),
        yaxis=dict(
            gridcolor="#30415A",
            linecolor="#30415A",
            tickfont=dict(color=MUTED),
            title_font=dict(color=MUTED),
        ),
    )
    return fig


def show_chart(fig):
    st.plotly_chart(
        chart_layout(fig),
        use_container_width=True,
        config={"displaylogo": False, "responsive": True},
    )


def clean_category(series):
    return series.astype("string").fillna("Unknown").str.strip()


# ============================================================
# LOAD DATA
# ============================================================

st.sidebar.markdown(
    f"""
    <h2 style="color:{GOLD};">AIRLINE INTELLIGENCE</h2>
    <p style="color:{MUTED};">EXECUTIVE CONTROL PANEL</p>
    """,
    unsafe_allow_html=True,
)

with st.spinner("Loading airline intelligence data..."):
    airline_df, monthly_df, delay_df, route_df = load_flight_summaries()
    passenger_df = load_passengers()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
    <div style="padding: 8px 0 18px 0;">
        <p style="color:{GOLD}; letter-spacing:3px; font-size:12px;">
            OPERATIONS • PERFORMANCE • CUSTOMER EXPERIENCE
        </p>
        <h1 style="font-size:36px; margin-bottom:5px;">
            Airline Intelligence
        </h1>
        <p style="color:{MUTED}; font-size:16px;">
            Executive analytics for flight operations, delays,
            cancellations and passenger satisfaction.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if airline_df.empty and monthly_df.empty and delay_df.empty and route_df.empty:
    st.error(
        "The four flight summary files could not be loaded. "
        "Check that the summary CSVs exist in the repository root "
        "or inside the dashboard_data folder."
    )
    st.code(
        "airline_summary.csv\n"
        "monthly_summary.csv\n"
        "delay_summary.csv\n"
        "route_summary.csv"
    )
    st.stop()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.divider()
st.sidebar.subheader("Flight Operations")

airline_name_col = find_column(
    airline_df, ["AIRLINE", "airline_name", "carrier", "name"]
)
airline_filter_col = find_column(
    airline_df, ["AIRLINE", "airline_name", "carrier", "name"]
)

filtered_airline_df = airline_df.copy()
if airline_filter_col and not airline_df.empty:
    airline_options = sorted(
        clean_category(airline_df[airline_filter_col]).unique().tolist()
    )
    selected_airlines = st.sidebar.multiselect(
        "Compare airlines",
        options=airline_options,
        default=airline_options,
    )
    filtered_airline_df = airline_df[
        clean_category(airline_df[airline_filter_col]).isin(selected_airlines)
    ].copy()
else:
    st.sidebar.caption("Airline names are not available in the summary.")

st.sidebar.divider()
st.sidebar.subheader("Passenger Experience")

passenger_filter_col = find_column(
    passenger_df, ["satisfaction", "customer_satisfaction"]
)
filtered_passenger_df = passenger_df.copy()

if not passenger_df.empty:
    for label, candidates in [
        ("Travel class", ["Class", "travel_class"]),
        ("Customer type", ["Customer Type", "customer_type"]),
        ("Travel type", ["Type of Travel", "travel_type"]),
        ("Satisfaction", ["satisfaction", "customer_satisfaction"]),
    ]:
        col = find_column(passenger_df, candidates)
        if col:
            options = sorted(clean_category(passenger_df[col]).unique().tolist())
            chosen = st.sidebar.multiselect(
                label,
                options=options,
                default=options,
                key=f"filter_{label}",
            )
            filtered_passenger_df = filtered_passenger_df[
                clean_category(filtered_passenger_df[col]).isin(chosen)
            ]

st.sidebar.divider()
st.sidebar.caption("AIRLINE ANALYTICS PROJECT")
st.sidebar.caption("Python • Pandas • Plotly • Streamlit")


# ============================================================
# EXECUTIVE KPI CALCULATIONS
# ============================================================

flights_col = numeric_column(
    filtered_airline_df,
    ["flights", "total_flights", "flight_count", "number_of_flights", "count"],
)
cancel_col = numeric_column(
    filtered_airline_df,
    ["cancellation_rate", "cancel_rate", "cancelled_rate", "canceled_rate"],
)
dep_delay_col = numeric_column(
    filtered_airline_df,
    ["avg_dep_delay", "average_departure_delay", "mean_dep_delay",
     "departure_delay", "dep_delay"],
)
arr_delay_col = numeric_column(
    filtered_airline_df,
    ["avg_arr_delay", "average_arrival_delay", "mean_arr_delay",
     "arrival_delay", "arr_delay"],
)

total_flights = (
    numeric_series(filtered_airline_df, flights_col).sum()
    if flights_col else 0
)

cancel_rate = (
    numeric_series(filtered_airline_df, cancel_col).mean()
    if cancel_col else None
)

avg_dep_delay = (
    numeric_series(filtered_airline_df, dep_delay_col).mean()
    if dep_delay_col else None
)

avg_arr_delay = (
    numeric_series(filtered_airline_df, arr_delay_col).mean()
    if arr_delay_col else None
)

st.subheader("Executive Overview")

k1, k2, k3, k4 = st.columns(4)

with k1:
    display_metric(
        "Flights Represented",
        f"{total_flights:,.0f}" if total_flights else "See airline table",
    )

with k2:
    display_metric(
        "Average Departure Delay",
        f"{avg_dep_delay:,.2f} min" if avg_dep_delay is not None else "N/A",
    )

with k3:
    display_metric(
        "Average Arrival Delay",
        f"{avg_arr_delay:,.2f} min" if avg_arr_delay is not None else "N/A",
    )

with k4:
    if cancel_rate is None:
        cancel_display = "N/A"
    elif cancel_rate <= 1:
        cancel_display = f"{cancel_rate * 100:.2f}%"
    else:
        cancel_display = f"{cancel_rate:.2f}%"
    display_metric("Cancellation Rate", cancel_display)

st.caption(
    "KPIs are calculated from the available summary columns. "
    "N/A means the required measure was not found in that summary."
)

tab_overview, tab_airlines, tab_delays, tab_passengers, tab_data = st.tabs(
    [
        "Executive Overview",
        "Airline Performance",
        "Delay Intelligence",
        "Passenger Experience",
        "Data Explorer",
    ]
)


# ============================================================
# TAB 1: EXECUTIVE OVERVIEW
# ============================================================

with tab_overview:
    st.subheader("Operational Performance Snapshot")

    left, right = st.columns(2)

    with left:
        if not filtered_airline_df.empty and airline_name_col:
            count_col = numeric_column(
                filtered_airline_df,
                ["flights", "total_flights", "flight_count",
                 "number_of_flights", "count"],
            )
            if count_col:
                plot_df = filtered_airline_df.copy()
                plot_df[count_col] = pd.to_numeric(
                    plot_df[count_col], errors="coerce"
                )
                plot_df = plot_df.dropna(subset=[count_col])
                plot_df = plot_df.nlargest(12, count_col)
                fig = px.bar(
                    plot_df,
                    x=airline_name_col,
                    y=count_col,
                    title="Airline Flight Volume",
                    color_discrete_sequence=[GOLD],
                    labels={airline_name_col: "Airline", count_col: "Flights"},
                )
                fig.update_xaxes(tickangle=-35)
                show_chart(fig)
            else:
                st.info("No flight-count column was found in airline_summary.csv.")
        else:
            st.info("Airline names are not available for this chart.")

    with right:
        if not delay_df.empty:
            category_col = find_column(
                delay_df, ["delay_cause", "cause", "category", "delay_type", "reason"]
            )
            value_col = numeric_column(
                delay_df,
                ["delay_minutes", "total_delay", "minutes", "total_minutes",
                 "delay", "value", "count"],
            )
            if category_col and value_col:
                plot_df = delay_df.copy()
                plot_df[value_col] = pd.to_numeric(
                    plot_df[value_col], errors="coerce"
                )
                plot_df = plot_df.dropna(subset=[value_col]).nlargest(10, value_col)
                fig = px.bar(
                    plot_df,
                    x=category_col,
                    y=value_col,
                    title="Delay Causes",
                    color_discrete_sequence=[TEAL],
                    labels={category_col: "Cause", value_col: "Minutes / Value"},
                )
                fig.update_xaxes(tickangle=-25)
                show_chart(fig)
            else:
                st.info("The delay summary does not contain recognizable category and numeric columns.")
        else:
            st.info("Delay summary data is unavailable.")

    st.subheader("Monthly Flight Trends")

    if not monthly_df.empty:
        month_col = find_column(
            monthly_df, ["month", "year_month", "flight_month", "period", "date"]
        )
        monthly_count_col = numeric_column(
            monthly_df,
            ["flights", "total_flights", "flight_count", "number_of_flights", "count"],
        )

        if month_col and monthly_count_col:
            plot_df = monthly_df.copy()
            plot_df[monthly_count_col] = pd.to_numeric(
                plot_df[monthly_count_col], errors="coerce"
            )
            plot_df = plot_df.dropna(subset=[monthly_count_col])
            fig = px.line(
                plot_df,
                x=month_col,
                y=monthly_count_col,
                markers=True,
                title="Flight Volume Over Time",
                color_discrete_sequence=[GOLD],
                labels={month_col: "Month", monthly_count_col: "Flights"},
            )
            show_chart(fig)
        else:
            st.dataframe(monthly_df.head(100), use_container_width=True)
            st.caption("Showing the monthly summary because standard trend columns were not detected.")
    else:
        st.info("Monthly summary data is unavailable.")


# ============================================================
# TAB 2: AIRLINE PERFORMANCE
# ============================================================

with tab_airlines:
    st.subheader("Airline Performance Comparison")

    if filtered_airline_df.empty:
        st.info("No airline records match the current filter.")
    else:
        st.dataframe(
            filtered_airline_df,
            use_container_width=True,
            hide_index=True,
        )

        airline_col = find_column(
            filtered_airline_df, ["AIRLINE", "airline_name", "carrier", "name"]
        )
        volume_col = numeric_column(
            filtered_airline_df,
            ["flights", "total_flights", "flight_count", "number_of_flights", "count"],
        )
        cancellation_col = numeric_column(
            filtered_airline_df,
            ["cancellation_rate", "cancel_rate", "cancelled_rate", "canceled_rate"],
        )

        if airline_col and volume_col:
            plot_df = filtered_airline_df.copy()
            plot_df[volume_col] = pd.to_numeric(plot_df[volume_col], errors="coerce")
            plot_df = plot_df.dropna(subset=[volume_col]).nlargest(20, volume_col)
            fig = px.bar(
                plot_df,
                x=airline_col,
                y=volume_col,
                title="Flight Volume by Airline",
                color_discrete_sequence=[BLUE],
                labels={airline_col: "Airline", volume_col: "Flights"},
            )
            fig.update_xaxes(tickangle=-35)
            show_chart(fig)

        if airline_col and cancellation_col:
            plot_df = filtered_airline_df.copy()
            plot_df[cancellation_col] = pd.to_numeric(
                plot_df[cancellation_col], errors="coerce"
            )
            plot_df = plot_df.dropna(subset=[cancellation_col])
            fig = px.bar(
                plot_df.sort_values(cancellation_col, ascending=False).head(20),
                x=airline_col,
                y=cancellation_col,
                title="Cancellation Rate by Airline",
                color_discrete_sequence=[PURPLE],
                labels={airline_col: "Airline", cancellation_col: "Cancellation rate"},
            )
            fig.update_xaxes(tickangle=-35)
            show_chart(fig)

        st.download_button(
            "Download Airline Summary",
            data=filtered_airline_df.to_csv(index=False).encode("utf-8"),
            file_name="airline_performance_filtered.csv",
            mime="text/csv",
        )


# ============================================================
# TAB 3: DELAY INTELLIGENCE
# ============================================================

with tab_delays:
    st.subheader("Flight Delay Intelligence")

    if delay_df.empty:
        st.info("Delay summary data is unavailable.")
    else:
        st.dataframe(delay_df, use_container_width=True, hide_index=True)

        cause_col = find_column(
            delay_df, ["delay_cause", "cause", "category", "delay_type", "reason"]
        )
        minutes_col = numeric_column(
            delay_df,
            ["delay_minutes", "total_delay", "minutes", "total_minutes",
             "delay", "value", "count"],
        )

        if cause_col and minutes_col:
            plot_df = delay_df.copy()
            plot_df[minutes_col] = pd.to_numeric(
                plot_df[minutes_col], errors="coerce"
            )
            plot_df = plot_df.dropna(subset=[minutes_col])
            plot_df = plot_df.sort_values(minutes_col, ascending=True)
            fig = px.bar(
                plot_df,
                x=minutes_col,
                y=cause_col,
                orientation="h",
                title="Delay Contribution by Cause",
                color_discrete_sequence=[TEAL],
                labels={minutes_col: "Minutes / Value", cause_col: "Delay cause"},
            )
            show_chart(fig)
        else:
            st.info("This delay summary's column names are not recognized for a chart.")

        st.download_button(
            "Download Delay Summary",
            data=delay_df.to_csv(index=False).encode("utf-8"),
            file_name="delay_summary.csv",
            mime="text/csv",
        )

    if not route_df.empty:
        st.subheader("Route Summary")
        st.dataframe(route_df.head(100), use_container_width=True, hide_index=True)


# ============================================================
# TAB 4: PASSENGER EXPERIENCE
# ============================================================

with tab_passengers:
    st.subheader("Passenger Satisfaction Intelligence")

    if filtered_passenger_df.empty:
        st.warning(
            "Passenger data could not be loaded. Ensure train.csv and test.csv "
            "are stored beside dashboard.py."
        )
    else:
        satisfaction_col = find_column(
            filtered_passenger_df, ["satisfaction", "customer_satisfaction"]
        )
        class_col = find_column(filtered_passenger_df, ["Class", "travel_class"])
        travel_col = find_column(
            filtered_passenger_df, ["Type of Travel", "travel_type"]
        )

        total_passengers = len(filtered_passenger_df)
        st.metric("Passenger Records in Filter", f"{total_passengers:,}")

        if satisfaction_col:
            satisfaction_values = clean_category(
                filtered_passenger_df[satisfaction_col]
            )
            satisfaction_counts = (
                satisfaction_values.value_counts().rename_axis("Satisfaction").reset_index(name="Passengers")
            )

            left, right = st.columns(2)

            with left:
                fig = px.pie(
                    satisfaction_counts,
                    names="Satisfaction",
                    values="Passengers",
                    hole=0.58,
                    title="Passenger Satisfaction Distribution",
                    color_discrete_sequence=[TEAL, GOLD, BLUE, PURPLE],
                )
                show_chart(fig)

            with right:
                fig = px.bar(
                    satisfaction_counts,
                    x="Satisfaction",
                    y="Passengers",
                    title="Passenger Satisfaction Counts",
                    color_discrete_sequence=[GOLD],
                )
                show_chart(fig)

            satisfied_labels = [
                value for value in satisfaction_values.dropna().unique()
                if "satisfied" in str(value).lower()
                and "dissatisfied" not in str(value).lower()
            ]
            satisfied_count = satisfaction_values.isin(satisfied_labels).sum()

            if total_passengers:
                satisfaction_rate = satisfied_count / total_passengers * 100
                st.metric("Satisfied Passengers", f"{satisfaction_rate:.1f}%")
        else:
            st.info("No satisfaction column was found in the passenger dataset.")

        if class_col and satisfaction_col:
            cross = filtered_passenger_df.copy()
            cross["_satisfaction"] = clean_category(cross[satisfaction_col])
            cross["_class"] = clean_category(cross[class_col])
            cross_tab = pd.crosstab(cross["_class"], cross["_satisfaction"])
            fig = px.bar(
                cross_tab.reset_index().melt(
                    id_vars="_class",
                    var_name="Satisfaction",
                    value_name="Passengers",
                ),
                x="_class",
                y="Passengers",
                color="Satisfaction",
                barmode="group",
                title="Satisfaction by Travel Class",
                color_discrete_sequence=[TEAL, GOLD, BLUE, PURPLE],
                labels={"_class": "Travel class"},
            )
            show_chart(fig)

        if travel_col and satisfaction_col:
            travel_cross = pd.crosstab(
                clean_category(filtered_passenger_df[travel_col]),
                clean_category(filtered_passenger_df[satisfaction_col]),
            )
            fig = px.bar(
                travel_cross.reset_index().melt(
                    id_vars=travel_cross.index.name or "index",
                    var_name="Satisfaction",
                    value_name="Passengers",
                ),
                x=travel_cross.index.name or "index",
                y="Passengers",
                color="Satisfaction",
                barmode="group",
                title="Satisfaction by Type of Travel",
                color_discrete_sequence=[TEAL, GOLD, BLUE, PURPLE],
            )
            show_chart(fig)

        st.caption(
            "Passenger satisfaction data is analyzed separately from flight "
            "operations data; individual passenger records are not linked to specific flights."
        )


# ============================================================
# TAB 5: DATA EXPLORER
# ============================================================

with tab_data:
    st.subheader("Data Explorer")

    dataset_options = {
        "Airline Summary": airline_df,
        "Monthly Summary": monthly_df,
        "Delay Summary": delay_df,
        "Route Summary": route_df,
        "Passenger Dataset": filtered_passenger_df,
    }

    selected_dataset_name = st.selectbox(
        "Choose a dataset",
        list(dataset_options.keys()),
    )
    chosen_data = dataset_options[selected_dataset_name]

    if chosen_data.empty:
        st.info("This dataset is empty or unavailable.")
    else:
        search_text = st.text_input(
            "Search displayed data",
            placeholder="Type a value to filter rows...",
        )

        display_df = chosen_data.copy()

        if search_text:
            mask = display_df.astype(str).apply(
                lambda column: column.str.contains(
                    search_text, case=False, na=False
                )
            ).any(axis=1)
            display_df = display_df[mask]

        st.caption(
            f"Showing {len(display_df):,} of {len(chosen_data):,} rows"
        )
        st.dataframe(display_df.head(500), use_container_width=True, hide_index=True)

        st.download_button(
            "Download Selected Dataset as CSV",
            data=display_df.to_csv(index=False).encode("utf-8"),
            file_name=(
                selected_dataset_name.lower().replace(" ", "_") + ".csv"
            ),
            mime="text/csv",
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.markdown(
    f"""
    <div style="text-align:center; padding:15px 0 25px 0;">
        <p style="color:{GOLD}; letter-spacing:2px; font-size:12px;">
            AIRLINE INTELLIGENCE
        </p>
        <p style="color:{MUTED};">
            OPERATIONS ANALYTICS • CUSTOMER EXPERIENCE
        </p>
        <p style="color:{MUTED}; font-size:12px;">
            Prepared for strategic performance review using the supplied datasets.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
