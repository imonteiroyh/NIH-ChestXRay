from typing import Any, Callable, Dict, Iterable, Tuple

import pytorch_lightning as L
import torch

from xrkit.models.base import AutoEncoder, BaseModel
from xrkit.models.unet import UNet
from xrkit.models.xception import Xception
from xrkit.segmentation import (
    DiceBCELoss,
    average_surface_distance,
    balanced_average_hausdorff_distance,
    dice,
    jaccard_index,
)

# mypy: disable-error-code="misc"


class XceptionUNetModel(L.LightningModule, BaseModel):
    def __init__(self, n_epochs: int) -> None:
        super().__init__()

        encoder = Xception()
        decoder = UNet()
        network = AutoEncoder(encoder=encoder, decoder=decoder)
        criterion = DiceBCELoss()
        metrics: Iterable[Tuple[Callable, Dict[str, Any]]] = (
            (dice, {}),
            (jaccard_index, {"average": "macro"}),
            (balanced_average_hausdorff_distance, {}),
            (average_surface_distance, {}),
        )
        activation_function = torch.sigmoid
        optimizer = torch.optim.Adam(network.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)

        self.save_hyperparameters()
        self.setup_model(
            network=network,
            criterion=criterion,
            metrics=metrics,
            activation_function=activation_function,
            optimizer=optimizer,
            scheduler=scheduler,
        )


if __name__ == "__main__":
    input = torch.rand((4, 1, 256, 256))

    model = XceptionUNetModel(n_epochs=1).network
    print(model(input).shape)