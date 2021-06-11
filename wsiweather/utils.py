def is_glob(key):
    return key.startswith('glob') and key[-1].isdigit()
