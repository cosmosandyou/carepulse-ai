# CarePulse AI

A privacy-safe healthcare operations analytics portfolio project for Dublin clinic networks. It uses fully synthetic appointment data to demonstrate no-show prediction, demand pressure forecasting, waiting-time risk analysis, anomaly detection, and operational recommendations.

## Run locally

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

The app generates deterministic synthetic data at first run; no patient-identifiable or real healthcare data is used.

## Public web app (Vercel + Clerk)

**Live application:** [carepulse-ai-flame.vercel.app](https://carepulse-ai-flame.vercel.app)

Anyone with the link can open the landing page and create an account through Clerk. Authentication secrets are configured in Vercel and are never committed to this repository.

The [`web`](./web) directory contains the Vercel-ready Next.js version of CarePulse AI. It includes a responsive executive dashboard, Clerk authentication, and public self-service signup.

1. In Clerk, create an application and enable **public sign-ups**.
2. In Vercel, import this GitHub repository and set **Root Directory** to `web`.
3. Add `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` from [`web/.env.example`](./web/.env.example) to Vercel's environment variables.
4. Deploy. The landing page remains public; `/dashboard` requires a user to sign in or sign up.

For real analytics workloads, place the Python models behind a FastAPI service hosted on Render or Railway. Do not upload real patient data to this portfolio deployment.

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
