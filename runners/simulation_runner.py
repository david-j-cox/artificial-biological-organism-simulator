from custom_3d_environment import Custom3DEnvironment
import numpy as np
import random
import datetime
import json
import os

def run_simulation(sim_timesteps=100):
    """
    Run a simulation in a custom 3D environment for a specified number of timesteps.

    Parameters:
    - sim_timesteps (int): The number of timesteps to run the simulation (default is 100).

    Returns:
    list: A list of dictionaries containing simulation data for each timestep. Each dictionary contains the following keys:
        - "timestep" (int): The current timestep.
        - "position" (tuple): The observation of the agent's position.
        - "reward" (float): The reward received at the current timestep.
        - "energy" (float): The agent's energy level in the environment.
        - "left_lever_contacts" (int): The number of contacts with the left lever at the current timestep.
        - "right_lever_contacts" (int): The number of contacts with the right lever at the current timestep.
        # Add other relevant data as needed.
    """
    env = Custom3DEnvironment()  # Create a custom 3D environment
    data = []  # Initialize an empty list to store simulation data

    for timestep in range(sim_timesteps):
        action = random.choice(env.action_space.n)  # Choose a random action from the action space
        obs, reward, done, info = env.step(action)  # Take a step in the environment

        # Collect data for the current timestep
        data.append({
            "timestep": timestep,
            "position": obs,
            "reward": reward,
            "energy": env.energy,
            "left_lever_contacts": env.left_lever_contacts[-1],
            "right_lever_contacts": env.right_lever_contacts[-1]
            # Add other relevant data here
        })

        if done:
            break  # End the simulation if the episode is finished

    # Save the simulation data
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_filename = f"data/simulation_data_{timestamp}.json"

    # Create the data directory if it does not exist
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    with open(output_filename, "w") as file:
        json.dump(data, file, indent=4)

    print(f"Simulation data saved to {output_filename}")

    return data  # Return the collected simulation data


if __name__ == "__main__":
    run_simulation()