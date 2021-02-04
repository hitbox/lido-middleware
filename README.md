# LIDO Weight and Balance Interface Middleware

Python 3

# Structure

Run as module, this project was designed to be as flat as possible. This is an
experiment to avoid deeply nested things.

```
python -m run
```

# Process

1. Download messages
2. Extract data strings
3. Deserialize strings to data types.
4. Use data types to create LIDO message.
5. Write LIDO message string to file.
