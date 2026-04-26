import { render, screen } from "@testing-library/react";
import { ChartDashboard } from "./ChartDashboard";

describe("ChartDashboard", () => {
  it("renders dashboard title", () => {
    render(<ChartDashboard />);
    expect(screen.getByText(/Export Dashboard/i)).toBeInTheDocument();
  });
});