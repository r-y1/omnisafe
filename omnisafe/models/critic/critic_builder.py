# Copyright 2023 OmniSafe Team. All Rights Reserved.
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
"""Implementation of CriticBuilder."""

from typing import List

from omnisafe.models.base import Critic
from omnisafe.models.critic.q_critic import QCritic
from omnisafe.models.critic.v_critic import VCritic
from omnisafe.typing import Activation, CriticType, InitFunction, OmnisafeSpace


# pylint: disable-next=too-few-public-methods
class CriticBuilder:
    """Implementation of CriticBuilder

    .. note::

        A :class:`CriticBuilder` is a class for building a critic network.
        In ``omnisafe``, instead of building the critic network directly,
        we build it by integrating various types of critic networks into the :class:`CriticBuilder`.
        The advantage of this is that each type of critic has a uniform way of passing parameters.
        This makes it easy for users to use existing critics,
        and also facilitates the extension of new critic types.
    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        obs_space: OmnisafeSpace,
        act_space: OmnisafeSpace,
        hidden_sizes: List[int],
        activation: Activation = 'relu',
        weight_initialization_mode: InitFunction = 'kaiming_uniform',
        num_critics: int = 1,
        use_obs_encoder: bool = False,
    ) -> None:
        """Initialize CriticBuilder.

        Args:
            obs_space (OmnisafeSpace): Observation space.
            act_space (OmnisafeSpace): Action space.
            hidden_sizes (List[int]): Hidden sizes of the critic network.
            activation (Activation): Activation function.
            weight_initialization_mode (InitFunction): Weight initialization mode.
            num_critics (int): Number of critics.
            use_obs_encoder (bool): Whether to use observation encoder, only used in q critic.
        """
        self._obs_space = obs_space
        self._act_space = act_space
        self._weight_initialization_mode = weight_initialization_mode
        self._activation = activation
        self._hidden_sizes = hidden_sizes
        self._num_critics = num_critics
        self._use_obs_encoder = use_obs_encoder

    def build_critic(
        self,
        critic_type: CriticType,
    ) -> Critic:
        """Build critic.

        Currently, we support two types of critics: ``q`` and ``v``.
        If you want to add a new critic type, you can simply add it here.

        Args:
            critic_type (str): Critic type.
        """
        if critic_type == 'q':
            return QCritic(
                obs_space=self._obs_space,
                act_space=self._act_space,
                hidden_sizes=self._hidden_sizes,
                activation=self._activation,
                weight_initialization_mode=self._weight_initialization_mode,
                num_critics=self._num_critics,
                use_obs_encoder=self._use_obs_encoder,
            )
        if critic_type == 'v':
            return VCritic(
                obs_space=self._obs_space,
                act_space=self._act_space,
                hidden_sizes=self._hidden_sizes,
                activation=self._activation,
                weight_initialization_mode=self._weight_initialization_mode,
                num_critics=self._num_critics,
            )

        raise NotImplementedError(
            f'critic_type "{critic_type}" is not implemented.'
            'Available critic types are: "q", "v".'
        )
