import unittest

import numpy as np

from src.model import SimulationConfig, simulate_pm25


class SimulationConfigTests(unittest.TestCase):
    def test_default_grid_geometry(self) -> None:
        config = SimulationConfig()
        self.assertEqual(config.cell_count, 100)
        self.assertEqual(config.cell_size_km, 0.5)

    def test_rejects_invalid_grid_size(self) -> None:
        with self.assertRaises(ValueError):
            SimulationConfig(grid_size=2)


class SimulationTests(unittest.TestCase):
    def test_output_shape_and_range(self) -> None:
        config = SimulationConfig(hours=4, grid_size=6)
        history = simulate_pm25(config)
        self.assertEqual(history.shape, (4, 6, 6))
        self.assertTrue(np.isfinite(history).all())
        self.assertTrue((history >= 0).all())

    def test_seed_makes_simulation_reproducible(self) -> None:
        config = SimulationConfig(hours=3)
        np.testing.assert_array_equal(simulate_pm25(config), simulate_pm25(config))


if __name__ == "__main__":
    unittest.main()
