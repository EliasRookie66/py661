from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QMenu

class A661TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 安装事件过滤器到 TabBar
        self.tabBar().installEventFilter(self)

    def eventFilter(self, source, event):
        if source == self.tabBar() and event.type() == event.MouseButtonPress:
            if event.button() == Qt.RightButton:
                # 获取鼠标位置并确定点击的 tab 索引
                tab_index = self.tabBar().tabAt(event.pos())
                if tab_index != -1:
                    self.showContextMenu(event.pos(), tab_index)
        return super().eventFilter(source, event)

    def showContextMenu(self, pos, tab_index):
        """显示右键菜单"""
        menu = QMenu(self)
        open_in_server_action = menu.addAction("Open In Server")
        menu.addSeparator()
        create_UACDS_interface_action = menu.addAction("Create UACDS Interface")
        open_UACDS_interface_action = menu.addAction("Open UACDS Interface")
        menu.addSeparator()
        refresh_action = menu.addAction("Refresh")
        close_action = menu.addAction("Close Tab")
        close_all_action = menu.addAction("Close All Tabs")
        close_other_action = menu.addAction("Close Other")
        close_other_action.setEnabled(False)

        # 显示菜单并捕获用户选择的动作
        action = menu.exec_(self.mapToGlobal(pos))
        if action == open_in_server_action:
            print('open_in_server_action is triggered')
        elif action == create_UACDS_interface_action:
            print('create_UACDS_interface_action is triggered')
        elif action == open_UACDS_interface_action:
            print('open_UACDS_interface_action is triggered')
        elif action == refresh_action:
            print('refresh_action is triggered')
        elif action == close_action:
            print('close_action is triggered')
            self.removeTab(tab_index)
        elif action == close_all_action:
            print('close_all_action is triggered')
            self.clear()
        elif action == close_other_action:
            print('close_other_action is triggered')
            for i in range(self.count() - 1, -1, -1):
                if i != tab_index:
                    self.removeTab(i)
