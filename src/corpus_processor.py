from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from utils.cleaner import TextCleaner
from utils.timer import Timer
import requests
import uuid
import math
import json
import os


class CorpusProcessor:
    """
    This processor class randomly retrieves a large number of Wikipedia articles in Romanian
    and generates a word frequency dictionary that will be used to classify "simple" and
    "complex" words.
    """

    MAX_WORKERS = 20
    DOCUMENTS_NUMBER = 2
    # RANDOM_WIKI = "https://ro.wikipedia.org/wiki/Special:Random"
    RANDOM_WIKI = "https://ro.wikipedia.org/wiki/Special:RandomInCategory?&wpcategory=Articole+de+calitate"
    RELATE_URL = "http://relate.racai.ro:5000/process"
    HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

    def generate_frequencies(self, file_suffix: str) -> str:
        f = open(
            f"../data/wikipedia/intermediary/{file_suffix}.json", "w", encoding="utf8"
        )
        f.close()

        word_frequencies = dict()
        wiki_articles_urls = list()

        print(f"{file_suffix} - 0/{self.DOCUMENTS_NUMBER} done")

        for i in range(self.DOCUMENTS_NUMBER):

            page = requests.get(self.RANDOM_WIKI)
            soup = BeautifulSoup(page.content, "html.parser")

            just_added = dict()

            for p in soup.find_all("p"):
                text = p.get_text()
                text = TextCleaner().clean_text(text)

                if text != "":
                    res = requests.post(
                        self.RELATE_URL,
                        headers=self.HEADERS,
                        data=f"tokenization=ttl-icia&text={text}  ",
                    )
                    res = res.json()["teprolin-result"]

                    splitted_text = text.split()
                    splitted_input = res["sentences"][0].split()

                    processed_list = res["tokenized"][0]
                    if len(splitted_text) > len(splitted_input):
                        diff = len(splitted_text) - len(splitted_input)
                        processed_list = processed_list[:-diff]
                    elif (
                        len(splitted_text) == len(splitted_input)
                        and splitted_text[-1] != splitted_input[-1]
                    ):
                        processed_list = processed_list[:-1]

                    for item in processed_list:
                        if item["_ctg"] not in [
                            "S",
                            "Y",
                            "M",
                            "CR",
                            "NP",
                            "PPSR",
                            "PERIOD",
                        ]:
                            word_frequencies[item["_lemma"]] = word_frequencies.get(
                                item["_lemma"], [0] * self.DOCUMENTS_NUMBER
                            )
                            just_added[item["_lemma"]] = (
                                just_added.get(item["_lemma"], 0) + 1
                            )

            # If the word was found in this iteration, we increase the number of documents it
            # is present in by one
            for word, value in just_added.items():
                word_frequencies[word][i] = value

            wiki_articles_urls.append(page.url)
            print(f"{file_suffix} - {i+1}/{self.DOCUMENTS_NUMBER} done - {page.url}")

            # Write to file during iteration to save progress
            f = open(
                f"../data/wikipedia/intermediary/{file_suffix}.json",
                "w",
                encoding="utf8",
            )
            json.dump(
                {
                    "wikipedia_articles_urls": wiki_articles_urls,
                    "word_frequencies": word_frequencies,
                },
                f,
                ensure_ascii=False,
            )
            f.flush()

        f.close()

        return file_suffix

    def get_lemma(self, word):
        res = requests.post(
            self.RELATE_URL,
            headers=self.HEADERS,
            data=f"tokenization=ttl-icia&text={word}  ",
        )
        return res.json()["teprolin-result"]["tokenized"][0][0]["_lemma"]

    def multithread_runner(self):
        threads = []
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            for _ in range(self.MAX_WORKERS):
                file_suffix = uuid.uuid1()
                threads.append(executor.submit(self.generate_frequencies, file_suffix))

            for task in as_completed(threads):
                print(f"Task {task.result()} completed!")

    def get_idf_merge(self):
        directory = "../data/wikipedia/intermediary"
        ro_wikipedia = {"wikipedia_articles_urls": [], "word_frequencies": {}}
        documents_total = 0

        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            f = open(file_path, "r", encoding="utf8")
            temp = json.load(f)
            f.close()

            ro_wikipedia["wikipedia_articles_urls"].extend(
                temp["wikipedia_articles_urls"]
            )
            documents_total += len(temp["wikipedia_articles_urls"])

            ro_wikipedia["word_frequencies"] = self.__merge_dictionaries(
                ro_wikipedia["word_frequencies"], temp["word_frequencies"]
            )

        # Calculate inverse document frequency (idf)
        for key, value in ro_wikipedia["word_frequencies"].items():
            ro_wikipedia["word_frequencies"][key] = math.log(documents_total / value)

        f = open("../data/wikipedia/ro_wikipedia.json", "w", encoding="utf8")
        json.dump(ro_wikipedia, f, ensure_ascii=False)
        f.close()

    def __merge_dictionaries(self, dict1: dict, dict2: dict):
        res_dict = {**dict1, **dict2}
        for key, value in res_dict.items():
            if key in dict1 and key in dict2:
                res_dict[key] = value + dict1[key]

        return res_dict


if __name__ == "__main__":
    t = Timer()
    cp = CorpusProcessor()

    t.start()
    cp.multithread_runner()
    # cp.get_idf_merge()
    # print(cp.get_lemma("aceluia"))
    t.stop()
