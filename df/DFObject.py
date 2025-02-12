class Model:
    def __init__(self, props=None, arrayprop=None):
        self.props = props or {}
        self.arrayprop = arrayprop or []
    
    def get_prop(self, name):
        return self.props.get(name)
    
    def set_prop(self, name, value):
        self.props[name] = value

    def __repr__(self):
        return f'Model({self.props})'

class Widget:
    def __init__(self, name, widget_type, model=None):
        self.name = name
        self.widget_type = widget_type
        self.model = model or Model()
        self.children = []

    def add_child(self, widget):
        self.children.append(widget)

    def __repr__(self):
        if self.widget_type == 'A661_COMBO_BOX':
            return f'Widget(name={self.name}, type={self.widget_type}, model={self.model.props},arrayprop={self.model.arrayprop})'
        return f'Widget(name={self.name}, type={self.widget_type}, model={self.model.props})'

class Layer:
    def __init__(self, name, model=None):
        self.name = name
        self.model = model or Model()
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)

    def __repr__(self):
        return f'Layer(model={self.model}, widgets={self.widgets})'
    
class DF:
    def __init__(self, name, library_version, supp_version, model=None):
        self.name = name
        self.library_version = library_version
        self.supp_version = supp_version
        self.model = model or Model()
        self.layers = []

    def add_layer(self, layer):
        self.layers.append(layer)

    def __repr__(self):
        return f'DF(library_version={self.library_version}, supp_version={self.supp_version}, model={self.model}, layers={self.layers})'
        