
from lxml import etree

widget_properties = {
    'WidgetIdent': 'ID',
    'Alignment': 'Alignment',
    'MaxNumberOfEntries': 'MaxNumberofEntries',
    'MaxStringLength': 'MaxStringLength',
    'OpeningMode': 'OpeningMode',
    'PosX': 'PosX',
    'PosY': 'PosY',
    'SelectingAreaHeight': 'SelectingAreaHeight',
    'SelectingAreaWidth': 'SelectingAreaWidth',
    'SizeX': 'SizeX',
    'SizeY': 'SizeY',
    'AutomaticFocusMotion': 'A661_AUTO_FOCUS_MOTION',
    'NextFocusedWidget': 'A661_NEXT_FOCUSED_WIDGET',
    'Enable': 'A661_ENABLE',
    'Visible': 'A661_VISIBLE',
    'NumberOfEntries': 'A661_NUMBER_OF_ENTRIES',
    'OpeningEntry': 'A661_OPENING_ENTRY',
    'SelectedEntry': 'A661_SELECTED_ENTRY',
    'StyleSet': 'A661_STYLE_SET',
}

def print_parts_info(part):
    for keys, values in part.items():  # a661_df, a661_layers, a661_widgets
        print(f'{keys}:')
        if isinstance(values, list):  # For layers or widgets (lists)
            for idx, value in enumerate(values):
                print(f'  [{idx + 1}]')
                for key, val in value.items():
                    if isinstance(val, dict):
                        print(f'    {key}:')
                        for k, v in val.items():
                            print(f'      {k} : {v}')
                    elif isinstance(val, list):
                        print(f'    {key}:')
                        for v in val:
                            print(f'      {v}')
                    else:
                        print(f'    {key} : {val}')
        else:  # For df (single dict)
            for key, val in values.items():
                if isinstance(val, dict):
                    print(f'  {key}:')
                    for k, v in val.items():
                        print(f'    {k} : {v}')
                else:
                    print(f'  {key} : {val}')
        print()


def parse_df(a661_df):
    a661_df_info = {
        'df_prop' : {},
        'model_prop': {}
    }

    # a661_df
    a661_df_info['df_prop']['name'] = a661_df.get('name')
    a661_df_info['df_prop']['library_version'] = a661_df.get('library_version')
    a661_df_info['df_prop']['supp_version'] = a661_df.get('supp_version')

    # model->prop
    model_props = a661_df.xpath('./model//prop')
    for prop in model_props:
        name = prop.get('name')
        value = prop.get('value')
        a661_df_info['model_prop'][name] = value

    return a661_df_info

def parse_layer(a661_layer):
    a661_layer_info = {
        'layer_prop' : {},
        'model_prop': {}
    }

    # a661_layer
    a661_layer_info['layer_prop']['name'] = a661_layer.get('name')

    # model->prop
    model_props = a661_layer.xpath('./model//prop')
    for prop in model_props:
        name = prop.get('name')
        value = prop.get('value')
        a661_layer_info['model_prop'][name] = value

    return a661_layer_info

def parse_widget(a661_widget):
    a661_widget_info = {
        'widget_prop' : {},
        'model_prop': {'prop': {}, 'arrayprop': {}}
    }

    # a661_widget
    a661_widget_info['widget_prop']['name'] = a661_widget.get('name')
    a661_widget_info['widget_prop']['type'] = a661_widget.get('type')

    # model->prop
    model_props = a661_widget.xpath('./model//prop')
    for prop in model_props:
        name = prop.get('name')
        value = prop.get('value')
        a661_widget_info['model_prop']['prop'][name] = value

    entry_values = a661_widget.xpath('./model//arrayprop/entry/@value')
    if entry_values is not None:
        a661_widget_info['model_prop']['arrayprop'] = entry_values

    return a661_widget_info

def parse(file_path):
    xml_root = etree.parse(file_path).getroot()

    result_dict = {
        'a661_df' : None,
        'a661_layer' : [],
        'a661_widget' : [],
    }
    # 提取 a661_df
    node_a661_df = xml_root.xpath('//a661_df')[0]
    result_dict['a661_df'] = parse_df(node_a661_df)

    # 提取 a661_layers
    nodes_a661_layers = xml_root.xpath('//a661_layer')
    for layer in nodes_a661_layers:
        result_dict['a661_layer'].append(parse_layer(layer))

    # 提取 a661_widgets
    nodes_a661_widgets = xml_root.xpath('//a661_widget')
    for widget in nodes_a661_widgets:
        result_dict['a661_widget'].append(parse_widget(widget))

    return result_dict