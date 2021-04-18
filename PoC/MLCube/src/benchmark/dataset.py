from monai.data import CacheDataset

class DataSet(CacheDataset):
    def __init__(self, dataset, transforms):
        super().__init__(data=dataset, transform=transforms)