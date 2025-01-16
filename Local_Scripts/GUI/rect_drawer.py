from PyQt6.QtWidgets import QGraphicsRectItem, QMessageBox
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import QRectF, Qt, pyqtSignal, QObject


class RectDrawer(QObject):
    sg_new_rect_placed = pyqtSignal(str, int, QRectF)
    sg_rect_selection_changes = pyqtSignal(str, int, QRectF)
    sg_rect_updated = pyqtSignal(str, int, QRectF)
    sg_rect_deleted = pyqtSignal(str, int)
    sg_key_pressed = pyqtSignal(str, int, str)

    def __init__(self):
        super().__init__()
        self.current_rect = None
        self.drawing_allowed = False
        self.list_rect = []
        self.selected_rect = None
        self.previous_rect_index = None
        self.is_resizing_any_rect = False
        self.resizing_side = None
        self.resizing_threshold = 7
        # for detecting clicks
        self.dragging_threshold = 10
        self.click_starting_position = None
        self.click_ending_position = None

    def start_rect(self, view, scene, event):
        position = view.mapToScene(event.pos())
        self.click_starting_position = position  # for tracking if it is click or drag
        # Checking if we are resizing or not
        if self.selected_rect and self.is_near_side(position):
            self.is_resizing_any_rect = True
            return

        if not self.select_rect(position):  # this click happens outside the rect
            # check if there is any rect exist and one is selected
            if len(self.list_rect) > 0:  # which means we have one or more rects on the scene
                if self.selected_rect:
                    self.previous_rect_index = self.list_rect.index(self.selected_rect)
                    self.deselect_current_rect()
                    self.place_a_rect(scene, position)
                else:
                    QMessageBox.information(None, "Information", "You need to Select any existing rectangle before placing new one")
            else:
                self.place_a_rect(scene, position)   # this is first time we are drawing rect no rect one the scene before



    def place_a_rect(self, scene, position):
        # Start drawing a new rectangle
        self.current_rect = QGraphicsRectItem(QRectF(position, position))
        pen = QPen(QColor(255, 90, 10))  # Set pen for the new rectangle
        pen.setWidth(2)
        self.current_rect.setPen(pen)
        scene.addItem(self.current_rect)

    def update_rect(self, view, event):
        position = view.mapToScene(event.pos())
        if self.is_resizing_any_rect:
            self.resizing_selected_rect(position)
        elif self.current_rect:
            # Update the current rectangle being drawn
            top_left = self.current_rect.rect().topLeft()
            bottom_right = position
            rect = QRectF(top_left, bottom_right).normalized()
            self.current_rect.setRect(rect)

    def finish_rect(self, view, scene, event):
        self.click_ending_position = view.mapToScene(event.pos())
        drag_amount = min(abs(self.click_ending_position.x() - self.click_starting_position.x()),
                          abs(self.click_ending_position.y() - self.click_starting_position.y()))
        allowed = drag_amount >= self.dragging_threshold
        if self.current_rect and allowed:
            if len(self.list_rect) == 0:
                self.list_rect.append(self.current_rect)
                index = 0
            else:
                index = self.previous_rect_index + 1
                self.list_rect.insert(self.previous_rect_index+1, self.current_rect)
            self.selected_rect = self.current_rect
            self.current_rect = None
            self.is_resizing_any_rect = False
            message = self.selected_rect.rect()
            self.sg_new_rect_placed.emit('rect',index, message)
            self.highlight_selected_rect(index)
        else:
            self.manage_clicks(scene)
    
    def manage_clicks(self, scene):
        if not self.selected_rect:
            scene.removeItem(self.current_rect)
            self.current_rect = None
            self.selected_rect = None
        else:
            self.is_resizing_any_rect = None

    def select_rect(self, position):
        for rect_item in self.list_rect:
            if rect_item.rect().contains(position):
                if self.select_rect:
                    self.deselect_current_rect()
            
                self.selected_rect = rect_item
                index = self.list_rect.index(rect_item)
                self.highlight_selected_rect(index)
                return True
        return False

    def highlight_selected_rect(self, index):
        if self.selected_rect:
            pen = QPen(QColor(Qt.GlobalColor.blue))  # Highlight color for selected rectangle
            pen.setWidth(2)
            self.selected_rect.setPen(pen)
            message = self.selected_rect.rect()
           
            self.sg_rect_selection_changes.emit('rect',index, message)

    def deselect_current_rect(self):
        if self.selected_rect:
            pen = QPen(QColor(255, 90, 10))  # Reset pen to original color (orange)
            pen.setWidth(2)
            self.selected_rect.setPen(pen)
            self.selected_rect = None

    def is_near_side(self, position):
        if not self.selected_rect:
            return False

        rect = self.selected_rect.rect()

        # Check proximity to the sides of the rectangle
        near_left = abs(position.x() - rect.left()) < self.resizing_threshold
        near_right = abs(position.x() - rect.right()) < self.resizing_threshold
        near_top = abs(position.y() - rect.top()) < self.resizing_threshold
        near_bottom = abs(position.y() - rect.bottom()) < self.resizing_threshold

        # Detect resizing sides based on proximity
        if near_left and rect.top() <= position.y() <= rect.bottom():
            self.resizing_side = 'left'
        elif near_right and rect.top() <= position.y() <= rect.bottom():
            self.resizing_side = 'right'
        elif near_top and rect.left() <= position.x() <= rect.right():
            self.resizing_side = 'top'
        elif near_bottom and rect.left() <= position.x() <= rect.right():
            self.resizing_side = 'bottom'
        else:
            self.resizing_side = None
            return False

        return True

    def resizing_selected_rect(self, position):
        if not self.selected_rect or not self.resizing_side or self.resizing_side is None:
            return
        
        rect = self.selected_rect.rect()

        if self.resizing_side == 'right':
            rect.setRight(position.x())
        elif self.resizing_side == 'left':
            rect.setLeft(position.x())
        elif self.resizing_side == 'top':
            rect.setTop(position.y())
        elif self.resizing_side == 'bottom':
            rect.setBottom(position.y())

        self.selected_rect.setRect(rect)
        message = self.selected_rect.rect()
        
        index = self.list_rect.index(self.selected_rect)
        self.sg_rect_updated.emit('rect', index, message)
        
        
    

    def update_on_cell_value_changes(self, caller, index, rect):
        if self.selected_rect:
            rrc = self.selected_rect.rect()
            rrc.setLeft(rect.left())
            rrc.setTop(rect.top())
            rrc.setWidth(rect.width())
            rrc.setHeight(rect.height())
            self.selected_rect.setRect(rect.normalized())
            index = self.list_rect.index(self.selected_rect)
            new_rect = self.selected_rect.rect()
            # self.sg_rect_updated.emit('rect', index, new_rect)  causing recursion needs to fix somehow

    def draw_new_rects_of_box_file(self, scene, list_of_tuples):
        # Clear any existing rectangles in the scene
        self.clear_everything(scene)

        for data in list_of_tuples:
            # Extract data from tuple
            char, x, y, width, height = data
            x, y, width, height = int(x), int(y), int(width), int(height)

            # Create QRectF from x, y, width, and height
            rect = QRectF(x, y, width, height)

            # Create a new rectangle item
            rect_item = QGraphicsRectItem(rect)

            # Customize rectangle appearance (pen color and width)
            pen = QPen(QColor(255, 90, 10))  # Use orange color for new rectangles
            pen.setWidth(2)
            rect_item.setPen(pen)

            # Add the rectangle to the scene
            scene.addItem(rect_item)

            # Optionally, store the rectangle for later reference (if needed)
            self.list_rect.append(rect_item)

            # You can also emit a signal to inform that a rectangle has been drawn if required
            # self.sg_new_rect_placed.emit('rect')

    def clear_everything(self, scene):
        if self.list_rect:
            for item in self.list_rect:
                scene.removeItem(item)

            self.list_rect.clear()

    def sidebar_selection_changes(self, caller, index):
        if -1 < index < len(self.list_rect):
            if self.selected_rect:
                self.deselect_current_rect()

            if len(self.list_rect) == 0:
                print("No rect found")
                return
            
            self.selected_rect = self.list_rect[index]
            self.highlight_selected_rect(index)

    def key_pressed_emitter(self, key):
        if self.selected_rect:
            try:
                index = self.list_rect.index(self.selected_rect)
                self.sg_key_pressed.emit('rect', index, key)
            except ValueError:
                print('we can not find the index this')

    def toolbar_delete_button_clicked(self, scene):
        if self.selected_rect:
            index = self.list_rect.index(self.selected_rect)
            self.sg_rect_deleted.emit('rect', index,)
            
            csr = self.list_rect[index]
            self.list_rect.remove(csr)
            scene.removeItem(self.selected_rect)
            self.selected_rect = None
            
    def toolbar_insert_button_clicked(self, scene):
        length = len(self.list_rect)
        if self.selected_rect and length > 0:
            margin = 5
            index = self.list_rect.index(self.selected_rect)+1
            rect = self.selected_rect.rect()
            place = rect.width() + rect.x() + margin 
            rect.moveLeft(place)
            
            rect_item = QGraphicsRectItem(rect.normalized())
            scene.addItem(rect_item)
            
            self.list_rect.insert(index, rect_item)
            self.deselect_current_rect()
            self.selected_rect = rect_item
            self.sg_new_rect_placed.emit('rect', index, rect)

            self.highlight_selected_rect(index)
        else:
            x, y, width, height = 200, 200, 430, 450
            rect = QRectF(x, y, width, height)
            rect_item = QGraphicsRectItem(rect)
            pen = QPen(QColor(255, 90, 10))  # Use orange color for new rectangles
            pen.setWidth(2)
            rect_item.setPen(pen)
            
            scene.addItem(rect_item)
            
            self.list_rect.append(rect_item)
            self.select_rected = rect_item
            self.sg_new_rect_placed.emit('rect', 0, rect)
            
            self.highlight_selected_rect(0)
        
    def reset_all_verables(self):
        self.current_rect = None
        self.previous_rect_index = None
        self.is_resizing_any_rect = False
        self.resizing_side = None
        self.click_starting_position = None
        self.click_ending_position = None
        
        print('=' * 40)
        print(f'\n Resizing side is now reset. status: {self.resizing_side} \n')