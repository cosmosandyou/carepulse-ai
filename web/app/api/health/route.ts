import { NextResponse } from "next/server";

export function GET() {
  return NextResponse.json({ status: "ok", service: "carepulse-ai-web", dataClassification: "synthetic" });
}
