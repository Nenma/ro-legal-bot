import rowordnet as rwn
import json
import re

from src.utils.cleaner import TextCleaner
from src.corpus_processor import CorpusProcessor


class ExplanationTool:
    tc = TextCleaner()
    cp = CorpusProcessor()
    lemmas = dict()

    def __init__(self):
        f = open("./data/corpus/dictionary.json", "r", encoding="utf8")
        g = open("./data/corpus/ro_wikipedia_final.json", "r", encoding="utf8")

        self.dictionary = json.load(f)
        self.ro_wikipedia = json.load(g)

        f.close()
        g.close()

    def simplify(self, text: str):
        text = text.replace("ş", "ș").replace("ţ", "ț")
        original_text = text[:]
        processed = {}

        words = re.findall(r"[a-zăâîșțA-ZĂÂÎȘȚ\.]+", text)
        words = [
            word
            for word in words
            if not self.tc.is_stopword(word) and len(word) > 1 and "." not in word
        ]

        for word in words:
            if word.lower() in self.lemmas:
                lemmatized_word = self.lemmas[word.lower()]
            else:
                lemmatized_word = self.cp.nlp(word)[0].lemma_.lower()
                self.lemmas[word] = lemmatized_word

            if word.lower() not in processed:
                rarity = self.ro_wikipedia["word_frequencies"].get(lemmatized_word, -1)

                if rarity <= 0.05:
                    if lemmatized_word not in self.dictionary:
                        dex_definition = self.cp.get_dex_definition(word)
                        self.dictionary[lemmatized_word] = dex_definition
                    definition = self.dictionary[lemmatized_word]

                    if len(re.findall(r"[a-zăâîșțA-ZĂÂÎȘȚ]+", definition)) > 1:
                        processed[
                            word.lower()
                        ] = f'<span class="highlightable tooltip"><i>{word}</i><span class="tooltiptext">{definition}</span></span>'

                f = open("./data/corpus/dictionary.json", "w", encoding="utf8")
                json.dump(self.dictionary, f, ensure_ascii=False, indent=3)
                f.flush()

            if word.lower() not in processed:
                processed[word.lower()] = word

        f.close()

        for word in set(words):
            original_text = original_text.replace(word, processed[word.lower()])

        return original_text


if __name__ == "__main__":
    st = ExplanationTool()
    st.simplify("ex")
