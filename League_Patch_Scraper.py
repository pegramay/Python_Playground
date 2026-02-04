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

from typing import List, Dict

import requests  # Library that simplifies making HTTP requests (Easy http info grabs)
from bs4 import BeautifulSoup  # Parses HTML and XML documents


def parse_ability_section(html: str) -> Dict[str, object]:
    """
    Parse a single ability block from League of Legends patch notes.

    Args:
        html (str): The string to the riot website and patch notes
            The raw HTML that contains:
                <h4 class="change-detail-title ability-title"> 
                    <ul>
                        <li></li>
                    </ul>
                </h4>

    Returns:
        Dict: A dictionary that holds the name of the ability scanned and the information associated with it
    """
    soup = BeautifulSoup(html, "html.parser")

    h4_tag = soup.find("h4", class_="change-detail-title")
    if not h4_tag:
        raise ValueError(
            "Missing <h4 class='change-detail-title'> in ability block."
        )

    # Ability name – strip the image tag and surrounding whitespace
    ability_name = h4_tag.get_text(strip=True)

    changes: List[Dict[str, str]] = []
    for li in soup.select("ul > li"):
        strong_tags = li.find_all("strong")
        if not strong_tags:
            continue  # skip malformed lines

        label = strong_tags[0].get_text(strip=True)

        raw_text = li.get_text(separator=" ", strip=True)
        parts = raw_text.split(":", 1)
        description = parts[1].strip() if len(parts) == 2 else raw_text

        changes.append({"label": label, "description": description})

    return {"name": ability_name, "changes": changes}


def scrape_patch_notes(url):
    """
    Scrapes League of Legends patch notes from Riot's website,
    extracting basic champion buff/nerf information.

    Args:
        url (str): The URL of the Riot Games patch notes page.

    Returns:
        list: A list of dictionaries which correlate between a champions name
              as well as the abilites that were nerfed or buffed next to them.
    """
    try:
        print("entered the try")
        response = requests.get(url, timeout=10)  # the timeout keeps it so it doesn't keep spamming the site and I get blocked
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, "html.parser") #ITS ABLE TO PARSE THE INFORMATION
        champion_changes: List[Dict[str, object]] = []

        # Find champion sections - adjust selector if Riot changes their HTML structure!
        # ERROR: Not able to gather information starting from here, div is incorrect
        champion_sections = soup.find_all("h2", class_="patch-champions")  # This is a key selector to change if the site updates
        print(champion_sections)
        for section in champion_sections:
            name_element = section.find("h3", class_="change-title")  # Find the champion name header
            print(name_element)
            if not name_element:
                pass  # Skip this section if no champion name is found

            link = name_element.find("a")
            champion_name = name_element.text.strip()
            print(f"Champion name: {champion_name}")
            champion_url = link["href"]
            print(f"URL: {champion_url}")

            # This is the ability section
            for h4_tag in champion_sections.find_next_siblings(
                "h4", class_="change-detail-title"
            ):
                if "ability-title" not in h4_tag.get("class", []):
                    continue  # skip non‑ability titles

                ul_tag = h4_tag.find_next_sibling("ul")
                if not ul_tag:
                    continue

                full_html = str(h4_tag) + str(ul_tag)
                ability_info = parse_ability_section(full_html)

                champion_changes.append(
                    {
                        "champion": champion_name,
                        "ability": ability_info["name"],
                        "changes": ability_info["changes"],
                    }
                )

        return champion_changes

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []


def main():
    """Main function to run the scraper and print results."""
    patch_notes_url = "https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-3-notes/"  # Replace with current patch notes URL

    changes = scrape_patch_notes(patch_notes_url)

    if changes:
        print("Champion Buffs and Nerfs:")
        for change in changes:
            print(
                f"- {change['champion']} ({change['ability']}): "
                + ", ".join(
                    f"{c['label']}: {c['description']}" for c in change["changes"]
                )
            )
    else:
        print("No champion buffs/nerfs found or an error occurred.")


if __name__ == "__main__":
    main()
