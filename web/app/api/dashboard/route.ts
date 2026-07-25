import { NextResponse } from "next/server";
import { getDashboardData } from "../../../lib/dashboard-data";

export function GET() {
  return NextResponse.json(getDashboardData(), { headers: { "Cache-Control": "no-store" } });
}
