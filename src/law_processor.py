from bs4 import BeautifulSoup
import requests
import json
import math
import re
import os


class LawProcessor:
    """
    The general structure of the legal text is: Content -> Books -> Titles -> Chapters -> Sections -> Articles.

    The processor creates a single general structure for all legal text documents.
    """

    def process_laws(self):
        self.process_general_code_type1(
            "../data/processed-laws/codes/constitution.json",
            "Constituția României / Constituție a României",
            "https://legislatie.just.ro/Public/FormaPrintabila/00000G0NF8LQJNGG75M2SUMLP2PIT6ZP",
        )
        self.process_general_code_type1(
            "../data/processed-laws/codes/fiscal_code.json",
            "Codul Fiscal al României",
            "https://legislatie.just.ro/Public/FormaPrintabila/00000G1ZAKIDCF325CT2OM2WBUU98MOP",
        )
        self.process_general_code_type1(
            "../data/processed-laws/codes/fiscal_procedure_code.json",
            "Codul de Procedură Fiscală al României",
            "https://legislatie.just.ro/Public/FormaPrintabila/00000G1SA6VV3H1PY8920ESSHWCB3WXT",
        )
        self.process_general_code_type1(
            "../data/processed-laws/codes/labor_code.json",
            "Codul Muncii al României",
            "https://legislatie.just.ro/Public/FormaPrintabila/00000G3RCE89TJASJDO1SWLGVM5I6DWB",
        )

        self.process_general_code_type2(
            "../data/processed-laws/codes/penal_code.json",
            "Codul Penal al României",
            "https://legislatie.just.ro/Public/FormaPrintabila/00000G3RCJVMCPZK1D5301YV9BG07ZE3",
            r"\nPartea (.*)\n\n",
        )
        self.process_general_code_type2(
            "../data/processed-laws/codes/penal_procedure_code.json",
            "Codul de Procedură Penală al României",
            "https://legislatie.just.ro/Public/FormaPrintabila/00000G3SGIENTQKF6QX0SUWA2W5Y3ZV3",
            r"\nPartea ([A-ZĂÎÂȘȚ]+)",
        )
        self.process_general_code_type2(
            "../data/processed-laws/codes/administrative_code.json",
            "Codul Administrativ al României",
            "https://legislatie.just.ro/Public/FormaPrintabila/00000G26T9IKD8IXCIZ0X39N88WZQ5GJ",
            r"\nPARTEA (.*)\n",
        )

        self.process_civil_code(
            "../data/processed-laws/codes/civil_code.json",
            "Codul Civil al României",
            "https://legislatie.just.ro/Public/FormaPrintabila/00000G1TT7EZVJJX6870CWN6ZG1TWPAC",
            "PRELIMINAR",
        )
        self.process_civil_code(
            "../data/processed-laws/codes/civil_procedure_code.json",
            "Codul de Procedură Civilă al României",
            "https://legislatie.just.ro/Public/FormaPrintabila/00000G1NE6WQB9B6WYG13YGXTQETNYA8",
            "PRELIMINAR",
        )

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
        self, outfile: str, code_name: str, code_url: str, first_book_name: str
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

            start, end = self.__process_book_titles(titles_text, b["name"], b["titles"])

            b["range"] = [start, end]

            civil_code["books"].append(b)

        civil_code["range"] = [
            civil_code["books"][0]["range"][0],
            civil_code["books"][-1]["range"][1],
        ]

        f = open(outfile, "w", encoding="utf8")
        json.dump(civil_code, f, ensure_ascii=False, indent=3)
        f.close()

    def process_general_code_type1(self, outfile: str, code_name: str, code_url: str):
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

        start, end = self.__process_book_titles(
            text, general_code["books"][0]["name"], general_code["books"][0]["titles"]
        )

        general_code["books"][0]["range"] = [start, end]
        general_code["range"] = [start, end]

        f = open(outfile, "w", encoding="utf8")
        json.dump(general_code, f, ensure_ascii=False, indent=3)
        f.close()

    def process_general_code_type2(
        self, outfile: str, code_name: str, code_url: str, delimiter: str
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

            start, end = self.__process_book_titles(titles_text, b["name"], b["titles"])

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

    def __process_book_titles(
        self, titles_text: str, book_name: str, book_titles: list
    ):
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

                        if "\nSecţiunea" in sections_text:
                            sections = re.split(r"\nSecţiunea ", sections_text)
                            # Excluding potential empty section after split
                            if re.split(r"\n", sections[0], 1)[0] == "":
                                sections = sections[1:]

                            for isc, section in enumerate(sections):
                                s = dict()

                                section_name, subsections_text = re.split(
                                    r"\n", section, 1
                                )

                                if "-" in section_name:
                                    s["name"] = section_name.split(" ", 2)[-1]
                                else:
                                    s["name"] = section_name.split(" ", 1)[-1]

                                s["number"] = isc + 1
                                s["subsections"] = []

                                if "\n§" in subsections_text:
                                    subsections = re.split(r"\n§", subsections_text)

                                    for iss, subsection in enumerate(subsections):
                                        if subsection != "":
                                            ss = dict()

                                            subsection_title, articles_text = re.split(
                                                r"\n", subsection, 1
                                            )

                                            subsection_split = re.split(
                                                r" ", subsection_title.strip(), 1
                                            )
                                            if len(subsection_split) > 1:
                                                subsection_name = subsection_split[1]
                                            else:
                                                subsection_name = (
                                                    f"Subsecțiunea {iss + 1}"
                                                )

                                            ss["name"] = subsection_name
                                            ss["number"] = iss + 1
                                            ss["articles"] = []

                                            start, end = self.__process_articles(
                                                articles_text, ss["articles"]
                                            )

                                            ss["range"] = [start, end]

                                            s["subsections"].append(ss)
                                else:
                                    s["subsections"].append(
                                        {"name": s["name"], "number": 1, "articles": []}
                                    )

                                    start, end = self.__process_articles(
                                        subsections_text,
                                        s["subsections"][0]["articles"],
                                    )

                                    s["subsections"][0]["range"] = [start, end]

                                s["range"] = [
                                    s["subsections"][0]["range"][0],
                                    s["subsections"][-1]["range"][1],
                                ]

                                c["sections"].append(s)

                            c["range"] = [
                                c["sections"][0]["range"][0],
                                c["sections"][-1]["range"][1],
                            ]
                        else:
                            c["sections"].append(
                                {
                                    "name": c["name"],
                                    "number": 1,
                                    "subsections": [
                                        {"name": c["name"], "number": 1, "articles": []}
                                    ],
                                }
                            )

                            start, end = self.__process_articles(
                                sections_text,
                                c["sections"][0]["subsections"][0]["articles"],
                            )

                            c["sections"][0]["subsections"][0]["range"] = [start, end]
                            c["sections"][0]["range"] = [start, end]
                            c["range"] = [start, end]

                        t["chapters"].append(c)

                    t["range"] = [
                        t["chapters"][0]["range"][0],
                        t["chapters"][-1]["range"][1],
                    ]
                else:
                    t["chapters"].append(
                        {
                            "name": t["name"],
                            "number": 1,
                            "sections": [
                                {
                                    "name": t["name"],
                                    "number": 1,
                                    "subsections": [
                                        {"name": t["name"], "number": 1, "articles": []}
                                    ],
                                }
                            ],
                        }
                    )

                    start, end = self.__process_articles(
                        chapters_text,
                        t["chapters"][0]["sections"][0]["subsections"][0]["articles"],
                    )

                    t["chapters"][0]["sections"][0]["subsections"][0]["range"] = [
                        start,
                        end,
                    ]
                    t["chapters"][0]["sections"][0]["range"] = [
                        start,
                        end,
                    ]
                    t["chapters"][0]["range"] = [start, end]
                    t["range"] = [start, end]

                book_titles.append(t)

            start = book_titles[0]["range"][0]
            end = book_titles[-1]["range"][1]
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

    def __process_articles(self, articles_text: str, appending_list: list):
        articles_text = articles_text.replace("ART ", "Articolul ")
        articles = re.split(r"\nArticolul ", articles_text)
        for article in articles:
            if len(article) > 1:
                a = dict()

                article = article.replace("Articolul ", "")

                article_number, article_body = re.split(r"\s+", article, 1)
                article_name, article_text = re.split(r"\n+", article_body, 1)

                print(article)

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
                if book["range"][0] <= article_number <= book["range"][1]:
                    for title in book["titles"]:
                        if title["range"][0] <= article_number <= book["range"][1]:
                            for chapter in title["chapters"]:
                                if (
                                    chapter["range"][0]
                                    <= article_number
                                    <= chapter["range"][1]
                                ):
                                    for section in chapter["sections"]:
                                        if (
                                            section["range"][0]
                                            <= article_number
                                            <= section["range"][1]
                                        ):
                                            for subsection in section["subsections"]:
                                                if (
                                                    subsection["range"][0]
                                                    <= article_number
                                                    <= subsection["range"][1]
                                                ):
                                                    for article in subsection[
                                                        "articles"
                                                    ]:
                                                        if (
                                                            article["number"]
                                                            == article_number
                                                        ):
                                                            return f'{article["name"]}\n{article["text"]}'
            return (
                f"Articolul cu numărul {article_number} nu există în acest cod de lege!"
            )
        else:
            return f"Codul de lege specificat ({legal_code}) nu există!"

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
            return f"{legal_code.capitalize()} are {size} articole."
        else:
            return f"Codul de lege specificat ({legal_code}) nu există!"


if __name__ == "__main__":
    lp = LawProcessor()
    lp.process_laws()
