from flask import Flask, request, jsonify
from openai import OpenAI
import os
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
import re
from analyse_code import analyse_code
import threading
from threading import Lock
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
csv_lock = Lock()
df_lock = Lock()

client = OpenAI()
questions_csv = "questions_data.csv"

if os.path.exists(questions_csv):
    questions_data = pd.read_csv(questions_csv)
else:
    questions_data = pd.DataFrame(columns=["question_id", "difficulty", "question", "test_cases", "time_complexity"])
    with csv_lock:
        questions_data.to_csv(questions_csv, index=False)

current_question_id = questions_data["question_id"].max() + 1 if not questions_data.empty else 1

def save_questions():
    global questions_data
    with csv_lock:
        questions_data.to_csv(questions_csv, index=False)

def update_questions():
    for difficulty in ["easy", "medium", "hard"]:
        global current_question_id, questions_data
        while len(questions_data[questions_data["difficulty"] == difficulty]) < 2:
            question, time_complexity = generate_question(difficulty)
            test_cases = genearate_input_test_cases(question)
            test_cases = parse_test_cases(test_cases)
            new_entry = pd.DataFrame({"question_id": [current_question_id], "difficulty": [difficulty], "question": [question], "test_cases": [test_cases], "time_complexity": [time_complexity]})
            with df_lock:
                questions_data = pd.concat([questions_data, new_entry])
            current_question_id += 1
        save_questions()

def init_questions():
    count = 1
    for difficulty in ["easy", "medium", "hard"]:
        global current_question_id, questions_data
        while len(questions_data[questions_data["difficulty"] == difficulty]) < 2:
            question, time_complexity = generate_question(difficulty)
            test_cases = genearate_input_test_cases(question)
            test_cases = parse_test_cases(test_cases)
            new_entry = pd.DataFrame({"question_id": [current_question_id], "difficulty": [difficulty], "question": [question], "test_cases": [test_cases], "time_complexity": [time_complexity]})
            with df_lock:
                questions_data = pd.concat([questions_data, new_entry])
            current_question_id += 1

            print("count: ", count)
            count += 1
        save_questions()


def generate_question(difficulty):
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
            "role": "system",
            "content": "You are an advanced question bank specialized in generating Data Structures and Algorithms (DSA) questions tailored to specified difficulty levels. Each question should include: 1. A clear problem statement. 2. The expected input format for the code solution. The expected code should only take numerical inputs. At the end of your reponse, mention the ideal time complxity for the question in tags example : <Time_Complexity>O(n)</Time_Complexity>. Your response should be structured and concise to facilitate parsing."
            },
            {
            "role": "user",
            "content": f"Generate a DSA question for difficulty level {difficulty}. The response should include the problem statement and the expected input format for the code solution."
            }
        ]
    )
    time_complexity = re.search(r"<Time_Complexity>(.*?)</Time_Complexity>", response.choices[0].message.content)
    if time_complexity is None:
        response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
            "role": "system",
            "content": "You have to fidn out the best possible time complexity of a given question. Your reponse should just be the time complexity example : O(n)"
            },
            {
            "role": "user",
            "content": f"Find the best possible time complexity for the following question: {response.choices[0].message.content}"
            }
        ]
        )
        time_complexity = response.choices[0].message.content
    else:
        time_complexity = time_complexity.group(1)
        response.choices[0].message.content = re.sub(r"<Time_Complexity>(.*?)</Time_Complexity>", "", response.choices[0].message.content, flags=re.DOTALL)
    return response.choices[0].message.content, time_complexity

def genearate_input_test_cases(code):
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
            "role": "system",
            "content": "You are a code understanding module. You are given a coding question with the expected input format and are expected to generate 1 input test case in plain text which is entirely numerical that could be used to test the code. Each test case should be on a new line and should start with '**Test Case No. [test case number]**'. After each test case, you should include a new line with the text '**Expected Output**' followed by the expected output for the test case. Each test case input and expected output should have no exmpty lines between them. Your response should be structured and concise to facilitate parsing."
            },
            {
            "role": "user",
            "content": f"Generate 5 input test cases for the following code: {code}"
            }
        ]
    )

    return response.choices[0].message.content


