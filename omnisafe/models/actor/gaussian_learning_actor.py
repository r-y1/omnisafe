# Copyright 2022-2023 OmniSafe Team. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Implementation of GaussianStdNetActor."""

from typing import List

import torch
import torch.nn as nn
from torch.distributions import Distribution, Normal

from omnisafe.models.actor.gaussian_actor import GaussianActor
from omnisafe.typing import Activation, InitFunction, OmnisafeSpace
from omnisafe.utils.model import build_mlp_network


# pylint: disable-next=too-many-instance-attributes
class GaussianLearningActor(GaussianActor):
    """Implementation of GaussianLearningActor."""

    def __init__(
        self,
        obs_space: OmnisafeSpace,
        act_space: OmnisafeSpace,
        hidden_sizes: List[int],
        activation: Activation = 'relu',
        weight_initialization_mode: InitFunction = 'kaiming_uniform',
    ) -> None:
        """Initialize GaussianLearningActor.

        Args:
            obs_space (OmnisafeSpace): Observation space.
            act_space (OmnisafeSpace): Action space.
            hidden_sizes (list): List of hidden layer sizes.
            activation (Activation): Activation function.
            weight_initialization_mode (InitFunction): Weight initialization mode.
            shared (nn.Module): Shared module.
        """
        super().__init__(obs_space, act_space, hidden_sizes, activation, weight_initialization_mode)
        self.mean = build_mlp_network(
            sizes=[self._obs_dim, *self._hidden_sizes, self._act_dim],
            activation=activation,
            weight_initialization_mode=weight_initialization_mode,
        )
        self.log_std = nn.Parameter(torch.zeros(self._act_dim), requires_grad=True)

    def _distribution(self, obs: torch.Tensor) -> Distribution:
        mean = self.mean(obs)
        std = torch.exp(self.log_std)
        return Normal(mean, std)

    def predict(self, obs: torch.Tensor, deterministic: bool = False) -> torch.Tensor:
        self._current_dist = self._distribution(obs)
        self._after_inference = True
        if deterministic:
            return self._current_dist.mean
        return self._current_dist.rsample()

    def forward(self, obs: torch.Tensor) -> Distribution:
        self._current_dist = self._distribution(obs)
        self._after_inference = True
        return self._current_dist

    def log_prob(self, act: torch.Tensor) -> torch.Tensor:
        assert self._after_inference, 'log_prob() should be called after predict() or forward()'
        self._after_inference = False
        return self._current_dist.log_prob(act).sum(axis=-1)

    @property
    def std(self) -> float:
        return torch.exp(self.log_std).mean().item()

    @std.setter
    def std(self, std: float) -> None:
        device = self.log_std.device
        self.log_std.data.fill_(torch.log(torch.tensor(std, device=device)))
