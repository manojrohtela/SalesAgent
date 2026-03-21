import { motion } from "motion/react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { AppCard } from "./ui/AppCard";

interface ChartCardProps {
  title: string;
  type: "line" | "bar" | "pie" | "area";
}

// Sample data
const lineData = [
  { name: "Jan", value: 4000 },
  { name: "Feb", value: 3000 },
  { name: "Mar", value: 5000 },
  { name: "Apr", value: 4500 },
  { name: "May", value: 6000 },
  { name: "Jun", value: 5500 },
];

const barData = [
  { name: "Electronics", value: 4000 },
  { name: "Clothing", value: 3000 },
  { name: "Food", value: 2000 },
  { name: "Books", value: 2780 },
  { name: "Toys", value: 1890 },
];

const pieData = [
  { name: "18-25", value: 400 },
  { name: "26-35", value: 300 },
  { name: "36-45", value: 300 },
  { name: "46+", value: 200 },
];

const areaData = [
  { name: "Week 1", value: 2400 },
  { name: "Week 2", value: 1398 },
  { name: "Week 3", value: 9800 },
  { name: "Week 4", value: 3908 },
];

const COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b"];

export function ChartCard({ title, type }: ChartCardProps) {
  const renderChart = () => {
    switch (type) {
      case "line":
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={lineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#fff",
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#6366f1"
                strokeWidth={3}
                dot={{ fill: "#6366f1", r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case "bar":
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#fff",
                }}
              />
              <Bar dataKey="value" fill="#6366f1" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case "pie":
        return (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#fff",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        );

      case "area":
        return (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={areaData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#fff",
                }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#6366f1"
                fill="#6366f1"
                fillOpacity={0.3}
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <AppCard hover>
        <h3 className="text-lg font-semibold mb-4 text-gray-100">{title}</h3>
        <div className="h-64">{renderChart()}</div>
      </AppCard>
    </motion.div>
  );
}