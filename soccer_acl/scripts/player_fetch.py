import json
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import seaborn as sns
import time
import os
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt

# File paths
ACL_FILE_PATH = "/Users/stephenmacneille/injured_players_before_4.xlsx"
CONTROL_FILE_PATH = "/Users/stephenmacneille/control_before_5.xlsx"

CONTROL_OUTPUT_FILE_PATH = "/Users/stephenmacneille/control_soccer_after_2.xlsx"
ACL_OUTPUT_FILE_PATH = "/Users/stephenmacneille/acl_soccer_after_2.xlsx"

input_file_path = ACL_FILE_PATH
output_file_path = ACL_OUTPUT_FILE_PATH

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
    import pdb;pdb.set_trace
    return playing_time_stats, shooting_stats

# Function to save intermediate results
def save_progress(players_data, file_path):
    df = pd.DataFrame(players_data)
    df['Pre'] = df['Pre'].apply(json.dumps)
    df['Post'] = df['Post'].apply(json.dumps)
    df.to_excel(file_path, index=False)
    print(f"Progress saved to {file_path}")

def identify_significant_changes(injured_file_path, control_file_path):
    def parse_dict(s):
        try:
            s = s.replace("'", "\"").replace("nan", "null")
            return json.loads(s)
        except Exception as e:
            print(f"Error parsing: {s}")
            raise e

    def flatten_dict(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def process_file(file_path):
        df = pd.read_excel(file_path)
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

        return pd.DataFrame(pre_stats), pd.DataFrame(post_stats)

    pre_injured, post_injured = process_file(injured_file_path)
    pre_control, post_control = process_file(control_file_path)

    if pre_injured.empty or post_injured.empty or pre_control.empty or post_control.empty:
        print("No data available for analysis.")
        return

    # Remove non-performance-related columns
    columns_to_exclude = ['age', 'season', 'team', 'country', 'comp_level', 'lg_finish']
    pre_injured = pre_injured.drop(columns=columns_to_exclude, errors='ignore')
    post_injured = post_injured.drop(columns=columns_to_exclude, errors='ignore')
    pre_control = pre_control.drop(columns=columns_to_exclude, errors='ignore')
    post_control = post_control.drop(columns=columns_to_exclude, errors='ignore')

    # Calculate differences
    diff_injured = post_injured.mean() - pre_injured.mean()
    diff_control = post_control.mean() - pre_control.mean()

    # Calculate normalized change
    norm_change = (diff_injured - diff_control) / pre_control.std()
    norm_change = norm_change.sort_values(ascending=False)
    norm_change.name = 'norm_change'  # Name the Series

    # Perform statistical testing (t-test) to determine significance
    p_values = {}
    for col in pre_injured.columns:
        t_stat, p_value = ttest_ind(post_injured[col].dropna(), pre_injured[col].dropna())
        p_values[col] = p_value

    # Convert p-values to DataFrame and sort by significance
    p_values_df = pd.DataFrame.from_dict(p_values, orient='index', columns=['p_value']).sort_values(by='p_value')

    # Filter for significant changes (p < 0.05)
    significant_changes = p_values_df[p_values_df['p_value'] < 1]

    # Create a DataFrame combining normalized change, raw difference, and p-values
    significant_changes = significant_changes.join(norm_change, how='inner')
    significant_changes['raw_difference'] = diff_injured[significant_changes.index]

    # Visualize the most significant changes
    top_changes = significant_changes.head(30)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_changes['norm_change'], y=top_changes.index, palette='coolwarm', dodge=False)
    plt.title('Statistical Changes Pre and Post Injury by P - Value')
    plt.xlabel('Mean Normalized Change')
    plt.ylabel('Statistic')

    # Annotate p-values and raw differences
    for i, (value, p_value, raw_diff) in enumerate(zip(top_changes['norm_change'], top_changes['p_value'], top_changes['raw_difference'])):
        if p_value < 0.001:
            plt.text(value, i, f'p < 0.001\nΔ = {raw_diff:.2f}', ha='center', va='center', fontsize=9, color='black')
        else:
            plt.text(value, i, f'p = {p_value:.3f}\nΔ = {raw_diff:.2f}', ha='center', va='center', fontsize=9, color='black')
    
    plt.tight_layout()
    plt.show()

    # Display the significant changes
    print("Significant Changes (p < 0.05):")
    print(significant_changes)
# # Example usage:
# injured_file_path = 'path/to/injured_players_file.xlsx'
# control_file_path = 'path/to/control_players_file.xlsx'
# identify_significant_changes(injured_file_path, control_file_path)

