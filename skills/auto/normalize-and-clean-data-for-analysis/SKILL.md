---
name: normalize-and-clean-data-for-analysis
description: Use this skill to preprocess raw data files for analysis by normalizing fields, parsing dates, removing duplicates, and handling missing values.
---
- Normalize categorical fields (e.g., region names) by stripping whitespace and applying consistent capitalization or canonical spelling.
- Parse date/time fields using robust methods; if external libraries are unavailable, implement manual parsing for expected formats.
- Convert all monetary values to a consistent unit (e.g., integer cents) to avoid floating-point errors.
- Remove duplicate records based on unique identifiers (e.g., order_id), keeping the first occurrence.
- Identify and exclude records with missing or invalid key values (e.g., amount = -999) from calculations.
- Count and report the number of duplicates removed and missing-value records for transparency.
- Write cleaned data to output files with correct headers and formats as specified.
- Ensure timestamps are converted to UTC and formatted in ISO 8601 with 'Z' suffix.
- Validate output against expected schema and rules before finalizing.