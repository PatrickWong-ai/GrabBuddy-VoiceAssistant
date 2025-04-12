import difflib

def get_intent_phrases():
    return {
        "performance": ["how am i doing", "my performance", "how many trips", "berapa trip", "berapa kali"],
        "new_order": ["new order", "got job", "got pickup", "ada order"],
        "income": ["how much i earn", "total income", "berapa income", "how much money"],
        "hours": ["how long online", "total time", "berapa jam"],
        "short_break": ["short break", "rest", "take break", "nak rehat"],
        "reconfirm": ["reconfirm trip", "confirm destination"],
        "eta": ["how long to pickup", "eta", "berapa minit", "when reach"],
        "contact": ["message passenger", "passenger contact", "chat with rider"],
        "time": ["pickup time", "scheduled pickup", "what time"],
        "map": ["back to map", "show map", "open map"],
        "cancel": ["cancel trip", "tak jadi", "batal trip"]
    }

def match_intent(text):
    text = text.lower()
    intent_phrases = get_intent_phrases()
    flattened = [(intent, phrase) for intent, phrases in intent_phrases.items() for phrase in phrases]

    # Get all phrases only
    phrases_only = [phrase for _, phrase in flattened]
    match = difflib.get_close_matches(text, phrases_only, n=1, cutoff=0.6)

    if match:
        matched_phrase = match[0]
        for intent, phrase in flattened:
            if phrase == matched_phrase:
                print(f"[Fuzzy Match] Matched '{matched_phrase}' to intent '{intent}'")
                return intent

    return None
