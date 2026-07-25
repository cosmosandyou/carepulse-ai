import Link from "next/link";
import { SignedIn, SignedOut, SignInButton, SignUpButton } from "@clerk/nextjs";

export default function Home() {
  return <main className="landing">
    <nav><span className="brand">✚ CarePulse AI</span><div><SignedOut><SignInButton><button className="ghost">Sign in</button></SignInButton><SignUpButton><button>Start free</button></SignUpButton></SignedOut><SignedIn><Link className="button" href="/dashboard">Open dashboard</Link></SignedIn></div></nav>
    <section className="hero"><p className="eyebrow">DUBLIN HEALTHCARE OPERATIONS</p><h1>Turn operational signals into faster, fairer care.</h1><p className="lede">CarePulse AI is a privacy-safe analytics demo for appointment demand, missed visits, waiting-time pressure, and access across Dublin clinic networks.</p><div className="actions"><SignedOut><SignUpButton><button>Create your account</button></SignUpButton></SignedOut><SignedIn><Link className="button" href="/dashboard">View live dashboard</Link></SignedIn><a className="text-link" href="#privacy">Privacy-first by design →</a></div></section>
    <section className="features"><article><b>Forecast demand</b><span>Plan capacity before pressure builds.</span></article><article><b>Reduce no-shows</b><span>Prioritise outreach using explainable risk signals.</span></article><article><b>Improve access</b><span>See service hotspots across Dublin clinics.</span></article></section>
    <section id="privacy" className="privacy"><b>Privacy-safe portfolio demonstration</b><p>This application uses synthetic data only. It is not a clinical decision-support system and must not be used to make individual patient-care decisions.</p></section>
  </main>;
}
