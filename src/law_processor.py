from bs4 import BeautifulSoup
import requests
import json
import math
import re
import os

from utils.law_urls import LawUrls


class LawProcessor:
    """
    The general structure of the legal text is: Content -> Books -> Titles -> Chapters -> Sections -> Subsections -> Articles.

    The processor creates a single general structure for all legal text documents.
    """

    def process_laws(self):
        print("done 0/9")

        self.process_general_code_type1(
            "../data/processed-laws/codes/constitution.json",
            "Constituția României / Constituție a României / Conținutul Constituției din România",
            LawUrls.CONSTITUTION,
        )
        print("done 1/9 - Constitution")
        self.process_general_code_type1(
            "../data/processed-laws/codes/fiscal_code.json",
            "Codul Fiscal al României / Cod Fiscal al României / Conținutul Codului Fiscal al României",
            LawUrls.FISCAL,
        )
        print("done 2/9 - Fiscal")
        self.process_general_code_type1(
            "../data/processed-laws/codes/fiscal_procedure_code.json",
            "Codul de Procedură Fiscală al României / Cod de Procedură Fiscală al României / Conținutul Codului de Procedură Fiscală al României",
            LawUrls.FISCAL_PROCEDURE,
        )
        print("done 3/9 - Fiscal procedure")
        self.process_general_code_type1(
            "../data/processed-laws/codes/labor_code.json",
            "Codul Muncii al României / Cod de Muncă al României / Conținutul Codului Muncii al României",
            LawUrls.LABOR,
        )
        print("done 4/9 - Labor")

        self.process_general_code_type2(
            "../data/processed-laws/codes/penal_code.json",
            "Codul Penal al României / Cod Penal al României / Conținutul Codului Penal al României",
            LawUrls.PENAL,
            r"\nPartea (.*)\n\n",
        )
        print("done 5/9 - Penal")
        self.process_general_code_type2(
            "../data/processed-laws/codes/penal_procedure_code.json",
            "Codul de Procedură Penală al României / Cod de Procedură Penală al României / Conținutul Codului de Procedură Penală al României",
            LawUrls.PENAL_PROCEDURE,
            r"\nPartea ([A-ZĂÎÂȘȚ]+)",
        )
        print("done 6/9 - Penal procedure")
        self.process_general_code_type2(
            "../data/processed-laws/codes/administrative_code.json",
            "Codul Administrativ al României / Cod Administrativ al României / Conținutul Codului Administrativ al României",
            LawUrls.ADMINISTRATIVE,
            r"\nPARTEA (.*)\n",
        )
        print("done 7/9 - Administrative")

        self.process_civil_code(
            "../data/processed-laws/codes/civil_code.json",
            "Codul Civil al României / Cod Civil al României / Conținutul Codului Civil al României",
            LawUrls.CIVIL,
            "PRELIMINAR",
        )
        print("done 8/9 - Civil")
        self.process_civil_code(
            "../data/processed-laws/codes/civil_procedure_code.json",
            "Codul de Procedură Civilă al României / Cod de Procedură Civilă al României / Conținutul Codului de Procedură Civilă al României",
            LawUrls.CIVIL_PROCEDURE,
            "PRELIMINAR",
        )
        print("done 9/9 - Civil procedure")

        self.__concatenate_laws()

    def __concatenate_laws(self):
        directory = "../data/processed-laws"

        codes_json = []
        for i, file_name in enumerate(os.listdir(f"{directory}/codes")):
            file_path = os.path.join(f"{directory}/codes", file_name)
            f = open(file_path, "r", encoding="utf8")
            codes_json.append(json.load(f))
            codes_json[i]["code_number"] = i + 1
            f.close()

        f = open(f"{directory}/codes.json", "w", encoding="utf8")
        json.dump(codes_json, f, ensure_ascii=False, indent=3)
        f.close()

    def process_civil_code(
        self, outfile: str, code_name: str, code_url: LawUrls, first_book_name: str
    ):
        text = self.__get_code_text(code_url)
        text = re.sub(r"\n[A-Z]+\. .*\n", "", text)

        civil_code = {"name": code_name, "books": []}

        books = re.split(r"\nCartea ", text)
        for ib, book in enumerate(books):
            b = dict()

            book_name, titles_text = re.split(r"\n", book, 1)

            if ib == 0:
                # First "book" does not have proper name
                b["name"] = first_book_name
            elif "-" in book_name:
                # ex: a II-a Despre familie
                b["name"] = book_name.split(" ", 2)[-1]
            else:
                # ex: I Despre persoane
                b["name"] = book_name.split(" ", 1)[-1]

            b["number"] = ib + 1
            b["titles"] = []

            start, end = self.__process_titles(titles_text, b["name"], b["titles"])

            b["range"] = [start, end]

            civil_code["books"].append(b)

        civil_code["range"] = [
            civil_code["books"][0]["range"][0],
            civil_code["books"][-1]["range"][1],
        ]

        f = open(outfile, "w", encoding="utf8")
        json.dump(civil_code, f, ensure_ascii=False, indent=3)
        f.close()

    def process_general_code_type1(
        self, outfile: str, code_name: str, code_url: LawUrls
    ):
        text = self.__get_code_text(code_url)

        general_code = {
            "name": code_name,
            "books": [
                {
                    "name": code_name,
                    "number": 1,
                    "titles": [],
                }
            ],
        }

        start, end = self.__process_titles(
            text, general_code["books"][0]["name"], general_code["books"][0]["titles"]
        )

        general_code["books"][0]["range"] = [start, end]
        general_code["range"] = [start, end]

        f = open(outfile, "w", encoding="utf8")
        json.dump(general_code, f, ensure_ascii=False, indent=3)
        f.close()

    def process_general_code_type2(
        self, outfile: str, code_name: str, code_url: LawUrls, delimiter: str
    ):
        text = self.__get_code_text(code_url)

        general_code = {"name": code_name, "books": []}

        books = re.split(delimiter, text)
        for i in range(1, len(books[1:]), 2):
            b = dict()

            _, titles_text = re.split(r"\n", books[i + 1], 1)
            b["name"] = books[i].strip()
            b["number"] = math.floor(i / 2) + 1
            b["titles"] = []

            start, end = self.__process_titles(titles_text, b["name"], b["titles"])

            b["range"] = [start, end]

            general_code["books"].append(b)

        general_code["range"] = [
            general_code["books"][0]["range"][0],
            general_code["books"][-1]["range"][1],
        ]

        f = open(outfile, "w", encoding="utf8")
        json.dump(general_code, f, ensure_ascii=False, indent=3)
        f.close()

    def __get_code_text(self, code_url):
        page = requests.get(code_url)
        soup = BeautifulSoup(page.content, "html.parser")

        for sp in soup.find_all("span", {"class": "S_ALN_TTL"}):
            sp.string = f"NEWLINE{sp.text}"

        for br in soup.find_all("br"):
            br.replaceWith("NEWLINE")

        return soup.get_text().replace("NEWLINE", "\n")

    def __process_titles(self, titles_text: str, book_name: str, book_titles: list):
        if "\nTitlul" in titles_text:
            titles = re.split(r"\nTitlul [A-Z]", titles_text)
            for it, title in enumerate(titles):
                if "EMITENT" in title or len(title) <= 1:
                    continue

                t = dict()

                title_name, chapters_text = re.split(r"\n", title, 1)

                t["name"] = title_name.split(" ", 1)[-1]
                t["number"] = it + 1
                t["chapters"] = []

                start, end = self.__process_chapters(
                    chapters_text, t["name"], t["chapters"]
                )
                t["range"] = [start, end]

                book_titles.append(t)

            return [book_titles[0]["range"][0], book_titles[-1]["range"][1]]
        else:
            book_titles.append(
                {
                    "name": book_name,
                    "number": 1,
                    "chapters": [
                        {
                            "name": book_name,
                            "number": 1,
                            "sections": [
                                {
                                    "name": book_name,
                                    "number": 1,
                                    "subsections": [
                                        {"name": book_name, "number": 1, "articles": []}
                                    ],
                                }
                            ],
                        }
                    ],
                }
            )

            start, end = self.__process_articles(
                titles_text,
                book_titles[0]["chapters"][0]["sections"][0]["subsections"][0][
                    "articles"
                ],
            )

            book_titles[0]["chapters"][0]["sections"][0]["subsections"][0]["range"] = [
                start,
                end,
            ]
            book_titles[0]["chapters"][0]["sections"][0]["range"] = [start, end]
            book_titles[0]["chapters"][0]["range"] = [start, end]
            book_titles[0]["range"] = [start, end]

            return start, end

    def __process_chapters(
        self, chapters_text: str, title_name: str, title_chapers: list
    ):
        if "\nCapitolul" in chapters_text:
            chapters = re.split(r"\nCapitolul ", chapters_text)
            # Excluding potential empty chapter after split
            if re.split(r"\n", chapters[0], 1)[0] == "":
                chapters = chapters[1:]

            for ic, chapter in enumerate(chapters):
                c = dict()

                chapter_name, sections_text = re.split(r"\n", chapter, 1)
                c["name"] = chapter_name.split(" ", 1)[-1]
                c["number"] = ic + 1
                c["sections"] = []

                start, end = self.__process_sections(
                    sections_text, c["name"], c["sections"]
                )
                c["range"] = [start, end]

                title_chapers.append(c)

            return [
                title_chapers[0]["range"][0],
                title_chapers[-1]["range"][1],
            ]
        else:
            title_chapers.append(
                {
                    "name": title_name,
                    "number": 1,
                    "sections": [
                        {
                            "name": title_name,
                            "number": 1,
                            "subsections": [
                                {"name": title_name, "number": 1, "articles": []}
                            ],
                        }
                    ],
                }
            )

            start, end = self.__process_articles(
                chapters_text,
                title_chapers[0]["sections"][0]["subsections"][0]["articles"],
            )

            title_chapers[0]["sections"][0]["subsections"][0]["range"] = [
                start,
                end,
            ]
            title_chapers[0]["sections"][0]["range"] = [
                start,
                end,
            ]
            title_chapers[0]["range"] = [start, end]

            return start, end

    def __process_sections(
        self, sections_text: str, chapter_name: str, chapter_sections: list
    ):
        if "\nSecţiunea" in sections_text:
            sections = re.split(r"\nSecţiunea ", sections_text)
            # Excluding potential empty section after split
            if sections[0] in ["\n", " ", ""] or "Articolul" not in sections[0]:
                sections = sections[1:]

            for isc, section in enumerate(sections):
                s = dict()

                section_name, subsections_text = re.split(r"\n", section, 1)

                if "-" in section_name:
                    s["name"] = section_name.split(" ", 2)[-1]
                else:
                    s["name"] = section_name.split(" ", 1)[-1]

                s["number"] = isc + 1
                s["subsections"] = []

                start, end = self.__process_subsections(
                    subsections_text, s["name"], s["subsections"]
                )
                s["range"] = [start, end]

                chapter_sections.append(s)

            return [
                chapter_sections[0]["range"][0],
                chapter_sections[-1]["range"][1],
            ]
        else:
            chapter_sections.append(
                {
                    "name": chapter_name,
                    "number": 1,
                    "subsections": [
                        {"name": chapter_name, "number": 1, "articles": []}
                    ],
                }
            )

            start, end = self.__process_articles(
                sections_text,
                chapter_sections[0]["subsections"][0]["articles"],
            )

            chapter_sections[0]["subsections"][0]["range"] = [start, end]
            chapter_sections[0]["range"] = [start, end]

            return start, end

    def __process_subsections(
        self, subsections_text: str, section_name: str, section_subsections: list
    ):
        if "\n§" in subsections_text:
            subsections = re.split(r"\n§", subsections_text)
            if subsections[0] == "":
                subsections = subsections[1:]

            for iss, subsection in enumerate(subsections):
                ss = dict()

                subsection_title, articles_text = re.split(r"\n", subsection, 1)

                subsection_split = re.split(r" ", subsection_title.strip(), 1)
                if len(subsection_split) > 1:
                    subsection_name = subsection_split[1]
                else:
                    subsection_name = f"Subsecțiunea {iss + 1}"

                ss["name"] = subsection_name
                ss["number"] = iss + 1
                ss["articles"] = []

                start, end = self.__process_articles(articles_text, ss["articles"])

                ss["range"] = [start, end]

                section_subsections.append(ss)

            return [
                section_subsections[0]["range"][0],
                section_subsections[-1]["range"][1],
            ]
        else:
            section_subsections.append(
                {"name": section_name, "number": 1, "articles": []}
            )

            start, end = self.__process_articles(
                subsections_text,
                section_subsections[0]["articles"],
            )

            section_subsections[0]["range"] = [start, end]

            return start, end

    def __process_articles(self, articles_text: str, appending_list: list):
        articles_text = articles_text.replace("ART ", "Articolul ")
        articles = re.split(r"\nArticolul ", articles_text)
        for article in articles:
            if len(article) > 1:
                a = dict()

                article = article.replace("Articolul ", "")
                article_number, article_body = re.split(r"\s+", article, 1)
                article_name, article_text = re.split(r"\n+", article_body, 1)

                if article_text != "":
                    a["name"] = re.sub(r"\s+", " ", article_name)
                    a["number"] = int(article_number.replace(".", "").replace(" ", ""))
                    a["text"] = article_text.strip()
                else:
                    a["name"] = f"Articolul {article_number}"
                    a["number"] = int(article_number.replace(".", "").replace(" ", ""))
                    a["text"] = article_name

                appending_list.append(a)

        start = appending_list[0]["number"]
        end = appending_list[-1]["number"]

        return start, end

    def find_article(self, article_number: int, legal_code: str):
        f = open("../data/processed-laws/codes.json", "r", encoding="utf8")
        codes = json.load(f)
        f.close()

        code_index = -1
        for i, code in enumerate(codes):
            if legal_code.lower() in code["name"].lower():
                code_index = i
                break

        if code_index != -1:
            for book in codes[code_index]["books"]:
                article = self.__find_article_by_number(book, article_number)
                if article is not None:
                    return f"{article['name']}\n{article['text']}"
            return (
                f"Articolul cu numărul {article_number} nu există în acest cod de lege!"
            )
        else:
            return f"Codul de lege specificat ({legal_code}) nu există!"

    def __find_article_by_number(self, obj: dict, article_number: int):
        if "range" in obj.keys():
            if obj["range"][0] <= article_number <= obj["range"][1]:
                for v in obj.values():
                    if isinstance(v, list) and not all(
                        [isinstance(elem, int) for elem in v]
                    ):
                        for elem in v:
                            article = self.__find_article_by_number(
                                elem, article_number
                            )
                            if article is not None:
                                return article
        elif obj["number"] == article_number:
            return obj

    # TODO: rethink utility
    # def find_relevant_text(self, keyword: str):
    #     f = open("../data/corpus/legal.json", "r", encoding="utf8")
    #     legal_frequencies = json.load(f)
    #     f.close()

    #     keyword = keyword.lower()
    #     candidates = dict()
    #     for code, values in legal_frequencies.items():
    #         if keyword in values:
    #             candidates[code] = {
    #                 "freq": values[keyword]["freq"],
    #                 "articles": values[keyword]["articles"],
    #             }

    #     message = ""
    #     for code, values in candidates.items():
    #         message += f"<span class=\"highlightable\">{code}</span> conține {values['freq']} apariții ale termenului, cu {len(values['articles'])} articole relevante: {values['articles']}.\n\n"

    #     if message != "":
    #         message += (
    #             "\nÎmi poți cere detalii despre oricare din articolele listate mai sus!"
    #         )
    #         return message
    #     else:
    #         return "Termenul nu se regăsește în niciun articol din lege.\nVerifică că a fost scris corect sau încearcă o altă formă a cuvântului!"

    def find_relevant_text(self, keyword: str):
        f = open("../data/processed-laws/codes.json", "r", encoding="utf8")
        codes = json.load(f)
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

        keyword = keyword.lower()
        candidates = dict()
        for i, code in enumerate(codes):
            articles = list()
            self.__find_articles_by_content(code, keyword, articles)
            if len(articles) > 0:
                candidates[codes_keywords[i]] = articles

        message = ""
        for code, values in candidates.items():
            message += f"<span class=\"highlightable\">{code}</span> conține {len(values)} articole relevante: {values}.\n\n"

        if message != "":
            message += (
                "\nÎmi poți cere detalii despre oricare din articolele listate mai sus!"
            )
            return message
        else:
            return "Termenul nu se regăsește în niciun articol din lege.\nVerifică că a fost scris corect sau încearcă o altă formă a cuvântului!"

    def __find_articles_by_content(self, obj: dict, keyword: str, results: list()):
        if "range" in obj.keys():
            for v in obj.values():
                if isinstance(v, list) and not all(
                    [isinstance(elem, int) for elem in v]
                ):
                    for elem in v:
                        self.__find_articles_by_content(elem, keyword, results)
        elif keyword in obj["text"].lower():
            results.append(obj["number"])

    def get_code_size(self, legal_code: str):
        f = open("../data/processed-laws/codes.json", "r", encoding="utf8")
        codes = json.load(f)
        f.close()

        code_index = -1
        for i, code in enumerate(codes):
            if legal_code.lower() in code["name"].lower():
                code_index = i
                break

        if code_index != -1:
            size = codes[code_index]["range"][1]
            return f'{legal_code.capitalize()} are <span class="highlightable">{size}</span> articole.'
        else:
            return f"Codul de lege specificat ({legal_code}) nu există!"


if __name__ == "__main__":
    lp = LawProcessor()
    lp.process_laws()
