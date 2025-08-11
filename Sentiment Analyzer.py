def analyze_sentiment(text):
    positive = ["great", "good", "excellent", "happy", "love"]
    negative = ["bad", "terrible", "sad", "hate", "angry"]
    
    text = text.lower()
    score = sum(word in text for word in positive) - sum(word in text for word in negative)

    if score > 0:
        return "Positive Sentiment"
    elif score < 0:
        return "Negative Sentiment"
    else:
        return "Neutral Sentiment"

print(analyze_sentiment("I love the new update, it's excellent!"))
