"""Interactive web dashboard for factory operations metrics."""
import sys
from pathlib import Path

# Add parent directory to path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from src.data import load_data, MACHINES
from src.metrics import (
    calculate_oee,
    get_downtime_analysis,
    get_quality_issues,
    get_scrap_metrics,
)

# Page config
st.set_page_config(page_title="Factory Dashboard", layout="wide")
st.title("Factory Operations Dashboard")

# Load data once
data: Optional[Dict[str, Any]] = load_data()
if data is None:
    st.error("No production data found. Please generate data first using the CLI.")
    st.stop()

start_date: str = data["start_date"].split("T")[0]
end_date: str = data["end_date"].split("T")[0]

# Sidebar filter
st.sidebar.header("Filters")
machine_names: list[str] = [m["name"] for m in MACHINES]
machine: str = st.sidebar.selectbox("Machine", ["All Machines"] + machine_names)
machine_filter: Optional[str] = None if machine == "All Machines" else machine

# Tabs
tab1, tab2, tab3 = st.tabs(["OEE", "Availability", "Quality"])

# OEE Tab
with tab1:
    st.header("Overall Equipment Effectiveness")

    # Get metrics
    metrics = calculate_oee(start_date, end_date, machine_filter)

    # Gauge chart
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=metrics["oee"] * 100,
            title={"text": "Current OEE %"},
            delta={"reference": 75, "suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 60], "color": "lightcoral"},
                    {"range": [60, 75], "color": "lightyellow"},
                    {"range": [75, 100], "color": "lightgreen"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 75,
                },
            },
        )
    )
    fig_gauge.update_layout(height=400)
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Trend line chart
    # Calculate daily OEE inline
    daily_data: list[Dict[str, Any]] = []
    current: datetime = datetime.fromisoformat(start_date)
    end_dt: datetime = datetime.fromisoformat(end_date)

    while current <= end_dt:
        date_str = current.strftime("%Y-%m-%d")
        day_metrics = calculate_oee(date_str, date_str, machine_filter)
        daily_data.append({"date": date_str, "oee": day_metrics["oee"] * 100})
        current += timedelta(days=1)

    df_oee = pd.DataFrame(daily_data)

    fig_trend = go.Figure()
    fig_trend.add_trace(
        go.Scatter(
            x=df_oee["date"],
            y=df_oee["oee"],
            mode="lines+markers",
            name="OEE %",
            line=dict(color="royalblue", width=3),
        )
    )
    fig_trend.update_layout(
        title="OEE Trend Over Time",
        xaxis_title="Date",
        yaxis_title="OEE %",
        height=400,
        yaxis=dict(range=[0, 100]),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# Availability Tab
with tab2:
    st.header("Availability & Downtime")

    # Get downtime data
    downtime_data = get_downtime_analysis(start_date, end_date, machine_filter)

    # Downtime by reason bar chart
    downtime_by_reason = downtime_data.get("downtime_by_reason", {})

    if downtime_by_reason:
        fig_downtime = go.Figure()
        fig_downtime.add_trace(
            go.Bar(
                y=list(downtime_by_reason.keys()),
                x=list(downtime_by_reason.values()),
                orientation="h",
                marker=dict(color="indianred"),
            )
        )
        fig_downtime.update_layout(
            title="Total Downtime by Reason (Hours)",
            xaxis_title="Hours",
            yaxis_title="Reason",
            height=400,
        )
        st.plotly_chart(fig_downtime, use_container_width=True)
    else:
        st.info("No downtime data available for this period")

    # Major events table
    st.subheader("Major Downtime Events (>2 hours)")
    major_events = downtime_data.get("major_events", [])

    if major_events:
        df_events = pd.DataFrame(major_events)
        df_events.columns = ["Date", "Machine", "Reason", "Description", "Hours"]
        st.dataframe(df_events, use_container_width=True, hide_index=True)
    else:
        st.info("No major downtime events in this period")

# Quality Tab
with tab3:
    st.header("Quality Metrics")

    # Get quality data
    quality_data = get_quality_issues(
        start_date, end_date, machine_name=machine_filter
    )
    scrap_data = get_scrap_metrics(start_date, end_date, machine_filter)

    # Scrap rate trend
    daily_scrap: list[Dict[str, Any]] = []
    current: datetime = datetime.fromisoformat(start_date)
    end_dt: datetime = datetime.fromisoformat(end_date)

    while current <= end_dt:
        date_str = current.strftime("%Y-%m-%d")
        day_scrap = get_scrap_metrics(date_str, date_str, machine_filter)
        daily_scrap.append(
            {"date": date_str, "scrap_rate": day_scrap["scrap_rate"] * 100}
        )
        current += timedelta(days=1)

    df_scrap = pd.DataFrame(daily_scrap)

    fig_scrap = go.Figure()
    fig_scrap.add_trace(
        go.Scatter(
            x=df_scrap["date"],
            y=df_scrap["scrap_rate"],
            mode="lines+markers",
            name="Scrap Rate %",
            line=dict(color="crimson", width=3),
            fill="tozeroy",
            fillcolor="rgba(220, 20, 60, 0.2)",
        )
    )
    fig_scrap.update_layout(
        title="Scrap Rate Trend",
        xaxis_title="Date",
        yaxis_title="Scrap Rate %",
        height=400,
    )
    st.plotly_chart(fig_scrap, use_container_width=True)

    # Quality issues table
    st.subheader("Quality Issues")

    if quality_data.get("issues"):
        df_issues = pd.DataFrame(quality_data["issues"])
        # Reorder columns: date, machine, type, severity, parts_affected, description
        df_issues = df_issues[
            ["date", "machine", "type", "severity", "parts_affected", "description"]
        ]
        df_issues.columns = [
            "Date",
            "Machine",
            "Type",
            "Severity",
            "Parts",
            "Description",
        ]

        # Color-code by severity
        def highlight_severity(row: pd.Series) -> list[str]:
            """Highlight rows based on severity level."""
            if row["Severity"] == "High":
                return ["background-color: #ff6b6b; color: white"] * len(row)
            elif row["Severity"] == "Medium":
                return ["background-color: #ffd93d; color: black"] * len(row)
            return ["background-color: #95e1d3; color: black"] * len(row)

        styled_df = df_issues.style.apply(highlight_severity, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.success("No quality issues in this period")
