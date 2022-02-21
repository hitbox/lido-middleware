# LIDO Weight and Balance Interface Middleware

Python 3


# Structure

Run as module, this project was designed to be as flat as possible. This is an
experiment to avoid deeply nested things.

```
python -m run path/to/config.py
```

# Process

1. Download messages
2. Extract data strings
3. Deserialize strings to data types.
4. Use data types to create LIDO message.
5. Write LIDO message string to file.


# CHANGES

2022-02-08
Incident: 16279
Branch: dev/paxdetail/issue1
Fix some one and two-digit flights are not processing.
Solution: pad flight number to three places with zeros.
commit: 06ee2f01f3d1f7c036c7a619724dd8311c07e50b
Notes: Padding the flight numbers led to revealing a problem with pulling the
       flight number from that jammed together string, at the top of pistol
       email messages. Downloaded the pistol emails inbox and processed ever
       message with a new flight number extractor that looks for numbers
       between letters and ignores leading zeros. See schema.py:45. Also
       schema.py:31 that was an earlier attempt that  just pulls all digits and
       ignores leading zeros. The `report` module was used to generate an Excel
       file demonstrating these methods.

2022-02-07
dev/central_load_plan/handle_other_crewmembers
Branch to implement handling O(ther) type persons in the remark field, for
central_load_plan.

XXXX-XX-XX
Other branches I've completely forgotten what are for:

dev/central_load_plan/emailchanges1
dev/central_load_plan/monospace_email
dev/central_load_plan/more_readable_emails
dev/database
stage
