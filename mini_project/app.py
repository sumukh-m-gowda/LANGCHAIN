from flask import Flask, render_template, request
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv()

app = Flask(__name__)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

@app.route("/", methods=["GET", "POST"])
def home():
    answer = ""

    if request.method == "POST":
        question = request.form["question"]
        response = llm.invoke(question)
        answer = response.content

    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run(debug=True)