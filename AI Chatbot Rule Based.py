def ai_chatbot(message):
    faqs = {
        "what is ai": "AI stands for Artificial Intelligence. It enables machines to mimic human intelligence.",
        "use of ai": "AI is used in marketing, healthcare, finance, robotics, and more.",
        "hello": "Hi! I'm your AI assistant. How can I help?"
    }
    return faqs.get(message.lower(), "Sorry, I don't understand that yet.")

print(ai_chatbot("What is AI"))
