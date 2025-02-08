from PyQt5.QtCore import Qt

A661_AUTO_FOCUS_MOTION = {
    'A661_TRUE' : True,
    'A661_FALSE' : False
}

A661_ENABLE = {
    'A661_TRUE' : True,
    'A661_FALSE' : False,
    'A661_TRUE_WITH_VALIDATION' : True
}

A661_VISIBLE = {    
    'A661_TRUE' : True,
    'A661_FALSE' : False
}

A661_ALIGNMENT = {
    'A661_CENTER' : Qt.AlignmentFlag.AlignCenter,
    'A661_LEFT' : Qt.AlignmentFlag.AlignLeft,
    'A661_RIGHT' : Qt.AlignmentFlag.AlignRight,

    'A661_TOP_LEFT' : Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
    'A661_TOP_RIGHT' : Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
    'A661_TOP_CENTER' : Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,

    'A661_BOTTOM_LEFT' : Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
    'A661_BOTTOM_RIGHT' : Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
    'A661_BOTTOM_CENTER' : Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
}

A661_WIDGET_EXTENSION = {
    'A661_CURSOR_EVENTS_EXTENSION' : {'NumEvents' : '1', 'EventIdArray' : 'A661_CURSOR_DOUBLE_CLICKED'},
    'A661_DIRECTIONAL_TABBING_EXTENSION' : {'NumDirections' : '0', 'A661_TAB_DIRECTION_WIDGET_ID_ARRAY' : [0, 0, 0]},
    'A661_FOCUS_STOP_EXTENSION' : {'A661_STOP_FORWARD' : 'A661_TRUE', 'A661_STOP_BACKWARD' : 'A661_TRUE'},
    'A661_INITIAL_FOCUS_EXTENSION' : 'A661_TRUE'
}

A661_ENTRY_VALID = {
    'A661_TRUE' : True,
    'A661_FALSE' : False
}