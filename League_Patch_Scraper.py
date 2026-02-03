"""
Reading patch notes is too much work, summarize it for me with hopefully this!

Important Considerations & Future Improvements:
NOTE
Riot's Website Structure Changes: Riot can change their website at any time, which will break the script. 
Hard coded CSS values for the div information

TODO
- Data Storage: Instead of just printing the results, you could store them in a file (CSV, JSON) or database for later analysis.
- Add more detail of specific information
- Possible search feature for specific champions
- GUI/Web Interface: You could create a graphical user interface (GUI) or web application to make the scraper more accessible to non-technical users.
- Automated Patch Detection
"""



import requests # Library that simplifies making HTTP requests (Easy http info grabs)
from bs4 import BeautifulSoup # Parses HTML and XML documents

def scrape_patch_notes(url):
    """
    Scrapes League of Legends patch notes from Riot's website, 
    extracting basic champion buff/nerf information.

    Args:
        url (str): The URL of the Riot Games patch notes page.

    Returns:
        list: A list of dictionaries, where each dictionary represents a 
              champion change with 'name', 'type' ('buff' or 'nerf'), and 'description'.
              Returns an empty list if scraping fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, 'html.parser')

        champion_changes = []

        # Find champion sections - adjust selector if Riot changes their HTML structure!
        champion_sections = soup.find_all('div', class_='notes-champion-section')  # This is a key selector to change if the site updates

        for section in champion_sections:
            name_element = section.find('h3', class_='notes-champion-header') # Find the champion name header
            if not name_element:
                continue  # Skip this section if no champion name is found

            champion_name = name_element.text.strip()

            change_elements = section.find_all('div', class_='notes-champion-ability') #Find ability changes within the champion section

            for change in change_elements:
                type_span = change.find('span', class_='notes-champion-ability-type')  # Find 'Buff' or 'Nerf' span
                if type_span:
                    change_type = type_span.text.strip().lower() # Get the buff/nerf type

                    description_element = change.find('div', class_='notes-champion-ability-description')  # Find description div
                    if description_element:
                        description = description_element.text.strip()
                    else:
                        description = "No detailed description available." #Handle missing descriptions

                    champion_changes.append({
                        'name': champion_name,
                        'type': change_type,
                        'description': description
                    })

        return champion_changes

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return []  
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []


def main():
    """Main function to run the scraper and print results."""
    patch_notes_url = "https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-2-notes/"  # Replace with current patch notes URL

    changes = scrape_patch_notes(patch_notes_url)

    if changes:
        print("Champion Buffs and Nerfs:")
        for change in changes:
            print(f"- {change['name']} ({change['type'].capitalize()}): {change['description']}")
    else:
        print("No champion buffs/nerfs found or an error occurred.")


if __name__ == "__main__":
    main()

