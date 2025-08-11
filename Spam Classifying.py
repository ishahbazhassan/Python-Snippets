def classify_message(message):
    spam_keywords = ["win", "free", "offer", "money", "urgent"]
    ham_keywords = ["meeting", "project", "schedule", "report"]

    message = message.lower()
    spam_score = sum(word in message for word in spam_keywords)
    ham_score = sum(word in message for word in ham_keywords)

    return "Spam" if spam_score > ham_score else "Ham"

print(classify_message("Congratulations! You win a free iPhone!"))
