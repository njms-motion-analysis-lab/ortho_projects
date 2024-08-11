import time
import scipy.stats as stats
import matplotlib.cm as cm
from scipy.stats import norm
import matplotlib.pyplot as plt
from scipy.stats import t
import pandas as pd
import np
from models import Player, Session
from helpers import aggregate_stats
import matplotlib.pyplot as plt
from scipy.stats import ttest_rel
from scipy.stats import ttest_ind
import seaborn as sns

from models.player_injury import PlayerInjury


class PlayerStats:
    def __init__(self, aggregated_stats, std_dev_stats, sample_size):
        self.aggregated_stats = aggregated_stats
        self.std_dev_stats = std_dev_stats
        self.sample_size = sample_size

    @classmethod
    def from_stats_dict(cls, stats_dict):
        aggregate = {}
        counts = {}
        sum_of_squares = {}

        for player_name, stats in stats_dict.items():
            if 'shooting_stats' in stats and stats['shooting_stats']:
                for key, value in stats['shooting_stats'].items():
                    if key in aggregate:
                        aggregate[key] += value
                        counts[key] += 1
                        sum_of_squares[key] += value**2
                    else:
                        aggregate[key] = value
                        counts[key] = 1
                        sum_of_squares[key] = value**2

            if 'playing_time_stats' in stats and stats['playing_time_stats']:
                for key, value in stats['playing_time_stats'].items():
                    if key in aggregate:
                        aggregate[key] += value
                        counts[key] += 1
                        sum_of_squares[key] += value**2
                    else:
                        aggregate[key] = value
                        counts[key] = 1
                        sum_of_squares[key] = value**2

        # Calculate the average for each stat
        for key in aggregate.keys():
            aggregate[key] /= counts[key]

        # Calculate the standard deviation for each stat
        std_dev = {}
        for key in aggregate.keys():
            mean_square = sum_of_squares[key] / counts[key]
            square_of_mean = aggregate[key]**2
            std_dev[key] = (mean_square - square_of_mean)**0.5

        non_empty_stats_keys = [key for key, stats in stats_dict.items() if stats]

        return cls(aggregate, std_dev, len(non_empty_stats_keys))


def calculate_changes_and_normalize(pre_stats, post_stats, control_pre_stats, control_post_stats):
    changes = {}
    
    for col in pre_stats.columns:
        if col in post_stats.columns and col in control_pre_stats.columns and col in control_post_stats.columns:
            injured_change = post_stats[col] - pre_stats[col]
            control_change = control_post_stats[col] - control_pre_stats[col]

            # Skip calculations if there is not enough variance or data
            if control_pre_stats[col].std() == 0 or len(post_stats[col].dropna()) < 1 or len(pre_stats[col].dropna()) < 1:
                continue

            # Normalize the changes (z-score normalization)
            norm_change = (injured_change.mean() - control_change.mean()) / control_pre_stats[col].std()

            # Perform t-test
            t_stat, p_value = ttest_rel(post_stats[col].dropna(), pre_stats[col].dropna())

            # changes[col] = {'change': norm_change, 'p_value': p_value}
        else:
            print(f"Column '{col}' is missing in one of the DataFrames.")
    
    changes_df = pd.DataFrame(changes).T

    # Check if 'p_value' exists before attempting to drop rows
    if 'p_value' in changes_df.columns:
        changes_df = changes_df.dropna(subset=['p_value'])  # Drop rows where p_value is None
    else:
        print("No valid p-values were computed. Skipping further analysis.")
        return pd.DataFrame()  # Return an empty DataFrame if no valid p-values

    return changes_df


def plot_statistical_changes(changes_df):
    if changes_df.empty:
        print("The changes DataFrame is empty. Skipping plotting.")
        return

    # Proceed with the plot if the DataFrame is not empty
    changes_df['significant'] = changes_df['p_value'] < 0.05
    changes_df = changes_df.sort_values(by='p_value')

    plt.figure(figsize=(12, 8))
    sns.barplot(
        x='change', 
        y=changes_df.index, 
        data=changes_df, 
        hue='significant', 
        dodge=False, 
        palette='coolwarm', 
        edgecolor=".2"
    )

    for i, (delta, p) in enumerate(zip(changes_df['change'], changes_df['p_value'])):
        plt.text(delta, i, f"p = {p:.3f}\nΔ = {delta:.2f}", ha='center', va='center', fontsize=10, color="black")
    
    plt.title('Statistical Changes Pre and Post Injury by P-Value')
    plt.xlabel('Mean Normalized Change')
    plt.ylabel('Statistic')
    plt.legend(title='Significant')
    plt.tight_layout()
    plt.show()

