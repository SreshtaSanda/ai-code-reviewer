import re
from flask import Flask, render_template, request
from ai_reviewer import review_code, ai_review, detect_language

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    code=""
    language=""
    rule_result=""
    #ai_result=""
    parsed_ai={}
    metrics = {
    "Correctness": 0,
    "Readability": 0,
    "Best Practices": 0,
    "Efficiency": 0,
    "Security": 0
}
  
    if request.method == "POST":

        code = request.form["code"]

    # Auto detect language
        language = detect_language(code)

        review = review_code(code, language)

        rule_result = review["result"]
        metrics = review["metrics"]
       
        parsed_ai = parse_ai_output(
            ai_review(code, language)
         )
       # Show detected language
        rule_result = (
            f"🔍 Detected Language: {language.upper()}\n\n"
            + rule_result
        )
    return render_template(
        "index.html",
        rule_result=rule_result,
        #ai_result=ai_result,
        parsed_ai=parsed_ai,
        code=code,
        language=language,
        metrics=metrics
    )

def parse_ai_output(ai_text):

    sections = {
        "overall_score": "",
        "correctness": "",
        "readability": "",
        "security": "",
        "efficiency": "",
        "best_practices_score": "",
        "summary": "",
        "bugs": "",
        "improvements": "",
        "practices": "",
        "code": ""
    }

    def get_value(pattern):
        match = re.search(pattern, ai_text, re.DOTALL)
        return match.group(1).strip() if match else ""

    sections["overall_score"] = get_value(
        r"OVERALL_SCORE:\s*(.*?)\s*CORRECTNESS:"
    )

    sections["correctness"] = get_value(
        r"CORRECTNESS:\s*(.*?)\s*READABILITY:"
    )

    sections["readability"] = get_value(
        r"READABILITY:\s*(.*?)\s*SECURITY:"
    )

    sections["security"] = get_value(
        r"SECURITY:\s*(.*?)\s*EFFICIENCY:"
    )

    sections["efficiency"] = get_value(
        r"EFFICIENCY:\s*(.*?)\s*BEST_PRACTICES_SCORE:"
    )

    sections["best_practices_score"] = get_value(
        r"BEST_PRACTICES_SCORE:\s*(.*?)\s*SUMMARY:"
    )

    sections["summary"] = get_value(
        r"SUMMARY:\s*(.*?)\s*BUGS:"
    )

    sections["bugs"] = get_value(
        r"BUGS:\s*(.*?)\s*IMPROVEMENTS:"
    )

    sections["improvements"] = get_value(
        r"IMPROVEMENTS:\s*(.*?)\s*BEST_PRACTICES:"
    )

    sections["practices"] = get_value(
        r"BEST_PRACTICES:\s*(.*?)\s*CORRECTED_CODE:"
    )

    sections["code"] = get_value(
        r"CORRECTED_CODE:\s*(.*)"
    )

    sections["code"] = re.sub(r"```[a-zA-Z0-9+#]*", "", sections["code"])
    sections["code"] = sections["code"].replace("```", "").strip()

    return sections
if __name__ == "__main__":
    app.run(debug=True)