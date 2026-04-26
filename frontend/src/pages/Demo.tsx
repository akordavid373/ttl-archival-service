import React, { useState } from 'react';
import OptimizedImage from '../components/common/OptimizedImage';
import FormWizard from '../components/common/FormWizard';
import { useVariant } from '../context/ABTestingContext';
import { useTracking } from '../services/analytics';

const Step1 = ({ formData, updateData }: any) => (
  <div className="space-y-4">
    <h3 className="text-lg font-semibold">Step 1: Personal Info</h3>
    <input
      type="text"
      placeholder="Name"
      className="w-full p-2 border rounded"
      value={formData.name || ''}
      onChange={(e) => updateData({ name: e.target.value })}
    />
  </div>
);

const Step2 = ({ formData, updateData }: any) => (
  <div className="space-y-4">
    <h3 className="text-lg font-semibold">Step 2: Preferences</h3>
    <select
      className="w-full p-2 border rounded"
      value={formData.theme || 'light'}
      onChange={(e) => updateData({ theme: e.target.value })}
    >
      <option value="light">Light</option>
      <option value="dark">Dark</option>
    </select>
  </div>
);

const Step3 = ({ formData }: any) => (
  <div className="space-y-4">
    <h3 className="text-lg font-semibold">Step 3: Review</h3>
    <pre className="p-4 bg-gray-50 rounded">{JSON.stringify(formData, null, 2)}</pre>
  </div>
);

export const Demo: React.FC = () => {
  const ctaVariant = useVariant('hero_cta_color');
  const { trackClick } = useTracking();
  const [wizardComplete, setWizardComplete] = useState(false);

  const steps = [
    { id: 'personal', title: 'Personal', component: <Step1 /> },
    { id: 'prefs', title: 'Preferences', component: <Step2 /> },
    { id: 'review', title: 'Review', component: <Step3 /> },
  ];

  const getButtonColor = (variant: string) => {
    switch (variant) {
      case 'green': return 'bg-green-600 hover:bg-green-700';
      case 'indigo': return 'bg-indigo-600 hover:bg-indigo-700';
      default: return 'bg-blue-600 hover:bg-blue-700';
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-12">
      <section>
        <h2 className="text-2xl font-bold mb-4">#149 A/B Testing & #151 Analytics</h2>
        <div className="p-6 border rounded-xl bg-white shadow-sm">
          <p className="mb-4">Current CTA Variant: <span className="font-mono font-bold">{ctaVariant}</span></p>
          <button
            onClick={() => trackClick('A/B Test CTA Click', { variant: ctaVariant })}
            className={`px-8 py-3 text-white font-bold rounded-lg transition-all ${getButtonColor(ctaVariant)}`}
          >
            Track Conversion
          </button>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">#144 Optimized Image</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <p className="mb-2 text-sm text-gray-500">Standard Optimized Image (Lazy, Blur-up)</p>
            <OptimizedImage
              src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=1000"
              webpSrc="https://images.unsplash.com/photo-1451187580459-43490279c0fa?fm=webp&w=1000"
              lowResSrc="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=10&w=100"
              alt="Space"
              aspectRatio="16/9"
              className="rounded-xl shadow-lg"
            />
          </div>
          <div>
            <p className="mb-2 text-sm text-gray-500">Feature Highlight</p>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>WebP format support</li>
              <li>Low-res preview (Blur-up)</li>
              <li>Lazy loading enabled</li>
              <li>Responsive container</li>
            </ul>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">#145 Multi-step Form Wizard</h2>
        {wizardComplete ? (
          <div className="p-12 text-center bg-green-50 rounded-xl border border-green-200">
            <h3 className="text-xl font-bold text-green-800 mb-2">Form Submitted!</h3>
            <p className="text-green-700">Check your localStorage (key: 'demo-wizard') to see the persisted data.</p>
            <button
              onClick={() => setWizardComplete(false)}
              className="mt-4 text-indigo-600 hover:underline"
            >
              Start Over
            </button>
          </div>
        ) : (
          <FormWizard
            steps={steps}
            persistenceKey="demo-wizard"
            onComplete={(data) => {
              console.log('Wizard Complete:', data);
              trackClick('Form Wizard Completed');
              setWizardComplete(true);
            }}
          />
        )}
      </section>
    </div>
  );
};
