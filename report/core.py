import pickle
import tempfile

import openpyxl

import utils

def report(config):
    """
    Generate Excel report and open in temp file.
    """
    # read messages
    with open(config.source_pickle, 'rb') as pickle_file:
        messages = pickle.load(pickle_file)
    # filter messages
    messages = (msg for msg in messages if eval(config.message_filter))
    # extract text values
    textdata = map(utils.printexcept(config.extractor), messages)
    # ignore some data
    textdata = (textdict for textdict in textdata if textdict and not eval(config.ignore))
    # unique by key
    textdata = {textdict[config.unique_key]: textdict for textdict in textdata}
    # back to list
    textdata = list(textdata.values())

    # add the flight number data from processing
    for textdict in textdata:
        args = [textdict[key] for key in config.update_from_args]
        data = config.update_from(*args)
        textdict.update(data)

    # create and open Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(config.outputfields)
    for textdict in textdata:
        ws.append([textdict[key] for key in config.outputfields])

    # open in default app
    with tempfile.NamedTemporaryFile(suffix='.xlsx') as file:
        wb.save(file.name)
        utils.startfile(file.name)
