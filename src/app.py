import os
import aiml
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from law_processor import LawProcessor

app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)

SESSION_ID = 13123


@app.route("/")
def start():
    return render_template("index.html", title="RoLegalBot")


@app.route("/send", methods=["POST"])
def send():
    data = request.json
    message = data["message"]
    bot_response = kernel.respond(message, SESSION_ID)
    message = message.lower()

    print(f"RoLegalBot> Primit mesajul {message}")

    if message == "salvează":
        kernel.saveBrain(f"../aiml/{SESSION_ID}.brn")
        return jsonify({"answer": "Conversație salvată!"})
    elif message.startswith("care este articolul"):
        article_number = int(kernel.getPredicate("article_number", SESSION_ID))
        legal_code = str(kernel.getPredicate("legal_code", SESSION_ID))

        # article_text = LawProcessor().find_article(article_number, legal_code)

        # return jsonify({"answer": article_text})
        return jsonify({"answer": f"Vrei să știi despre articolul {article_number} din {legal_code}"})
    elif message == "":
        return jsonify({"answer": "Voiai să mă întrebi ceva?"})
    else:
        return jsonify({"answer": bot_response})


if __name__ == "__main__":
    kernel = aiml.Kernel()

    # Check for existing "brain", meaning existing kernel progress saved
    # If there is, load it, if not, learn from existing AIML file
    if os.path.isfile(f"../aiml/{SESSION_ID}.brn"):
        kernel.bootstrap(brainFile=f"../aiml/{SESSION_ID}.brn")
    else:
        kernel.bootstrap(learnFiles="../aiml/std-startup.xml", commands="load aiml b")
        kernel.saveBrain(f"../aiml/{SESSION_ID}.brn")

    app.run(port=5000, debug=True)
