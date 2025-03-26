import ollama

response1 = ollama.generate(model='phi3', prompt='What is the capital of France? (Only capital name)')
response2 = ollama.generate(model='phi3', prompt='And what about Germany? (Only capital name)')

print(response1['response'])
print(response2['response'])
