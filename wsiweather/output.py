from pathlib import Path

def get_output_path(data, output_format):
    check_until_unique = ''
    while True:
        output_path = output_format.format(check_until_unique=check_until_unique, **data)
        output_path = Path(output_path)
        if not output_path.exists():
            break
        try:
            check_until_unique = '.' + str(int(check_until_unique.lstrip('.')) + 1)
        except ValueError:
            check_until_unique = '.0'
    return output_path
