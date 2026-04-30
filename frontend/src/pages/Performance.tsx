import React from "react";
import { PerformanceDashboard } from "../components/PerformanceDashboard";
import { PrintStyles } from "../components/PrintStyles";

export function Performance() {
  return (
    <PrintStyles title="Performance Dashboard">
      <PerformanceDashboard />
    </PrintStyles>
  );
}
