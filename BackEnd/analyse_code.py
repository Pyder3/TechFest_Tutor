from transformers import T5ForConditionalGeneration, AutoTokenizer
import torch
import requests
from sphere_engine import CompilersClientV4
from openai import OpenAI
import time



def analyse_code(problem_desc, code, input, time_complexity):
    API_KEY = "b3028c0db10ceef68b38c2d93bc545a5"
    client = CompilersClientV4(API_KEY, '8978b2c4.compilers.sphere-engine.com')
    r = client.submissions.create(code, 116, input)
    time.sleep(10)
    result = client.submissions.get(r['id'])
    result = result.get('result').get('status').get('code')

    if result != 15:
        print("compiler error")
        return False
    
    GPTclient = OpenAI()
    response = GPTclient.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
            "role": "system",
            "content": "You are a code checking module. You are given a coding question and a code solution. You are expected to tell if the code is functionally correct or not. Answer in one word 'true' if code is fucntionally correct or 'false' if code is functionally wrong."
            },
            {
            "role": "user",
            "content": f"Check if the code is correct for not : The problem description is {problem_desc} and the code is {code}"
            }
        ]
    )
    if response.choices[0].message.content.lower() == "true":
        return True
    return False
    

# if __name__ == "__main__":
#     code = 'print("Hello, World!")'

#     submission_id = analyse_code("Print Hello World", code)
#     print(submission_id)

    
# if __name__ == "__main__":
#     code = 'print("Hello, World!")'

#     submission_id = analyse_code("Print Hello World", code)
#     print(submission_id)
# def analyse_code(problem_desc, code):
#     model = T5ForConditionalGeneration.from_pretrained('/Applications/C_codes/TechFest/codet5_finetuned_critic')
#     tokenizer = AutoTokenizer.from_pretrained('Salesforce/codet5-large')
#     tokens = tokenizer(problem_desc + code, return_tensors="pt").input_ids
#     with torch.no_grad():
#         output = model.generate(tokens, max_length=8)

#     print(tokenizer.decode(output[0], skip_special_tokens=True))

# if(__name__ == "__main__"):
#     problem_desc = "Find the factorial of a number using recursion."
#     code = "def factorial(n):\n    if n = :\n        return 1\n    else:\n        return n * factorial(n-1)"
#     analyse_code(problem_desc, code)

if __name__ == "__main__":
    problem_desc = "Find the factorial of a number using recursion."
    code = "n=int(input())\ndef factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)"
    input = "5"
    time_complexity = "O(n)"
    print(analyse_code(problem_desc, code, input, time_complexity))