import sable2.extract
import pistol2.extract

class Extract:
    """
    Handle extracting data from message for sable or pistol via from address.
    Depending on the from-address, we route to the loadplan extractor.
    """

    def __init__(self, sable_from, pistol_from):
        self.sable_from = sable_from
        self.pistol_from = pistol_from

    def __call__(self, message):
        """
        delegate extract to sable2, pistol2, etc.
        """
        from_ = message.from_.lower()

        if from_ in self.sable_from:
            return sable2.extract.loadplan_from_message(message)

        elif from_ in self.pistol_from:
            return pistol2.extract.loadplan_from_message(message)

        raise ValueError