def create_double_comparison_plots(injured_file_path, control_file_path):
    def parse_dict(s):
        try:
            # Convert single quotes to double quotes and handle 'nan'
            s = s.replace("'", "\"").replace("nan", "null")
            return json.loads(s)
        except Exception as e:
            print(f"Error parsing: {s}")
            raise e

    def flatten_dict(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def process_file(file_path):
        df = pd.read_excel(file_path)
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

        return pd.DataFrame(pre_stats), pd.DataFrame(post_stats)

    pre_injured, post_injured = process_file(injured_file_path)
    pre_control, post_control = process_file(control_file_path)

    if pre_injured.empty or post_injured.empty or pre_control.empty or post_control.empty:
        print("No data available for plotting statistics.")
        return

    pre_injured['Injury'] = 'Pre-Injury (Injured)'
    post_injured['Injury'] = 'Post-Injury (Injured)'
    pre_control['Injury'] = 'Pre-Injury (Control)'
    post_control['Injury'] = 'Post-Injury (Control)'

    plot_data = pd.concat([pre_injured, post_injured, pre_control, post_control])
    plot_data = plot_data.melt(id_vars=['Injury'], var_name='Statistic', value_name='Value')

    plt.figure(figsize=(20, 10))
    sns.boxplot(x='Statistic', y='Value', hue='Injury', data=plot_data)
    plt.xticks(rotation=90)
    plt.title('Box and Whisker Plots for Statistics Averages Pre and Post Injury (Injured vs Control)')
    plt.tight_layout()
    plt.show()


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

    # Assume parse_dict and flatten_dict are defined elsewhere
    def parse_dict(s):
        try:
            # Convert single quotes to double quotes and handle 'nan'
            s = s.replace("'", "\"").replace("nan", "null")
            return json.loads(s)
        except Exception as e:
            print(f"Error parsing: {s}")
            raise e

    def flatten_dict(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    pre_stats = []
    post_stats = []

    for index, row in df.iterrows():
        try:
            print("INDEX:", index, "ROW:", row, "PRE", row["Pre"], "Post", row["Post"])
            pre_dict = parse_dict(row['Pre'])
            post_dict = parse_dict(row['Post'])
            
            pre_flat = flatten_dict(pre_dict['playing_time'])
            pre_flat.update(flatten_dict(pre_dict['shooting']))
            post_flat = flatten_dict(post_dict['playing_time'])
            post_flat.update(flatten_dict(post_dict['shooting']))
            
            pre_stats.append(pre_flat)
            post_stats.append(post_flat)
        except Exception as e:
            import pdb;pdb.set_trace()
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

# Function to read spreadsheet
def read_spreadsheet(file_path, sheet_name=None):
    try:
        # Load the spreadsheet using pandas with openpyxl engine
        print(f"Reading file: {file_path}")
        spreadsheet = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')

        # Debug: Print the first few rows of the spreadsheet
        if isinstance(spreadsheet, dict):
            print("Multiple sheets detected.")
            sheet_names = list(spreadsheet.keys())
            print(f"Available sheets: {sheet_names}")
            spreadsheet = spreadsheet[sheet_names[0]]  # Default to the first sheet

        print("Spreadsheet loaded successfully:")
        print(spreadsheet.head())

        # Filter out rows where 'Stats Link' ends with 'all_stats_keeper'
        spreadsheet = spreadsheet.dropna(subset=['Stats Link'])
        spreadsheet = spreadsheet[~spreadsheet['Stats Link'].str.endswith('all_stats_keeper')]
        
        return spreadsheet
    except ValueError as ve:
        print(f"Error: {ve}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an issue
    except Exception as e:
        print(f"Error reading spreadsheet: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an issue

# Function to process each player
def process_player(player_name, stats_link, year_prior, year_after):
    print(f"Fetching data for {player_name} from {stats_link}")
    
    # Fetch data
    playing_time_stats, shooting_stats = fetch_player_data(stats_link)

    # Extract all unique years played
    all_years = sorted(set(int(stats['season'][:4]) for stats in playing_time_stats if stats['season'][:4].isdigit()))
    
    # Determine midpoint year if year_prior and year_after are None
    if (year_prior is None and year_after is None):
        midpoint_index = len(all_years) // 2
        midpoint_year = all_years[midpoint_index] if all_years else None
        year_prior = midpoint_year
        year_after = midpoint_year

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
    
    return player_stats
# Main processing logic
# Main processing logic
def main_processing(spreadsheet, output_file_path, both=False, control=False):
    # Check if the output file exists and is not empty
    # if both:
    #     control_output = CONTROL_OUTPUT_FILE_PATH
    #     injured_output = ACL_OUTPUT_FILE_PATH
    #     identify_significant_changes(injured_output, control_output)
        
    # if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
    #     print(f"Output file {output_file_path} exists and is not empty. Visualizing data.")
    #     create_comparison_plots(output_file_path)
    # else:
    #     print(f"Output file {output_file_path} does not exist or is empty. Fetching data.")
        
        # List to store player data
        players_data = []
        # import pdb;pdb.set_trace()
        # Iterate over each player in the spreadsheet
        for index, row in spreadsheet.iterrows():
            try:
                player_name = row['Player']
                stats_link = row['Stats Link']
                year_prior = int(row['Year Prior?']) if not pd.isna(row['Year Prior?']) else None
                year_after = int(row['Year After?']) if not pd.isna(row['Year After?']) else None
                
                if not control and (year_prior is None or year_after is None):
                    print(f"Skipping {player_name} due to missing Year Prior or Year After values.")
                    continue
                
                
                player_stats = process_player(player_name, stats_link, year_prior, year_after)
                
                # Append to the list
                players_data.append(player_stats)
                
                # Sleep to avoid overloading the server
                time.sleep(6.1)  # Adjust the timing as necessary
            
            except Exception as e:
                print(f"Error fetching data for {player_name}: {e}")
                save_progress(players_data, output_file_path)

        # Convert list to DataFrame and save final results
        players_df = pd.DataFrame(players_data)

        # Debug print statement to check the DataFrame contents
        print(players_df.head())

        # Ensure 'Pre' and 'Post' columns exist before applying json.dumps
        if 'Pre' in players_df.columns and 'Post' in players_df.columns:
            players_df['Pre'] = players_df['Pre'].apply(json.dumps)
            players_df['Post'] = players_df['Post'].apply(json.dumps)
        else:
            print("Missing 'Pre' or 'Post' columns in the DataFrame.")
            return

        players_df.to_excel(output_file_path, index=False)
        print(f"Final data saved to {output_file_path}")

        # Create comparison plots
        create_comparison_plots(output_file_path)

# Load the spreadsheet
spreadsheet = read_spreadsheet(input_file_path)

# Run the main processing logic
main_processing(spreadsheet, output_file_path, both=True, control=True)