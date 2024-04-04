from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def load_pickems_page(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.wf-module-item"))
    )
    elements = driver.find_elements(By.CSS_SELECTOR, "a.wf-module-item")
    pickem_urls = [element.get_attribute("href") for element in elements]  # Collect URLs
    names = [element.find_element(By.CSS_SELECTOR, "div[style*='margin-bottom: 2px;']").text for element in elements]
    print(f"Found {len(names)} names")
    return names, pickem_urls

def load_each_pickem(driver, pickem_urls, names, week, match_num):
    picks_by_team = {}  # Dictionary to store picks keyed by team name

    for x, url in enumerate(pickem_urls):
        driver.get(url)
        container_selector = f"div.event-subseries-container:nth-child({int(week)+1}) > div:nth-child(2) > div:nth-child({int(match_num)})"

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
            )
            teams_elements = driver.find_elements(By.CSS_SELECTOR, f"{container_selector} .pi-match-item-team")
        except TimeoutException:
            print(f"No match found for week {week} and match {match_num}")
            break

        for team in teams_elements:
            is_selected = "mod-selected" in team.get_attribute("class")
            if is_selected:
                team_name = team.find_element(By.CSS_SELECTOR, ".pi-match-item-name").text
                
                # Add the picker's name to the team's list in the dictionary
                if team_name not in picks_by_team:
                    picks_by_team[team_name] = [names[x]]
                else:
                    picks_by_team[team_name].append(names[x])
    
    return picks_by_team


def main():
    url = input("Enter the pickem group url: ")
    week = input("Enter the week number for the match: ")
    match_num = input("Enter the match number for that week: ")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")

    chrome_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    names, pickem_urls = load_pickems_page(driver, url)

    picks_by_team = load_each_pickem(driver, pickem_urls, names, week, match_num)
    
    # Print the results
    for team, pickers in picks_by_team.items():
        print(f"\n{team}:")
        for picker in pickers:
            print(picker)
    print("\n")
    for team, pickers in picks_by_team.items():
        print(f"{len(pickers)} total picked {team}")

    driver.quit()


if __name__ == "__main__":
    main()