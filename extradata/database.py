import sqlalchemy as sa

def first_working_url(url_data_list):
    """
    Return the first url that connects.
    """
    for url_data in url_data_list:
        url = sa.engine.URL.create(**url_data)
        engine = sa.create_engine(url)
        try:
            with engine.connect() as connection:
                pass
            return url_data
        except Exception as e:
            pass
