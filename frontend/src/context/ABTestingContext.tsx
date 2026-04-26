import React, { createContext, useContext, useState, useEffect } from 'react';
import { analytics } from '../services/analytics';

interface Experiment {
  id: string;
  variants: string[];
  weights?: number[];
}

interface ABTestingContextType {
  getVariant: (experimentId: string) => string;
  allVariants: Record<string, string>;
}

const ABTestingContext = createContext<ABTestingContextType | undefined>(undefined);

const EXPERIMENTS: Experiment[] = [
  { id: 'hero_cta_color', variants: ['blue', 'green', 'indigo'] },
  { id: 'pricing_layout', variants: ['standard', 'simplified'] },
];

export const ABTestingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [assignments, setAssignments] = useState<Record<string, string>>({});

  useEffect(() => {
    const storedAssignments = localStorage.getItem('ab_test_assignments');
    let currentAssignments = storedAssignments ? JSON.parse(storedAssignments) : {};
    let updated = false;

    EXPERIMENTS.forEach((exp) => {
      if (!currentAssignments[exp.id]) {
        const randomIndex = Math.floor(Math.random() * exp.variants.length);
        currentAssignments[exp.id] = exp.variants[randomIndex];
        updated = true;
        
        // Track the assignment
        analytics.trackEvent({
          category: 'A/B Test',
          action: 'Assignment',
          label: `${exp.id}: ${currentAssignments[exp.id]}`,
        });
      }
    });

    if (updated) {
      localStorage.setItem('ab_test_assignments', JSON.stringify(currentAssignments));
    }
    setAssignments(currentAssignments);
  }, []);

  const getVariant = (experimentId: string) => {
    return assignments[experimentId] || EXPERIMENTS.find(e => e.id === experimentId)?.variants[0] || 'default';
  };

  return (
    <ABTestingContext.Provider value={{ getVariant, allVariants: assignments }}>
      {children}
    </ABTestingContext.Provider>
  );
};

export const useVariant = (experimentId: string) => {
  const context = useContext(ABTestingContext);
  if (!context) {
    throw new Error('useVariant must be used within an ABTestingProvider');
  }
  return context.getVariant(experimentId);
};
