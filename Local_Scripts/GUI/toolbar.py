from PyQt6.QtWidgets import QWidget, QPushButton, QSizePolicy, QSpacerItem, QHBoxLayout, QSplitter
from PyQt6.QtCore import pyqtSignal, QRectF, QObject, Qt


class Toolbar(QObject):
    sg_save_button_clicked = pyqtSignal(str)
    sg_reload_button_clicked = pyqtSignal(str)
    sg_insert_button_clicked = pyqtSignal(str)
    sg_delete_button_clicked = pyqtSignal(str)
    sg_previous_button_clicked = pyqtSignal(str, str, int)
    sg_next_button_clicked = pyqtSignal(str, str, int)

    def __init__(self, image_loader):
        super().__init__()
        self.toolbar = QWidget()
        self.toolbar.setObjectName('toolbar')
        self.image_loader = image_loader
        self.list_images = None
        self.MAX_IMAGE_RANGE = None
        self.layouts = QHBoxLayout()
        self.current_index = None
        self.MAX_RANGE = 99999

        # making buttons
        self.btn_save = QPushButton('Save')
        self.btn_reload = QPushButton('Reload')
        self.btn_prvious = QPushButton('<')
        self.btn_next = QPushButton('>')
        self.btn_delete = QPushButton('Delete')
        self.btn_insert = QPushButton('Insert')

        self.set_layouts()

        self.btn_save.clicked.connect(self.save_box_file)
        self.btn_reload.clicked.connect(self.reload_button_clicked)
        self.btn_insert.clicked.connect(self.insert_button_clicked)
        self.btn_delete.clicked.connect(self.delete_button_clicked)
        
        self.btn_prvious.clicked.connect(self.previous_button_clicked)
        self.btn_next.clicked.connect(self.next_button_clicked)
        
        self.toolbar.setEnabled(False)
        

        self.toolbar.setStyleSheet("""
                QWidget#toolbar {
                border: 1px solid gray;
                }
                QWidget QSpinBox {
                margin-right: 15px;
                }
                QWidget QLabel{
                font-size: 12px;
                }
                QWidget QLineEdit{
                margin-right: 20px;
                width: 10px;
                }
        """)
        

    def set_layouts(self):
        self.layouts.addWidget(self.btn_save)
        self.layouts.addWidget(self.btn_reload)

        spacer1 = QSpacerItem(30, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.layouts.addItem(spacer1)

        self.layouts.addWidget(self.btn_insert)
        self.layouts.addWidget(self.btn_delete)

        spacer2 = QSpacerItem(30, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.layouts.addItem(spacer2)
        
        self.layouts.addWidget(self.btn_prvious)
        self.layouts.addWidget(self.btn_next)
        
        spacer3 = QSpacerItem(30, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.layouts.addItem(spacer3)

        self.toolbar.setLayout(self.layouts)


    def image_loaded_event_from_main(self, action):
        self.toolbar.setEnabled(True)
        self.btn_prvious.setEnabled(False)
        self.list_images = self.image_loader.get_image_list()
        self.current_index = 0
        self.MAX_IMAGE_RANGE = len(self.list_images) - 1

    def save_box_file(self):
        self.sg_save_button_clicked.emit('toolbar')

    def delete_button_clicked(self):
        self.sg_delete_button_clicked.emit('toolbar')

    def reload_button_clicked(self):
        self.sg_reload_button_clicked.emit('toolbar')
    
    def insert_button_clicked(self):
        self.sg_insert_button_clicked.emit('toolbar')
        
    def previous_button_clicked(self):
        if self.current_index - 1 > 0:
            self.current_index -= 1
        elif self.current_index - 1 == 0:
            self.current_index -= 1
        else:
            return
        
        file_name = self.list_images[self.current_index]
        self.sg_previous_button_clicked.emit('toolbar', file_name, self.current_index)
        self.enable_disable_nav_buttons('', '', self.current_index)
    
    def next_button_clicked(self):
        if self.current_index + 1 < self.MAX_IMAGE_RANGE:
            self.current_index += 1
        elif self.current_index + 1 == self.MAX_IMAGE_RANGE:
            self.current_index += 1
        else:
            return
        
        file_name = self.list_images[self.current_index]
        self.sg_next_button_clicked.emit('toolbar', file_name, self.current_index)
        self.enable_disable_nav_buttons('', '', self.current_index)
        
    def enable_disable_nav_buttons(self, _, name, index):
        self.current_index = index
        if self.current_index == 0:                             # staring Position
            self.btn_prvious.setEnabled(False)
            self.btn_next.setEnabled(True)
        elif self.current_index == self.MAX_IMAGE_RANGE:        # ending Position
            self.btn_next.setEnabled(False)
            self.btn_prvious.setEnabled(True)
        else:                                                   # middle Position
            self.btn_prvious.setEnabled(True)
            self.btn_next.setEnabled(True)

    def get_toolbar(self):
        return self.toolbar
