import gym
from gym import spaces
import numpy as np
import random


class Custom3DEnvironment(gym.Env):
    """A custom 3D environment for OpenAI gym."""

    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(Custom3DEnvironment, self).__init__()

        # Define a 3D space
        self.grid_size_x = 1.0
        self.grid_size_y = 1.0
        self.grid_size_z = 2.0

        # Actions:
        self.action_space = spaces.Discrete(5)

        # Observation space: the x, y, z coordinates in the grid
        self.observation_space = spaces.Box(low=np.array([0, 0, 0]), 
                                            high=np.array([self.grid_size_x, self.grid_size_y, self.grid_size_z]), 
                                            dtype=np.float32)

        # Initial position and orientation
        self.position = np.array([random.uniform(0, self.grid_size_x), 
                                  random.uniform(0, self.grid_size_y), 
                                  0.15])
        self.orientation = 0  # Orientation in degrees (0: facing along positive X-axis)

        # Initialize history of positions for 2D plots
        self.position_history = {'xy': [], 'xz': [], 'yz': []}

        # Add rewards earned function
        self.rewards_earned = 0

        # Initialize lists for lever contacts
        self.left_lever_contacts = [0]
        self.right_lever_contacts = [0]

        # Initialize energy reserves
        self.energy = 200
        self.energy_history = [self.energy]
        self.log_ratio_history = [0]

    def step(self, action):
        # Initialize reward and done flag
        reward = 0
        done = False

        # Define movement step size and rat dimensions
        step_size = 0.15
        rat_length = 0.2  # Length of the rat along the X-axis

        # Sample an action based on probabilities
        if action == 0:
            pass  # No movement
        elif action == 1:
            angle = np.random.uniform(0, 2 * np.pi)     # Choose a random angle
            distance = np.random.uniform(0, step_size)  # Choose a random distance

            # Calculate the new position
            new_x = self.position[0] + distance * np.cos(angle)
            new_y = self.position[1] + distance * np.sin(angle)

            # Check if the new position is within the box boundaries
            new_x = np.clip(new_x, 0.1, self.grid_size_x - 0.1)
            new_y = np.clip(new_y, 0.1, self.grid_size_y - 0.1)

            # Update the position
            self.position[0] = new_x
            self.position[1] = new_y

        # Action 0: 'stay' - no movement
        if action == 0:
            reward = 0  # No reward for staying still

        # Dimensions of the box
        box_half_length = 0.2 / 2  # half of the box length

        # Calculate the extents of the box
        box_x_min = self.position[0] - box_half_length
        box_x_max = self.position[0] + box_half_length
        box_y_min = self.position[1] - box_half_length
        box_y_max = self.position[1] + box_half_length

        # Define lever positions and sizes
        lever_length = 0.15
        lever_height = 0.025
        lever_width = 0.025
        lever1_pos = [0, 0.3]
        lever2_pos = [0, 0.815]
        lever_size = [lever_length, lever_width]

        # Check if any part of the box is within lever bounds
        box_contact_with_lever1 = (
            box_x_min <= lever1_pos[0] + lever_size[0]/2 and
            box_x_max >= lever1_pos[0] - lever_size[0]/2 and
            box_y_min <= lever1_pos[1] + lever_size[1]/2 and
            box_y_max >= lever1_pos[1] - lever_size[1]/2)

        box_contact_with_lever2 = (
            box_x_min <= lever2_pos[0] + lever_size[0]/2 and
            box_x_max >= lever2_pos[0] - lever_size[0]/2 and
            box_y_min <= lever2_pos[1] + lever_size[1]/2 and
            box_y_max >= lever2_pos[1] - lever_size[1]/2)

        # Lever 1
        if box_contact_with_lever1==True:
            self.rewards_earned += 1

        # Lever 2
        if box_contact_with_lever2==True:
            self.rewards_earned += 1

        # Check for lever contact and update lists
        if box_contact_with_lever1:
            self.left_lever_contacts.append(self.left_lever_contacts[-1] + 1)
            self.right_lever_contacts.append(self.right_lever_contacts[-1])
        elif box_contact_with_lever2:  # Replace with your actual condition
            self.right_lever_contacts.append(self.right_lever_contacts[-1] + 1)
            self.left_lever_contacts.append(self.left_lever_contacts[-1])
        else:
            self.left_lever_contacts.append(self.left_lever_contacts[-1])
            self.right_lever_contacts.append(self.right_lever_contacts[-1])

        # Ensure that lever counts don't start from 0 to avoid division by zero
        left_lever_count = max(self.left_lever_contacts[-1], 1)
        right_lever_count = max(self.right_lever_contacts[-1], 1)

        # Calculate log ratio
        log_ratio = np.log2(left_lever_count / right_lever_count)
        self.log_ratio_history.append(log_ratio)

        # Set placeholder for info
        info = {}

        # Update position history for 2D plots
        self.position_history['xy'].append((self.position[0], self.position[1]))
        self.position_history['xz'].append((self.position[0], self.position[2]))
        self.position_history['yz'].append((self.position[1], self.position[2]))

        # Handle energy changes
        self.energy -= 0.25  # Decrease energy each step
        if box_contact_with_lever1 or box_contact_with_lever2:
            self.energy += 5
        self.energy_history.append(self.energy)

        # Return step information
        return np.array(self.position), reward, done, info

    def reset(self): # Reset the state of the environment to an initial state
        # Reset to a random initial position within the grid
        self.position = np.array([
            random.uniform(0, self.grid_size_x - 0.1),  # X-coordinate
            random.uniform(0, self.grid_size_y - 0.1),  # Y-coordinate
            0.15  # Z-coordinate (fixed, as the rat moves on the floor)
        ])

        # Reset additional attributes if any (like total_rewards, lever_press_count, etc.)
        # self.lever_press_count = 0
        # self.total_rewards = 0

        # Return the initial observation
        return np.array(self.position)

    def add_rectangle(self, ax, xyz, width, height, color='black'):
        x, y, z = xyz
        p = plt.Rectangle((x, y), width, height, color=color)
        ax.add_patch(p)
        art3d.pathpatch_2d_to_3d(p, z=z, zdir="x")

    def add_box(self, ax, center, l, h, w, color='gray'):
        # Define the corners of the box
        x = np.array([0, l, l, 0, 0, l, l, 0]) - l/2 + center[0]
        y = np.array([0, 0, h, h, 0, 0, h, h]) - h/2 + center[1]
        z = np.array([0, 0, 0, 0, w, w, w, w]) - w/2 + center[2]

        # Define the vertices of each face
        vertices = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4],
                    [2, 3, 7, 6], [1, 2, 6, 5], [4, 7, 3, 0]]

        # Draw each face
        for vert in vertices:
            X = [x[i] for i in vert]
            Y = [y[i] for i in vert]
            Z = [z[i] for i in vert]
            ax.add_collection3d(art3d.Poly3DCollection([list(zip(X, Y, Z))], color=color))