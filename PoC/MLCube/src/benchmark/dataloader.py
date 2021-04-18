from torch.utils.data import DataLoader

class DataLoader(DataLoader):
    def __init__(self, dataset, num_workers=0):
        super().__init__(dataset=dataset,num_workers=num_workers)