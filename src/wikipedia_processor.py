from bs4 import BeautifulSoup
import stopwords
import requests
import csv

f = open("../data/wikipedia/ro_wikipedia.csv", "w", encoding="utf8", newline="")
writer = csv.writer(f)
columns = ["url", "title", "raw_content", "content"]
writer.writerow(columns)

ro_stopwords = stopwords.get_stopwords("romanian")

if __name__ == "__main__":
    for _ in range(10):
        page = requests.get("https://ro.wikipedia.org/wiki/Special:Random")
        soup = BeautifulSoup(page.content, "html.parser")

        url = page.url
        title = soup.find_all("title")[0].get_text().split(" - Wikipedia")[0]

        raw_content = []
        content = []
        for p in soup.find_all("p"):
            text = p.get_text()

            if text not in ["", "\n"]:
                text = text.replace("\xa0", " ").strip()

                raw_content.append(text)
                content.append(text.lower())

            raw_content.append(p.get_text())

        writer.writerow([url, title, raw_content, content])

    f.close()
