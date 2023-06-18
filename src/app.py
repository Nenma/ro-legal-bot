import os
import re
import aiml
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from law_processor import LawProcessor
from simplification import SimplificationTool

app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)

SESSION_ID = 13123
KERNEL = aiml.Kernel()
MEMORISED_TEXT = ""


@app.route("/")
def start():
    return render_template("index.html", title="RoLegalBot")


@app.route("/send", methods=["POST"])
def send():
    global MEMORISED_TEXT
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
        response = LawProcessor().get_code_size(legal_code)

        return jsonify({"answer": response})

    elif re.match(r"^care e.* articolul", message):
        article_number = int(KERNEL.getPredicate("article_number", SESSION_ID))
        legal_code = str(KERNEL.getPredicate("legal_code", SESSION_ID)).strip()
        response = LawProcessor().find_article(article_number, legal_code)
        MEMORISED_TEXT = response

        return jsonify({"answer": response})

    elif message == "mai simplu":
        simple_response = SimplificationTool().simplify(MEMORISED_TEXT)

        return jsonify({"answer": simple_response})

    elif message == "":
        return jsonify({"answer": "Voiai să mă întrebi ceva?"})

    else:
        return jsonify({"answer": bot_response})


if __name__ == "__main__":
    # Check for existing "brain", meaning existing kernel progress saved
    # If there is, load it, if not, learn from existing AIML file
    if os.path.isfile(f"../aiml/{SESSION_ID}.brn"):
        KERNEL.bootstrap(brainFile=f"../aiml/{SESSION_ID}.brn")
    else:
        KERNEL.bootstrap(learnFiles="../aiml/std-startup.xml", commands="load aiml b")
        KERNEL.saveBrain(f"../aiml/{SESSION_ID}.brn")

    app.run(port=5000, debug=True)
