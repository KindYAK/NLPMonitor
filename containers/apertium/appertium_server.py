import subprocess

from flask import Flask, request
app = Flask(__name__)


@app.route('/')
def hello_world():
    text = request.args.get('text')
    lemmatized = subprocess.getoutput(f"echo '{text}' | apertium -d . kaz-disam")
    lines = [l.strip() for l in lemmatized.split("\n")]
    result = ""
    for i, line in enumerate(lines):
        if line.startswith("\"<") and line.endswith(">\""):
            token = lines[i+1].split("\"")[1].replace("*", "").strip()
            if not token.isalpha():
                continue
            result += token + " "
    return {
        "result": result
    }
