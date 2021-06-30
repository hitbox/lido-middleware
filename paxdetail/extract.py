

def loadplan_from_message(message):
    """
    delegate extract to sable2, pistol2, etc.
    """
    import sable2.extract
    import pistol2.extract

    from_ = message.from_.lower()

    if from_ in ('amazon-sable@amazon-wb.com', 'avibar@dhl.com'):
        return sable2.extract.loadplan_from_message(message)

    elif from_ in ('pstl.data@atsg-inc.com', ):
        return pistol2.extract.loadplan_from_message(message)

    raise ValueError
