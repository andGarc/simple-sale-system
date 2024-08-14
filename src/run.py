import datetime
import pandas as pd
import numpy as np
import os
import pickle
from utils import load_config
from sales_system import (get_new_customers, predict_purchases, predict_quantities)


def configure(config_file_name):
    """
    Load configuration file and sets configuration settings

    Parameters
    ----------
    config_file_name: string
        The name of the configuration file.
    
    Returns 
    ------
    dictionary
        A dictionary containing the configuration parameters 

    """
        
    #  Load the configuration file
    settings = load_config(config_file_name)

    #  Set variables from configuration file
    starting_seed = settings['seed']
    iterations = settings['iterations']
    months = settings['months']
    shirt_price = settings['shirt_price']
    cost_per_shirt = settings['cost_per_shirt']
    monthly_inflation_rate = settings['inflation_rate'] / 12
    starting_existing_customers = settings['n_existing_customers']
    campaigns = settings['campaigns']

    return {'starting_seed':starting_seed, 
            'iterations':iterations,
            'months':months, 
            'shirt_price':shirt_price,
            'cost_per_shirt':cost_per_shirt, 
            'monthly_inflation_rate':monthly_inflation_rate,
            'starting_existing_customers':starting_existing_customers,
            'campaigns':campaigns}

def campaign_months(settings):
    """
    Identifying the months when campaigns will be applied based on the set cadence.
    Updates the campaign months.

    Parameters
    ----------
    settings: dictionary
        The dictionary containing the settings from the configuration file.
    
    Returns 
    ------
    None

    """

    for key, value in settings['campaigns'].items():
        cur_campaign_months = list(range(0, settings['months'], settings['months'] // value['n_times'])) 
        settings['campaigns'][key].update({'campaign_months': cur_campaign_months})
 
def monte_carlo(settings):
    """
    Perform a Monte Carlo simulation for campaigns

    Parameters
    ----------
    settings: dictionary
        Dictionary containing the setting for the simulations
    
    Returns 
    ------
    big_res: dictionary
        A dictionary where keys are campaign names and values are DataFrames containing the profit results for 
        each iteration of the corresponding campaign

    """
    seed = settings['starting_seed']
    big_res = {}

    #  Looping over the campaigns
    for key, value in settings['campaigns'].items():
        iter_res = pd.DataFrame()
        for i in range(settings['iterations']):
            #  Resetting profits and cost per shirt, and starting customer base at the start of each iteration
            profits = []
            cur_shirt_cost = settings['cost_per_shirt']
            n_existing_customers = settings['starting_existing_customers']
            #  Creating a random number generator that we'll use to sample in an iteration
            #  Ensures simulation results are reproducible 
            cur_rng = np.random.default_rng(seed)
            for t in range(settings['months']):
                #  Sales step -----------------------------------------------------------------------------
                cur_n_new_customers = get_new_customers(t)

                #  Determining how many of the new customers make a purchase
                #  this month
                n_new_purchases = predict_purchases(cur_n_new_customers,
                                                    p_purchase=0.01)

                if t in value['campaign_months']:
                    n_existing_purchases = predict_purchases(n_existing_customers, 
                                                            p_purchase=value['prob_purchase'],
                                                            rng=cur_rng)
                    cur_existing_discount = value['discount']
                else:
                    #  10% of existing customers visit the website during 
                    #  non-campaign months driven by traditional email 
                    #  messaging (with no discounts)
                    cur_n_existing_customers = np.round(n_existing_customers * 0.1).astype(int)
                    n_existing_purchases = predict_purchases(cur_n_existing_customers,
                                                            p_purchase=0.05,
                                                            rng=cur_rng)
                    cur_existing_discount = 0

                #  Simulating the quantity of shirts in each order for purchases
                n_new_quantity = predict_quantities(n_new_purchases, rng=cur_rng)
                n_existing_quantity = predict_quantities(n_existing_purchases, rng=cur_rng)

                total_sales = n_new_quantity * settings['shirt_price'] * (1 - 0.1) + n_existing_quantity * settings['shirt_price'] * (1 - cur_existing_discount)
                
                #  Cost step -------------------------------------------------------------------------------
                total_cost = cur_shirt_cost * (n_new_quantity + n_existing_quantity)
                
                #  Accounting step -------------------------------------------------------------------------
                #  Calculating the profit in this month
                cur_profit = total_sales - total_cost
                profits.append(cur_profit)

                #  Updating the shirt cost with inflation 
                cur_shirt_cost = cur_shirt_cost * (1 + settings['monthly_inflation_rate'])

                #  Adding the new customers who made a purchase to the existing customer base
                n_existing_customers += n_new_purchases
            #  Incrementing the seed so we can create a new, reproducible random number generator for the
            #  next iteration    
            seed += 1    
            iter_res = pd.concat([iter_res, pd.Series(profits)], axis=1, ignore_index=True)

        big_res[key] = iter_res.copy()  
    return big_res

def save_pickle(big_res, path):
    """
    Save the simulation results as a pickle file.

    Parameters
    ----------
    big_res: dictionary
        The dictionary with the results for each simulations
        Key: simulation id
        Value: profit results from simulation
    
    path: string 
        The path were the results will be saved
    Returns 
    ------
    pickle
        Saves a pickle file to the specified path.

    """
    now_str = datetime.datetime.now().strftime('%Y_%m_%d %H_%M_%S')

    run_path = os.path.join(path, '{}.pickle'.format(now_str))
    with open(run_path, 'wb') as handle:
        pickle.dump(big_res, handle, protocol=pickle.HIGHEST_PROTOCOL)

def main():
    """
    Main Function
    """

    # Set configuration file name and results path
    config_file_name = "baseline.yaml"
    results_path = '../data/processed'

    # Load and configure parameters
    settings = configure(config_file_name)

    # Identifying the months when campaigns will be applied based on the set cadence
    campaign_months(settings)

    # Run simulation
    big_res = monte_carlo(settings)

    # Save results
    save_pickle(big_res, results_path)

    
if __name__ == "__main__":
  main()