---
name: parse-and-structure-logs-for-triage
description: Use this skill to extract, normalize, and structure log entries for error triage and reporting according to strict formatting rules.
---
- Read the raw log file line by line, identifying log entries by timestamp and log level.
- Filter entries to include only ERROR and CRITICAL levels (case-insensitive).
- Normalize service names by converting to lowercase and replacing hyphens with underscores.
- Convert all timestamps to UTC timezone and format as ISO 8601 with 'Z' suffix.
- Extract the main message from the first line after the service name.
- Detect and extract exception tracebacks if present; capture the last line of the traceback as the exception message.
- Detect and sum repeat counts from lines like "-- last message repeated N times --" following each entry.
- Aggregate counts of errors by service using the normalized service names.
- Sort the final error list by service name and then by timestamp ascending.
- Include required top-level metadata fields such as schema_version and generated_by.
- Validate the output JSON against the schema and rules before submission.