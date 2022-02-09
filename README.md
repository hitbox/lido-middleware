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


# NOTES

* The `sable` directory is unused. It was created before it was known what the
  source for it would be. The initial sources were found deficient. An
  alternative was found and the `amazon_lsh` directory was created to extract
  and parse this new source.


# Sable: Amazon LSH / LDM

The directory `sable` was the original, intended Sable to LIDO middleware. The
`amazon_lsh` directory is another implementation that lacks a few things. And,
most recently, `sablev2` is intended as the full implementation.


# CHANGES

2022-02-08
dev/paxdetail/issue1
Fix some one and two-digit flights are not processing.
Solution: pad flight number to three places with zeros.
commit: 06ee2f01f3d1f7c036c7a619724dd8311c07e50b

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
