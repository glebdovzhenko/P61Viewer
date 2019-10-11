from NexusHistogram import NexusHistogram


class AppState:
    def __init__(self):
        self._histograms = []

    def get_histogram(self, idx: int) -> NexusHistogram:
        return self._histograms[idx]

    def set_histogram(self, idx: int, value: NexusHistogram):
        self._histograms[idx] = value

    def histogram_list_len(self) -> int:
        return len(self._histograms)

    def del_histograms(self, r1, r2):
        del self._histograms[r1:r2]

    def insert_histograms(self, row, count):
        self._histograms = self._histograms[:row] + [NexusHistogram() for _ in range(count)] + self._histograms[row:]

    def get_hist_ids(self):
        return [x.dataset_id for x in self._histograms]

    def get_plot_lines(self):
        return [x.plot_line for x in self._histograms if x.active]