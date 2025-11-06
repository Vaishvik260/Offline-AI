from langchain_community.llms import Ollama

llm = Ollama(model="mistral")

print("🤖 Hello! Ask me anything (type 'exit' to quit).")

while True:
    question = input("\nYou: ")
    if question.lower() == "exit":
        break
    answer = llm.invoke(question)
    print("Robot:", answer)

from langchain_community.llms import Ollama

llm = Ollama(model="mistral")

print("🤖 Hello! Ask me anything (type 'exit' to quit).")

while True:
    question = input("\nYou: ")
    if question.lower() == "exit":
        break
    answer = llm.invoke(question)
    print("Robot:", answer)
hello
exit
from langchain_community.llms import Ollama

llm = Ollama(model="mistral")

print("🤖 Hello! Ask me anything (type 'exit' to quit).")

while True:
    question = input("\nYou: ")
    if question.lower() == "exit":
        break
    answer = llm.invoke(question)
    print("Robot:", answer)
O

