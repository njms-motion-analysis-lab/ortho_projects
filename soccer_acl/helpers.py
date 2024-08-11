import datetime
import pandas as pd
from sqlalchemy.orm.exc import NoResultFound

def parse_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%m/%d/%y').date()
    except ValueError:
        return None

def aggregate_stats(seasons):
    # Convert seasons to a DataFrame
    data = [
        {
            'goals': season.gls,
            'matches_played': season.mp,
            'minutes': season.min,
            'nineties': season.n90s,
            'starts': season.starts,
            'substitutions': season.subs,
            'unused_substitutions': season.unsub,
            'assists': season.ast,
            'goals_and_assists': season.g_a,
            'goals_penalty_kicks': season.g_pk,
            'penalty_kicks_scored': season.pk,
            'penalty_kicks_attempted': season.pk_att,
            'penalty_kicks_missed': season.pk_m,
            'penalty_kick_percentage': (season.pk / season.pk_att * 100) if season.pk_att is not None and season.pk_att > 0 else None
        }
        for season in seasons
    ]

    df = pd.DataFrame(data)

    # Ensure that only numerical columns are aggregated
    df = df.select_dtypes(include='number')

    return df.mean()

def flexible_name_search(Session, Player, full_name):
    # First, try an exact match
    try:
        return Session.query(Player).filter_by(name=full_name).one()
    except NoResultFound:
        pass
    
    # Try searching by first name
    first_name = full_name.split()[0]
    players = Session.query(Player).filter(Player.name.like(f"%{first_name}%")).all()
    
    if len(players) == 1:
        return players[0]
    
    # Try searching by first name and initial of the last name
    if len(full_name.split()) > 1:
        last_name_initial = full_name.split()[1][0]
        players = Session.query(Player).filter(
            Player.name.like(f"%{first_name} {last_name_initial}%")
        ).all()
    
    if len(players) == 1:
        return players[0]
    
    return None

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

