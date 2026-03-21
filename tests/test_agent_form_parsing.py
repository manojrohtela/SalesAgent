import unittest
from unittest.mock import patch

import pandas as pd
from fastapi.testclient import TestClient

from backend.agent import AnalysisResponse, app


class AnalyzeFormParsingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch("backend.agent._run_full_analysis")
    @patch("backend.agent._ensure_demo_dataset")
    def test_question_is_parsed_from_multipart_form_data_without_file(
        self,
        mock_ensure_demo_dataset,
        mock_run_full_analysis,
    ) -> None:
        mock_ensure_demo_dataset.return_value = pd.DataFrame(
            {"date": ["2026-01-01"], "revenue": [10]}
        )
        mock_run_full_analysis.return_value = AnalysisResponse(
            structured_report="ok",
            charts={},
            follow_up_questions=[],
            dataset_summary="Rows: 1, Columns: 2",
            key_insights=[],
            visual_analysis=[],
            business_recommendations=[],
            action_plan=[],
            stats_snapshot={},
        )

        response = self.client.post(
            "/analyze",
            files={
                "use_demo": (None, "true"),
                "question": (None, "what is total revenue?"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["structured_report"], "ok")
        self.assertEqual(
            mock_run_full_analysis.call_args.kwargs["user_question"],
            "what is total revenue?",
        )

    @patch("backend.agent._run_full_analysis")
    def test_question_is_parsed_from_multipart_form_data_with_file(
        self,
        mock_run_full_analysis,
    ) -> None:
        mock_run_full_analysis.return_value = AnalysisResponse(
            structured_report="ok",
            charts={},
            follow_up_questions=[],
            dataset_summary="Rows: 1, Columns: 3",
            key_insights=[],
            visual_analysis=[],
            business_recommendations=[],
            action_plan=[],
            stats_snapshot={},
        )

        response = self.client.post(
            "/analyze",
            data={"question": "show me the top region"},
            files={
                "file": (
                    "sales.csv",
                    b"date,revenue,region\n2026-01-01,100,North\n",
                    "text/csv",
                )
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["structured_report"], "ok")
        self.assertEqual(
            mock_run_full_analysis.call_args.kwargs["user_question"],
            "show me the top region",
        )

    def test_compare_endpoint_accepts_current_and_comparison_files(self) -> None:
        response = self.client.post(
            "/compare",
            files={
                "primary_file": (
                    "baseline.csv",
                    b"date,revenue,region\n2026-01-01,100,North\n2026-01-02,150,South\n",
                    "text/csv",
                ),
                "comparison_file": (
                    "candidate.csv",
                    b"date,revenue,region\n2026-01-01,120,North\n2026-01-02,190,South\n",
                    "text/csv",
                ),
            },
            data={"primary_use_demo": "false"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["baseline_label"], "baseline.csv")
        self.assertEqual(payload["comparison_label"], "candidate.csv")
        self.assertEqual(payload["primary_metric"], "revenue")
        self.assertIn("comparison_summary", payload)
        self.assertGreaterEqual(len(payload["cards"]), 3)


if __name__ == "__main__":
    unittest.main()
