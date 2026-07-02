import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def review_code(code, language):    

    lines = code.split("\n")
 
    loop_count = 0
    condition_count = 0
    function_count = 0

    loop_keywords=[
        "for(","for (", "while(","while (","do{", "do {"
    ]
    condition_keywords = [
        "if(","if (", "else if", "elif ", "switch", "case "
    ]
    function_keywords = [
        "def ",
        "function ",
        "void ",
        "public ",
        "private ",
        "protected ",
        "fun ",
        "fn ",
        "main("
    ]

    for line in lines:

        text = line.strip().lower()

        if any(keyword in text for keyword in loop_keywords):
            loop_count += 1

        if any(keyword in text for keyword in condition_keywords):
            condition_count += 1

        if any(keyword in text for keyword in function_keywords):
            function_count += 1


    complexity_score = loop_count + condition_count + function_count

    if complexity_score <= 3:
        complexity_level = "Low"
    elif complexity_score <= 6:
        complexity_level = "Medium"
    else:
        complexity_level = "High"
    metrics = {
        "Language": language.upper(),
        "Loops": loop_count,
        "Functions": function_count,
        "Conditions": condition_count,
        "Complexity": complexity_level
    }

    
    result = f"""
📊 Complexity:
Loops: {loop_count}
Conditions: {condition_count}
Functions: {function_count}
Level: {complexity_level}
"""
    return {
        "result": result,
        "metrics": metrics
}

def groq_review(code, language):

    try:

        prompt = f"""
You are an expert software engineer and senior code reviewer.

Analyze the following {language} code carefully.

Return your response ONLY in the EXACT format below.

Do NOT use markdown.
Do NOT use code fences.
Do NOT add explanations outside this format.

====================================

OVERALL_SCORE: <0-100>

CORRECTNESS: <0-100>
READABILITY: <0-100>
SECURITY: <0-100>
EFFICIENCY: <0-100>
BEST_PRACTICES_SCORE: <0-100>

SUMMARY:
<Write a short 2-3 sentence summary of the overall code quality.>

BUGS:
- Severity: Critical/Warning
  Line: <line number>
  Problem: <brief problem>
  Suggestion: <brief fix>

- Severity: Critical/Warning
  Line: <line number>
  Problem: <brief problem>
  Suggestion: <brief fix>

IMPROVEMENTS:
- <improvement 1>
- <improvement 2>

BEST_PRACTICES:
- <best practice 1>
- <best practice 2>

CORRECTED_CODE:
<Return the complete corrected source code only.
Preserve formatting and indentation.
Do not explain the code.>

====================================

Scoring Guidelines:

CORRECTNESS:
- Logical errors
- Syntax mistakes
- Wrong operators
- Missing validations

READABILITY:
- Naming
- Formatting
- Comments
- Structure

SECURITY:
- Hardcoded credentials
- eval()
- SQL Injection
- XSS
- Unsafe APIs
- Sensitive data exposure

EFFICIENCY:
- Unnecessary loops
- Nested loops
- Time complexity
- Memory usage

BEST_PRACTICES:
- Language conventions
- Clean code
- Maintainability
- Reusability

Rules:

1. Detect the programming language automatically from the provided code.
2. Support ANY programming language.
3. Report the exact line number whenever possible.
4. Be strict when scoring.
5. If no bugs exist, write:
   BUGS:
   None
6. If no improvements exist, write:
   IMPROVEMENTS:
   None
7. If no best practices are applicable, write:
   BEST_PRACTICES:
   None
8. Always return the corrected code.

Code to review:

{code}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content
        
    except Exception as e:
        return f"⚠️ Groq Error: {str(e)}"
def detect_language(code):

    code_lower = code.lower()

    # Python
    if (
        "def " in code
        or "import " in code
        or "print(" in code
    ):
        return "python"

    # Java
    elif (
        "public class" in code
        or "system.out.println" in code_lower
        or "public static void main" in code
    ):
        return "java"

    # C
    elif (
        "#include<stdio.h>" in code
        or "printf(" in code
        or "scanf(" in code
    ):
        return "c"

    # C++
    elif (
        "#include<iostream>" in code
        or "std::cout" in code
    ):
        return "cpp"

    # JavaScript
    elif (
        "function " in code
        or "console.log(" in code
        or "const " in code
        or "let " in code
    ):
        return "javascript"

    return detect_language_ai(code)


def detect_language_ai(code):

    try:

        prompt = f"""
Identify the programming language of this code.

Reply with ONLY the language name.

Examples:
python
java
c
cpp
javascript
typescript
go
rust
php
kotlin

Code:
{code}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        return response.choices[0].message.content.strip().lower()

    except:
        return "unknown"

def get_language(code):
    return detect_language(code)
# ---------------------------
# MAIN AI FUNCTION
# ---------------------------
def ai_review(code, language):
    return groq_review(code, language)
        
