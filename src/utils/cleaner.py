import stopwords
import re


class TextCleaner:
    RO_STOPWORDS = stopwords.get_stopwords("romanian")

    def clean_text(self, text: str):
        # Remove special characters
        text = re.sub(
            r"(@\[A-Za-zĂÎÂȘȚăîâșț]+)|([^A-Za-zĂÎÂȘȚăîâșțşţ \t])|(\w+:\/\/\S+)|^rt|http.+?",
            " ",
            text,
        )
        # Reduce spacing inbetween words
        text = re.sub(r"\s+", " ", text)
        # Remove stopwords and one-character words
        text = " ".join(
            [
                word
                for word in text.split()
                if word not in self.RO_STOPWORDS and len(word) > 1
            ]
        )

        return text

    def is_stopword(self, word: str):
        return word in self.RO_STOPWORDS

    def has_numbers(self, word: str):
        return bool(re.search(r"\d", word))
