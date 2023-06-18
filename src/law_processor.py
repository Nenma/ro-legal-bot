import re
import json


class LawProcessor:
    """
    The general structure of the legal text is: Content -> Books -> Titles -> Chapters -> Sections -> Articles.

    The processor creates a single general structure for all legal text documents.
    """

    def process_laws(self):
        self.process_constitution()
        self.process_penal_code()
        self.process_penal_procedure_code()
        self.process_civil_code(
            "../data/base-laws/civil_code.txt",
            "../data/processed-laws/civil_code.json",
            "Codul Civil al României",
            "PRELIMINAR",
        )
        self.process_civil_code(
            "../data/base-laws/civil_procedure_code.txt",
            "../data/processed-laws/civil_procedure_code.json",
            "Codul de Procedură Civilă al României",
            "PRELIMINAR",
        )
        self.process_general_code(
            "../data/base-laws/fiscal_code.txt",
            "../data/processed-laws/fiscal_code.json",
            "Codul Fiscal al României",
        )
        self.process_general_code(
            "../data/base-laws/fiscal_procedure_code.txt",
            "../data/processed-laws/fiscal_procedure_code.json",
            "Codul de Procedură Fiscală al României",
        )
        self.process_general_code(
            "../data/base-laws/labor_code.txt",
            "../data/processed-laws/labor_code.json",
            "Codul Muncii al României",
        )

        self.__concatenate_laws()

    def __concatenate_laws(self):
        codes = [
            "civil_code",
            "civil_procedure_code",
            "constitution",
            "fiscal_code",
            "fiscal_procedure_code",
            "penal_code",
            "penal_procedure_code",
            "labor_code",
        ]

        codes_json = []
        for i, code in enumerate(codes):
            f = open(f"../data/processed-laws/{code}.json", "r", encoding="utf8")
            codes_json.append(json.load(f))
            codes_json[i]["code_number"] = i + 1
            f.close()

        f = open("../data/processed-laws/codes.json", "w", encoding="utf8")
        json.dump(codes_json, f, ensure_ascii=False, indent=3)
        f.close()

    def process_constitution(self):
        """
        The structure of the Constitution titles boils down to: Titles -> Chapters -> Sections -> Articles.

        However, most cases follow the Titles -> Articles structure, thus we need to check at every step.
        """

        f = open("../data/base-laws/constitution.txt", "r", encoding="utf8")
        text = f.read()
        f.close()

        constitution = {
            "name": "Constituția României / Constituție a României",
            "books": [
                {
                    "book_name": "The Romanian Constitution",
                    "book_number": 1,
                    "book_titles": [],
                }
            ],
        }

        titles = re.split(r"TITLUL .*\n", text)
        for it, title in enumerate(titles[1:]):
            t = dict()

            title_name, chapters_text = re.split(r"\n", title, 1)
            t["title_name"] = title_name
            t["title_number"] = it + 1
            t["title_chapters"] = []

            if "CAPITOLUL" in chapters_text:
                # If we have chapters we further check for existing sections
                chapters = re.split(r"CAPITOLUL .*\n", chapters_text)

                for ic, chapter in enumerate(chapters[1:]):
                    c = dict()

                    chapter_name, sections_text = re.split(r"\n", chapter, 1)
                    c["chapter_name"] = chapter_name
                    c["chapter_number"] = ic + 1
                    c["chapter_sections"] = []

                    if "SECŢIUNEA" in sections_text:
                        # If we have sections we can safely begin parsing the article text
                        sections = re.split(r"SECŢIUNEA .*\n", sections_text)

                        for isc, section in enumerate(sections[1:]):
                            s = dict()

                            section_name, articles_text = re.split(r"\n", section, 1)
                            s["section_name"] = section_name
                            s["section_number"] = isc + 1
                            s["section_articles"] = []

                            start, end = self.__process_constitution_articles(
                                articles_text, s["section_articles"]
                            )

                            s["article_range"] = [start, end]

                            c["chapter_sections"].append(s)

                        c["article_range"] = [
                            c["chapter_sections"][0]["article_range"][0],
                            c["chapter_sections"][-1]["article_range"][1],
                        ]
                    else:
                        # If we do not have sections we assume a chapter with a single section of the same name
                        # and the article text is the splitted section text itself
                        c["chapter_sections"].append(
                            {
                                "section_name": c["chapter_name"],
                                "section_number": 1,
                                "section_articles": [],
                            }
                        )

                        start, end = self.__process_constitution_articles(
                            sections_text, c["chapter_sections"][0]["section_articles"]
                        )

                        c["chapter_sections"][0]["article_range"] = [start, end]
                        c["article_range"] = [start, end]

                    t["title_chapters"].append(c)

                t["article_range"] = [
                    t["title_chapters"][0]["article_range"][0],
                    t["title_chapters"][-1]["article_range"][1],
                ]
            else:
                # If we do not have chapters we assume a title with a single chapter with its single section,
                # both of the same name, and the article text is the splitted chapter text itself
                t["title_chapters"].append(
                    {
                        "chapter_name": t["title_name"],
                        "chapter_number": 1,
                        "chapter_sections": [
                            {
                                "section_name": t["title_name"],
                                "section_number": 1,
                                "section_articles": [],
                            }
                        ],
                    }
                )

                start, end = self.__process_constitution_articles(
                    chapters_text,
                    t["title_chapters"][0]["chapter_sections"][0]["section_articles"],
                )

                t["title_chapters"][0]["chapter_sections"][0]["article_range"] = [
                    start,
                    end,
                ]
                t["title_chapters"][0]["article_range"] = [start, end]
                t["article_range"] = [start, end]

            constitution["books"][0]["book_titles"].append(t)

        constitution["books"][0]["article_range"] = [
            constitution["books"][0]["book_titles"][0]["article_range"][0],
            constitution["books"][0]["book_titles"][-1]["article_range"][1],
        ]
        constitution["article_range"] = constitution["books"][0]["article_range"]

        f = open("../data/processed-laws/constitution.json", "w", encoding="utf8")
        json.dump(constitution, f, ensure_ascii=False, indent=3)
        f.close()

    def __process_constitution_articles(self, articles_text: str, appending_list: list):
        articles = re.split(r"(.*ARTICOLUL \d+)\n", articles_text)
        for i in range(1, len(articles), 2):
            a = dict()
            article_name, article_number = re.split(r"\tARTICOLUL ", articles[i])
            article_text = articles[i + 1].replace("\n\n", "\n").strip()

            a["article_name"] = article_name
            a["article_number"] = int(article_number)
            a["text"] = article_text

            appending_list.append(a)

        start = appending_list[0]["article_number"]
        end = appending_list[-1]["article_number"]

        return start, end

    def process_civil_code(
        self, infile: str, outfile: str, code_name: str, first_book_name: str
    ):
        f = open(infile, "r", encoding="utf8")
        text = f.read()
        f.close()

        civil_code = {"name": code_name, "books": []}

        books = re.split(r"\nCartea ", text)
        for ib, book in enumerate(books):
            b = dict()

            book_name, titles_text = re.split(r"\n", book, 1)

            if ib == 0:
                # First "book" does not have proper name
                b["book_name"] = first_book_name
            elif "-" in book_name:
                # ex: a II-a Despre familie*)
                b["book_name"] = book_name.split(" ", 2)[-1][:-2]
            else:
                # ex: I Despre persoane*)
                b["book_name"] = book_name.split(" ", 1)[-1][:-2]

            b["book_number"] = ib + 1
            b["book_titles"] = []

            start, end = self.__process_book_titles(titles_text, b["book_titles"])

            b["article_range"] = [start, end]

            civil_code["books"].append(b)

        civil_code["article_range"] = [
            civil_code["books"][0]["article_range"][0],
            civil_code["books"][-1]["article_range"][1],
        ]

        f = open(outfile, "w", encoding="utf8")
        json.dump(civil_code, f, ensure_ascii=False, indent=3)
        f.close()

    def process_penal_code(self):
        f = open("../data/base-laws/penal_code.txt", "r", encoding="utf8")
        text = f.read()
        f.close()

        penal_code = {"name": "Codul Penal al României", "books": []}

        text = re.split(r"\n\n\nPartea ", text)[-1]

        books = re.split(r"PARTEA ", text)
        for ib, book in enumerate(books[1:]):
            b = dict()

            book_name, titles_text = re.split(r"\n", book, 1)
            b["book_name"] = book_name
            b["book_number"] = ib + 1
            b["book_titles"] = []

            start, end = self.__process_book_titles(titles_text, b["book_titles"])

            b["article_range"] = [start, end]

            penal_code["books"].append(b)

        penal_code["article_range"] = [
            penal_code["books"][0]["article_range"][0],
            penal_code["books"][-1]["article_range"][1],
        ]

        f = open("../data/processed-laws/penal_code.json", "w", encoding="utf8")
        json.dump(penal_code, f, ensure_ascii=False, indent=3)
        f.close()

    def process_penal_procedure_code(self):
        f = open("../data/base-laws/penal_procedure_code.txt", "r", encoding="utf8")
        text = f.read()
        f.close()

        penal_procedure_code = {
            "name": "Codul de Procedură Penală al României",
            "books": [],
        }
        penal_procedure_book_names = ["GENERALĂ", "SPECIALĂ"]

        books = re.split(r"\nPartea [A-Z]", text)
        for ib, book in enumerate(books[1:]):
            b = dict()

            _, titles_text = re.split(r"\n", book, 1)
            b["book_name"] = penal_procedure_book_names[ib]
            b["book_number"] = ib + 1
            b["book_titles"] = []

            start, end = self.__process_book_titles(titles_text, b["book_titles"])

            b["article_range"] = [start, end]

            penal_procedure_code["books"].append(b)

        penal_procedure_code["article_range"] = [
            penal_procedure_code["books"][0]["article_range"][0],
            penal_procedure_code["books"][-1]["article_range"][1],
        ]

        f = open(
            "../data/processed-laws/penal_procedure_code.json", "w", encoding="utf8"
        )
        json.dump(penal_procedure_code, f, ensure_ascii=False, indent=3)
        f.close()

    def process_general_code(self, infile: str, outfile: str, code_name: str):
        f = open(infile, "r", encoding="utf8")
        text = f.read()
        f.close()

        fiscal_code = {
            "name": code_name,
            "books": [
                {
                    "book_name": code_name,
                    "book_number": 1,
                    "book_titles": [],
                }
            ],
        }

        start, end = self.__process_book_titles(
            text, fiscal_code["books"][0]["book_titles"]
        )

        fiscal_code["books"][0]["article_range"] = [start, end]
        fiscal_code["article_range"] = [start, end]

        f = open(outfile, "w", encoding="utf8")
        json.dump(fiscal_code, f, ensure_ascii=False, indent=3)
        f.close()

    def __process_book_titles(self, titles_text: str, book_titles: list):
        titles = re.split(r"\nTitlul [A-Z]", titles_text)
        for it, title in enumerate(titles[1:]):
            t = dict()

            title_name, chapters_text = re.split(r"\n", title, 1)

            # if ib == 0 and it == 0:
            #     # First title of first "book" does not have proper name
            #     t["title_name"] = "Preliminar"
            # else:
            t["title_name"] = title_name.split(" ", 1)[-1]

            t["title_number"] = it + 1
            t["title_chapters"] = []

            if "\nCapitolul" in chapters_text:
                chapters = re.split(r"\nCapitolul ", chapters_text)
                # Excluding potential empty chapter after split
                if re.split(r"\n", chapters[0], 1)[0] == "":
                    chapters = chapters[1:]

                for ic, chapter in enumerate(chapters):
                    c = dict()

                    chapter_name, sections_text = re.split(r"\n", chapter, 1)
                    c["chapter_name"] = chapter_name.split(" ", 1)[-1]
                    c["chapter_number"] = ic + 1
                    c["chapter_sections"] = []

                    if "\nSecţiunea" in sections_text:
                        sections = re.split(r"\nSecţiunea ", sections_text)
                        # Excluding potential empty section after split
                        if re.split(r"\n", sections[0], 1)[0] == "":
                            sections = sections[1:]

                        for isc, section in enumerate(sections):
                            s = dict()

                            section_name, articles_text = re.split(r"\n", section, 1)

                            if "-" in section_name:
                                s["section_name"] = section_name.split(" ", 2)[-1]
                            else:
                                s["section_name"] = section_name.split(" ", 1)[-1]

                            s["section_number"] = isc + 1
                            s["section_articles"] = []

                            start, end = self.__process_articles(
                                articles_text, s["section_articles"]
                            )

                            s["article_range"] = [start, end]

                            c["chapter_sections"].append(s)

                        c["article_range"] = [
                            c["chapter_sections"][0]["article_range"][0],
                            c["chapter_sections"][-1]["article_range"][1],
                        ]
                    else:
                        c["chapter_sections"].append(
                            {
                                "section_name": c["chapter_name"],
                                "section_number": 1,
                                "section_articles": [],
                            }
                        )

                        start, end = self.__process_articles(
                            sections_text,
                            c["chapter_sections"][0]["section_articles"],
                        )

                        c["chapter_sections"][0]["article_range"] = [start, end]
                        c["article_range"] = [start, end]

                    t["title_chapters"].append(c)

                t["article_range"] = [
                    t["title_chapters"][0]["article_range"][0],
                    t["title_chapters"][-1]["article_range"][1],
                ]
            else:
                t["title_chapters"].append(
                    {
                        "chapter_name": t["title_name"],
                        "chapter_number": 1,
                        "chapter_sections": [
                            {
                                "section_name": t["title_name"],
                                "section_number": 1,
                                "section_articles": [],
                            }
                        ],
                    }
                )

                start, end = self.__process_articles(
                    chapters_text,
                    t["title_chapters"][0]["chapter_sections"][0]["section_articles"],
                )

                t["title_chapters"][0]["chapter_sections"][0]["article_range"] = [
                    start,
                    end,
                ]
                t["title_chapters"][0]["article_range"] = [start, end]
                t["article_range"] = [start, end]

            book_titles.append(t)

        start = book_titles[0]["article_range"][0]
        end = book_titles[-1]["article_range"][1]

        return start, end

    def __process_articles(self, articles_text: str, appending_list: list):
        articles = re.split(r"\nArticolul ", articles_text)
        for article in articles[1:]:
            a = dict()

            article_number, article_body = re.split(r"\n\n", article, 1)
            article_name, article_text = re.split(r"\n", article_body, 1)

            if article_text != "":
                a["article_name"] = article_name
                a["article_number"] = int(article_number.replace(".", ""))
                a["text"] = article_text.strip()
            else:
                a["article_name"] = f"Articolul {article_number}"
                a["article_number"] = int(article_number.replace(".", ""))
                a["text"] = article_name

            appending_list.append(a)

        start = appending_list[0]["article_number"]
        end = appending_list[-1]["article_number"]

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
                if (
                    book["article_range"][0]
                    <= article_number
                    <= book["article_range"][1]
                ):
                    for title in book["book_titles"]:
                        if (
                            title["article_range"][0]
                            <= article_number
                            <= book["article_range"][1]
                        ):
                            for chapter in title["title_chapters"]:
                                if (
                                    chapter["article_range"][0]
                                    <= article_number
                                    <= chapter["article_range"][1]
                                ):
                                    for section in chapter["chapter_sections"]:
                                        if (
                                            section["article_range"][0]
                                            <= article_number
                                            <= section["article_range"][1]
                                        ):
                                            for article in section["section_articles"]:
                                                if (
                                                    article["article_number"]
                                                    == article_number
                                                ):
                                                    return f'{article["article_name"]}\n{article["text"]}'
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
            size = codes[code_index]["article_range"][1]
            return f"{legal_code.capitalize()} are {size} articole."
        else:
            return f"Codul de lege specificat ({legal_code}) nu există!"


if __name__ == "__main__":
    lp = LawProcessor()
    lp.process_laws()
    # lp.find_article(45, "codul fiscal")
