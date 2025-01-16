from PyQt6.QtWidgets import QFrame, QLabel
class myFrame:
    def __init__(self) -> None:
        self.frame = QFrame()
        
        
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setLineWidth(2)
        self.frame.setStyleSheet('background-color: lightblue;')

    def get_frame(self):
        return self.frame