import React, { useState, useEffect } from "react";

interface Step {
  id: string;
  title: string;
  component: React.ReactNode;
  isValid?: boolean;
}

interface FormWizardProps {
  steps: Step[];
  onComplete: (data: any) => void;
  persistenceKey?: string;
}

const FormWizard: React.FC<FormWizardProps> = ({
  steps,
  onComplete,
  persistenceKey,
}) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [formData, setFormData] = useState<Record<string, any>>({});

  useEffect(() => {
    if (persistenceKey) {
      const saved = localStorage.getItem(persistenceKey);
      if (saved) {
        setFormData(JSON.parse(saved));
      }
    }
  }, [persistenceKey]);

  const handleNext = () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1);
    } else {
      onComplete(formData);
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1);
    }
  };

  const updateData = (newData: Record<string, any>) => {
    const updated = { ...formData, ...newData };
    setFormData(updated);
    if (persistenceKey) {
      localStorage.setItem(persistenceKey, JSON.stringify(updated));
    }
  };

  const progress = ((currentStepIndex + 1) / steps.length) * 100;

  return (
    <div className="form-wizard max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-lg">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          {steps.map((step, index) => (
            <div key={step.id} className="flex flex-col items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 ${
                  index <= currentStepIndex
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-200 text-gray-500"
                }`}
              >
                {index + 1}
              </div>
              <span className="text-xs mt-2 font-medium text-gray-600">
                {step.title}
              </span>
            </div>
          ))}
        </div>
        <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
          <div
            className="bg-indigo-600 h-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="wizard-content min-h-[300px] mb-8">
        {React.cloneElement(
          steps[currentStepIndex].component as React.ReactElement,
          {
            formData,
            updateData,
            onNext: handleNext,
          },
        )}
      </div>

      <div className="flex justify-between pt-6 border-t border-gray-100">
        <button
          onClick={handleBack}
          disabled={currentStepIndex === 0}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            currentStepIndex === 0
              ? "bg-gray-100 text-gray-400 cursor-not-allowed"
              : "bg-white text-gray-700 hover:bg-gray-50 border border-gray-300"
          }`}
        >
          Back
        </button>
        <button
          onClick={handleNext}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
        >
          {currentStepIndex === steps.length - 1 ? "Finish" : "Next"}
        </button>
      </div>
    </div>
  );
};

export default FormWizard;
