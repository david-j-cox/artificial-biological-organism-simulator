import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D, art3d
from matplotlib.patches import Rectangle
import imageio.v2 as imageio
import os
import glob

def add_rectangle(ax, xyz, width, height, color='black'):
    """
    Add a 3D rectangle to a given Axes3D object.

    Parameters:
    - ax (mpl_toolkits.mplot3d.Axes3D): The 3D axes to which the rectangle will be added.
    - xyz (tuple of float): The (x, y, z) coordinates of the rectangle's lower-left corner.
    - width (float): The width of the rectangle.
    - height (float): The height of the rectangle.
    - color (str): The color of the rectangle (default is 'black').

    Returns:
    None
    """
    x, y, z = xyz
    p = plt.Rectangle((x, y), width, height, color=color)
    ax.add_patch(p)
    art3d.pathpatch_2d_to_3d(p, z=z, zdir="x")


def add_box(ax, center, length, height, width, color='gray'):
    """
    Add a 3D box to a given Axes3D object.

    Parameters:
    - ax (mpl_toolkits.mplot3d.Axes3D): The 3D axes to which the box will be added.
    - center (tuple of float): The (x, y, z) coordinates of the center of the box.
    - length (float): The length of the box along the x-axis.
    - height (float): The height of the box along the y-axis.
    - width (float): The width of the box along the z-axis.
    - color (str): The color of the box (default is 'gray').

    Returns:
    None
    """
    # Define the corners of the box
    x = np.array([0, length, length, 0, 0, length, length, 0]) - length/2 + center[0]
    y = np.array([0, 0, height, height, 0, 0, height, height]) - height/2 + center[1]
    z = np.array([0, 0, 0, 0, width, width, width, width]) - width/2 + center[2]

    # Define the vertices of each face
    vertices = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4],
                [2, 3, 7, 6], [1, 2, 6, 5], [4, 7, 3, 0]]

    # Draw each face
    for vert in vertices:
        X = [x[i] for i in vert]
        Y = [y[i] for i in vert]
        Z = [z[i] for i in vert]
        ax.add_collection3d(art3d.Poly3DCollection([list(zip(X, Y, Z))], color=color))


