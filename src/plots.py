import os
import glob
import pickle
import matplotlib.pyplot as plt

def load_latest_pickle(directory):
    """
    Load the latest pickle file from the specified directory.

    Parameters
    ----------
    directory: string
        directory where the simulation results are stored.
    
    Returns 
    ------
    loaded_data: dictionary
        Dictionary containing the results for each simulation.
        Keys are the simulation ids. Values are data frames containing the profits. 
    """

    # Use glob to find all pickle files in the directory
    pickle_files = glob.glob(os.path.join(directory, '*.pickle'))

    # Check if any pickle files are found
    if pickle_files:
        # Get the latest file based on the modification time
        latest_file = max(pickle_files, key=os.path.getmtime)
        # Load the pickle from the latest file
        with open(latest_file, 'rb') as f:
            loaded_data = pickle.load(f)
        print(f"Loaded data from: {latest_file}")
        return loaded_data
    else:
        print("No pickle files found in the specified directory.")
        return None

def cumulative_avg(data_frames):
    """
    Generates a plot for the cumulative average of profits.

    Parameters
    ----------
    data_frames: data frame
        data frame from the pickle file containing the results for a simulation
    
    Returns 
    ------
    plot
        A plot for the cumulative average over time
    """

    for key, df in data_frames.items():
        # Calculate cumulative sums and averages
        cumulative_sum = df.cumsum()
        cumulative_average = cumulative_sum / (df.index.values[:, None] + 1)  # Adding 1 to avoid division by zero
        
        # Plot cumulative average
        plt.plot(cumulative_average.index, cumulative_average.mean(axis=1), label=f'Cumulative Average {key}', linewidth=2)
        
    # Title and labels
    plt.title('Cumulative Average Profit Over Time for Simulations')
    plt.xlabel('Month')
    plt.ylabel('Cumulative Average Profit')
    plt.grid()
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')  # Position legend outside the plot
    plt.show()

def cumulative_sum(data_frames):
    """
    Generates a plot for the cumulative sum of profits.

    Parameters
    ----------
    data_frames: data frame
        data frame from the pickle file containing the results for a simulation
    
    Returns 
    ------
    plot
        A plot for the cumulative sum over time
    """

    for key, df in data_frames.items():
        # Calculate cumulative sums
        cumulative_sum = df.cumsum()

        # Plot cumulative average
        plt.plot(cumulative_sum.index, cumulative_sum.mean(axis=1), label=f'Cumulative Sum {key}', linewidth=2)
        
    # Title and labels
    plt.title('Cumulative Sum of Profit Over Time for Simulations ')
    plt.xlabel('Month')
    plt.ylabel('Cumulative Sum Profit')
    plt.grid()
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    plt.show()

def main():
    """
    Main Function
    """
    # Specify the directory where the pickle files are stored
    directory = '../data/processed/'

    # load latest pickle file
    pickle = load_latest_pickle(directory)

    # Call the plotting functions if pickle file exists
    if pickle: 
        cumulative_avg(pickle)
        cumulative_sum(pickle)


if __name__ == "__main__":
  main()