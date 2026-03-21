export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface AnalysisResponse {
  structured_report: string;
  charts: Record<string, any>;
  follow_up_questions: string[];
  dataset_summary: string;
  key_insights: string[];
  visual_analysis: string[];
  business_recommendations: string[];
  action_plan: string[];
  stats_snapshot: Record<string, string | number>;
}

export const analyzeDataset = async (
  useDemo: boolean,
  question: string,
  file?: File,
  demoDatasetName?: string
): Promise<AnalysisResponse> => {
  const formData = new FormData();
  if (file) {
    formData.append('file', file);
  } else {
    formData.append('use_demo', String(useDemo));
    if (demoDatasetName) {
      formData.append('demo_dataset_name', demoDatasetName);
    }
  }
  if (question) {
    formData.append('question', question);
  }

  const response = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Analysis failed');
  }

  return response.json();
};
