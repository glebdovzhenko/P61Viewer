import unittest
import lmfit_utils


class TestGetPeakIntervals(unittest.TestCase):
    """"""
    def test_two_peaks(self):
        md = None
        md = lmfit_utils.add_md(name='GaussianModel', init_params={'center': 0, 'sigma': 1}, composite=md)
        md = lmfit_utils.add_md(name='GaussianModel', init_params={'center': 1, 'sigma': 1}, composite=md)

        self.assertEqual(lmfit_utils.utils.get_peak_intervals(md), [[-3.0, 4.0]])


if __name__ == '__main__':
    unittest.main()
