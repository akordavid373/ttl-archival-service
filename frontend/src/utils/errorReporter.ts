export function reportError(error: Error, errorInfo?: any) {
  console.error("Captured Error:", error, errorInfo);

  // Example integration (Sentry, LogRocket, etc.)
  if (typeof window !== "undefined") {
    fetch("/api/log-error", {
      method: "POST",
      body: JSON.stringify({
        message: error.message,
        stack: error.stack,
        info: errorInfo,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    }).catch(() => {});
  }
}
