import logging

import requests
from bs4 import BeautifulSoup


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
        x = [f"Character Name: {self.character_name}", f"Webpage URL: {self.webpage_url}",
             f"Description: {self.description}"]

        return f"Search Result #{self.result_num}:" + "\n\t-" + "\n\t-".join(x)


class CharacterSearcher:
    def __init__(self, character_name: str, lang="en", page_num=1):
        self.lang = lang
        self.page_num = page_num
        self.results = []
        self.character_name = character_name
        self.search_character()

    def search_character(self):
        joined_name = self.character_name.strip().replace(" ", "+")
        search_url = f"https://vsbattles.fandom.com/wiki/" \
                     f"Special:Search?query={joined_name}&lang={self.lang}&page={self.page_num}"

        response = requests.get(search_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        soup = BeautifulSoup(response.text, 'html.parser')
        search_result_list = soup.find('ul', class_="unified-search__results")

        search_results = search_result_list.find_all('li')
        character_datas = []
        for index, search_result in enumerate(search_results):
            character_datas.append(self._extract_info_from_search_res(search_result, index + 1))

        self.results = character_datas
        print(self)

    def get_page_by_num(self, page_num: int):
        if page_num < 1:
            logging.error("The page numbers start from 1.")
        else:
            self.page_num = page_num
            self.search_character()

    def get_next_page(self):
        self.get_page_by_num(self.page_num + 1)

    def get_prev_page(self):
        self.get_page_by_num(self.page_num - 1)

    @staticmethod
    def _extract_info_from_search_res(search_result, result_num) -> CharacterSearchResult:
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

            return CharacterSearchResult(anchor_text.strip(), href.strip(), content_text.strip(), result_num)
        except Exception as e:
            logging.error("An error occurred while parsing search results: ", str(e))

    def __str__(self):
        if len(self.results) == 0:
            return f"No results to print for page #{self.page_num}!\n"
        else:
            res_string = f"Displaying search results for page #{self.page_num}:\n"
            res_string += '\n'.join(map(str, self.results))
            return res_string
