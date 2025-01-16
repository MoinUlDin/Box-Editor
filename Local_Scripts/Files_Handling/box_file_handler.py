from PyQt6.QtCore import pyqtSignal, QObject
import os


class BoxFileHandler(QObject):
    sg_bax_file_loaded = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.box_file_directory = None
        self.list_of_tuples = []

    def extract_box_list(self, file, img_height):
        if file:
            self.box_file_directory = os.path.splitext(file)[0] + '.box'
            try:
                with open(self.box_file_directory, 'r') as f:
                    for line in f:
                        line.strip()  # remove the leading or ending spaces
                        parts = line.split()  # splits the list by
                        if len(parts) == 0 or len(parts) != 6:
                            continue
                        char, x, y, width, height, _ = parts

                        yn, wn, hn = self.revert_cords(x, y, width, height, img_height)
                        self.list_of_tuples.append((char, x, yn, wn, hn))

                self.sg_bax_file_loaded.emit(self.list_of_tuples)
            except FileNotFoundError:
                print("No box file found")
        return None

    def revert_cords(self, x, y, w, h, img_height):
        y_new = img_height - int(h)
        width_new = int(w) - int(x)
        height_new = img_height - y_new - int(y)

        return y_new, width_new, height_new

    def get_list_of_tuples(self):
        return self.list_of_tuples

    def clear_list_of_tuples(self):
        self.list_of_tuples.clear()
