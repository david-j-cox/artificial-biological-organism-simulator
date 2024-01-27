from simulation_runner import run_simulation
import data_analysis
from visualization import render, create_gif

def main():
    simulation_data = run_simulation()

    # Analyze data (make sure this function is implemented correctly)
    analysis_results = data_analysis.analyze_data(simulation_data)

    # Render simulation frames
    for timestep in range(len(simulation_data)):
        render(simulation_data[timestep], timestep)

    # Create a GIF from rendered frames
    create_gif(image_folder='./images/', output_path='output/my_simulation.gif')

if __name__ == "__main__":
    main()