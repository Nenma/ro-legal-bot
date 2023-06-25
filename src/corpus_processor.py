from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import requests
import spacy
import uuid
import math
import json
import re
import os

from utils.cleaner import TextCleaner
from utils.timer import Timer
from law_processor import LawProcessor


class CorpusProcessor:
    """
    This processor class collects word frequency data for both general (Wikipedia) texts
    and legal texts, as well as handles formatting and processing of it.
    """

    MAX_WORKERS = 1
    DOCUMENTS_NUMBER = 1

    DEX_URL = "https://dexonline.ro/definitie"

    QUALITY_ARTICLES = 200  # number recorded as of June 2023
    RANDOM_QUALITY_WIKI = "https://ro.wikipedia.org/wiki/Special:RandomInCategory?&wpcategory=Articole+de+calitate"

    GOOD_ARTICLES = 493  # number recorded as of June 2023
    RANDOM_GOOD_WIKI = "https://ro.wikipedia.org/wiki/Special:RandomInCategory?&wpcategory=Articole+bune"

    RELATE_URL = "http://relate.racai.ro:5000/process"
    RELATE_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

    nlp = spacy.load("ro_core_news_lg")
    tc = TextCleaner()
    lp = LawProcessor()

    def get_articles_list(self, outfile: str, url: str, list_size: str):
        wikis = {}

        f = open(f"../data/wikipedia/{outfile}", "w", encoding="utf8")
        f.close()

        while len(wikis) < list_size:
            page = requests.get(url)
            wikis[page.url] = wikis.get(page.url, 0) + 1

            f = open(f"../data/wikipedia/{outfile}", "w", encoding="utf8")
            json.dump(wikis, f, ensure_ascii=False, indent=3)
            f.flush()
        f.close()

    # TODO: rethink utility
    def generate_legal_frequencies(self):
        f = open("../data/corpus/legal.json", "w", encoding="utf8")
        f.close()

        codes_keywords = [
            "Codul administrativ",
            "Codul civil",
            "Codul de procedură civilă",
            "Constituția",
            "Codul fiscal",
            "Codul de procedură fiscală",
            "Codul muncii",
            "Codul penal",
            "Codul de procedură penală",
        ]
        word_frequencies = dict()

        print(f"0/{len(codes_keywords)} done")
        for i, key in enumerate(codes_keywords):
            word_frequencies[key] = dict()

            code_size = self.lp.get_code_size(key)
            code_size = int(re.findall(r"\d+", code_size)[0])

            for j in range(1, code_size + 1):
                clean_article = self.tc.clean_text(self.lp.find_article(j, key))
                res = self.nlp(clean_article)
                for word in res:
                    if word.pos_ not in ["PNOUN", "PUNCT"]:
                        w = word.lemma_.lower()
                        word_frequencies[key][w] = word_frequencies[key].get(
                            w, {"freq": 0, "articles": []}
                        )
                        word_frequencies[key][w]["freq"] += 1
                        if j not in word_frequencies[key][w]["articles"]:
                            word_frequencies[key][w]["articles"].append(j)

            print(f"{i+1}/{len(codes_keywords)} done - {key}")

            f = open("../data/corpus/legal.json", "w", encoding="utf8")
            json.dump(word_frequencies, f, ensure_ascii=False, indent=3)
            f.flush()

        f.close()

    def generate_frequencies_with_scipy(self, infile: str):
        f = open(f"../data/wikipedia/{infile}", "r", encoding="utf8")
        url_list = json.load(f).keys()
        f.close()

        f = open(f"../data/corpus/intermediary/{infile}", "w", encoding="utf8")
        f.close()

        word_frequencies = dict()
        wiki_articles_urls = list()

        print(f"{infile} - 0/{len(url_list)} done")

        for i, url in enumerate(url_list):
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            just_added = dict()

            for p in soup.find_all("p"):
                text = p.get_text()
                text = TextCleaner().clean_text(text)

                if text != "":
                    res = self.nlp(text)

                    for word in res:
                        if word.pos_ not in ["PROPN", "PUNCT"]:
                            w = word.lemma_.lower()
                            word_frequencies[w] = word_frequencies.get(
                                w, [0] * len(url_list)
                            )
                            just_added[w] = just_added.get(w, 0) + 1

            for word, value in just_added.items():
                word_frequencies[word][i] = value

            wiki_articles_urls.append(page.url)
            print(f"{infile} - {i+1}/{len(url_list)} done - {page.url}")

            # Write to file during iteration to save progress
            f = open(
                f"../data/corpus/intermediary/{infile}",
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
                indent=3,
            )
            f.flush()

        f.close()

    # TODO: readjust with articles list
    def generate_frequencies_with_relate(self, file_suffix: str) -> str:
        f = open(
            f"../data/corpus/intermediary/{file_suffix}.json", "w", encoding="utf8"
        )
        f.close()

        word_frequencies = dict()
        wiki_articles_urls = list()

        print(f"{file_suffix} - 0/{self.DOCUMENTS_NUMBER} done")

        for i in range(self.DOCUMENTS_NUMBER):
            page = requests.get(self.RANDOM_QUALITY_WIKI)
            soup = BeautifulSoup(page.content, "html.parser")

            just_added = dict()

            for p in soup.find_all("p"):
                text = p.get_text()
                text = TextCleaner().clean_text(text)

                if text != "":
                    res = requests.post(
                        self.RELATE_URL,
                        headers=self.RELATE_HEADERS,
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

            for word, value in just_added.items():
                word_frequencies[word][i] = value

            wiki_articles_urls.append(page.url)
            print(f"{file_suffix} - {i+1}/{self.DOCUMENTS_NUMBER} done - {page.url}")

            # Write to file during iteration to save progress
            f = open(
                f"../data/corpus/intermediary/{file_suffix}.json",
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
                indent=3,
            )
            f.flush()

        f.close()

        return file_suffix

    def get_lemma_with_relate(self, word):
        word = word.lower()
        res = requests.post(
            self.RELATE_URL,
            headers=self.RELATE_HEADERS,
            data=f"lemmatization=ttl-icia&text={word}  ",
        )
        return res.json()["teprolin-result"]["tokenized"][0][0]["_lemma"]

    def get_dex_definition(self, word):
        word = word.lower()
        page = requests.get(f"{self.DEX_URL}/{word}")
        soup = BeautifulSoup(page.content, "html.parser")

        definitions = soup.find_all("span", {"class": "def html"})
        alt_definition = soup.find_all("span", {"class": "def"})

        if len(definitions) > 0:
            definition = definitions[0].text.strip()
        elif len(alt_definition) > 0:
            definition = alt_definition[0].text.strip()
        else:
            definition = word

        return definition

    def multithread_runner(self):
        threads = []
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            for _ in range(self.MAX_WORKERS):
                file_suffix = uuid.uuid1()
                threads.append(
                    executor.submit(self.generate_frequencies_with_scipy, file_suffix)
                )

            for task in as_completed(threads):
                print(f"Task {task.result()} completed!")

    def get_tfidf_merge(self):
        directory = "../data/corpus"
        ro_wikipedia = {"wikipedia_articles_urls": [], "word_frequencies": {}}

        for file_name in os.listdir(f"{directory}/intermediary"):
            if file_name.endswith(".json"):
                file_path = os.path.join(f"{directory}/intermediary", file_name)
                f = open(file_path, "r", encoding="utf8")
                temp = json.load(f)
                f.close()

                for i, url in enumerate(temp["wikipedia_articles_urls"]):
                    if url not in ro_wikipedia["wikipedia_articles_urls"]:
                        ro_wikipedia["wikipedia_articles_urls"].append(url)

                        for key, value in temp["word_frequencies"].items():
                            ro_wikipedia["word_frequencies"][key] = ro_wikipedia[
                                "word_frequencies"
                            ].get(
                                key,
                                {
                                    "raw": [0]
                                    * (
                                        len(ro_wikipedia["wikipedia_articles_urls"]) - 1
                                    ),
                                    "tf": 0,
                                    "tfidf": [],
                                },
                            )
                            ro_wikipedia["word_frequencies"][key]["raw"].append(
                                value[i]
                            )
                            if value[i] > 0:
                                ro_wikipedia["word_frequencies"][key]["tf"] += 1

                        for key in ro_wikipedia["word_frequencies"].keys():
                            if key not in temp["word_frequencies"].keys():
                                ro_wikipedia["word_frequencies"][key]["raw"].append(0)

        # Calculate tf-idf
        documents_total = len(ro_wikipedia["wikipedia_articles_urls"])
        for key, value in ro_wikipedia["word_frequencies"].items():
            for i, freq in enumerate(value["raw"]):
                ro_wikipedia["word_frequencies"][key]["tfidf"].append(
                    self.get_tfidf(freq, documents_total, value["tf"])
                )

        f = open(f"{directory}/ro_wikipedia.json", "w", encoding="utf8")
        json.dump(ro_wikipedia, f, ensure_ascii=False, indent=3)
        f.close()

        for key, value in ro_wikipedia["word_frequencies"].items():
            ro_wikipedia["word_frequencies"][key] = sum(value["tfidf"]) / len(
                value["tfidf"]
            )

        f = open(f"{directory}/ro_wikipedia_final.json", "w", encoding="utf8")
        json.dump(ro_wikipedia, f, ensure_ascii=False, indent=3)
        f.close()

    def get_tfidf(self, tf: int, n: int, d: int) -> float:
        """
        Get tf-idf value of a word.

        :param int tf: The number of occurences in the document
        :param int n: The total number of documents
        :param int d: The number of documents in which the word is present
        """
        return math.log(1 + tf) * math.log(n / (d + 1))


if __name__ == "__main__":
    t = Timer()
    cp = CorpusProcessor()

    t.start()
    # cp.multithread_runner()
    # cp.generate_legal_frequencies()
    cp.get_tfidf_merge()
    # cp.get_tfidf_merge()
    t.stop()
