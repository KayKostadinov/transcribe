import sys
import os
import subprocess
import whisper

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTextEdit,
)
#from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

class WhisperGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setAcceptDrops(True)
        self.load_stylesheet("styles.qss")

    def load_stylesheet(self, filename):
        """Loads a QSS file and applies it to the application."""
        try:
            with open(filename, "r") as f:
                stylesheet = f.read()
                # self.setStyleSheet(stylesheet)  # Apply to the current widget
                app.setStyleSheet(stylesheet)  # Apply to the whole application
        except FileNotFoundError:
            print(f"Error: Stylesheet file '{filename}' not found.")

    def initUI(self):
        self.setWindowTitle("Transcribe")

        self.file_button = QPushButton("Select Audio File")
        self.file_button.clicked.connect(self.select_file)

        self.transcribe_button = QPushButton("Transcribe")
        self.transcribe_button.clicked.connect(self.transcribe)

        self.text_output = QTextEdit("output")
        self.text_output.setReadOnly(True)

        self.selected_files = QTextEdit("Selected files")
        self.selected_files.setReadOnly(True)

        grid = QGridLayout()
        grid.addWidget(self.file_button, 0, 0, 1, 1)
        grid.addWidget(self.transcribe_button, 0, 1, 1, 1)
        grid.addWidget(self.selected_files, 1, 0, 1, 2)
        grid.addWidget(self.text_output, 0, 2, 2, 10)

        self.setLayout(grid)

    def select_file(self):
        self.file_path, _ = QFileDialog.getOpenFileNames(
            self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.ogg *.m4a)"
        )
        self.file_names = [os.path.basename(path) for path in self.file_path]
        self.set_files()

    def set_files(self):
        for file in self.file_names:
            self.selected_files.setText(self.selected_files.toPlainText() + "\n" + file)



    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():

            event.acceptProposedAction()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                self.file_names.append(file_path)
            self.set_files()


    def transcribe(self):
        if hasattr(self, "file_path"):
            try:
                for path in self.file_path:
                    model = whisper.load_model("large")
                    result = model.transcribe(path)
                    self.text_output.setText(' '.join(result["text"]))
            except Exception as e:
                self.text_output.setText(f"Error: {e}")
        else:
            self.text_output.setText("Please select an audio file first.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhisperGUI()
    window.show()
    sys.exit(app.exec())
