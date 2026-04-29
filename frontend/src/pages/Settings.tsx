import React from "react";
import { SEO } from "../components/common/SEO";
import { ThemePicker } from "../components/theme/ThemePicker";
import { User, Lock, Bell, Globe, CreditCard, Monitor } from "lucide-react";

export const Settings: React.FC = () => {
  const categories = [
    { label: "Appearance", icon: Monitor, active: true },
    { label: "Profile", icon: User },
    { label: "Security", icon: Lock },
    { label: "Notifications", icon: Bell },
    { label: "Network", icon: Globe },
    { label: "Billing", icon: CreditCard },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <SEO
        title="Settings"
        description="Customize your account and application appearance."
      />

      <div>
        <h2 className="text-3xl font-bold">Settings</h2>
        <p className="text-gray-500">
          Manage your account preferences and customize your experience.
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar */}
        <aside className="w-full md:w-64 shrink-0">
          <nav className="space-y-1">
            {categories.map((cat) => (
              <button
                key={cat.label}
                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all
                  ${
                    cat.active
                      ? "bg-white dark:bg-gray-900 shadow-sm text-primary font-semibold"
                      : "text-gray-500 hover:bg-white/50 dark:hover:bg-gray-900/50"
                  }
                `}
              >
                <cat.icon className="w-5 h-5" />
                {cat.label}
              </button>
            ))}
          </nav>
        </aside>

        {/* Content */}
        <div className="flex-1">
          <ThemePicker />

          <div className="mt-8 p-6 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
            <h3 className="text-xl font-bold mb-4">Export All Data</h3>
            <p className="text-sm text-gray-500 mb-6">
              Download all your settings, archives, and policies in a single
              JSON file for backup or migration.
            </p>
            <button className="px-6 py-3 bg-gray-100 dark:bg-gray-800 rounded-xl font-medium hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
              Prepare Export
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