def aggregate_player_stats(player, season_type, compare_player=None):
    """
    Aggregates stats for a given player based on season_type ('pre' or 'post').
    If compare_player is provided, we try to match control seasons based on the compare_player's career progression.
    """
    if compare_player:
        # Determine the year of the injury relative to the compare_player's career
        injury_season_index = len(compare_player.pre_injury_seasons())

        if season_type == 'pre':
            control_season_index = injury_season_index - 1  # Pre-injury: 1 year before the injury year
        elif season_type == 'post':
            control_season_index = injury_season_index + 1  # Post-injury: 1 year after the injury year
        else:
            raise ValueError("Invalid season_type. Must be 'pre' or 'post'.")

        # Filter the control player's seasons based on the calculated control_season_index
        seasons = [
            season for idx, season in enumerate(sorted(player.seasons, key=lambda s: s.season.year))
            if idx == control_season_index
        ]
    else:
        # Normal case: aggregate all seasons of the specified type
        seasons = getattr(player, f'{season_type}_injury_seasons')()

    if not seasons:
        return {}

    aggregated_stats = aggregate_stats(seasons)
    return aggregated_stats


def find_control_player(injured_player, session):
    """
    Find a control player based on the closest match in the pre-injury season stats.
    Exclude players who have had injuries.
    """
    # Fetch the pre-injury season
    try:
        pre_injury_season = injured_player.pre_injury_seasons()[-1]  # Assuming last pre-injury season is the most relevant
    except IndexError:
        # print(f"No pre-injury seasons found for {injured_player.name}")
        return None

    # Find potential control matches
    control_matches = pre_injury_season.find_control_matches()
    closest_match = None
    
    for control_match in control_matches:
        control_player = control_match.player
        
        # Check if the control player has had an injury
        has_injury = session.query(PlayerInjury).filter(PlayerInjury.player_id == control_player.id).first()
        
        if not has_injury:
            closest_match = control_player
            break  # Assuming we take the first valid match

    if closest_match:
        print(f"Control player found: {closest_match.name} for injured player {injured_player.name}")
    else:
        print(f"No suitable control player found for {injured_player.name}")
    
    return closest_match

def find_control_matches(player_season):
    control_matches = player_season.find_control_matches()
    
    # Exclude control players who have injuries
    control_matches = [match for match in control_matches if not match.player.injuries]
    
    # Ensure control player has at least one additional player season after the matched one
    control_matches = [
        match for match in control_matches 
        if any(season.year > match.season.year for season in match.player.seasons)
    ]
    
    return control_matches

