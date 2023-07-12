import sys
import time
from pyqtconfig import ConfigManager

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, QTimer

from interface.design.Ui_MainWindow import Ui_MainWindow
from interface.camera_widget import CameraWidget


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, camera_models = [], plugins = [], dark_mode=True):
        super().__init__()
        self.setupUi(self)

        # Set geometry relative to screen
        self.screen = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        x_pos = (self.screen.width() - self.width()) // 2
        y_pos = 3 * (self.screen.height() - self.height()) // 4
        self.move(x_pos, y_pos)

        # Configure color scheme
        if dark_mode:
            self.active_color = QtGui.QColorConstants.DarkMagenta
            self.paused_color = QtGui.QColorConstants.DarkGray
            self.inactive_color = QtGui.QColorConstants.Black
        else:
            self.active_color = QtGui.QColorConstants.Green
            self.paused_color = QtGui.QColorConstants.LightGray
            self.inactive_color = QtGui.QColorConstants.DarkGray

        # Create ID look-ups for cameras, widgets, and configs
        self.cameras = {}
        self.camera_widgets = {}
        self.camera_models = camera_models
        self.populate_available_cameras()

        self.camera_configs = {id : ConfigManager() for id in self.cameras.keys()}
        self.populate_camera_properties()
        self.populate_camera_stats()

        # Create name look-ups for plugin classes and configs
        self.plugins = {p.__name__ : p for p in plugins}
        self.populate_plugin_list()

        self.plugin_configs = {p.__name__ : ConfigManager() for p in plugins}
        self.populate_plugin_settings()
        self.populate_plugin_pipeline()
        
        # Create camera widget and start pipeline 
        self.start_button.clicked.connect(self.start_camera_widgets)
        self.start_button.setStyleSheet("background-color: darkgreen; color: white; font-weight: bold")

        # Pause camera and plugin pipeline
        self.pause_button.clicked.connect(self.pause_camera_widgets)
        self.pause_button.setStyleSheet("background-color: grey; color: white; font-weight: bold")

        # Close camera, stop pipeline and delete widget
        self.stop_button.clicked.connect(self.stop_camera_widgets)
        self.stop_button.setStyleSheet("background-color: darkred; color: white; font-weight: bold")

        # Update camera stats occasionally
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_camera_stats)
        self.update_timer.start(500)


    def update_camera_stats(self):
        for row, camera in enumerate(self.cameras.values()):
            self.cam_stats.item(row, 0).setText(camera.getName())
            self.cam_stats.item(row, 1).setText(str(camera.frames_acquired))
            if hasattr(camera, "frames_dropped"):
                self.cam_stats.item(row, 2).setText(str(camera.frames_dropped))
            else:
                self.cam_stats.item(row, 2).setText("N/A")
    
    # def update_plugin_stats(self):
    #     pass

    def populate_available_cameras(self):
        self.cam_list.clear()
        self.cam_list.setItemAlignment(Qt.AlignmentFlag.AlignTop)
        self.cam_list.itemChanged.connect(self.populate_plugin_pipeline)
        self.cam_list.itemDoubleClicked["QListWidgetItem*"].connect(
            lambda item: item.setCheckState(Qt.CheckState.Checked 
                if item.checkState() == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked
            )
        )

        for camera_cls in self.camera_models:
            cam_list = camera_cls.getAvailableCameras()
            for cam in cam_list:
                # TODO: use name instead and preserve checked state
                item = QtWidgets.QListWidgetItem(cam.getName())
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked)
                self.cam_list.addItem(item)
                if cam.getName() not in self.cameras.keys():
                    self.cameras[cam.getName()] = cam
                    self.camera_widgets[cam.getName()] = None
        
        # Ensure consistent ordering throughout interface
        self.cameras = dict(sorted(self.cameras.items()))
        self.camera_widgets = dict(sorted(self.camera_widgets.items()))
    

    def populate_camera_properties(self):
        for camID, config in self.camera_configs.items():
            tab = QtWidgets.QLabel('camID')
            cls = self.cameras[camID].__class__
            tab = QtWidgets.QWidget()
            if hasattr(cls, "DEFAULT_PROPS"):
                config.set_defaults(cls.DEFAULT_PROPS)
                for key, setting in cls.DEFAULT_PROPS.items():
                    mapper = (lambda x: x, lambda x: x)
                    if isinstance(setting, bool):
                        widget = QtWidgets.QCheckBox()
                    elif isinstance(setting, str):
                        widget = QtWidgets.QLineEdit()
                    elif isinstance(setting, int):
                        widget = QtWidgets.QSpinBox()
                    elif isinstance(setting, list):
                        widget = QtWidgets.QComboBox()
                        widget.addItems(setting)
                        config.set_default(key, setting[0]) # Default to first value
                    elif isinstance(setting, dict):
                        widget = QtWidgets.QComboBox()
                        options = list(setting.keys())
                        widget.addItems(options)
                        config.set_default(key, setting[options[0]]) # Default to first value
                        mapper = setting

                    config.add_handler(key, widget, mapper)
            
            layout = make_config_layout(config)
            # layout.setSpacing(0)
            # layout.addStretch()
            layout.insertStretch(1, 1)
            tab.setLayout(layout)
            self.cam_props.addTab(tab, str(camID))


    def populate_camera_stats(self):
        self.cam_stats.setRowCount(len(self.cameras))
        for row, (name, camera)  in enumerate(self.cameras.items()):
            self.cam_stats.setItem(row, 0, QtWidgets.QTableWidgetItem(name))
            self.cam_stats.setItem(row, 1, QtWidgets.QTableWidgetItem(str(camera.frames_acquired)))

            if hasattr(camera, "frames_dropped"):
                self.cam_stats.setItem(row, 2, QtWidgets.QTableWidgetItem(str(camera.frames_dropped)))
            else:
                self.cam_stats.setItem(row, 2, QtWidgets.QTableWidgetItem("N/A"))

        self.cam_stats.resizeColumnsToContents()


    def populate_plugin_list(self):
        self.plugin_list.clear()
        self.plugin_list.setItemAlignment(Qt.AlignmentFlag.AlignTop)
        self.plugin_list.itemChanged.connect(self.populate_plugin_pipeline)
        self.plugin_list.itemDoubleClicked["QListWidgetItem*"].connect(
            lambda item: item.setCheckState(Qt.CheckState.Checked 
                if item.checkState() == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked
            )
        )

        for name in self.plugins.keys():
            item = QtWidgets.QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.plugin_list.addItem(item)

    def populate_plugin_settings(self):
        for name, config in self.plugin_configs.items():
            cls = self.plugins[name]
            tab = QtWidgets.QWidget()
            if hasattr(cls, "DEFAULT_CONFIG"):
                config.set_defaults(cls.DEFAULT_CONFIG)
                for key, value in cls.DEFAULT_CONFIG.items():
                    if isinstance(value, bool):
                        widget = QtWidgets.QCheckBox()
                    elif isinstance(value, str):
                        widget = QtWidgets.QLineEdit()
                    elif isinstance(value, int):
                        widget = QtWidgets.QSpinBox()
                    elif isinstance(value, list):
                        widget = QtWidgets.QComboBox()
                        widget.addItems(value)
                        config.set_default(key, value[0])

                    config.add_handler(key, widget)
            
            layout = make_config_layout(config)
            layout.insertStretch(1, 1)
            tab.setLayout(layout)
            self.plugin_settings.addTab(tab, name)
    

    def populate_plugin_pipeline(self):
        self.plugin_pipeline.clear()
        try: self.plugin_pipeline.disconnect() # Disconnect all signal-slots
        except Exception: pass

        self.plugin_pipeline.setRowCount(len(self.camera_widgets))
        self.plugin_pipeline.setVerticalHeaderLabels(self.camera_widgets.keys())

        self.plugin_pipeline.setColumnCount(len(self.plugins.keys()))
        self.plugin_pipeline.setHorizontalHeaderLabels(self.plugins.keys())

        checked_camera_names = [c.text() for c in get_checked_items(self.cam_list)]
        checked_plugin_names = [p.text() for p in get_checked_items(self.plugin_list)]

        for row, (camID, widget) in enumerate(self.camera_widgets.items()):
            for col, plugin_name in enumerate(self.plugins.keys()):
                item = self.plugin_pipeline.item(row, col)
                if item is None:
                    item = QtWidgets.QTableWidgetItem()
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.plugin_pipeline.setItem(row, col, item)

                if widget is not None: # Active
                    plugin_active = None
                    for plugin in widget.plugins: # Find plugin by name
                        if isinstance(plugin, self.plugins[plugin_name]):
                            plugin_active = plugin.active
                            break

                    if not widget.active:
                         item.setText("Paused")
                         item.setBackground(self.paused_color)
                    elif plugin_active == None:
                        item.setText("Inactive")
                        item.setBackground(self.inactive_color)
                    elif plugin_active:
                        item.setText("Active")
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(Qt.CheckState.Checked)
                        item.setBackground(self.active_color)
                    else:
                        item.setText("Paused")
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(Qt.CheckState.Unchecked)
                        item.setBackground(self.paused_color)
                elif camID in checked_camera_names: # Enabled
                    if plugin_name in checked_plugin_names:
                        item.setText("Enabled")
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(Qt.CheckState.Checked)
                    else:
                        item.setText("")
                        item.setBackground(self.inactive_color)
                else:
                    item.setText("")
                    item.setBackground(self.inactive_color)
        
        self.plugin_pipeline.itemChanged.connect(self.toggle_camera_plugin)
        self.plugin_pipeline.resizeColumnsToContents()


    def toggle_camera_plugin(self, item):
        camID = self.plugin_pipeline.verticalHeaderItem(item.row()).text()
        plugin_name = self.plugin_pipeline.horizontalHeaderItem(item.column()).text()

        if item.checkState() == Qt.CheckState.Checked:
            if item.text() == "Paused":
                item.setText("Active")
                item.setBackground(self.active_color)
                widget = self.camera_widgets[camID]
                for plugin in widget.plugins: # Find plugin by name
                    if isinstance(plugin, self.plugins[plugin_name]):
                        plugin.active = True
                        break
            elif item.text() == "Disabled":
                item.setText("Enabled")
                item.setData(Qt.ItemDataRole.BackgroundRole, None) # Reset to default color

        elif item.checkState() == Qt.CheckState.Unchecked:
            if item.text() == "Active":
                item.setText("Paused")
                item.setBackground(self.paused_color)
                widget = self.camera_widgets[camID]
                for plugin in widget.plugins: # Find plugin by name
                    if isinstance(plugin, self.plugins[plugin_name]):
                        plugin.active = False
                        break
            elif item.text() == "Enabled":
                item.setText("Disabled")
                item.setBackground(self.inactive_color)


    def start_camera_widgets(self):
        screen_width = self.screen.width()
        for row in range(self.plugin_pipeline.rowCount()):
            camID = self.plugin_pipeline.verticalHeaderItem(row).text()
            widget = self.camera_widgets[camID]
            if widget is None: # Create new widget
                enabled_plugins = []
                for col in range(self.plugin_pipeline.columnCount()):
                    plugin_name = self.plugin_pipeline.horizontalHeaderItem(col).text()
                    item = self.plugin_pipeline.item(row, col)
                    if item.text() == "Enabled":
                        enabled_plugins.append((self.plugins[plugin_name], self.plugin_configs[plugin_name]))
                if len(enabled_plugins) == 0:
                    # print("At least one plugin must be selected")
                    continue
                
                config = self.camera_configs[camID].as_dict()
                widget = CameraWidget(camera=self.cameras[camID], cam_config=config, plugins=enabled_plugins)
                x_pos = min(widget.width() * row, screen_width - widget.width())
                y_pos = (widget.height() // 2) * (row * widget.width() // screen_width)
                widget.move(x_pos,y_pos)
                self.camera_widgets[camID] = widget
                self.cam_list.item(row).setBackground(self.active_color)
                self.camera_widgets[camID].show()
            elif not widget.active: # Toggle paused widget to resume
                widget.active = True
                self.cam_list.item(row).setBackground(self.active_color)
                self.camera_widgets[camID].show()

        self.populate_plugin_pipeline()


    def pause_camera_widgets(self):
        for cam_item in get_checked_items(self.cam_list):
            camID = cam_item.text()
            cam_widget = self.camera_widgets[camID]
            if cam_widget is not None:
                cam_widget.active = False
                cam_item.setBackground(self.paused_color)


    def stop_camera_widgets(self):
        for cam_item in get_checked_items(self.cam_list):
            camID = cam_item.text()
            cam_widget = self.camera_widgets[camID]
            if cam_widget is not None:
                self.camera_widgets[camID] = None
                cam_widget.close_widget()
                cam_item.setData(Qt.ItemDataRole.BackgroundRole, None) # Reset to default color


    def closeEvent(self, event):
        for cam_widget in self.camera_widgets.values():
            if cam_widget is not None:
                cam_widget.close_widget()
        # Wait for threads to stop TODO: More sophisticated way to wait for threads to stop
        time.sleep(0.42)

        # Release camera-specific resources
        for cam_type in self.camera_models:
            cam_type.releaseResources()

        event.accept() # let the window close


def get_checked_items(check_list: QtWidgets.QListWidget) -> list:
    checked = []
    for idx in range(check_list.count()):
        item = check_list.item(idx)
        if item.checkState() == Qt.CheckState.Checked:
            checked.append(item)
    return checked


def make_config_layout(config, cols=2):
    """
    Generate a QHBoxLayout based on the input ConfigManager where each column is a QFormLayout
    For each row, the label is the config dict key, and the field is the config handler for that key.

    :param config: ConfigManager
    :param cols: Number of columns to use
    :return: QHBoxLayout
    """
    layout = QtWidgets.QHBoxLayout()
    forms = [QtWidgets.QFormLayout() for _ in range(cols)]
    for form in forms:
        layout.addLayout(form, 4)

    for i, key in enumerate(config.get_visible_keys()):
        f_index = i % cols
        handler = config.handlers[key]

        label = QtWidgets.QLabel(key)
        forms[f_index].addRow(label, handler)

    return layout