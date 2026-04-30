import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { X, Save, Clock, Shield, Database, Trash2 } from "lucide-react";
import { ArchivalPolicy, PolicyFormData } from "../../types/policy";
import { cn } from "../../utils/cn";

const policySchema = z.object({
  name: z.string().min(3, "Policy name must be at least 3 characters"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  ttl_days: z
    .number()
    .min(1, "Retention period must be at least 1 day")
    .max(3650, "Max retention is 10 years"),
  storage_location: z.string().min(1, "Please select a storage location"),
  compression_enabled: z.boolean().default(true),
  encryption_enabled: z.boolean().default(true),
  auto_cleanup: z.boolean().default(true),
  status: z.enum(["Active", "Inactive", "Draft"]).default("Active"),
});

interface PolicyFormProps {
  policy?: ArchivalPolicy;
  onSubmit: (data: PolicyFormData) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export function PolicyForm({
  policy,
  onSubmit,
  onCancel,
  isSubmitting,
}: PolicyFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<PolicyFormData>({
    resolver: zodResolver(policySchema),
    defaultValues: policy
      ? {
          name: policy.name,
          description: policy.description,
          ttl_days: policy.ttl_days,
          storage_location: policy.storage_location,
          compression_enabled: policy.compression_enabled,
          encryption_enabled: policy.encryption_enabled,
          auto_cleanup: policy.auto_cleanup,
          status: policy.status,
        }
      : {
          name: "",
          description: "",
          ttl_days: 30,
          storage_location: "S3 Standard",
          compression_enabled: true,
          encryption_enabled: true,
          auto_cleanup: true,
          status: "Active",
        },
  });

  const ttlPresets = [
    { label: "7 Days", value: 7 },
    { label: "30 Days", value: 30 },
    { label: "90 Days", value: 90 },
    { label: "1 Year", value: 365 },
  ];

  const currentTtl = watch("ttl_days");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="w-full max-w-2xl bg-card border border-border/50 rounded-[2.5rem] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
        <div className="flex items-center justify-between p-8 border-b border-border/30 bg-accent/5">
          <div className="flex flex-col">
            <h3 className="text-2xl font-bold tracking-tight">
              {policy ? "Edit Archival Policy" : "Create New Policy"}
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              Configure retention rules and storage settings.
            </p>
          </div>
          <button
            onClick={onCancel}
            className="p-3 rounded-2xl hover:bg-accent transition-colors"
          >
            <X className="h-6 w-6 text-muted-foreground" />
          </button>
        </div>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="p-8 space-y-8 max-h-[70vh] overflow-y-auto custom-scrollbar"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
                  Policy Name
                </label>
                <input
                  {...register("name")}
                  placeholder="e.g. System Logs Retention"
                  className={cn(
                    "w-full px-5 py-4 bg-accent/30 rounded-2xl border border-transparent focus:border-primary/50 focus:bg-accent/50 outline-none transition-all",
                    errors.name && "border-rose-500/50",
                  )}
                />
                {errors.name && (
                  <p className="text-[10px] text-rose-500 font-bold ml-2">
                    {errors.name.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
                  Description
                </label>
                <textarea
                  {...register("description")}
                  placeholder="Explain the purpose of this policy..."
                  rows={4}
                  className={cn(
                    "w-full px-5 py-4 bg-accent/30 rounded-2xl border border-transparent focus:border-primary/50 focus:bg-accent/50 outline-none transition-all resize-none",
                    errors.description && "border-rose-500/50",
                  )}
                />
                {errors.description && (
                  <p className="text-[10px] text-rose-500 font-bold ml-2">
                    {errors.description.message}
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Retention Period (Days)
                </label>
                <div className="flex gap-2 mb-3 overflow-x-auto pb-1 no-scrollbar">
                  {ttlPresets.map((preset) => (
                    <button
                      key={preset.value}
                      type="button"
                      onClick={() => setValue("ttl_days", preset.value)}
                      className={cn(
                        "whitespace-nowrap px-4 py-2 text-[10px] font-bold rounded-xl border transition-all",
                        currentTtl === preset.value
                          ? "bg-primary text-primary-foreground border-primary"
                          : "bg-accent/20 text-muted-foreground border-border/40 hover:border-primary/40",
                      )}
                    >
                      {preset.label}
                    </button>
                  ))}
                </div>
                <input
                  type="number"
                  {...register("ttl_days", { valueAsNumber: true })}
                  className={cn(
                    "w-full px-5 py-4 bg-accent/30 rounded-2xl border border-transparent focus:border-primary/50 focus:bg-accent/50 outline-none transition-all",
                    errors.ttl_days && "border-rose-500/50",
                  )}
                />
                {errors.ttl_days && (
                  <p className="text-[10px] text-rose-500 font-bold ml-2">
                    {errors.ttl_days.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                  <Database className="h-4 w-4" />
                  Storage Target
                </label>
                <select
                  {...register("storage_location")}
                  className={cn(
                    "w-full px-5 py-4 bg-accent/30 rounded-2xl border border-transparent focus:border-primary/50 focus:bg-accent/50 outline-none transition-all appearance-none cursor-pointer",
                    errors.storage_location && "border-rose-500/50",
                  )}
                >
                  <option value="S3 Standard">S3 Standard Performance</option>
                  <option value="Glacier Deep">
                    Amazon Glacier Deep Archive
                  </option>
                  <option value="Google Archive">Google Cloud Archive</option>
                  <option value="Azure Blob">Azure Blob Archive Tier</option>
                </select>
                {errors.storage_location && (
                  <p className="text-[10px] text-rose-500 font-bold ml-2">
                    {errors.storage_location.message}
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-6 bg-accent/10 rounded-3xl border border-border/20">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                {...register("compression_enabled")}
                className="w-5 h-5 rounded-lg accent-primary cursor-pointer"
              />
              <label className="text-xs font-bold text-muted-foreground">
                LZ4 Compression
              </label>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                {...register("encryption_enabled")}
                className="w-5 h-5 rounded-lg accent-primary cursor-pointer"
              />
              <label className="text-xs font-bold text-muted-foreground">
                AES-256 Encryption
              </label>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                {...register("auto_cleanup")}
                className="w-5 h-5 rounded-lg accent-primary cursor-pointer"
              />
              <label className="text-xs font-bold text-muted-foreground">
                Auto-Cleanup
              </label>
            </div>
            <div className="flex items-center gap-3">
              <select
                {...register("status")}
                className="bg-transparent text-[10px] font-bold text-primary focus:outline-none cursor-pointer"
              >
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
                <option value="Draft">Draft</option>
              </select>
            </div>
          </div>
        </form>

        <div className="p-8 border-t border-border/30 bg-accent/5 flex items-center justify-end gap-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-3 text-xs font-bold text-muted-foreground hover:bg-accent rounded-2xl transition-all"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit(onSubmit)}
            disabled={isSubmitting}
            className="flex items-center gap-2 px-8 py-3 bg-primary text-primary-foreground font-bold text-sm rounded-2xl shadow-lg shadow-primary/20 hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:scale-100"
          >
            {isSubmitting ? (
              <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            {policy ? "Update Policy" : "Save Policy"}
          </button>
        </div>
      </div>
    </div>
  );
}
