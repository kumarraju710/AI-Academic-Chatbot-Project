def predict_intent(text):
    text = text.lower()

    if "enroll" in text:
        return "enrollment"
    elif "fee" in text or "payment" in text:
        return "fees"
    else:
        return "general"