def render(self, mode='human', timestep=0):
    """
    Render the environment and generate a figure with subplots for visualization.

    Parameters:
    - mode (str): Rendering mode ('human' or other, default is 'human').
    - timestep (int): The current timestep (default is 0).

    Returns:
    None
    """
    # Create a figure with subplots
    fig = plt.figure(figsize=(30, 16))

    # 3D plot for the environment
    ax1 = fig.add_subplot(231, projection='3d')
    ax2 = fig.add_subplot(232)
    ax3 = fig.add_subplot(233)
    ax4 = fig.add_subplot(234)
    ax5 = fig.add_subplot(235)
    ax6 = fig.add_subplot(236)

    # Draw the 3D environment in ax1
    # Set the limits of the axes to the size of the box
    ax1.set_xlim(0, grid_size_x)
    ax1.set_ylim(0, grid_size_y)
    ax1.set_zlim(0, 1)  # Assuming the height of the box is 1

    # Draw the rat (as a cube)
    rat_length = 0.2
    rat_height = 0.2
    rat_width = 0.2
    rat_center = [position[0], position[1], rat_height / 2]
    add_box(ax1, rat_center, rat_length, rat_height, rat_width, color='blue')

    # Create vertices for a cube
    r = [0, 1]
    X, Y = np.meshgrid(r, r)
    Z = np.array([[1, 1], [1, 1]])
    ax1.plot_surface(X, Y, Z, alpha=0.1, color='grey') # Top
    ax1.plot_surface(X, Y, Z-1, alpha=0.5, color='grey') # Floor
    ax1.plot_surface(X, 0, Y, alpha=0.1, color='blue') # Front
    ax1.plot_surface(X, 1, Y, alpha=0.1, color='red') # Back
    ax1.plot_surface(1, X, Y, alpha=0.1, color='green') # Right
    ax1.plot_surface(0, X, Y, alpha=0.1, color='grey') # Left

    # Levers
    lever_length = 0.15
    lever_height = 0.025
    lever_width = 0.025
    add_box(ax1, (0, 0.3, 0.2 - lever_height/2), lever_length, lever_height, lever_width) # Left lever
    add_box(ax1, (0, 0.815, 0.2 - lever_height/2), lever_length, lever_height, lever_width) # Right lever

    # Food dispensers/hoppers
    add_rectangle(ax1, (0.185, 0.01, -0.05), 0.2, 0.1) # Left
    add_rectangle(ax1, (0.7, 0.01, -0.05), 0.2, 0.1) # Right

    # Signal lights
    ax1.scatter([0], [0.25], [0.6], color="red", s=400, label="Signal Lights")
    ax1.scatter([0], [0.75], [0.6], color="green", s=400, label="Signal Lights")

    # Set labels and title for 3D plot
    ax1.set_xlabel('X axis')
    ax1.set_ylabel('Y axis')
    ax1.set_zlabel('')
    ax1.w_zaxis.line.set_lw(0)
    ax1.set_zticklabels([])
    ax1.set_title('')

    # Set axes limits for tight fit when rendering
    ax1.set_xlim(0, grid_size_x)
    ax1.set_ylim(0, grid_size_y)
    ax1.set_zlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax6.set_ylim(0, max(energy_history)+(max(energy_history)*0.1))

    # Set the aspect ratio
    ax1.set_box_aspect((grid_size_x, grid_size_y, 1))

    # Display rewards earned
    ax1.text2D(
        0.0, 0.9,
        f"Rewards Earned:\n{rewards_earned}",
        transform=ax1.transAxes,
        fontsize=14,
        ha='center')

    # 2D Plots
    figsize_dims = (12, 8)
    ax2.figure.set_size_inches(figsize_dims)
    ax2.plot([pos[0] for pos in position_history['xy']], [pos[1] for pos in position_history['xy']], color='black')
    ax2.scatter(position_history['xy'][-1][0], position_history['xy'][-1][1], color='black')
    ax2.set_xlabel("X Coordinate", fontsize=16, labelpad=12)
    ax2.set_ylabel("Y Coordinate", fontsize=16, labelpad=12)

    ax3.figure.set_size_inches(figsize_dims)
    ax3.plot(
            range(len(position_history['xz'])),
            [pos[0] for pos in position_history['xz']],
            label="X Location",
            color='red')
    ax3.plot(range(
            len(position_history['yz'])),
            [pos[0] for pos in position_history['yz']],
            label="Y Location",
            color='black')
    ax3.set_title("")
    ax3.set_ylabel("Coordinate", fontsize=16, labelpad=12)
    ax3.set_xlabel("Time Step", fontsize=16, labelpad=12)
    ax3.legend(loc='upper left')

    ax4.figure.set_size_inches(figsize_dims)
    ax4.plot(left_lever_contacts, label='Left Lever', color='red')
    ax4.plot(right_lever_contacts, label='Right Lever', color='black')
    ax4.set_xlabel("Time Step", fontsize=16, labelpad=12)
    ax4.set_ylabel("Cumulative Responses", fontsize=16, labelpad=12)
    ax4.legend(loc='upper left')

    # Plot for log2 ratio of lever responses
    ax5.figure.set_size_inches(figsize_dims)
    ax5.plot(range(len(log_ratio_history)), log_ratio_history, color='black')
    ax5.set_xlabel("Time Step", fontsize=16, labelpad=12)
    ax5.set_ylabel("Log2 Ratio (Left/Right Lever)", fontsize=16, labelpad=12)

    # Plot for energy reserves
    ax6.figure.set_size_inches(figsize_dims)
    ax6.plot(range(len(energy_history)), energy_history, color='black')
    ax6.set_xlabel("Time Step", fontsize=16, labelpad=12)
    ax6.set_ylabel("Energy Reserves Remaining", fontsize=16, labelpad=12)

    # Set the spacing between subplots and adjust layout
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95, wspace=0.3, hspace=0.3)

    # Save the figure
    filename = f"./images/frame_{timestep:04d}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.tight_layout()

    # Close the figure to free up memory
    plt.close(fig)


def create_gif(image_folder, output_path, frame_duration=0.02):
    """
    Creates a GIF from a sequence of images in a specified folder.

    :param image_folder: The folder where the images are stored.
    :param output_path: The path to save the output GIF.
    :param frame_duration: Duration of each frame in the GIF (in seconds).
    """
    # Find all PNG files in the folder
    filenames = sorted(glob.glob(os.path.join(image_folder, 'frame_*.png')))

    # Compile the frames into a GIF
    with imageio.get_writer(output_path, mode='I', duration=frame_duration) as writer:
        for filename in filenames:
            try:
                image = imageio.imread(filename)
                writer.append_data(image)
            except Exception as e:
                print(f"Error appending {filename}: {e}")
                continue

    # Optionally delete the individual frames if no longer needed
    for filename in filenames:
        try:
            os.remove(filename)
        except Exception as e:
            print(f"Error deleting {filename}: {e}")
            continue