from mppiisaac.planner.isaacgym_wrapper import IsaacGymWrapper
from isaacgym import gymapi
import hydra
import zerorpc
from mppiisaac.utils.config_store import ExampleConfig
from mppiisaac.utils.transport import torch_to_bytes, bytes_to_torch
import time
from torch.linalg import norm



@hydra.main(version_base=None, config_path=".", config_name="omni_panda_pick")
def run_omnipanda_robot(cfg: ExampleConfig):

    sim = IsaacGymWrapper(
        cfg.isaacgym,
        actors=cfg.actors,
        init_positions=cfg.initial_actor_positions,
        num_envs=1,
        viewer=True,
        device=cfg.mppi.device,
    )

    planner = zerorpc.Client()
    planner.connect("tcp://127.0.0.1:4242")
    print("Mppi server found!")

    sim._gym.viewer_camera_look_at(
        sim.viewer,
        None,
        gymapi.Vec3(1.0, 6.5, 4),
        gymapi.Vec3(1.0, 0, 0),  # CAMERA LOCATION, CAMERA POINT OF INTEREST
    )
    for _ in range(10):
        t = time.time()
        for i in range(cfg.n_steps):
            # Compute action
            action = bytes_to_torch(
                planner.compute_action_tensor(
                    torch_to_bytes(sim._dof_state), torch_to_bytes(sim._root_state)
                )
            )

            # Apply action
            sim.apply_robot_cmd(action)

            # Step simulator
            sim.step()

            # # Visualize samples
            # rollouts = bytes_to_torch(planner.get_rollouts())
            # sim._gym.clear_lines(sim.viewer)
            # sim.draw_lines(rollouts)

            # Timekeeping
            actual_dt = time.time() - t
            rt = cfg.isaacgym.dt / actual_dt
            if rt > 1.0:
                time.sleep(cfg.isaacgym.dt - actual_dt)
                actual_dt = time.time() - t
                rt = cfg.isaacgym.dt / actual_dt
            # print(f"FPS: {1/actual_dt}, RT={rt}")
            t = time.time()

            block_pos = sim.get_actor_position_by_name("panda_pick_block")
            goal_pos = sim.get_actor_position_by_name("goal")
            block_to_goal = block_pos[:, 0:3] - goal_pos[:, 0:3]
            if norm(block_to_goal) < 0.2:
                print("Goal reached!")
                break
        sim.reset_to_initial_poses()
        print("Elapsed time: ", (i+1) * cfg.isaacgym.dt)


if __name__ == "__main__":
    res = run_omnipanda_robot()
