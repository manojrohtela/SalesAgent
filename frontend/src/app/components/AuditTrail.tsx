import { FileSearch, Hash, Sigma } from "lucide-react";
import { AnswerAudit } from "../api";

interface AuditTrailProps {
  audit?: AnswerAudit;
}

function humanize(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

export function AuditTrail({ audit }: AuditTrailProps) {
  if (!audit) {
    return null;
  }

  const evidence = audit.evidence?.filter(Boolean) ?? [];
  const columnsUsed = audit.columns_used?.filter(Boolean) ?? [];
  const dimensions = audit.dimensions?.filter(Boolean) ?? [];
  const datasetRows = audit.dataset_scope?.rows;

  if (
    !audit.question_type &&
    columnsUsed.length === 0 &&
    evidence.length === 0 &&
    !audit.generated_query &&
    !audit.result_preview
  ) {
    return null;
  }

  return (
    <details className="mt-3 rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.04] px-4 py-3 text-xs text-slate-300">
      <summary className="flex cursor-pointer list-none items-center gap-2 text-cyan-100">
        <FileSearch className="h-3.5 w-3.5" />
        Audit & citations
      </summary>

      <div className="mt-3 space-y-3">
        <div className="flex flex-wrap gap-2">
          {audit.question_type ? (
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
              Intent: {humanize(audit.question_type)}
            </span>
          ) : null}
          {audit.metric ? (
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
              <Sigma className="mr-1 inline h-3 w-3" />
              Metric: {humanize(audit.metric)}
            </span>
          ) : null}
          {typeof datasetRows === "number" ? (
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
              Rows reviewed: {datasetRows.toLocaleString()}
            </span>
          ) : null}
        </div>

        {dimensions.length > 0 ? (
          <p className="text-slate-400">Detected dimensions: {dimensions.map(humanize).join(", ")}</p>
        ) : null}

        {columnsUsed.length > 0 ? (
          <div>
            <p className="mb-2 flex items-center gap-2 text-slate-200">
              <Hash className="h-3.5 w-3.5" />
              Columns used
            </p>
            <div className="flex flex-wrap gap-2">
              {columnsUsed.map((column) => (
                <span
                  key={column}
                  className="rounded-full border border-white/10 bg-[#08111f]/80 px-3 py-1 text-[11px] text-slate-200"
                >
                  {column}
                </span>
              ))}
            </div>
          </div>
        ) : null}

        {evidence.length > 0 ? (
          <div className="space-y-2">
            {evidence.map((item, index) => (
              <div
                key={`audit-evidence-${index}`}
                className="rounded-xl border border-white/8 bg-white/5 px-3 py-2 leading-relaxed text-slate-300"
              >
                {item}
              </div>
            ))}
          </div>
        ) : null}

        {audit.generated_query ? (
          <div className="rounded-xl border border-white/8 bg-[#08111f]/90 px-3 py-3">
            <p className="mb-2 text-slate-200">Generated query</p>
            <code className="block whitespace-pre-wrap break-words text-[11px] leading-relaxed text-cyan-100">
              {audit.generated_query}
            </code>
          </div>
        ) : null}

        {audit.result_preview ? (
          <div className="rounded-xl border border-white/8 bg-white/5 px-3 py-3 text-slate-300">
            <p className="mb-2 text-slate-200">Result preview</p>
            <p className="whitespace-pre-wrap break-words leading-relaxed">{audit.result_preview}</p>
          </div>
        ) : null}
      </div>
    </details>
  );
}
