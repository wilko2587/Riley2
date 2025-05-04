# ROADMAP (Terminal-Friendly)

====================================
||  Email & Calendar Verification ||
====================================

🟧 highlevel.verify_email_calendar status: in-progress
   note: Ensure that core agents (email and calendar) are functionally stable and aligned with real APIs.

├── 🟧 checkpoint.test_email_agent status: in-progress
│   note: Validate email send/receive behavior, mock-vs-real agent consistency.
│   ├── 🟩 lowlevel.compare_email_mock_vs_real status: completed
│   │   note: Ensure method signatures and output formats match real-world agent.
│   └── 🟨 → lowlevel.test_email_edge_cases status: in-progress
│       note: Validate handling of failures, retries, malformed inputs.

└── 🟥 checkpoint.test_calendar_agent status: open
    note: Evaluate calendar block merging, conflict resolution.
    └── 🟥 lowlevel.compare_calendar_mock_vs_real status: open
        note: Ensure behavior of mock calendar matches backend agent logic.

====================================
||       WhatsApp Integration      ||
====================================

🟥 highlevel.integrate_whatsapp status: open
note: Add Twilio-based WhatsApp message support.

====================================
||         Nest Integration        ||
====================================

🟥 highlevel.integrate_nest status: open
note: Integrate Nest thermostat agent with calendar scheduling.

====================================
||       Location Services         ||
====================================

🟥 highlevel.location_services status: open
note: Track and respond to user location changes.
