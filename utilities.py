from collections import deque

history = deque(maxlen=10)

def add_interaction(llm_response):
    history.append({
        "your_response": llm_response,
    })
        
