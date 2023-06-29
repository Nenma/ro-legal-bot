import os
import re
import aiml
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from src.law_processor import LawProcessor
from src.explanation import ExplanationTool
from src.corpus_processor import CorpusProcessor

lp = LawProcessor()
st = ExplanationTool()
cp = CorpusProcessor()
app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)

SESSION_ID = "RLB"

KERNEL = aiml.Kernel()
# Check for existing "brain", meaning existing kernel progress saved
# If there is, load it, if not, learn from existing AIML file
if os.path.isfile(f"./aiml/{SESSION_ID}.brn"):
    KERNEL.bootstrap(brainFile=f"./aiml/{SESSION_ID}.brn")
else:
    KERNEL.bootstrap(learnFiles="./aiml/std-startup.xml", commands="load aiml b")
    KERNEL.saveBrain(f"./aiml/{SESSION_ID}.brn")


@app.route("/")
def start():
    return render_template("index.html", title="RoLegalBot")


@app.route("/send", methods=["POST"])
def send():
    data = request.json
    message = data["message"]
    bot_response = KERNEL.respond(message, SESSION_ID)
    message = message.lower()

    print(f"RoLegalBot> Primit mesajul {message}")

    if message == "salvează":
        KERNEL.saveBrain(f"../aiml/{SESSION_ID}.brn")

        return jsonify({"answer": "Conversație salvată!"})

    elif message == "resetează":
        KERNEL.resetBrain()
        KERNEL.bootstrap(learnFiles="../aiml/std-startup.xml", commands="load aiml b")
        KERNEL.saveBrain(f"../aiml/{SESSION_ID}.brn")

        return jsonify({"answer": "Conversație resetată!"})

    elif message.startswith("câte articole"):
        legal_code = str(KERNEL.getPredicate("legal_code_size", SESSION_ID)).strip()
        response = lp.get_code_size(legal_code)

        return jsonify({"answer": response})

    elif re.match(r"^care e.* articolul", message):
        article_number = int(KERNEL.getPredicate("article_number", SESSION_ID))
        legal_code = str(KERNEL.getPredicate("legal_code", SESSION_ID)).strip()
        response = lp.find_article(article_number, legal_code)
        explained = st.simplify(response)

        return jsonify({"answer": explained})

    elif message.startswith(
        (
            "ce ar trebui să știu despre",
            "ce legi sunt legate de",
            "care legi sunt legate de",
            "ce legi sunt despre",
            "care legi sunt despre",
            "care sunt legile legate de",
            "care sunt legile despre",
            "ce legi au legătură cu",
            "care legi au legătură cu",
            "aș vrea să știu despre",
            "vreau să știu despre",
            "zi despre",
            "spune despre",
        )
    ):
        keyword = KERNEL.getPredicate("search_term", SESSION_ID).strip()
        response = lp.find_relevant_text(keyword)

        return jsonify({"answer": response})

    elif message.startswith(("definește", "ce înseamnă")):
        word = KERNEL.getPredicate("word_definition", SESSION_ID)
        definition = cp.get_dex_definition(word)

        if definition != word.lower():
            return jsonify({"answer": definition})
        else:
            return jsonify(
                {"answer": f'Din păcate nu pot găsi o definiție pentru "{word}"...'}
            )

    elif message == "":
        return jsonify({"answer": "Voiai să mă întrebi ceva?"})

    else:
        return jsonify({"answer": bot_response})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
