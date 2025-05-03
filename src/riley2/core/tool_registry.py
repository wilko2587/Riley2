from riley2.agents.calendar_agent import calendar_scan
from riley2.agents.email_agent import (
    email_download_chunk,
    email_filter_by_sender,
    email_summarize_batch,
)
from riley2.core.time_tools import get_current_time
from riley2.core.meta_agent import meta_query

TOOL_FUNCTIONS = {
    "calendar_scan": calendar_scan,
    "email_download_chunk": email_download_chunk,
    "email_filter_by_sender": email_filter_by_sender,
    "email_summarize_batch": email_summarize_batch,
    "get_current_time": get_current_time,
    "meta_query": meta_query,
}