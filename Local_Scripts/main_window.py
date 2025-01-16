import os.path

from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QMainWindow, QHBoxLayout, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QAction, QColor
import sys

# importing own classes
from Local_Scripts.GUI.toolbar import Toolbar
from Local_Scripts.GUI.sidebar import Sidebar
from Local_Scripts.Files_Handling.images_handler import ImageHandler
from Local_Scripts.Files_Handling.box_file_handler import BoxFileHandler
from Local_Scripts.GUI.rect_drawer import RectDrawer


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, rect_drawer, sidebar, toolbar):
        super().__init__(scene)
        self.rect_drawer = rect_drawer
        self.sidebar = sidebar
        self.toolbar = toolbar
        self.dragging = False
        self.is_drawing_allowed = False
        self.zoom_factor = 1.25  # Factor by which the view zooms in/out
        self.current_zoom = 1.0
        self.max_zoom_in = 10.0  # Maximum zoom-in level
        self.max_zoom_out = 0.1  # Maximum zoom-out level
        self.initial_zoom_level = 1.0

    def keyPressEvent(self, event):
        #                                              key: 16777249, ----------> Ctrl
        #                                              key: 16777248, ----------> Shift
        #                                              key: 16777251, ----------> Alt
        key_text = event.text()
        key = event.key()
        not_allowed_list = [16777249, 16777248, 16777251]
        if key not in not_allowed_list:
            self.rect_drawer.key_pressed_emitter(key_text)
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing_allowed:
            self.dragging = True  # Track that dragging has started
            self.rect_drawer.start_rect(self, self.scene(), event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.rect_drawer.update_rect(self, event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False  # Reset dragging state
            self.rect_drawer.finish_rect(self, self.scene(), event)

    def wheelEvent(self, event):
        modifier = event.modifiers()
        if modifier == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:  # wheel up zoom in
                new_zoom = self.current_zoom * self.zoom_factor
                if new_zoom <= self.max_zoom_in:
                    self.scale(self.zoom_factor, self.zoom_factor)
                    self.current_zoom = new_zoom
            else:  # wheel down zoom out
                new_zoom = self.current_zoom / self.zoom_factor
                if new_zoom >= self.max_zoom_out:
                    self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
                    self.current_zoom = new_zoom
        elif modifier == Qt.KeyboardModifier.ShiftModifier:
            scroll_amount = event.angleDelta().y()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - scroll_amount)

        else:
            super().wheelEvent(event)

    def set_initial_zoom(self):
        self.scale(self.initial_zoom_level, self.initial_zoom_level)


class MainWindow(QMainWindow):
    sg_image_loaded = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # instance
        self.image_loader = ImageHandler()
        self.box_Loader = BoxFileHandler()
        self.toolbar = Toolbar(self.image_loader)
        self.sidebar = Sidebar(self.image_loader)
        self.rect_drawer = RectDrawer()

        # variables
        self.v_width = 1100
        self.v_height = 600
        self.drawing = False
        self.sidebar_width = 0.26
        self.pixmap = None

        self.scene = QGraphicsScene(self)
        self.view = CustomGraphicsView(self.scene, self.rect_drawer, self.sidebar, self.toolbar)

        # dragging
        self.dragging = False

        self.setWindowTitle('Box Editor')
        self.setGeometry(100, 50, self.v_width, self.v_height)

        # Components
        menu = self.menuBar()
        self.file_menu = menu.addMenu("File")
        self.help_menu = menu.addMenu("Help")

        self.open_file_action = QAction('Open File', self)
        self.open_directory_action = QAction('Select Directory', self)
        self.exit_action = QAction('Exit', self)

        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addAction(self.open_directory_action)
        self.file_menu.addAction(self.exit_action)

        # connection to functions for menu
        self.open_file_action.triggered.connect(self.open_file)
        self.open_directory_action.triggered.connect(self.open_directory)
        self.exit_action.triggered.connect(self.close_application)


        # layouts
        self.main_layout = QWidget(self)
        self.main_row = QHBoxLayout()
        self.layouts = QVBoxLayout()

        self.layouts.addWidget(self.toolbar.get_toolbar())
        self.main_row.addWidget(self.sidebar)
        self.main_row.addWidget(self.view)
        self.layouts.addLayout(self.main_row)

        self.main_layout.setLayout(self.layouts)
        self.setCentralWidget(self.main_layout)

        # Other Module Connections
        self.connect_other_modules()

        # layouts sizes
        self.sidebar.setFixedWidth(int(self.v_width * self.sidebar_width))

        self.view.installEventFilter(self)
        # =====================================================================================================
        # =================================== init function ends here =========================================
        # =====================================================================================================

    def connect_other_modules(self):
        # from rect_drawer to other
        self.rect_drawer.sg_rect_updated.connect(self.sidebar.on_rect_updated)                       # ------------------> sidebar
        self.rect_drawer.sg_new_rect_placed.connect(self.sidebar.on_rect_placed)                     # ------------------> sidebar
        self.rect_drawer.sg_key_pressed.connect(self.sidebar.on_key_press)                           # ------------------> sidebar
        self.rect_drawer.sg_rect_deleted.connect(self.sidebar.handling_rect_deletion)                # ------------------> sidebar
        self.rect_drawer.sg_rect_selection_changes.connect(self.sidebar.on_rect_selection_changes)   # ------------------> sidebar

        # from box_loader to others                                                             From Box_loader
        self.box_Loader.sg_bax_file_loaded.connect(self.sidebar.update_box_cords)        # ------------------> sidebar
        self.box_Loader.sg_bax_file_loaded.connect(self.call_rect_drawer_to_draw)        # ------------------> rect_drawer

        # from toolbar to others                                                                From Toolbar
        self.toolbar.sg_save_button_clicked.connect(self.toolbar_save_btn_clicked)           # ------------------> self
        self.toolbar.sg_delete_button_clicked.connect(self.toolbar_delete_btn_clicked)       # ------------------> self
        self.toolbar.sg_insert_button_clicked.connect(self.toolbar_insert_btn_clicked)       # ------------------> self
        self.toolbar.sg_reload_button_clicked.connect(self.sidebar.reloding) 
        self.toolbar.sg_previous_button_clicked.connect(self.sidebar.toolbar_navigation_buttons_handling)   # ----> sidebar
        self.toolbar.sg_next_button_clicked.connect(self.sidebar.toolbar_navigation_buttons_handling)       # ----> sidebar
        self.toolbar.sg_previous_button_clicked.connect(self.open_image_from_list)                         # ----> Self
        self.toolbar.sg_next_button_clicked.connect(self.open_image_from_list)                             # ----> Self

        # from Sidebar to others                                                                        From Sidebar
        self.sidebar.sg_coordinates_change.connect(self.rect_drawer.update_on_cell_value_changes)  # ----------> rect_drawer
        self.sidebar.sg_selection_changes.connect(self.rect_drawer.sidebar_selection_changes)      # ----------> rect_drawer
        self.sidebar.sg_image_selection_changes.connect(self.toolbar.enable_disable_nav_buttons)   # ----------> toolbar
        self.sidebar.sg_image_selection_changes.connect(self.open_image_from_list)                 # ----------> Self
        
        # from me                                                                                 From Self
        self.sg_image_loaded.connect(self.sidebar.show_box_cords)                          # ----------> sidebar
        self.sg_image_loaded.connect(self.toolbar.image_loaded_event_from_main)            # ----------> toolbar
        
        # other connection to functions
        

    def close_application(self):
        reply = QMessageBox.question(self, 'Quit', 'Are you sure you want to exit?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            sys.exit()

    def call_rect_drawer_to_draw(self, list_of_tuples):
        self.rect_drawer.draw_new_rects_of_box_file(self.scene, list_of_tuples)

    # =========================================================================================================
    # ================================== Image Display and control ============================================
    # =========================================================================================================
    def open_file(self):
        self.pixmap = self.image_loader.open_image()
        self.sidebar.clear_everything()
        self.load_image()
        
        self.sg_image_loaded.emit('file')

    def open_directory(self):
        old_directory = self.image_loader.directory
        self.pixmap = self.image_loader.select_directory()
        if old_directory != self.image_loader.directory:
            self.sidebar.clear_everything()
        self.load_image()
        self.sg_image_loaded.emit('folder')

    def open_image_from_list(self, caller ,file_name, index):
        print(f"Signal from: {caller}, File: {file_name}, Index: {index}")
        if len(self.image_loader.list_images) > 1:
            self.pixmap = self.image_loader.open_image_from_list(file_name)
            if self.pixmap:
                self.load_image()

    def load_image(self):
        if self.pixmap and not self.pixmap.isNull():
            self.clear_everything()
            self.scene.setBackgroundBrush(QColor(Qt.GlobalColor.lightGray))
            self.scene.addPixmap(self.pixmap)
            self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.change_title()

            # loading the boxes
            _, height = self.image_loader.get_image_size()
            self.box_Loader.extract_box_list(self.image_loader.current_image_opened, height)
            self.view.set_initial_zoom()
            self.view.is_drawing_allowed = True
            self.view.current_zoom = 1.0

    def clear_everything(self):
        self.rect_drawer.clear_everything(self.scene)
        self.scene.clear()
        self.box_Loader.clear_list_of_tuples()

    # =========================================================================================================
    # ================================ Events Controller and setup ============================================
    # =========================================================================================================
    # =========================================================================================================
    # ================================== Not Decided yet  =====================================================
    # =========================================================================================================

    def change_title(self):
        title = 'Box Editor    (' + self.image_loader.current_image_base_name + ")"
        self.setWindowTitle(title)

    # =========================================================================================================
    # ================================== Re routing signals  ==================================================
    # =========================================================================================================
    def toolbar_save_btn_clicked(self, _):
        try:
            name = os.path.join(self.image_loader.directory, self.image_loader.current_image_base_name)
            name = os.path.splitext(name)[0] + '.box'
            self.sidebar.handling_the_save_button(name)
        except TypeError:
            print('Error: No file opened')
    def toolbar_delete_btn_clicked(self, _):
        self.rect_drawer.toolbar_delete_button_clicked(self.scene)

    def toolbar_insert_btn_clicked(self, _):
        self.rect_drawer.toolbar_insert_button_clicked(self.scene)