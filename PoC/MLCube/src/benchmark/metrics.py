from monai.metrics import DiceMetric,HausdorffDistanceMetric


class Metrics():
    def __init__(self, metrics_list):
        self.metrics = []
        for metric in metrics_list:
            if 'DiceMetric' == metric:
                self.metrics.append([Dice(),'DiceMetric'])
            if 'HausdorffDistanceMetric' == metric:
                self.metrics.append([HausdorffDistance(),'HausdorffDistanceMetric'])

    def __getitem__(self,index):
        return self.metrics[index]

class Dice(DiceMetric):
    def __init__(self):
        super().__init__(include_background=True, reduction="mean")

class HausdorffDistance(HausdorffDistanceMetric):
    def __init__(self):
        super().__init__(include_background=True, reduction="mean")