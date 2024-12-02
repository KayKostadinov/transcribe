import sys
import os
# import subprocess
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
    QComboBox,
    QLabel,
    QLineEdit
    # QGraphicsSceneDragDropEvent
)
#from PyQt6.QtCore import Qt, QMimeData
# from PyQt6.QtGui import QDragEnterEvent, QDropEvent

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

        self.file_button = QPushButton("Select Audio Files")
        self.file_button.clicked.connect(self.select_file)

        self.transcribe_button = QPushButton("Transcribe")
        self.transcribe_button.clicked.connect(self.transcribe)

        self.text_output = QTextEdit("output")
        self.text_output.setReadOnly(True)

        self.selected_files = QTextEdit("Selected files")
        self.selected_files.setReadOnly(True)

        self.model_dropdown = QComboBox(self)
        self.model_dropdown.addItem("large")
        self.model_dropdown.addItem("medium")
        self.model_dropdown.addItem("base")
        self.model_dropdown.addItem("small")
        self.model_dropdown.addItem("tiny")

        self.model_label = QLabel("Select Model:", self)


        self.language_dropdown = QComboBox(self)
        self.language_dropdown.addItem("Bulgarian")
        self.language_dropdown.addItem("English")
        self.language_dropdown.addItem("auto detect")

        self.language_label = QLabel("Select Language:", self)


        self.output_dir_label = QLabel("Output Directory:", self)
        self.output_dir_field = QLineEdit(self)
        self.output_dir_button = QPushButton("Browse", self)
        self.output_dir_button.clicked.connect(self.select_output_dir)

        grid = QGridLayout()
        grid.addWidget(self.file_button, 0, 0, 1, 1)
        grid.addWidget(self.transcribe_button, 0, 1, 1, 2)

        grid.addWidget(self.model_label, 1, 0, 1, 1)  # Add the dropdown to the grid
        grid.addWidget(self.model_dropdown, 1, 1, 1, 2)  # Add the dropdown to the grid
        grid.addWidget(self.language_label, 2, 0, 1, 1)  # Add the dropdown to the grid
        grid.addWidget(self.language_dropdown, 2, 1, 1, 2)  # Add the dropdown to the grid

        grid.addWidget(self.output_dir_label, 3, 0, 1, 1)  # Add output dir label
        grid.addWidget(self.output_dir_field, 3, 1, 1, 1)  # Add output dir field
        grid.addWidget(self.output_dir_button, 3, 2, 1, 1)  # Add output dir button
        grid.addWidget(self.selected_files, 4, 0, 1, 3)  # Adjust row index for selected_files
        grid.addWidget(self.text_output, 0, 3, 5, 10)
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

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir_field.setText(dir_path)

    # def dragenterevent(self, event):
    #     if event.mimedata().hasurls():
    #         self.text_output.setText('here')
    #         event.acceptProposedAction()

    # def dropEvent(self, event):
    #     self.text_output.setText('here')
        # [self.text_output.setText(x.toLocalFile()) for x in event.mimeData().urls()]
        # if event.mimeData().hasUrls():

        #     event.acceptProposedAction()
        #     for url in event.mimeData().urls():
        #         self.text_output.setText(url.toLocalFile())
        #         file_path = url.toLocalFile()
        #         self.file_names.append(file_path)
        #     self.set_files()


    def transcribe(self):
        if hasattr(self, "file_path"):
            try:
                all_transcriptions = []
                for path in self.file_path:
                    model_name = self.model_dropdown.currentText()
                    model = whisper.load_model(model_name)
                    result = model.transcribe(path)
                    all_transcriptions.append(result["text"])

                    output_dir = self.output_dir_field.text()
                    if output_dir:
                        file_name = os.path.splitext(os.path.basename(path))[0] + ".txt"
                        output_path = os.path.join(output_dir, file_name)
                        with open(output_path, "w") as f:
                            f.write(''.join(result["text"]))

                    self.text_output.setText(''.join(result["text"]))

                combined_text = '\n'.join([f"{os.path.basename(path)}:\n{''.join(text)}" for path, text in zip(self.file_path, all_transcriptions)])

                output_dir = self.output_dir_field.text()
                if output_dir:
                    combined_file_name = "combined_transcription.txt"  # Choose a filename
                    combined_output_path = os.path.join(output_dir, combined_file_name)
                    with open(combined_output_path, "w") as f:
                        f.write(combined_text)
            except Exception as e:
                self.text_output.setText(f"Error: {e}")
        else:
            self.text_output.setText("Please select an audio file first.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhisperGUI()
    window.show()
    window.setFocus()
    sys.exit(app.exec())