def main():
    session = Session()

    # Step 1: Gather injured players and their pre/post injury seasons
    injured_players = session.query(Player).filter(Player.injuries.any()).all()
    injured_pre_stats = {}
    injured_post_stats = {}
    control_pre_stats = {}
    control_post_stats = {}

    def get_fb_stats(player):
        try:
            player.store_fbref_stats()
            print(f"Successfully stored fbref stats for {player.name}")
            time.sleep(6.1)
        except Exception as e:
            print(f"Error storing fbref stats for {player.name}: {e}")

    control_players = []
    for player in injured_players:
        print("INJ", player.name)
        # Step 2: Ensure each player has only one set of fbref stats
        if len(player.fbref_stats) > 1:
            for stat in player.fbref_stats[1:]:
                session.delete(stat)
            session.commit()

        # Step 3: Fetch fbref stats if missing, otherwise skip the player
        if not player.fbref_stats:
            print(f"No fbref stats found for {player.name}. Attempting to fetch...")
            get_fb_stats(player)
            if not player.fbref_stats:
                print(f"No fbref stats could be fetched for {player.name}. Skipping player.")
                continue

        # Step 4: Get the last pre-injury season and related stats
        try:
            last_pre_injury_season = player.pre_injury_seasons()[-1]
            
            pre_injury_stats = player.control_pre_seasons(last_pre_injury_season)
            post_injury_stats = player.control_post_seasons(last_pre_injury_season)

            print("PRE", pre_injury_stats)
            print()
            print("POST", post_injury_stats)
        except IndexError:
            print(f"No pre-injury seasons found for {player.name}. Skipping player.")
            continue

        # Step 5: Find the control player for the last pre-injury season
        control_matches = last_pre_injury_season.find_control_matches()
        if not control_matches:
            print(f"No control matches found for {player.name}. Skipping player.")
            continue

        control_season = control_matches[0]
        control_player = control_season.player

        print("CONTROL", control_player.name)

        # Ensure control player has only one set of fbref stats
        if len(control_player.fbref_stats) > 1:
            for stat in control_player.fbref_stats[1:]:
                session.delete(stat)
            session.commit()

        if not control_player.fbref_stats:
            print(f"No fbref stats found for control player {control_player.name}. Attempting to fetch...")
            get_fb_stats(control_player)
            if not control_player.fbref_stats:
                print(f"No fbref stats could be fetched for control player {control_player.name}. Skipping control player.")
                continue

        # Step 6: Collect pre and post stats for control player
        try:
            pre_injury_control_stats = control_player.control_pre_seasons(control_season)
            post_injury_control_stats = control_player.control_post_seasons(control_season)
        except IndexError:
            print(f"No valid control seasons found for control player {control_player.name}. Skipping control player.")
            continue

        # Aggregate the stats
        injured_pre_stats[player.name] = pre_injury_stats
        injured_post_stats[player.name] = post_injury_stats
        control_pre_stats[control_player.name] = pre_injury_control_stats
        control_post_stats[control_player.name] = post_injury_control_stats

    # Step 7: Handle missing data and aggregate the stats
    def aggregate_stats(stats_dict):
        aggregate = {}
        counts = {}
        stat_sumsq = {}  # To calculate variance and standard deviation

        for player_name, stats in stats_dict.items():
            if 'shooting_stats' in stats and stats['shooting_stats']:
                for key, value in stats['shooting_stats'].items():
                    if key in aggregate:
                        aggregate[key] += value
                        counts[key] += 1
                        stat_sumsq[key] += value ** 2
                    else:
                        aggregate[key] = value
                        counts[key] = 1
                        stat_sumsq[key] = value ** 2

            if 'playing_time_stats' in stats and stats['playing_time_stats']:
                for key, value in stats['playing_time_stats'].items():
                    if key in aggregate:
                        aggregate[key] += value
                        counts[key] += 1
                        stat_sumsq[key] += value ** 2
                    else:
                        aggregate[key] = value
                        counts[key] = 1
                        stat_sumsq[key] = value ** 2

        # Calculate the average for each stat
        for key in aggregate.keys():
            aggregate[key] /= counts[key]

        # Calculate the standard deviation for each stat
        std_devs = {}
        for key in aggregate.keys():
            if counts[key] > 1:
                mean_sumsq = stat_sumsq[key] / counts[key]
                variance = mean_sumsq - (aggregate[key] ** 2)
                std_devs[key] = (variance ** 0.5) if variance > 0 else 0.0
            else:
                std_devs[key] = None  # Not enough data to calculate standard deviation

        non_empty_stats_keys = [key for key, stats in stats_dict.items() if stats]

        return aggregate, std_devs, len(non_empty_stats_keys)

    # Example usage:
    # Assuming you have the data from your earlier aggregation
    # aggregated_injured_pre, aggregated_injured_post, aggregated_control_pre, aggregated_control_post
    # Convert dictionaries to DataFrames

    aggregated_injured_pre, std_dev_injured_pre, injured_pre_counts = aggregate_stats(injured_pre_stats)
    aggregated_injured_post, std_dev_injured_post, injured_post_counts = aggregate_stats(injured_post_stats)
    aggregated_control_pre, std_dev_control_pre, control_pre_counts = aggregate_stats(control_pre_stats)
    aggregated_control_post, std_dev_control_post, control_post_counts = aggregate_stats(control_post_stats)


    # Create PlayerStats objects directly
    injured_pre_stats = PlayerStats(aggregated_injured_pre, std_dev_injured_pre, injured_pre_counts)
    injured_post_stats = PlayerStats(aggregated_injured_post, std_dev_injured_post, injured_post_counts)
    control_pre_stats = PlayerStats(aggregated_control_pre, std_dev_control_pre, control_pre_counts)
    control_post_stats = PlayerStats(aggregated_control_post, std_dev_control_post, control_post_counts)


    def analyze_diff_in_diff(injured_pre_stats, injured_post_stats, control_pre_stats, control_post_stats, alt_diff=None):
        norm_diff_diffs = {}
        raw_diff_diffs = {}
        p_values = {}
        t_statistics = {}
        
        for stat in injured_pre_stats.aggregated_stats.keys():
            if stat in injured_post_stats.aggregated_stats and stat in control_pre_stats.aggregated_stats and stat in control_post_stats.aggregated_stats:
                # Calculate the differences

                
                diff_injured = injured_post_stats.aggregated_stats[stat] - injured_pre_stats.aggregated_stats[stat]
                diff_control = control_post_stats.aggregated_stats[stat] - control_pre_stats.aggregated_stats[stat]

                if alt_diff is 'injured':
                    diff_in_diff = diff_injured
                elif alt_diff is 'control':
                    diff_in_diff = diff_control
                else:
                    diff_in_diff = diff_injured - diff_control

                
                # Store raw difference-in-differences
                raw_diff_diffs[stat] = diff_in_diff
                
                # Calculate pooled standard error
                se_injured = (injured_pre_stats.std_dev_stats[stat]**2 / injured_pre_stats.sample_size + 
                            injured_post_stats.std_dev_stats[stat]**2 / injured_post_stats.sample_size)**0.5
                se_control = (control_pre_stats.std_dev_stats[stat]**2 / control_pre_stats.sample_size + 
                            control_post_stats.std_dev_stats[stat]**2 / control_post_stats.sample_size)**0.5
                se_diff_in_diff = (se_injured**2 + se_control**2)**0.5
                
                # Normalize using the standard error
                if se_diff_in_diff != 0:  # Avoid division by zero
                    normalized_diff_in_diff = diff_in_diff / se_diff_in_diff
                else:
                    normalized_diff_in_diff = None  # Handle the case where standard error is zero
                
                if normalized_diff_in_diff is not None:
                    norm_diff_diffs[stat] = normalized_diff_in_diff
                    
                    # Calculate degrees of freedom (approximation)
                    df = (injured_pre_stats.sample_size + injured_post_stats.sample_size + 
                        control_pre_stats.sample_size + control_post_stats.sample_size - 4)
                    
                    # Calculate t-statistic and p-value
                    t_stat = normalized_diff_in_diff
                    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))
                    
                    t_statistics[stat] = t_stat
                    p_values[stat] = p_value
        
        return norm_diff_diffs, raw_diff_diffs, t_statistics, p_values

    def plot_diff_in_diff(results, p_vals, t_stats, normalized=True, significance_level=0.05, alt_diff=None):
        # Define a dictionary for human-readable labels and filter out non-performance stats
        stat_labels = {
            "games": "Games Played",
            "shots_on_target": "Shots on Target",
            "npxg": "Non-Penalty Expected Goals",
            # "minutes": "Minutes Played",
            "shots_per90": "Shots per 90 Minutes",
            "xg": "Expected Goals",
            "minutes_per_start": "Minutes per Start",
            "minutes_90s": "90-Minute Periods Played",
            "shots_free_kicks": "Free Kick Shots",
            "minutes_pct": "Percentage of Minutes Played",
            "games_starts": "Games Started",
            "npxg_per_shot": "Non-Penalty Expected Goals per Shot",
            "goals": "Goals Scored",
            "games_subs": "Substitute Appearances",
            "games_complete": "Complete Games",
            "average_shot_distance": "Average Shot Distance",
            "goals_per_shot_on_target": "Goals per Shot on Target",
            "goals_per_shot": "Goals per Shot",
            "minutes_per_game": "Minutes per Game",
            "on_xg_for": "On-Target Expected Goals For",
            "shots": "Total Shots",
            "pens_made": "Penalties Scored",
            "pens_att": "Penalties Attempted",
            "on_xg_against": "On-Target Expected Goals Against",
            "minutes_per_sub": "Minutes per Substitute Appearance",
            "shots_on_target_pct": "Shot on Target Percentage",
            "on_goals_against": "On-Target Goals Against",
            "points_per_game": "Points per Game",
            "on_goals_for": "On-Target Goals For",
            "unused_subs": "Unused Substitute Appearances",
            "shots_on_target_per90": "Shots on Target per 90 Minutes"
        }

        # Filter and prepare the stats and values for sorting
        stats_with_vals = [(stat, results[stat], p_vals[stat], t_stats[stat]) 
                        for stat in results.keys() if stat in stat_labels]
        
        # Sort by p-value (smallest p-value first)
        stats_with_vals.sort(key=lambda x: x[2])
        stats_with_vals.reverse()  # Reverse to have smallest p-values at the top
        
        sorted_stats = [stat_labels[stat] for stat, _, _, _ in stats_with_vals]
        sorted_results = [res for _, res, _, _ in stats_with_vals]
        sorted_p_vals = [p for _, _, p, _ in stats_with_vals]
        sorted_t_stats = [t for _, _, _, t in stats_with_vals]
        
        # Prepare labels
        y_labels = [f"{stat}\np={p:.4f}, t={t:.2f}" for stat, p, t in zip(sorted_stats, sorted_p_vals, sorted_t_stats)]
        
        # Normalize the results for color mapping
        norm = plt.Normalize(min(sorted_results), max(sorted_results))
        colors = cm.RdYlBu(norm(sorted_results))

        # Plotting
        fig, ax = plt.subplots(figsize=(14, 16))  # Increased figure size for better readability
        bars = ax.barh(range(len(sorted_stats)), sorted_results, color=colors)

        # Set custom y-ticks and labels
        ax.set_yticks(range(len(sorted_stats)))
        ax.set_yticklabels(y_labels, fontsize=8)  # Adjusted font size for readability

        
        if alt_diff is 'injured':
            ax.set_xlabel("Normalized Difference for Injured Players" if normalized else "Raw Difference for Injured Players")
            ax.set_title(f"{'Normalized' if normalized else 'Raw'} Statistical Changes for Injured Players (Ordered by P-Value)")
        elif alt_diff is 'control':
            ax.set_xlabel("Normalized Difference for Controls" if normalized else "Raw Difference for Controls")
            ax.set_title(f"{'Normalized' if normalized else 'Raw'} Statistical Changes for Controls (Ordered by P-Value)")
        else:
            ax.set_xlabel("Normalized Difference-in-Differences" if normalized else "Raw Difference-in-Differences")
            ax.set_title(f"{'Normalized' if normalized else 'Raw'} Statistical Changes for Injured Players vs. Controls Pre and Post Injury (Ordered by P-Value)")
        

        
        

        # Add value labels to the end of each bar
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, f'{width:.2f}', 
                    ha='left' if width >= 0 else 'right', va='center')

        # Show plot
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    # # Assuming you have your stats objects defined
    # alt_diff = None
    # results, raw_results, t_stats, p_vals = analyze_diff_in_diff(injured_pre_stats, injured_post_stats, control_pre_stats, control_post_stats, alt_diff=alt_diff)

    # # Plot normalized differences
    # plot_diff_in_diff(results, p_vals, t_stats, normalized=True, alt_diff=alt_diff)
    # plot_diff_in_diff(raw_results, p_vals, t_stats, normalized=False, alt_diff=alt_diff)

    # alt_diff = 'injured'
    # results, raw_results, t_stats, p_vals = analyze_diff_in_diff(injured_pre_stats, injured_post_stats, control_pre_stats, control_post_stats, alt_diff=alt_diff)

    # # Plot normalized differences
    # plot_diff_in_diff(results, p_vals, t_stats, normalized=True, alt_diff=alt_diff)
    # plot_diff_in_diff(raw_results, p_vals, t_stats, normalized=False, alt_diff=alt_diff)

    alt_diff = 'control'
    results, raw_results, t_stats, p_vals = analyze_diff_in_diff(injured_pre_stats, injured_post_stats, control_pre_stats, control_post_stats, alt_diff=alt_diff)

    # Plot normalized differences
    plot_diff_in_diff(results, p_vals, t_stats, normalized=True, alt_diff=alt_diff)
    plot_diff_in_diff(raw_results, p_vals, t_stats, normalized=False, alt_diff=alt_diff)


    injured_pre_df = pd.DataFrame(aggregated_injured_pre, index=[0])
    injured_post_df = pd.DataFrame(aggregated_injured_post, index=[0])
    control_pre_df = pd.DataFrame(aggregated_control_pre, index=[0])
    control_post_df = pd.DataFrame(aggregated_control_post, index=[0])


if __name__ == "__main__":
    main()