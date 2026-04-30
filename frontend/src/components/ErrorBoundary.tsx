import React, { Component, ErrorInfo, ReactNode } from "react";
import { reportError } from "../utils/errorReporter";

type Props = {
  children: ReactNode;
  fallback?: ReactNode;
};

type State = {
  hasError: boolean;
  error?: Error;
};

export class ErrorBoundary extends Component<Props, State> {
  state: State = {
    hasError: false,
  };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    reportError(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div style={styles.container}>
          <h2>Something went wrong.</h2>
          <p>{this.state.error?.message}</p>

          <button onClick={this.handleRetry} style={styles.button}>
            Retry
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

const styles = {
  container: {
    padding: "20px",
    textAlign: "center" as const,
  },
  button: {
    marginTop: "10px",
    padding: "8px 16px",
    cursor: "pointer",
  },
};
