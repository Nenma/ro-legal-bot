from utils.cleaner import TextCleaner
from corpus_processor import CorpusProcessor
import rowordnet as rwn
import json
import math


class SimplificationTool:
    tc = TextCleaner()
    cp = CorpusProcessor()

    def simplify(self, text: str):
        f = open("../data/wikipedia/ro_wikipedia.json", "r", encoding="utf8")
        word_frequencies = json.load(f)
        f.close()

        corpus_size = self.cp.DOCUMENTS_NUMBER

        text = text.split()
        for i, word in enumerate(text):
            if not self.tc.is_stopword(word) and not self.tc.has_numbers(word):
                word = word.lower()

                # Threshold is set at 10% rarity
                threshold = math.log(corpus_size / (corpus_size * 0.1))
                rarity = word_frequencies.get(word, round(threshold))

                if rarity > threshold:
                    lemmatized_word = self.cp.get_lemma(word)
                    replacement = self.find_synonym(lemmatized_word)

                    text[i] = replacement

        return " ".join(text)

    def find_synonym(self, word: str):
        wn = rwn.RoWordNet()
        id_list = wn.synsets(word)

        print(f"Number of synsets is {len(id_list)}")
        if id_list != []:
            for sid in id_list:
                synset_id = sid
                synset = wn.synset(synset_id)

                print(f"\nPrint all literals of {synset_id}: {synset.literals}")

                print(f"\nPrint all outbound relations of {synset}")
                outbound_relations = wn.outbound_relations(synset_id)
                for outbound_relation in outbound_relations:
                    target_synset_id = outbound_relation[0]
                    relation = outbound_relation[1]
                    print(
                        f"\tRelation [{relation}] to synset {wn.synset(target_synset_id)}"
                    )

                print(f"\nPrint all inbound relations of {synset}")
                inbound_relations = wn.inbound_relations(synset_id)
                for inbound_relation in inbound_relations:
                    target_synset_id = inbound_relation[0]
                    relation = inbound_relation[1]
                    print(
                        f"\tRelation [{relation}] to synset {wn.synset(target_synset_id)}"
                    )

                # if len(synset.literals) > 1:
                #     return synset.literals[1]

                # return synset.literals[0]
        else:
            print("Word not present in wordnet...")
            return word


if __name__ == "__main__":
    st = SimplificationTool()
    print(st.find_synonym("cetățenia"))
