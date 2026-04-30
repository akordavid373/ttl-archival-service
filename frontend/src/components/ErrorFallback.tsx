import React from "react";

export const ErrorFallback = ({ onRetry }: { onRetry: () => void }) => {
  return (
    <div style={{ padding: 20, textAlign: "center" }}>
      <h3>Oops! Something broke.</h3>
      <p>Please try again.</p>
      <button onClick={onRetry}>Retry</button>
    </div>
  );
};
