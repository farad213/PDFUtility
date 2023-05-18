import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QRadioButton, QHBoxLayout, QVBoxLayout, QLabel, QWidget, \
    QPushButton, QSizePolicy, QListWidget, QListWidgetItem, QFileDialog, QMessageBox
from PyQt5.QtGui import QDropEvent, QFont
from PyQt5.QtCore import Qt
import backend


class FilePathWidget(QWidget):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.label = QLabel(file_path)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)


class DraggableListWidgetItem(QListWidgetItem):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        font = QFont()
        font.setPointSize(14)  # Set the font size
        self.setFont(font)

    def clone(self):
        return DraggableListWidgetItem(self.file_path)

    def data(self, role):
        if role == Qt.DisplayRole:
            return self.file_path
        return super().data(role)


class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)

    def dragMoveEvent(self, event):
        if ((target := self.row(self.itemAt(event.pos()))) ==
                (current := self.currentRow()) + 1 or
                (current == self.count() - 1 and target == -1)):
            event.ignore()
        else:
            super().dragMoveEvent(event)


class PDFUtility(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDFUtility")
        self.resize(600, 400)
        self.setAcceptDrops(True)

        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setAlignment(Qt.AlignTop)

        main_layout.setContentsMargins(10, 0, 10, 10)

        options = ["Convert", "Merge", "Split"]

        radio_widget = QWidget()
        radio_layout = QHBoxLayout(radio_widget)
        radio_layout.setAlignment(Qt.AlignTop)


        self.radio_buttons = []

        for option in options:
            radio_button = QRadioButton(option)
            radio_button.setObjectName("radioButton")
            radio_button.setFixedHeight(32)
            radio_layout.addWidget(radio_button)
            self.radio_buttons.append(radio_button)

        self.radio_buttons[0].setChecked(True)

        radio_layout.setContentsMargins(0, 0, 0, 10)
        # radio_layout.setSpacing(1)

        widget.setStyleSheet(open('resources/styles.css').read())

        main_layout.addWidget(radio_widget)

        self.file_list_widget = DraggableListWidget()
        main_layout.addWidget(self.file_list_widget)
        self.file_list_widget.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Expanding
        )

        empty_widget = QWidget()
        empty_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        main_layout.addWidget(empty_widget)

        go_button = QPushButton("Go")
        main_layout.addWidget(go_button, alignment=Qt.AlignCenter)
        go_button.clicked.connect(self.handleGoButtonClicked)

        self.setCentralWidget(widget)

        for radio_button in self.radio_buttons:
            radio_button.toggled.connect(self.handleRadioButtonToggled)

    def get_active_radio_button(self):
        for radio_button in self.radio_buttons:
            if radio_button.isChecked():
                return radio_button.text()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.file_list_widget.setStyleSheet("""
                        background-color: teal;
                    """)

    def dragLeaveEvent(self, event):
        self.file_list_widget.setStyleSheet("""
                background-color: rgb(92, 108, 124);
            """)

    def dropEvent(self, event: QDropEvent):
        self.file_list_widget.setStyleSheet("""
                background-color: rgb(92, 108, 124);
            """)
        file_paths = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            file_paths.append(file_path)

        file_paths = backend.get_files(file_paths)

        active_radio_button = self.get_active_radio_button()

        if active_radio_button == "Merge":
            file_paths = backend.get_pdf_files(file_paths)
        elif active_radio_button == "Convert":
            file_paths = backend.get_supported_paths(file_paths)
        elif active_radio_button == "Split":
            file_paths = backend.get_pdf_files(file_paths)

        self.file_list_widget.clear()
        for file_path in file_paths:
            list_item = DraggableListWidgetItem(file_path)
            self.file_list_widget.addItem(list_item)

    def handleRadioButtonToggled(self, checked):
        if checked:
            if self.file_list_widget.count() > 0:
                self.file_list_widget.clear()

    def get_ordered_file_paths(self):
        ordered_file_paths = []
        for i in range(self.file_list_widget.count()):
            item = self.file_list_widget.item(i)
            ordered_file_paths.append(item.file_path)
        return ordered_file_paths

    def handleGoButtonClicked(self):
        # Check if there are any paths selected
        if self.file_list_widget.count() == 0:
            QMessageBox.warning(self, "Warning", "No files selected.")
            return

        # Prompt the user to choose a destination folder
        dest_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")

        # If the user didn't select a directory, don't proceed
        if not dest_folder:
            return

        # Get the currently selected radio button
        active_radio_button = self.get_active_radio_button()
        file_paths = self.get_ordered_file_paths()

        # Decide what to do based on the selected radio button
        if active_radio_button == "Merge":
            # Call the function to merge the files
            backend.merge_pdfs(paths=file_paths, output_dir=dest_folder)
        elif active_radio_button == "Convert":
            # Call the function to convert the files
            backend.convert_to_pdf(paths=file_paths, output_dir=dest_folder)
        elif active_radio_button == "Split":
            backend.split_pdf(input_files=file_paths, output_dir=dest_folder)


def main():
    app = QApplication(sys.argv)
    utility = PDFUtility()
    utility.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
