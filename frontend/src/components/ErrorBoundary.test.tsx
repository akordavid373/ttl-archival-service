import React from "react";
import { render, screen } from "@testing-library/react";
import { ErrorBoundary } from "./ErrorBoundary";

const ProblemChild = () => {
  throw new Error("Test error");
};

describe("ErrorBoundary", () => {
  it("catches errors and displays fallback UI", () => {
    render(
      <ErrorBoundary>
        <ProblemChild />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
  });

  it("renders children when no error", () => {
    render(
      <ErrorBoundary>
        <div>Safe Component</div>
      </ErrorBoundary>
    );

    expect(screen.getByText("Safe Component")).toBeInTheDocument();
  });
});