def check_optimal_code(question, code):
    response = client.chat.completions.create(
  model="gpt-4",
  messages=[
    {
      "role": "system",
      "content": "I am giving you a code which is the solution to a given problem. You need to give me a one word response true/false telling me if the solution provided is the most efficient solution in terms of time complexity."
    },
    {
      "role": "user",
      "content": f"Check if the following code is optimal.\nProblem : {question}\nCode: {code}"
    }
  ],
  temperature=0.7,
  top_p=1
)
    if response.choices[0].message.content.lower() == "true":
        return True
    return False

def parse_test_cases(test_case_response):
    lines = test_case_response.split("\n")
    test_cases = []
    current_test_case = None
    capturing_input = False
    capturing_output = False
    for line in lines:
        if line.startswith("**Test Case No."):
            if current_test_case:
                test_cases.append(current_test_case)
            current_test_case = {"input": "", "output": ""}
            capturing_input = True
            capturing_output = False
        elif line.startswith("**Expected Output"):
            capturing_input = False
            capturing_output = True
        else:
            if capturing_input:
                current_test_case["input"] += line.strip("`").strip()
            elif capturing_output:
                current_test_case["output"] += line.strip("`").strip()

    if current_test_case:
        test_cases.append(current_test_case)  # Append the last test case if it exists

    return test_cases
        

def give_hint(question, code):
    response = client.chat.completions.create(
  model="gpt-4",
  messages=[
    {
      "role": "system",
      "content": "You are to provide one hint for solving programming problems aimed at achieving a specified best-case time complexity. The hint should guide the user towards the solution without revealing the direct answer or logic, as this is for a game."
    },
    {
      "role": "user",
      "content": f"Here's a programming problem: {question}. The user has written the following code: {code}. Provide a hint to help the user achieve the best-case time complexity."
    }
  ],
  temperature=0.7,
  top_p=1
)
    return response.choices[0].message.content

@app.route("/submit_code", methods=["POST"])
def submit_code():
    code = request.json.get("code")
    # question_id = request.json.get("question_id")
    test_cases = request.json.get("test_cases")
    time_complexity = request.json.get("time_complexity")
    question = request.json.get("question")
    if not code or not test_cases or not time_complexity or not question:
        return jsonify({"error": "Invalid request"}), 400
    
    code_correct = analyse_code(question, code, test_cases, time_complexity)
    if code_correct:
        is_optimal_code = check_optimal_code(question, code)
        if is_optimal_code:
            return jsonify({"is_code_correct": str(code_correct), "is_optimal_code": str(is_optimal_code)})
        else:
            hint = give_hint(question, code)
            return jsonify({"is_code_correct": str(code_correct), "is_optimal_code": str(is_optimal_code), "hint": hint})
    else:
        return jsonify({"is_code_correct": str(code_correct)})


@app.route("/generate-question", methods=["POST"])
def generate_question_route():
    difficulty = request.json.get("difficulty")
    print(difficulty)
    if difficulty not in ["easy", "medium", "hard"]:
        return jsonify({"error": "Invalid difficulty level"}), 400
    
    global questions_data
    available_questions = questions_data[questions_data["difficulty"] == difficulty]
    if available_questions.empty:
        update_questions()
        available_questions = questions_data[questions_data["difficulty"] == difficulty]
    
    question = available_questions.sample(n=1).iloc[0]
    with df_lock:
        questions_data = questions_data.drop(question.name)
    save_questions()

    threading.Thread(target=update_questions).start()
    return jsonify({"question_id" : str(question["question_id"]), "question": question["question"], "test_cases": question["test_cases"], "time_complexity": question["time_complexity"]})



if __name__ == "__main__":
    init_questions()
    print("questions initialized")


@app.route("/generate_code", methods=["POST"])
def generate_code():
    print("request received")
    question = request.json.get("question")
    response = client.chat.completions.create(
  model="gpt-4",
  messages=[
    {
      "role": "system",
      "content": "You will be provided with a programming question. You need to return the most efficient Python code solution along with explanation."
    },
    {
      "role": "user",
      "content": question
    }
  ],
  temperature=0.7,
  top_p=1
)
    print(response.choices[0].message.content)
    return jsonify({"code": response.choices[0].message.content})
    
app.run(debug=True)
# if __name__ == "__main__":
#     if not os.path.exists("questions.csv"):
#         question_data = pd.DataFrame({"difficulty": [], "question": []})
#         question_data.to_csv("questions.csv", index=False)
#     else :
        
        

#     app.run(debug=True)
# if __name__ == "__main__":
#     generate_question_route()
