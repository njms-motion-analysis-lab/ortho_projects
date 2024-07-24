import ast
import json
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import seaborn as sns
import time
import os
import matplotlib.pyplot as plt

# File paths
input_file_path = "/Users/stephenmacneille/acl_soccer_before.xlsx"
output_file_path = "/Users/stephenmacneille/acl_soccer_after.xlsx"

# Function to fetch player data from fbref
def fetch_player_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract relevant stats from Playing Time table
    playing_time_table = soup.select_one('table#stats_playing_time_dom_lg')
    shooting_table = soup.select_one('table#stats_shooting_dom_lg')

    # Parse the tables
    def parse_table(table):
        data = []
        if table:
            rows = table.select('tbody tr')
            for row in rows:
                season = row.select_one('th[data-stat="year_id"]').text if row.select_one('th[data-stat="year_id"]') else ''
                stats = {col['data-stat']: col.text for col in row.select('td')}
                stats['season'] = season
                data.append(stats)
        return data
    
    playing_time_stats = parse_table(playing_time_table)
    shooting_stats = parse_table(shooting_table)
    
    return playing_time_stats, shooting_stats

# Function to save intermediate results
def save_progress(players_data, file_path):
    df = pd.DataFrame(players_data)
    df['Pre'] = df['Pre'].apply(json.dumps)
    df['Post'] = df['Post'].apply(json.dumps)
    df.to_excel(file_path, index=False)
    print(f"Progress saved to {file_path}")

# Function to create comparison plots
    # Function to create comparison plots
def create_comparison_plots(file_path):
    # Load the completed output file
    df = pd.read_excel(file_path)

        # Function to flatten nested dictionaries
    def clean_dict_string(s):
        # Remove newlines and extra spaces
        s = re.sub(r'\s+', ' ', s)
        # Replace 'nan' with 'None' for Python compatibility
        s = s.replace('nan', 'None')
        return s

    def parse_dict(s):
        try:
            # Clean the string and evaluate it as a Python expression
            return ast.literal_eval(clean_dict_string(s))
        except:
            print(f"Error parsing: {s}")
            return {}

    def flatten_dict(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = f'{parent_key}{sep}{k}' if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    # Load the completed output file
    df = pd.read_excel(output_file_path)

    pre_stats = []
    post_stats = []

    for index, row in df.iterrows():
        try:
            pre_dict = parse_dict(row['Pre'])
            post_dict = parse_dict(row['Post'])
            
            pre_flat = flatten_dict(pre_dict['playing_time'])
            pre_flat.update(flatten_dict(pre_dict['shooting']))
            post_flat = flatten_dict(post_dict['playing_time'])
            post_flat.update(flatten_dict(post_dict['shooting']))
            
            pre_stats.append(pre_flat)
            post_stats.append(post_flat)
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            continue

    # Convert lists of dictionaries to DataFrames for plotting
    pre_df = pd.DataFrame(pre_stats)
    post_df = pd.DataFrame(post_stats)

    # Ensure that NaNs are ignored when calculating means
    if pre_df.empty or post_df.empty:
        print("No data available for plotting statistics.")
    else:
        # Fill NaNs with zeros or use skipna=True when calculating means
        plot_data = pd.concat([pre_df, post_df], keys=['Pre-Injury', 'Post-Injury'])
        plot_data = plot_data.melt(ignore_index=False, var_name='Statistic', value_name='Value')
        plot_data = plot_data.reset_index(level=0).rename(columns={'level_0': 'Injury'})

        # Create the plot
        plt.figure(figsize=(20, 10))
        sns.boxplot(x='Statistic', y='Value', hue='Injury', data=plot_data)
        plt.xticks(rotation=90)
        plt.title('Box and Whisker Plots for Statistics Averages Pre and Post Injury')
        plt.tight_layout()
        plt.show()


# Check if the output file exists and is not empty
if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
    print(f"Output file {output_file_path} exists and is not empty. Visualizing data.")
    create_comparison_plots(output_file_path)
else:
    print(f"Output file {output_file_path} does not exist or is empty. Fetching data.")
    
    # Load the spreadsheet
    spreadsheet = pd.read_excel(input_file_path)

    # Filter out rows where 'Stats Link' ends with 'all_stats_keeper'
    spreadsheet = spreadsheet.dropna(subset=['Stats Link'])
    spreadsheet = spreadsheet[~spreadsheet['Stats Link'].str.endswith('all_stats_keeper')]
    import pdb;pdb.set_trace()

    # List to store player data
    players_data = []

    # Iterate over each player in the spreadsheet
    for index, row in spreadsheet.iterrows():
        try:
            player_name = row['Player']
            stats_link = row['Stats Link']
            date_of_injury = row['Date of Injury']
            year_prior = int(row['Year Prior?']) if not pd.isna(row['Year Prior?']) else None
            year_after = int(row['Year After?']) if not pd.isna(row['Year After?']) else None
            
            if year_prior is None or year_after is None:
                print(f"Skipping {player_name} due to missing Year Prior or Year After values.")
                continue
            
            print(f"Fetching data for {player_name} from {stats_link}")
            
            # Fetch data
            playing_time_stats, shooting_stats = fetch_player_data(stats_link)

            
            
            # Divide data into pre and post injury
            pre_stats, post_stats = {'playing_time': [], 'shooting': []}, {'playing_time': [], 'shooting': []}
            
            for stats in playing_time_stats:
                season_year = stats['season'][:4]
                if season_year.isdigit():
                    if int(season_year) <= year_prior:
                        pre_stats['playing_time'].append(stats)
                    else:
                        post_stats['playing_time'].append(stats)
            
            for stats in shooting_stats:
                season_year = stats['season'][:4]
                if season_year.isdigit():
                    if int(season_year) <= year_prior:
                        pre_stats['shooting'].append(stats)
                    else:
                        post_stats['shooting'].append(stats)

            # Calculate averages
            def calculate_averages(data):
                if not data:
                    return {}
                df = pd.DataFrame(data)
                df = df.apply(pd.to_numeric, errors='coerce')
                return df.mean().to_dict()

            pre_averages = {
                'playing_time': calculate_averages(pre_stats['playing_time']),
                'shooting': calculate_averages(pre_stats['shooting'])
            }
            post_averages = {
                'playing_time': calculate_averages(post_stats['playing_time']),
                'shooting': calculate_averages(post_stats['shooting'])
            }
            
            player_stats = {
                'Player': player_name,
                'Pre': pre_averages,
                'Post': post_averages
            }
            
            # Append to the list
            players_data.append(player_stats)
            
            # Sleep to avoid overloading the server
            time.sleep(6.1)  # Adjust the timing as necessary
        
        except Exception as e:
            print(f"Error fetching data for {player_name}: {e}")
            save_progress(players_data, output_file_path)

    # Convert list to DataFrame and save final results
    players_df = pd.DataFrame(players_data)
    players_df['Pre'] = players_df['Pre'].apply(json.dumps)
    players_df['Post'] = players_df['Post'].apply(json.dumps)
    players_df.to_excel(output_file_path, index=False)
    print(f"Final data saved to {output_file_path}")

    # Create comparison plots
    create_comparison_plots(output_file_path)