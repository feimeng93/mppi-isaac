from mppiisaac.planner.isaacgym_wrapper import IsaacGymWrapper, ActorWrapper
from mppiisaac.utils.transport import bytes_to_torch, torch_to_bytes
from mppi_torch.mppi import MPPIPlanner as MPPIPlanner
import mppiisaac
from typing import Callable, Optional
import io
import os
import yaml
from yaml.loader import SafeLoader

from isaacgym import gymtorch
import torch


torch.set_printoptions(precision=2, sci_mode=False)


class MPPIisaacPlanner(object):
    """
    Wrapper class that inherits from the MPPIPlanner and implements the required functions:
        dynamics, running_cost, and terminal_cost
    """

    def __init__(self, cfg, objective: Callable, prior: Optional[Callable] = None):
        self.cfg = cfg
        self.objective = objective
        self.done = False

        self.sim = IsaacGymWrapper(
            cfg.isaacgym,
            actors=cfg.actors,
            obs_actors=cfg.obs_actors,
            init_positions=cfg.initial_actor_positions,
            num_envs=cfg.mppi.num_samples, 
            device=cfg.mppi.device,
            # viewer=True
        )

        if prior:
            self.prior = lambda state, t: prior.compute_command(self.sim)
        else:
            self.prior = None

        self.mppi = MPPIPlanner(
            cfg.mppi,
            cfg.nx,
            dynamics=self.dynamics,
            running_cost=self.running_cost,
            prior=self.prior,
        )

        # Note: place_holder variable to pass to mppi so it doesn't complain, while the real state is actually the isaacgym simulator itself.
        self.state_place_holder = torch.zeros((self.cfg.mppi.num_samples, self.cfg.nx))
    
    def update_objective(self, objective):
        self.objective = objective

    def dynamics(self, _, u, t=None):
        # Note: normally mppi passes the state as the first parameter in a dynamics call, but using isaacgym the state is already saved in the simulator itself, so we ignore it.
        # Note: t is an unused step dependent dynamics variable

        self.sim.apply_robot_cmd(u)

        self.sim.step()

        return (self.state_place_holder, u)

    def running_cost(self, _):
        # Note: again normally mppi passes the state as a parameter in the running cost call, but using isaacgym the state is already saved and accesible in the simulator itself, so we ignore it and pass a handle to the simulator.
        return self.objective.compute_cost(self.sim)

    def compute_action(self, q, qdot, obst=None, obst_tensor=None):
        self.sim.reset_root_state()
        self.sim.reset_robot_state(q, qdot)

        # NOTE: There are two different ways of updating obstacle root_states
        # Both update based on id in the list of obstacles
        if obst:
            self.sim.update_root_state_tensor_by_obstacles(obst)

        if obst_tensor:
            self.sim.update_root_state_tensor_by_obstacles_tensor(obst_tensor)

        self.sim.save_root_state()
        actions = self.mppi.command(self.state_place_holder).cpu()
        return actions

    def reset_rollout_sim(
        self, dof_state_tensor, root_state_tensor, rigid_body_state_tensor=None
    ):
        self.sim.visualize_link_buffer = []
        self.sim._dof_state[:] = bytes_to_torch(dof_state_tensor)
        self.sim._root_state[:] = bytes_to_torch(root_state_tensor)

        self.sim._gym.set_dof_state_tensor(
            self.sim._sim, gymtorch.unwrap_tensor(self.sim._dof_state)
        )
        self.sim._gym.set_actor_root_state_tensor(
            self.sim._sim, gymtorch.unwrap_tensor(self.sim._root_state)
        )

        # Not implemented by nvidia
        # self.sim._rigid_body_state[:] = bytes_to_torch(rigid_body_state_tensor)
        # self.sim._gym.set_rigid_body_state_tensor(
        #     self.sim._sim, gymtorch.unwrap_tensor(self.sim._rigid_body_state)
        # )

    def compute_action_tensor(self, dof_state_tensor, root_state_tensor):
        self.objective.reset()
        self.reset_rollout_sim(dof_state_tensor, root_state_tensor)
        return self.command()

    def command(self):
        return torch_to_bytes(self.mppi.command(self.state_place_holder))

    def add_to_env(self, env_cfg_additions):
        self.sim.add_to_envs(env_cfg_additions)

    def get_rollouts(self):
        # lines = lines[:, self.mppi.important_samples_indexes, :]
        # print(type(self.mppi.important_samples_indexes))
        if not self.sim._visualize_link_present:
            return torch_to_bytes(torch.zeros((1, 1, 1)))

        return torch_to_bytes(torch.stack(self.sim.visualize_link_buffer))

    def update_weights(self, weights):
        self.objective.weights = weights

    def update_mppi_params(self, params):
        self.cfg.mppi.noise_sigma = params['noise_sigma']

        self.mppi = MPPIPlanner(
            self.cfg.mppi,
            self.cfg.nx,
            dynamics=self.dynamics,
            running_cost=self.running_cost,
            prior=self.prior,
        )