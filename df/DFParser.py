from lxml import etree
from df.DFObject import *

class DFParser:
    @staticmethod
    def parse(xml_file):
        tree = etree.parse(xml_file)
        root = tree.getroot()

        df_name = root.attrib.get('name')
        library_version = root.attrib.get('library_version')
        supp_version = root.attrib.get('supp_version')

        # df
        model_elem = root.find('model')
        df_model = DFParser._parse_model(model_elem) if model_elem is not None else Model()
        df_obj = DF(df_name, library_version, supp_version, df_model)
        
        # layer
        for layer_elem in root.findall('a661_layer'):
            layer = DFParser._parse_layer(layer_elem)
            df_obj.add_layer(layer)
            
        return df_obj

    @staticmethod
    def _parse_model(model_elem):
        props = {}
        arrayprop = []

        for prop in model_elem.xpath('./prop'):
            name = prop.attrib.get('name')
            value = prop.attrib.get('value')
            props[name] = value
        
        for arrayprop_node in model_elem.xpath('./arrayprop'):
            for entry in arrayprop_node.xpath('./entry'):
                value = entry.attrib.get('value')
                arrayprop.append(value)
            return Model(props, arrayprop)
        return Model(props)

    @classmethod
    def _parse_layer(cls, layer_elem):
        layer_name = layer_elem.attrib.get('name')
        layer_model = None
        widgets = []

        for child in layer_elem:
            if child.tag == 'model':
                layer_model = cls._parse_model(child)
            elif child.tag == 'a661_widget':
                widget = cls._parse_widget(child)
                widgets.append(widget)

        layer = Layer(layer_name, layer_model)
        for widget in widgets:
            layer.add_widget(widget)
        return layer

    @classmethod
    def _parse_widget(cls, widget_elem):
        widget_name = widget_elem.attrib.get('name')
        widget_type = widget_elem.attrib.get('type')
        widget_model = None
        children_widgets = []

        for child in widget_elem:
            if child.tag == 'model':
                widget_model = cls._parse_model(child)
            elif child.tag == 'a661_widget':
                child_widget = cls._parse_widget(child)
                children_widgets.append(child_widget)

        widget = Widget(widget_name, widget_type, widget_model)
        widget.children = children_widgets
        return widget