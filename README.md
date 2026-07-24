# CarePulse AI

A privacy-safe healthcare operations analytics portfolio project for Dublin clinic networks. It uses fully synthetic appointment data to demonstrate no-show prediction, demand pressure forecasting, waiting-time risk analysis, anomaly detection, and operational recommendations.

## Run locally

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

The app generates deterministic synthetic data at first run; no patient-identifiable or real healthcare data is used.

## Included analytics

- Executive KPI and trend dashboard
- Next-week clinic demand pressure forecast
- No-show risk model with probability scoring
- Waiting-time and capacity analysis
- Appointment-demand anomaly detection
- Dublin clinic access and demand map
- Rule-grounded executive operations briefing

## Privacy statement

**CarePulse AI is a privacy-safe synthetic analytics platform inspired by operational challenges faced by urban healthcare providers in Dublin.** It is a portfolio demonstration, not a clinical decision-support system.
