import unittest
import pandas as pd
from src.data.profiler import profile_dataframe
from src.state import SessionStateManager

class TestPhase7Premium(unittest.TestCase):
    def setUp(self):
        SessionStateManager.init_state()
        
    def test_weighted_quality_score_calculation(self):
        # Create a df with missing, duplicate, empty, and mixed columns
        data = {
            "name": ["Alice", "Bob", "Charlie", "Alice"], # 1 duplicate row
            "age": [25, 30, None, 25],                  # 1 null cell
            "empty_col": [None, None, None, None],        # 1 entirely empty column
            "mixed_col": [10, "ten", 10.0, 10]           # 1 mixed column
        }
        df = pd.DataFrame(data)
        
        profile = profile_dataframe(df)
        
        self.assertIn("data_quality_score", profile)
        self.assertIn("data_quality_breakdown", profile)
        
        breakdown = profile["data_quality_breakdown"]
        self.assertEqual(breakdown["empty_cols"], 1)
        self.assertEqual(breakdown["mixed_cols"], 1)
        self.assertEqual(profile["duplicate_rows"], 1)
        self.assertEqual(profile["total_missing_cells"], 5)
        
        # Test math logic
        total_cells = 4 * 4
        expected_missing_factor = (total_cells - 5) / total_cells
        expected_duplicate_factor = 3 / 4
        expected_completeness_factor = 3 / 4
        expected_consistency_factor = 3 / 4
        
        expected_score = (
            (expected_missing_factor * 0.40) + 
            (expected_duplicate_factor * 0.30) + 
            (expected_completeness_factor * 0.15) + 
            (expected_consistency_factor * 0.15)
        ) * 100.0
        
        self.assertAlmostEqual(profile["data_quality_score"], expected_score, places=2)

    def test_voice_ux_state_initialization(self):
        # Ensure voice state is ready
        status = SessionStateManager.get_voice_status()
        self.assertEqual(status, "idle")
        
        SessionStateManager.set_voice_status("transcribing")
        self.assertEqual(SessionStateManager.get_voice_status(), "transcribing")

if __name__ == "__main__":
    unittest.main()
