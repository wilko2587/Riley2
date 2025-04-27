from datetime import datetime, timedelta

def calendar_scan(start_date, end_date, query=None):
    """Scan calendar events between dates, optionally filtering by keyword."""
    events = [
        {"title": "Italy Trip", "date": "2025/05/12"},
        {"title": "William Lunch", "date": "2025/04/27"},
        {"title": "Doctor Appointment", "date": "2025/05/04"},
    ]

    start = datetime.strptime(start_date, "%Y/%m/%d")
    end = datetime.strptime(end_date, "%Y/%m/%d")

    matched = []
    for event in events:
        event_date = datetime.strptime(event["date"], "%Y/%m/%d")
        if start <= event_date <= end:
            if query:
                if query.lower() in event["title"].lower():
                    matched.append(event)
            else:
                matched.append(event)

    if not matched:
        return "No matching events found."

    return f"Found events: {matched}"