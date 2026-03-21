import { useState } from "react";
import { TrendingUp, ShoppingCart, Users } from "lucide-react";
import { motion } from "motion/react";
import { LoadingScreen } from "./LoadingScreen";
import { useNavigate } from "react-router";
import { BackgroundGradient } from "./ui/BackgroundGradient";
import { DatasetCard } from "./DatasetCard";
import { UploadSection } from "./UploadSection";
import { Container } from "./ui/Container";
import { Grid } from "./ui/Grid";
import { Section } from "./ui/Section";

const dummyDatasets = [
  {
    id: 1,
    name: "E-commerce Sales",
    description: "Product sales, revenue, and customer data",
    rows: 10000,
    columns: 8,
    icon: ShoppingCart,
  },
  {
    id: 2,
    name: "Customer Analytics",
    description: "User behavior, demographics, and engagement",
    rows: 25000,
    columns: 12,
    icon: Users,
  },
  {
    id: 3,
    name: "Revenue Growth",
    description: "Monthly revenue, expenses, and profit margins",
    rows: 5000,
    columns: 6,
    icon: TrendingUp,
  },
];

export function Landing() {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleDatasetSelect = () => {
    setIsLoading(true);
    setTimeout(() => {
      navigate("/dashboard");
    }, 3000);
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-white relative overflow-hidden">
      <BackgroundGradient />

      <Container maxWidth="xl" className="py-12 sm:py-20 relative z-10">
        {/* Header */}
        <Section animate className="mb-12 sm:mb-16">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Sales Agent
            </h1>
            <p className="text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto px-4">
              Turn your data into actionable insights with AI
            </p>
          </div>
        </Section>

        {/* Upload Section */}
        <Section className="mb-12 sm:mb-16">
          <UploadSection />
        </Section>

        {/* Dummy Data Section */}
        <Section
          subtitle="Or try with sample data"
          animate
          delay={0.4}
        >
          <Grid cols={{ default: 1, md: 2, lg: 3 }} gap={6}>
            {dummyDatasets.map((dataset, index) => (
              <DatasetCard
                key={dataset.id}
                name={dataset.name}
                description={dataset.description}
                rows={dataset.rows}
                columns={dataset.columns}
                icon={dataset.icon}
                onSelect={handleDatasetSelect}
                delay={0.5 + index * 0.1}
              />
            ))}
          </Grid>
        </Section>
      </Container>
    </div>
  );
}