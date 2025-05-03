import logging
from datetime import datetime, timedelta
from riley2.core.logger_utils import logger

def calendar_scan(start_date, end_date, query=None):
    logger.debug(f"Scanning calendar events from {start_date} to {end_date} with query: {query}")
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

    logger.info(f"Scanned {len(events)} events, found {len(matched)} matching events.")

    if not matched:
        logger.debug("No matching events found.")
        return "No matching events found."

    result = f"Found events: {matched}"
    logger.debug(f"Calendar scan result: {result}")
    return result