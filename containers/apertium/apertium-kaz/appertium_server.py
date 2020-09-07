import subprocess

from flask import Flask, request
app = Flask(__name__)


@app.route('/')
def hello_world():
    text = request.args.get('text')
    lemmatized = subprocess.getoutput(f"echo '{text}' | apertium -d . kaz-disam | python3 /kaz-tagger/kaz_tagger.py")
    lines = [l.strip() for l in lemmatized.split("\n")]

    with open("stopwords.txt", "r") as f:
        stopwords = [l.strip() for l in f.readlines()]

    result = ""
    for i, line in enumerate(lines):
        if line.startswith("\"<") and line.endswith(">\""):
            token = lines[i+1].split("\"")[1].replace("*", "").strip().lower()
            if not token.isalpha():
                continue
            if token in stopwords:
                continue
            result += token + " "
    return {
        "result": result
    }
