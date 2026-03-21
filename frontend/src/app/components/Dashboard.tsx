import { useNavigate } from "react-router";
import { Database } from "lucide-react";
import { ChartCard } from "./ChartCard";
import { BackgroundGradient } from "./ui/BackgroundGradient";
import { PageHeader } from "./PageHeader";
import { ChatPanel } from "./ChatPanel";
import { Grid } from "./ui/Grid";

export function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#0f172a] text-white relative overflow-hidden">
      <BackgroundGradient variant="subtle" />

      <PageHeader
        title="Sales Agent"
        icon={Database}
        action={
          <button
            onClick={() => navigate("/")}
            className="px-5 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium transition-all duration-300 hover:scale-105"
          >
            Change Data
          </button>
        }
      />

      {/* Main Layout - Auto-layout with flexbox */}
      <div className="flex flex-col lg:flex-row h-[calc(100vh-73px)] relative">
        {/* Left Side - Charts - Flexible width */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 relative z-10">
          <Grid cols={{ default: 1, xl: 2 }} gap={6} className="max-w-7xl mx-auto">
            <ChartCard title="Revenue Trend" type="line" />
            <ChartCard title="Sales by Category" type="bar" />
            <ChartCard title="Customer Distribution" type="pie" />
            <ChartCard title="Monthly Performance" type="area" />
            <ChartCard title="Product Comparison" type="bar" />
            <ChartCard title="Growth Rate" type="line" />
          </Grid>
        </div>

        {/* Right Side - Chat Panel - Responsive width */}
        <ChatPanel />
      </div>
    </div>
  );
}