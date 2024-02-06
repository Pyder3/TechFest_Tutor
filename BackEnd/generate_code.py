from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4",
  messages=[
    {
      "role": "system",
      "content": "You will be provided with a programming question. You need to return the most efficient Python code solution along with explanation."
    },
    {
      "role": "user",
      "content": "Write the code to perform fibbonachi sequence."
    }
  ],
  temperature=0.7,
  top_p=1
)

print(response.choices[0].message.content)