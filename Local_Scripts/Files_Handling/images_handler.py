from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal
import os


class ImageHandler():
    def __init__(self):
        self.current_image_opened = None
        self.directory = None
        self.current_image_index = -1
        self.current_image_base_name = ''
        self.list_images = []

    def open_image(self):
        self.current_image_opened, _ = QFileDialog.getOpenFileName(None, 'Select Image', r'D:\New DataSet\Img',
                                                                   'Images (*.png *.jpeg *.jpg *.bmp)')
        if self.current_image_opened:
            self.list_images.clear()
            self.current_image_base_name = os.path.basename(self.current_image_opened)
            self.list_images.append(self.current_image_base_name)
            return QPixmap(self.current_image_opened)
        else:
            print('No image to load')

    def select_directory(self):
        self.directory = QFileDialog.getExistingDirectory(None, 'Select Directory', r'D:\New DataSet\Img')
        if self.directory:
            self.list_images.clear()
            self.list_images = [f for f in os.listdir(self.directory) if
                                f.lower().endswith(('.png', '.jpeg', '.jpg', '.bmp'))]
            self.current_image_index = 0

            if self.list_images:
                self.current_image_opened = os.path.join(self.directory, self.list_images[self.current_image_index])
                self.current_image_base_name = os.path.basename(self.current_image_opened)
                return QPixmap(self.current_image_opened)
            else:
                print('There is no image to open')

    def get_next_image(self):
        if self.directory and self.list_images:
            self.current_image_index += 1
            if self.current_image_index < len(self.list_images):
                self.current_image_opened = self.list_images[self.current_image_index]
                self.current_image_base_name = os.path.basename(self.current_image_opened)
                return QPixmap(self.current_image_opened)
            else:
                QMessageBox.information(None, 'Completion Message', 'There is no more images in the directory')

    def open_image_from_list(self, name):
        if name in self.list_images:
            index = self.list_images.index(name)
            self.current_image_index = index
            self.current_image_opened = os.path.join(self.directory, name)
            self.current_image_base_name = os.path.basename(self.current_image_opened)
            return QPixmap(self.current_image_opened)
        else:
            print(f'there is no file found in list with name {name}')

    def get_current_opened_image_base_name(self):
        return self.current_image_base_name

    def get_image_list(self):
        return self.list_images

    def get_image_size(self):
        img = QPixmap(self.current_image_opened)
        width = img.width()
        height = img.height()
        return width, height
