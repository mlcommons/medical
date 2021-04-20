
from monai.transforms import (
    Activations,
    AsDiscrete,
    AsChannelFirstd,
    ConvertToMultiChannelBasedOnBratsClassesd,
    CenterSpatialCropd,
    Compose,
    LoadImaged,
    MapTransform,
    NormalizeIntensityd,
    Orientationd,
    RandFlipd,
    RandScaleIntensityd,
    RandShiftIntensityd,
    RandSpatialCropd,
    Spacingd,
    ToTensord,
)

class Tranforms(Compose):
    def __init__(self, tranforms):
        self.tranform_list = []
        for tranform in tranforms:
            if 'LoadImaged' == tranform:
                self.tranform_list.append(LoadImaged(keys=["image", "label"]))
            elif 'AsChannelFirstd' == tranform:
                self.tranform_list.append(AsChannelFirstd(keys="image"))
            elif 'ConvertToMultiChannelBasedOnBratsClassesd' == tranform:
                self.tranform_list.append(ConvertToMultiChannelBasedOnBratsClassesd(keys="label"))
            elif 'Spacingd' == tranform:
                self.tranform_list.append(Spacingd(keys=["image", "label"], pixdim=(1.5, 1.5, 2.0), mode=("bilinear", "nearest")))
            elif 'Orientationd' == tranform:
                self.tranform_list.append(Orientationd(keys=["image", "label"], axcodes="RAS"))
            elif 'CenterSpatialCropd' == tranform:
                self.tranform_list.append(CenterSpatialCropd(keys=["image", "label"], roi_size=[128, 128, 64]))
            elif 'NormalizeIntensityd' == tranform:
                self.tranform_list.append(NormalizeIntensityd(keys="image", nonzero=True, channel_wise=True))
            elif 'ToTensord' == tranform:
                self.tranform_list.append(ToTensord(keys=["image", "label"]))
            elif 'Activations' == tranform:
                self.tranform_list.append(Activations(sigmoid=True))
            elif 'AsDiscrete' == tranform:
                self.tranform_list.append(AsDiscrete(threshold_values=True))
            else:
                raise ValueError(
                    f"Unsupported tranform: {tranform}. Please add it to support it."
                )

        super().__init__(self.tranform_list)
