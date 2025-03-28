import sys
import os
import imageio_ffmpeg

def setup_ffmpeg_path_auto():
    try:
        ffmpeg_exe_path = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = os.path.dirname(ffmpeg_exe_path)
        print(f"Using FFmpeg from imageio-ffmpeg: {ffmpeg_exe_path}") # Debugging line
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
        print(f"Added to PATH: {ffmpeg_dir}") # Debugging line
    except ImportError:
        print("Warning: imageio-ffmpeg not installed. Cannot automatically configure FFmpeg path.", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Error configuring FFmpeg path using imageio-ffmpeg: {e}", file=sys.stderr)

setup_ffmpeg_path_auto()


import whisper

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QGridLayout,
    QTextEdit,
    QComboBox,
    QLabel,
    QLineEdit
)

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
                app.setStyleSheet(stylesheet)  
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

        grid.addWidget(self.model_label, 1, 0, 1, 1)  
        grid.addWidget(self.model_dropdown, 1, 1, 1, 2)  
        grid.addWidget(self.language_label, 2, 0, 1, 1)  
        grid.addWidget(self.language_dropdown, 2, 1, 1, 2)  

        grid.addWidget(self.output_dir_label, 3, 0, 1, 1)  
        grid.addWidget(self.output_dir_field, 3, 1, 1, 1) 
        grid.addWidget(self.output_dir_button, 3, 2, 1, 1)
        grid.addWidget(self.selected_files, 4, 0, 1, 3) 
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
        if not hasattr(self, "file_path") or not self.file_path:
             self.text_output.setText("Please select one or more audio files first.")
             return
        if not self.output_dir_field.text():
            self.text_output.setText("Please select an output directory first.")
            return

        output_dir = self.output_dir_field.text()
        os.makedirs(output_dir, exist_ok=True)

        try:
            self.transcribe_button.setEnabled(False)
            self.text_output.setText("Loading model and starting transcription...")
            QApplication.processEvents()

            model_name = self.model_dropdown.currentText()
            language_choice = self.language_dropdown.currentText()
            language_code = None 
            if language_choice == "Bulgarian":
                language_code = "bg"
            elif language_choice == "English":
                language_code = "en"

            model = whisper.load_model(model_name)

            all_transcriptions = []
            self.text_output.clear() 

            for i, path in enumerate(self.file_path):
                file_basename = os.path.basename(path)
                self.text_output.append(f"Transcribing ({i+1}/{len(self.file_path)}): {file_basename}...")
                QApplication.processEvents() 

                transcribe_options = {}
                if language_code:
                    transcribe_options['language'] = language_code

                result = model.transcribe(path, **transcribe_options)
                transcription_text = str(result["text"])
                all_transcriptions.append((path, transcription_text))

                self.text_output.append(f"Finished: {file_basename}\n---")
                QApplication.processEvents() 

                file_name_no_ext = os.path.splitext(file_basename)[0]
                output_filename = f"{file_name_no_ext}_({model_name})_{language_choice}.txt"
                output_path = os.path.join(output_dir, output_filename)
                try:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(transcription_text)
                    self.text_output.append(f"Saved transcription to: {output_path}\n---")
                except Exception as save_e:
                     self.text_output.append(f"Error saving file {output_path}: {save_e}\n---")
                QApplication.processEvents()


            combined_text = '\n\n---\n\n'.join([f"File: {os.path.basename(path)}\n\n{text}" for path, text in all_transcriptions])
            combined_file_name = f"combined_transcription_({model_name})_{language_choice}.txt"
            combined_output_path = os.path.join(output_dir, combined_file_name)
            try:
                with open(combined_output_path, "w", encoding="utf-8") as f:
                    f.write(combined_text)
                self.text_output.append(f"\nSaved combined transcription to: {combined_output_path}")
            except Exception as save_e:
                 self.text_output.append(f"\nError saving combined file {combined_output_path}: {save_e}")


        except Exception as e:
            self.text_output.append(f"\n\nError during transcription: {e}")
        finally:
            self.transcribe_button.setEnabled(True) 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhisperGUI()
    window.show()
    window.setFocus()
    sys.exit(app.exec())
