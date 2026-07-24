"""CarePulse AI — privacy-safe, synthetic Dublin healthcare operations analytics."""
from __future__ import annotations

import math
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

st.set_page_config(page_title="CarePulse AI", page_icon="✚", layout="wide")

CLINICS = {
    "Tallaght": (53.2859, -6.3691, 1.17),
    "Blanchardstown": (53.3906, -6.3758, 1.12),
    "North Dublin": (53.3910, -6.1940, 1.06),
    "Rathmines": (53.3217, -6.2654, 0.93),
    "Sandyford": (53.2753, -6.2253, 0.89),
    "Clontarf": (53.3624, -6.2007, 0.96),
}
SPECIALTIES = ["General Practice", "Cardiology", "Dermatology", "Physiotherapy", "Mental Health"]


@st.cache_data(show_spinner=False)
def make_data(n: int = 18000) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    start = pd.Timestamp("2025-07-01")
    appt_date = start + pd.to_timedelta(rng.integers(0, 365, n), unit="D")
    clinic = rng.choice(list(CLINICS), n, p=[.21, .19, .18, .15, .14, .13])
    specialty = rng.choice(SPECIALTIES, n, p=[.39, .14, .12, .18, .17])
    age_band = rng.choice(["18–34", "35–49", "50–64", "65+"], n, p=[.24, .30, .27, .19])
    appointment_type = rng.choice(["New consultation", "Follow-up", "Review"], n, p=[.35, .47, .18])
    referral = rng.choice(["Self referral", "GP referral", "Hospital discharge"], n, p=[.22, .65, .13])
    dow = appt_date.day_name()
    month = appt_date.month
    previous_missed = rng.poisson(.42, n).clip(0, 4)
    reminder = rng.binomial(1, .74, n)
    rain = rng.binomial(1, .43, n)
    distance = np.round(rng.gamma(2.4, 2.1, n), 1).clip(.3, 22)
    clinic_pressure = np.array([CLINICS[x][2] for x in clinic])
    monday = (dow == "Monday").astype(int)
    winter = np.isin(month, [11, 12, 1, 2]).astype(int)
    specialty_delay = pd.Series(specialty).map({"General Practice": 4, "Cardiology": 18, "Dermatology": 14, "Physiotherapy": 9, "Mental Health": 12}).to_numpy()
    wait = np.maximum(2, rng.normal(11 + specialty_delay + 10 * (clinic_pressure - .9) + 3 * winter, 8, n)).round(1)
    logit = -2.0 + .62 * previous_missed + .33 * monday + .25 * rain + .055 * distance + .22 * (appointment_type == "Follow-up") - .72 * reminder + .18 * (age_band == "18–34")
    no_show_prob = 1 / (1 + np.exp(-logit))
    no_show = rng.binomial(1, no_show_prob)
    return pd.DataFrame({
        "appointment_date": appt_date, "clinic": clinic, "specialty": specialty, "age_band": age_band,
        "appointment_type": appointment_type, "referral_source": referral, "distance_km": distance,
        "previous_missed": previous_missed, "reminder_sent": reminder, "rain_flag": rain,
        "wait_time_days": wait, "no_show": no_show, "day_of_week": dow,
    })


