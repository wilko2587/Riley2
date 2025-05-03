def meta_query(query):
    """Answers user questions about backend capabilities."""
    capabilities = [
        "Scan your calendar for upcoming events within a time window",
        "Search your calendar for events containing specific keywords",
        "Download emails in weekly chunks",
        "Filter emails by sender",
        "Summarize batches of emails",
        "Tell the current date and time"
    ]
    
    if "calendar" in query.lower():
        return "I can scan your calendar for any events between two dates, and filter them if you provide a keyword."
    elif "email" in query.lower():
        return "I can download recent emails, filter them by sender, and summarize batches of emails for you."
    elif "time" in query.lower():
        return "I can tell you the current date and time."
    else:
        return f"I am equipped with the following capabilities: {', '.join(capabilities)}"