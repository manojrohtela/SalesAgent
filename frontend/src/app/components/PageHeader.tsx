import { ReactNode } from "react";
import { IconContainer } from "./ui/IconContainer";
import { LucideIcon } from "lucide-react";

interface PageHeaderProps {
  title: string;
  icon: LucideIcon;
  action?: ReactNode;
}

export function PageHeader({ title, icon, action }: PageHeaderProps) {
  return (
    <div className="border-b border-gray-800 bg-[#1e293b]/50 backdrop-blur-sm sticky top-0 z-10">
      <div className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <IconContainer icon={icon} />
          <h1 className="text-2xl font-bold">{title}</h1>
        </div>
        {action && <div>{action}</div>}
      </div>
    </div>
  );
}
