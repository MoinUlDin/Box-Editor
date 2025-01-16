from PyQt6.QtWidgets import QWidget, QPushButton, QMessageBox, QListWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QHBoxLayout
from PyQt6.QtCore import pyqtSignal, QRectF
from PyQt6.QtGui import QColor
from Local_Scripts.Files_Handling.box_file_handler import BoxFileHandler


class Sidebar(QWidget):  # Inherit from QWidget or QObject
    sg_coordinates_change = pyqtSignal(str, int, QRectF)
    sg_selection_changes = pyqtSignal(str, int)
    sg_image_selection_changes = pyqtSignal(str, str, int)

    def __init__(self, image_loader):
        super().__init__()  # Call the QWidget constructor
        self.image_loader = image_loader
        self.box_file_handler = BoxFileHandler()
        self.list_image = None
        self.setObjectName('sidebar')
        self.layouts = QVBoxLayout()

        # Define buttons
        self.btn_box = QPushButton('Box Cords')
        self.btn_list = QPushButton('Image List')

        # Define widgets (both QListWidget and QTableWidget)
        self.image_list_widget = QListWidget()
        self.box_table = QTableWidget()

        # layouts
        self.tabs_row = QHBoxLayout()
        self.tabs_row.addWidget(self.btn_box)
        self.tabs_row.addWidget(self.btn_list)
        self.layouts.addLayout(self.tabs_row)

        # Add both widgets to the layout (only one will be visible at a time)
        self.layouts.addWidget(self.image_list_widget)
        self.layouts.addWidget(self.box_table)
        self.setLayout(self.layouts)

        # Initially hide the box table (show only image list)
        self.box_table.hide()

        # Apply stylesheet
        self.setStyleSheet('QWidget#sidebar {border: 1px solid gray;}')

        # Connect buttons to respective methods
        self.btn_list.clicked.connect(self.show_image_list)
        self.btn_box.clicked.connect(self.show_box_cords)
        self.box_table.cellClicked.connect(self.on_table_cell_clicked)

        self.box_table.cellChanged.connect(self.on_cell_value_changed)  # if value changes in  table

        self.image_list_widget.itemDoubleClicked.connect(self.item_in_list_doubleclicked)
        self.setEnabled(False)

    def item_in_list_doubleclicked(self, event):
        name = event.text()
        if name in self.list_image:
            index = self.list_image.index(name)
            self.sg_image_selection_changes.emit('sidebar', name, index)
    
    
    def on_cell_value_changed(self, row, col):

        if col in [1, 2, 3, 4]:
            try:
                # checking if last element is exists than other must exist.
                height_element = self.box_table.item(row, 4)
                if height_element:
                    x = int(self.box_table.item(row, 1).text())
                    y = int(self.box_table.item(row, 2).text())
                    width = int(self.box_table.item(row, 3).text())
                    height = int(self.box_table.item(row, 4).text())

                    updated_rect = QRectF(x, y, width, height)
                    self.sg_coordinates_change.emit('sidebar', row, updated_rect)

            except ValueError:
                print('Error: None integer value entered')
            except Exception:
                print('somthing went wrong in on_cell_value_changed()')

    def on_table_cell_clicked(self, row, _):
        self.sg_selection_changes.emit('sidebar', row)

    def on_rect_placed(self, caller, index, rect):
        if index == 0:
            self.box_table.setColumnCount(5)
            self.box_table.setHorizontalHeaderLabels(['Char', 'X', 'Y', 'Width', 'Height'])
            self.box_table.clearContents()
            self.resize_table_column_widht()
            
        self.box_table.insertRow(index)
        self.box_table.setItem(index, 0, QTableWidgetItem(''))  # first item is a key
        self.update_row(index, rect)

    def on_rect_updated(self, caller, index, rect):
        if caller == 'rect':
            self.box_table.blockSignals(True)
        self.update_row(index, rect)
        self.box_table.blockSignals(False)
    def update_row(self, index, rect):
        self.box_table.setItem(index, 1, QTableWidgetItem(str(int(rect.x()))))
        self.box_table.setItem(index, 2, QTableWidgetItem(str(int(rect.y()))))
        self.box_table.setItem(index, 3, QTableWidgetItem(str(int(rect.width()))))
        self.box_table.setItem(index, 4, QTableWidgetItem(str(int(rect.height()))))

    def show_image_list(self):
        self.box_table.hide()
        self.image_list_widget.show()
        if self.list_image:
            self.image_list_widget.clear()
            for image_name in self.list_image:
                self.image_list_widget.addItem(image_name)
        
        self.select_the_opened_one_in_list()

    def show_box_cords(self, action):
        self.list_image = self.image_loader.get_image_list()
        self.setEnabled(True)
        self.show_image_list()
        
        self.image_list_widget.hide()
        self.box_table.show()

    def select_the_opened_one_in_list(self):
        name = self.image_loader.get_current_opened_image_base_name()
        self.list_image = self.image_loader.get_image_list()
        
        if name in self.list_image:
            index = self.list_image.index(name)
            item = self.image_list_widget.item(index)
            if item is not None:
                item.setSelected(True)
            print(f'We have a item {item}')

    def update_box_cords(self, list_tuples, key='a'):
        if self.box_table:
            self.clear_box_table()

        try:
            if list_tuples:
                self.box_table.blockSignals(True)
                self.box_table.setColumnCount(5)
                self.box_table.setHorizontalHeaderLabels(['Char', 'X', 'Y', 'Width', 'Height'])
                self.box_table.clearContents()
                self.box_table.setRowCount(len(list_tuples))

                for i, row_data in enumerate(list_tuples):
                    for j, data in enumerate(row_data):
                        item = QTableWidgetItem(str(data))
                        self.box_table.setItem(i, j, item)

                self.resize_table_column_widht()

                self.box_table.blockSignals(False)
        except ValueError:
            print('Value Error:')
        except TypeError:
            print("Type Error")
        except MemoryError:
            print('Memory Error: ')
        except Exception:
            print('Haha you loose other type of error')

    def resize_table_column_widht(self):
        table_width = self.width()
        column_width = (table_width // 5) - 7
        for i in range(5):
            self.box_table.setColumnWidth(i, column_width)
    
    def clear_box_table(self):
        self.box_table.clearContents()
        self.box_table.setRowCount(0)

    def clear_everything(self):
        self.image_list_widget.clear()

    def on_key_press(self, caller, index, key):
        limit = self.box_table.rowCount()
        if index < limit:
            item = self.box_table.item(index, 0)
            if item is not None:
                item.setText(key)
            else:
                print('Error:')
                print(f'we got index: {index} and Key: {key} and item: {item}')

    def handling_the_save_button(self, file_name):
        rows = self.box_table.rowCount()
        for row in range(rows):
            for col in range(5):
                val = self.box_table.item(row, col).text()
                if val == '' or val == 0:
                    QMessageBox.information(None, 'Information',
                                            'Some values in table are not correct or empty. \n We can not save this to file')
                    return
        width, height = self.image_loader.get_image_size()
        self.save_table_to_box_file(file_name, height)

    def save_table_to_box_file(self, filename, image_height):
        try:
            # Open a file with the .box extension
            with open(filename, 'w') as file:
                rows = self.box_table.rowCount()

                # Iterate over all rows
                for row in range(rows):
                    # Extract the 'key', 'x', 'y', 'width', 'height' values from the table
                    key = self.box_table.item(row, 0).text()
                    x = int(self.box_table.item(row, 1).text())  # x-coordinate
                    y = int(self.box_table.item(row, 2).text())  # original y-coordinate
                    width = int(self.box_table.item(row, 3).text())  # original width
                    height = int(self.box_table.item(row, 4).text())  # original height

                    # Apply the transformation formulas
                    y_new = image_height - height - y  # Adjust y
                    height_new = image_height - y  # Adjust height
                    width_new = width + x  # Adjust width

                    # Format the data as: key x y_new width_new height_new 0
                    box_line = f"{key} {x} {y_new} {width_new} {height_new} 0"

                    # Write the formatted data to the file
                    file.write(box_line + '\n')

            print(f"Y: {y_new}, Height: {height_new}, Width: {width_new}")

        except Exception as e:
            print(f"Error saving file: {e}")

    def handling_rect_deletion(self, _, index):
        self.box_table.removeRow(index)

    def on_rect_selection_changes(self, _, index):
        self.box_table.selectRow(index)

    def reloding(self, _):
        self.box_table.selectRow(0)
        
    def toolbar_navigation_buttons_handling(self, caller, name, index):
        item = self.image_list_widget.item(index)
        item.setSelected(True)