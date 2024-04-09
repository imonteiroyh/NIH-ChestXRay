from typing import Any, Callable, Dict, Iterable, Tuple

import pytorch_lightning as L
import torch

from xrkit.models.base import AutoEncoder, BaseModel
from xrkit.models.densenet201 import DenseNet201
from xrkit.models.unet import UNet
from xrkit.segmentation import (
    DiceBCELoss,
    average_surface_distance,
    balanced_average_hausdorff_distance,
    dice,
    jaccard_index,
)

# mypy: disable-error-code="misc"


class DenseNet201UNetModel(L.LightningModule, BaseModel):
    def __init__(self, n_epochs: int) -> None:
        """
        Initializes DenseNet201UNetModel.

        Parameters:
            n_epochs (int):
                Number of epochs for training.
        """

        super().__init__()

        encoder = DenseNet201()
        decoder = UNet()
        network = AutoEncoder(encoder=encoder, decoder=decoder)
        criterion = DiceBCELoss()
        metrics: Iterable[Tuple[Callable, Dict[str, Any]]] = (
            (dice, {}),
            (jaccard_index, {"average": "weighted"}),
            (balanced_average_hausdorff_distance, {}),
            (average_surface_distance, {"threshold": 0.3}),
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