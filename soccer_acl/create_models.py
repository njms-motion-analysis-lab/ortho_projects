import pdb  # Standard import at the top
from models import Player, Session, Season, PlayerSeason, PlayerInjury  # Import all required classes
from helpers import flexible_name_search

# Create a new session
session = Session()
Player.where(name='Megan Rapinoe')[0].seasons[0].find_control_matches()



# Commit the session to save the data

def add_link(control_players):
    for player_name, fbref_link in control_players:
        try:
            found_control_player = flexible_name_search(session, Player, player_name)
            print(found_control_player.name, fbref_link)
            Player.update(found_control_player.id, fbref_link=fbref_link)
        except Exception as e:
            print(e)


        

# Close the session
control_players = [
    ["Savannah Demelo","https://fbref.com/en/players/add26dda/Savannah-Demelo#all_stats_standard"],
    ["Jodie Taylor","https://fbref.com/en/players/dc02c40a/Jodie-Taylor#all_stats_standard"],
    ["Sam Mewis","https://fbref.com/en/players/9faa1610/Sam-Mewis#all_stats_standard"],
    ["Adriana","https://fbref.com/en/players/1c9111b9/Adriana#all_stats_standard"],
    ["Alex Morgan","https://fbref.com/en/players/1a64f434/Alex-Morgan#all_stats_standard"],
    ["Erika Tymrak","https://fbref.com/en/players/8443ab57/Erika-Tymrak#all_stats_standard"],
    ["Hal Hershfelt","https://fbref.com/en/players/277ae96a/Hal-Hershfelt#all_stats_standard"],
    ["Dana Foederer","https://fbref.com/en/players/2e6a5e3e/Dana-Foederer#all_stats_standard"],
    ["Morgan Andrews","https://fbref.com/en/players/5c38ee99/Morgan-Andrews#all_stats_standard"],
    ["Alex Singer","https://fbref.com/en/players/0e53dd2e/Alex-Singer#all_stats_standard"],
    ["Emma Sears","https://fbref.com/en/players/7ec2ba7c/Emma-Sears#all_stats_standard"],
    ["Ellie Carpenter","https://fbref.com/en/players/5f2af172/Ellie-Carpenter#all_stats_standard"],
    ["Jonelle Filigno","https://fbref.com/en/players/ba51312d/Jonelle-Filigno#all_stats_standard"],
    ["Dagn√Ω Brynjarsd√≥ttir","https://fbref.com/en/players/ba51312d/Jonelle-Filigno#all_stats_standard"],
    ["Jordan Jackson","https://fbref.com/en/players/bac69c3a/Jordan-Jackson#all_stats_standard"],
    ["Katie Naughton","https://fbref.com/en/players/fa5e9ae1/Katie-Naughton#all_stats_standard"],
    ["Tiffany McCarty","https://fbref.com/en/players/0eee4661/Tiffany-McCarty#all_stats_standard"],
    ["Katie Bowen","https://fbref.com/en/players/aae0d96d/Katie-Bowen#all_stats_standard"],
    ["Jackie Acevedo","https://fbref.com/en/players/4118ae70/Jackie-Acevedo#all_stats_standard"],
    ["Cheyna Matthews","https://fbref.com/en/players/45755108/Cheyna-Matthews#all_stats_standard"],
    ["Hannah Betfort","https://fbref.com/en/players/130c8e6e/Hannah-Betfort#all_stats_standard"],
    ["Ashley Nick","https://fbref.com/en/players/130c8e6e/Hannah-Betfort#all_stats_standard"],
    ["Dani Weatherholt","https://fbref.com/en/players/442d8200/Dani-Weatherholt#all_stats_standard"],
    ["Marissa Everett","https://fbref.com/en/players/56d6c719/Marissa-Everett#all_stats_standard"],
    ["Sarah Clark","https://fbref.com/en/players/0074594d/Sarah-Clark#all_stats_standard"],
    ["Desiree Scott","https://fbref.com/en/players/38c57ecb/Desiree-Scott#all_stats_standard"],
    ["Taylor Porter","https://fbref.com/en/players/3fd67fb6/Taylor-Porter#all_stats_standard"],
    ["Elli Pikkuj√§ms√§","https://fbref.com/en/players/350886ec/Elli-Pikkujamsa#all_stats_standard"],
    ["Sam Witteman","https://fbref.com/en/players/7cfc8b0b/Sam-Witteman#all_stats_standard"],
    ["Luana","https://fbref.com/en/players/55455231/Luana#all_stats_standard"],
    ["Aubrey Kingsbury","https://fbref.com/en/players/020eaa4d/Aubrey-Kingsbury#all_stats_standard"],
    ["Haley Kopmeyer","https://fbref.com/en/players/85a11d14/Haley-Kopmeyer#all_stats_standard"],
    ["Morgan Gautrat","https://fbref.com/en/players/f44c4259/Morgan-Gautrat#all_stats_standard"],
    ["Sam Witteman","https://fbref.com/en/players/7cfc8b0b/Sam-Witteman#all_stats_standard"],
    ["Lori Lindsey","https://fbref.com/en/players/48950247/Lori-Lindsey#all_stats_standard"],
    ["Nicole Barnhart","https://fbref.com/en/players/ad0f455b/Nicole-Barnhart#all_stats_standard"],
    ["Sarah Clark","https://fbref.com/en/players/0074594d/Sarah-Clark#all_stats_standard"],
]

add_link(control_players)

session.commit()

# Query the database
# players = session.query(Player).all()
# for player in players:
#     print(player.name, player.nation)




session.close()