def model_scores(df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    features = ["distance_km", "previous_missed", "reminder_sent", "rain_flag", "wait_time_days"]
    x = df[features].copy()
    x["monday"] = (df.day_of_week == "Monday").astype(int)
    x["follow_up"] = (df.appointment_type == "Follow-up").astype(int)
    split = int(len(x) * .8)
    model = RandomForestClassifier(n_estimators=160, min_samples_leaf=12, random_state=42, n_jobs=-1)
    model.fit(x.iloc[:split], df.no_show.iloc[:split])
    scores = model.predict_proba(x)[:, 1]
    auc = roc_auc_score(df.no_show.iloc[split:], scores[split:])
    output = df.copy()
    output["no_show_risk"] = scores
    output["risk_band"] = pd.cut(scores, [-.01, .15, .3, 1], labels=["Low", "Medium", "High"])
    return output, auc


data, auc = model_scores(make_data())
max_date = data.appointment_date.max().date()

st.markdown("# CarePulse AI")
st.caption("Privacy-safe synthetic analytics for Dublin healthcare operations · Portfolio demonstration only")

with st.sidebar:
    st.header("Dashboard filters")
    selected_clinics = st.multiselect("Clinics", list(CLINICS), default=list(CLINICS))
    selected_specialties = st.multiselect("Specialties", SPECIALTIES, default=SPECIALTIES)
    start_date, end_date = st.date_input("Appointment period", (max_date - timedelta(days=89), max_date), min_value=data.appointment_date.min().date(), max_value=max_date)
    page = st.radio("View", ["Executive overview", "Clinic demand", "No-show risk", "Waiting times & access"], label_visibility="collapsed")
    st.divider()
    st.caption("Data: fully synthetic · Updated in-app")

filtered = data[(data.clinic.isin(selected_clinics)) & (data.specialty.isin(selected_specialties)) & (data.appointment_date.dt.date.between(start_date, end_date))].copy()
if filtered.empty:
    st.warning("No appointments match these filters.")
    st.stop()

def kpi(label: str, value: str, delta: str | None = None):
    st.metric(label, value, delta)

if page == "Executive overview":
    total = len(filtered)
    noshow_rate = filtered.no_show.mean()
    high_risk = (filtered.risk_band == "High").sum()
    avg_wait = filtered.wait_time_days.mean()
    cols = st.columns(4)
    with cols[0]: kpi("Appointments", f"{total:,}")
    with cols[1]: kpi("No-show rate", f"{noshow_rate:.1%}", "Target < 12%")
    with cols[2]: kpi("Average wait", f"{avg_wait:.1f} days")
    with cols[3]: kpi("High-risk appointments", f"{high_risk:,}")
    daily = filtered.groupby("appointment_date").agg(appointments=("no_show", "size"), no_shows=("no_show", "sum")).reset_index()
    fig = px.line(daily, x="appointment_date", y="appointments", title="Appointment demand trend", color_discrete_sequence=["#1b7f8c"])
    st.plotly_chart(fig, use_container_width=True)
    clinic_summary = filtered.groupby("clinic").agg(Appointments=("no_show", "size"), **{"No-show rate": ("no_show", "mean"), "Avg. wait (days)": ("wait_time_days", "mean")}).reset_index()
    clinic_summary["No-show rate"] = clinic_summary["No-show rate"].map("{:.1%}".format)
    st.subheader("AI operations briefing")
    worst = filtered.groupby("clinic").agg(volume=("no_show", "size"), no_show=("no_show", "mean"), wait=("wait_time_days", "mean")).sort_values(["wait", "no_show"], ascending=False).head(2)
    top_names = " and ".join(worst.index.tolist())
    st.info(f"**Focus next week: {top_names}.** These clinics have the highest combined waiting-time and attendance pressure in the selected period. Prioritise reminders for high-risk follow-up appointments, review Monday morning capacity, and hold a 4% flexible overbooking buffer only for low-risk slots.")
    st.dataframe(clinic_summary, hide_index=True, use_container_width=True)

elif page == "Clinic demand":
    st.subheader("Next-week appointment pressure")
    daily = filtered.groupby(["clinic", "appointment_date"]).size().rename("appointments").reset_index()
    forecast = daily.groupby("clinic").appointments.mean().rename("expected_daily_appointments").reset_index()
    forecast["next_week_forecast"] = (forecast.expected_daily_appointments * 5 * forecast.clinic.map(lambda c: CLINICS[c][2])).round().astype(int)
    forecast["pressure"] = pd.cut(forecast.next_week_forecast / forecast.next_week_forecast.max(), [0, .62, .82, 1], labels=["Stable", "Watch", "High"])
    fig = px.bar(forecast.sort_values("next_week_forecast"), x="next_week_forecast", y="clinic", color="pressure", orientation="h", title="Forecasted appointments (next 5 working days)", color_discrete_map={"Stable":"#3ca370", "Watch":"#e4a11b", "High":"#d9534f"})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(forecast[["clinic", "next_week_forecast", "pressure"]].sort_values("next_week_forecast", ascending=False), hide_index=True, use_container_width=True)

elif page == "No-show risk":
    st.subheader("No-show prediction")
    c1, c2, c3 = st.columns(3)
    with c1: kpi("Model discrimination (AUC)", f"{auc:.2f}")
    with c2: kpi("High-risk rate", f"{(filtered.risk_band == 'High').mean():.1%}")
    with c3: kpi("Reminder coverage", f"{filtered.reminder_sent.mean():.1%}")
    risk_by = filtered.groupby("clinic").agg(Appointments=("no_show", "size"), **{"Observed no-show rate": ("no_show", "mean"), "Predicted risk": ("no_show_risk", "mean")}).reset_index()
    fig = px.scatter(risk_by, x="Predicted risk", y="Observed no-show rate", size="Appointments", color="clinic", title="Observed vs predicted no-show risk", size_max=55)
    st.plotly_chart(fig, use_container_width=True)
    factors = pd.DataFrame({"Factor": ["Previous missed appointments", "No reminder sent", "Monday appointment", "Longer distance to clinic", "Rain on appointment day"], "Operational action": ["Target personalised reminders", "Close messaging coverage gap", "Review early-week slot mix", "Offer remote / nearby alternatives", "Use weather-aware reminder timing"]})
    st.dataframe(factors, hide_index=True, use_container_width=True)

else:
    st.subheader("Waiting time and Dublin access")
    by_specialty = filtered.groupby("specialty", as_index=False).agg(**{"Average wait (days)": ("wait_time_days", "mean"), "Appointments": ("no_show", "size"), "No-show rate": ("no_show", "mean")})
    fig = px.bar(by_specialty.sort_values("Average wait (days)"), x="Average wait (days)", y="specialty", color="No-show rate", orientation="h", color_continuous_scale="Teal", title="Waiting-time pressure by specialty")
    st.plotly_chart(fig, use_container_width=True)
    map_rows = filtered.groupby("clinic").agg(appointments=("no_show", "size"), avg_wait=("wait_time_days", "mean")).reset_index()
    map_rows["lat"] = map_rows.clinic.map(lambda c: CLINICS[c][0])
    map_rows["lon"] = map_rows.clinic.map(lambda c: CLINICS[c][1])
    map_rows["pressure_score"] = map_rows.appointments * map_rows.avg_wait
    fig = px.scatter_map(map_rows, lat="lat", lon="lon", size="pressure_score", color="avg_wait", hover_name="clinic", hover_data={"appointments": True, "avg_wait": ":.1f", "lat": False, "lon": False}, zoom=9.4, center={"lat": 53.3498, "lon": -6.2603}, map_style="open-street-map", color_continuous_scale="Teal", title="Dublin service-demand hotspots")
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=45, b=0))
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("CarePulse AI uses synthetic records only. Outputs are operational planning signals and require human review; they must not be used for clinical care decisions.")
