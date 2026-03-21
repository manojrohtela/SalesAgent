import { motion } from "motion/react";
import { BellRing } from "lucide-react";
import { AlertItem } from "../api";
import { AppCard } from "./ui/AppCard";

interface AlertsCardProps {
  alerts?: AlertItem[];
}

const severityStyles: Record<string, string> = {
  high: "border-rose-400/30 bg-rose-400/10 text-rose-100",
  medium: "border-amber-300/30 bg-amber-300/10 text-amber-100",
  positive: "border-emerald-400/30 bg-emerald-400/10 text-emerald-100",
};

export function AlertsCard({ alerts = [] }: AlertsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: 0.05 }}
    >
      <AppCard className="h-full overflow-hidden border-amber-300/20 bg-[radial-gradient(circle_at_top_right,_rgba(245,158,11,0.14),_rgba(15,23,42,0.97)_60%)]">
        <div className="mb-5 flex items-start gap-4">
          <div className="rounded-2xl bg-gradient-to-br from-amber-300/25 to-rose-400/10 px-4 py-4 text-amber-100">
            <BellRing className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-slate-400">AI Watchlist</p>
            <h3 className="mt-2 text-xl font-semibold text-white">Alerts & Briefing Cadence</h3>
          </div>
        </div>

        <div className="space-y-4">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className="rounded-2xl border border-white/8 bg-white/5 p-4"
            >
              <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                <h4 className="text-sm font-semibold text-white">{alert.title}</h4>
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.2em] ${
                      severityStyles[alert.severity] ?? "border-cyan-400/30 bg-cyan-400/10 text-cyan-100"
                    }`}
                  >
                    {alert.severity}
                  </span>
                  <span className="rounded-full border border-white/10 bg-[#08111f]/80 px-3 py-1 text-[11px] text-slate-300">
                    {alert.cadence}
                  </span>
                </div>
              </div>
              <p className="text-sm leading-7 text-slate-300">{alert.message}</p>
            </div>
          ))}
        </div>
      </AppCard>
    </motion.div>
  );
}
