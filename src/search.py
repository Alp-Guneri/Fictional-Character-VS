import logging

import requests
from bs4 import BeautifulSoup
from typing import List


class CharacterSearchResult:
    def __init__(self, character_name: str, webpage_url: str, description: str, result_num: int) -> None:
        self.character_name = character_name
        self.webpage_url = webpage_url
        self.description = description
        self.result_num = result_num

    def __eq__(self, other):
        if isinstance(other, CharacterSearchResult):
            return self.webpage_url == other.webpage_url
        return False

    def __str__(self):
        return f"Search Result #{self.result_num}: \n\t-Character Name: {self.character_name}\n" \
               f"Webpage URL: {self.webpage_url}\nDescription: {self.description}\n"


def search_character(character_name: str, lang="en", page_num=1) -> List[CharacterSearchResult]:
    joined_name = character_name.strip().replace(" ", "+")
    search_url = f"https://vsbattles.fandom.com/wiki/Special:Search?query={joined_name}&lang={lang}&page={page_num}"

    response = requests.get(search_url)
    response.raise_for_status()  # Raise an HTTPError for bad responses

    soup = BeautifulSoup(response.text, 'html.parser')
    search_result_list = soup.find('ul', class_="unified-search__results")

    search_results = search_result_list.find_all()
    character_datas = []
    for index, search_result in enumerate(search_results):
        character_datas.append(extract_info_from_search_res(search_result, index))

    return character_datas


def extract_info_from_search_res(search_result, result_num) -> CharacterSearchResult:
    try:
        href = None
        anchor_text = None
        content_text = None
        # Find the anchor element within the <h3> element
        h3_element = search_result.find('h3')
        if h3_element:
            anchor_element = h3_element.find('a')
            if anchor_element:
                href = anchor_element.get('href')
                anchor_text = anchor_element.get_text()

        # Find the <div> element with class "unified-search__result__content"
        content_div = search_result.find('div', class_='unified-search__result__content')
        if content_div:
            content_text = content_div.get_text()

        return CharacterSearchResult(anchor_text, href, content_text, result_num)
    except Exception as e:
        logging.error("An error occurred while parsing search results: ", str(e))


def display_results(results: List[CharacterSearchResult], page_number=1):
    res_string = f"Displaying search results for page #{page_number}:"
    res_string += '\n'.join(map(str, results))
    print(res_string)
    