def render(data):
    """
    :param data: XML as processed through pluck.fromxml and WSIWeatherSchema.load
    """
    items = []
    items.append(data['message_identifier'])
    items.append('%04d' % data['number_of_messages'])
    items.append(data['separator'])
    items.append(data['icao_originator'])
    items.append(data['weather_identifier'])
    items.append(data['time_of_observation'].strftime('%d%H%M'))
    if data['remark'] == 'ROU':
        remark = ' ' * 3
    elif data['remark'] == 'AMD':
        remark = 'AMD'
    else:
        raise NotImplementedError('remark: %r' % data['remark'])
    items.append(remark)
    items.append(data['input_office'])
    items.append(data['start_of_validity'])
    items.append(data['end_of_validity'])
    items.append(data['weather_text'])
    # end of message
    items.append('=')
    return ''.join(items)

def main(argv=None):
    """
    Convert XML to data.
    """
    import argparse
    import xml.etree.ElementTree as ET

    from . import pluck
    from . import schema

    parser = argparse.ArgumentParser()
    parser.add_argument('xmlfiles', nargs='+')
    args = parser.parse_args(argv)

    for xmlfile in args.xmlfiles:
        print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        data = pluck.fromxml(root)
        data = schema.WSIWeatherSchema().load(data)
        message = render(data)
        print(message)

if __name__ == '__main__':
    main()
