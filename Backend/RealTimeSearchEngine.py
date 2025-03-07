from googlesearch import search
from groq import Groq
import json
from json import load , dump
import datetime
from dotenv import load_dotenv
import os

# Getting Environment Variables From .env File
load_dotenv()


# Reterive specific environment variable for username, assistant name and api key
Username = os.getenv("USERNAME")
AssistantName = os.getenv("ASSISTANT_NAME")
GroqApiKey = os.getenv("GROQ_API_KEY")
print(f"API Key: {GroqApiKey}") 
client = Groq(api_key=GroqApiKey)


messages =[]


System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {AssistantName} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

SystemChatBot = [
    {"role": "system" , "content" : System}
]

try:
    with open(r"../Data/ChatLog.json" , "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"../Data/ChatLog.json" , "w") as f:
        dump([] , f)


def GoogleSearch(Query):
    results = list(search(Query, advanced =True , num_results=5))
    Answer = f"The Search Results for '{Query}' are:\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n"
    Answer += "[end]"
    return Answer

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%I")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    # Format data into string
    data = f"Use this real time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}.\n"
    data += f"Time: {hour} hours:{minute} minutes:{second} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

def RealTimeSearchEngine(prompt):
    global SystemChatBot , messages
    with open(r"../Data/ChatLog.json" , "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content":f"{prompt}"})
    SystemChatBot.append({"role": "system", "content":GoogleSearch(prompt)})

    completion= client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content":Information()}]+ messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
    Answer = ""

    for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
    Answer = Answer.replace("</s>","")
    messages.append({"role": "assistant", "content":Answer})
    with open(r"../Data/ChatLog.json" , "w") as f:
        dump(messages , f , indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)



if __name__ == "__main__":
    while True:
      user_input = input("Enter Your Question: ")
      print(RealTimeSearchEngine(user_input))
