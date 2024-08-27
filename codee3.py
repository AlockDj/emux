import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QFileDialog, QMessageBox, 
    QMenuBar, QAction, QToolBar, QLineEdit, QPushButton, QStatusBar, QDockWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QDialog, QFormLayout, QSpinBox, QComboBox, QCheckBox, QTabWidget, 
    QInputDialog, QDialogButtonBox
)
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor, QTextCursor
from PyQt5.QtCore import QRegExp, Qt, QTimer
import os

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, language='python'):
        super(SyntaxHighlighter, self).__init__(parent)
        self.language = language
        self.highlightingRules = []
        self.setup_rules()

    def setup_rules(self):
        if self.language == 'python':
            self.highlight_python()
        elif self.language == 'java':
            self.highlight_java()
        # Add more languages here as needed

    def highlight_python(self):
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("blue"))
        keywords = ["if", "else", "while", "for", "return", "import", "from", "def", "class"]
        self.highlightingRules += [(QRegExp(r'\b' + keyword + r'\b'), keywordFormat) for keyword in keywords]

        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor("green"))
        self.highlightingRules.append((QRegExp(r'#.*'), commentFormat))

        stringFormat = QTextCharFormat()
        stringFormat.setForeground(QColor("red"))
        self.highlightingRules.append((QRegExp(r'".*?"'), stringFormat))
        self.highlightingRules.append((QRegExp(r"'.*?'"), stringFormat))

    def highlight_java(self):
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("blue"))
        keywords = ["if", "else", "while", "for", "return", "import", "public", "class", "static", "void"]
        self.highlightingRules += [(QRegExp(r'\b' + keyword + r'\b'), keywordFormat) for keyword in keywords]

        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor("green"))
        self.highlightingRules.append((QRegExp(r'//.*'), commentFormat))

        stringFormat = QTextCharFormat()
        stringFormat.setForeground(QColor("red"))
        self.highlightingRules.append((QRegExp(r'".*?"'), stringFormat))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Code Editor")
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.line_col_label = QLabel()
        self.status_bar.addWidget(self.line_col_label)
        self.update_status_bar()

        # Setup menu
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo_action)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo_action)
        edit_menu.addAction(redo_action)

        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste_action)
        edit_menu.addAction(paste_action)

        find_action = QAction("Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)

        replace_action = QAction("Replace", self)
        replace_action.setShortcut("Ctrl+R")
        replace_action.triggered.connect(self.show_replace_dialog)
        edit_menu.addAction(replace_action)

        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+T")
        settings_action.triggered.connect(self.show_settings_dialog)
        edit_menu.addAction(settings_action)

        theme_menu = menu_bar.addMenu("Theme")
        light_theme_action = QAction("Light Theme", self)
        light_theme_action.setShortcut("Ctrl+L")
        light_theme_action.triggered.connect(self.set_light_theme)
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("Dark Theme", self)
        dark_theme_action.setShortcut("Ctrl+D")
        dark_theme_action.triggered.connect(self.set_dark_theme)
        theme_menu.addAction(dark_theme_action)

        git_menu = menu_bar.addMenu("Git")
        init_git_action = QAction("Initialize Git Repo", self)
        init_git_action.triggered.connect(self.init_git_repo)
        git_menu.addAction(init_git_action)

        commit_action = QAction("Commit Changes", self)
        commit_action.setShortcut("Ctrl+M")
        commit_action.triggered.connect(self.commit_changes)
        git_menu.addAction(commit_action)

        status_action = QAction("Git Status", self)
        status_action.triggered.connect(self.git_status)
        git_menu.addAction(status_action)

        run_action = QAction("Run Python Script", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_python_script)
        file_menu.addAction(run_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(about_action)

        # Toolbars
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)
        toolbar.addAction(cut_action)
        toolbar.addAction(copy_action)
        toolbar.addAction(paste_action)
        toolbar.addSeparator()
        toolbar.addAction(find_action)
        toolbar.addAction(replace_action)
        toolbar.addAction(settings_action)
        toolbar.addAction(run_action)

        # Auto-Save Feature
        self.auto_save_interval = 60000  # 60 seconds
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_file)
        self.auto_save_timer.start(self.auto_save_interval)

        self.current_file = None
        self.settings = {
            'font_size': 10,
            'theme': 'light'
        }

    def get_current_editor(self):
        """Get the currently selected editor from the tabs."""
        if self.tabs.currentWidget() is not None:
            return self.tabs.currentWidget()
        return None

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_name:
            try:
                with open(file_name, "r") as file:
                    content = file.read()
                editor = QTextEdit()
                editor.setPlainText(content)
                language = self.detect_language(file_name)
                SyntaxHighlighter(editor.document(), language)
                editor.setFont(QFont("Courier New", self.settings['font_size']))
                self.tabs.addTab(editor, os.path.basename(file_name))
                self.tabs.setCurrentWidget(editor)
                self.current_file = file_name
                self.update_status_bar()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def save_file(self):
        if self.current_file:
            try:
                editor = self.get_current_editor()
                if editor is not None:
                    with open(self.current_file, "w") as file:
                        file.write(editor.toPlainText())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "All Files (*)")
        if file_name:
            try:
                editor = self.get_current_editor()
                if editor is not None:
                    with open(file_name, "w") as file:
                        file.write(editor.toPlainText())
                    self.current_file = file_name
                    self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(file_name))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def auto_save_file(self):
        if self.current_file:
            self.save_file()

    def close_tab(self, index):
        if self.tabs.count() > 0:
            self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.current_file = None

    def set_light_theme(self):
        self.set_theme("white", "black")

    def set_dark_theme(self):
        self.set_theme("black", "white")

    def set_theme(self, bg_color, text_color):
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if editor:
                editor.setStyleSheet(f"background-color: {bg_color}; color: {text_color};")
        self.status_bar.setStyleSheet(f"background-color: lightgrey; color: black;")
        self.settings['theme'] = 'light' if bg_color == 'white' else 'dark'

    def detect_language(self, file_name):
        if file_name.endswith('.py'):
            return 'python'
        elif file_name.endswith('.java'):
            return 'java'
        # Add more file extensions here
        return 'python'

    def update_status_bar(self):
        editor = self.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            column = cursor.columnNumber() + 1
            self.line_col_label.setText(f"Line: {line}, Column: {column}")

    def show_find_dialog(self):
        if self.get_current_editor() is not None:
            self.find_dialog = FindReplaceDialog(self, "Find")
            self.find_dialog.exec_()

    def show_replace_dialog(self):
        if self.get_current_editor() is not None:
            self.replace_dialog = FindReplaceDialog(self, "Replace")
            self.replace_dialog.exec_()

    def show_settings_dialog(self):
        self.settings_dialog = SettingsDialog(self, self.settings)
        if self.settings_dialog.exec_() == QDialog.Accepted:
            self.settings = self.settings_dialog.get_settings()
            for i in range(self.tabs.count()):
                editor = self.tabs.widget(i)
                if editor:
                    editor.setFont(QFont("Courier New", self.settings['font_size']))

    def run_python_script(self):
        if self.current_file and self.current_file.endswith('.py'):
            try:
                result = subprocess.run(["python", self.current_file], capture_output=True, text=True)
                QMessageBox.information(self, "Script Output", result.stdout if result.returncode == 0 else result.stderr)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to run script: {e}")
        else:
            QMessageBox.warning(self, "Error", "Open a Python file to run.")

    def init_git_repo(self):
        if not self.current_file:
            QMessageBox.warning(self, "Git Error", "No file is currently open.")
            return
        repo_dir = os.path.dirname(self.current_file)
        try:
            subprocess.run(["git", "init"], cwd=repo_dir, check=True)
            QMessageBox.information(self, "Git", "Git repository initialized.")
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "Git Error", "Failed to initialize Git repository.")

    def commit_changes(self):
        if not self.current_file:
            QMessageBox.warning(self, "Git Error", "No file is currently open.")
            return
        repo_dir = os.path.dirname(self.current_file)
        try:
            subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
            commit_message, ok = QInputDialog.getText(self, "Commit Message", "Enter commit message:")
            if ok and commit_message:
                subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_dir, check=True)
                QMessageBox.information(self, "Git", "Changes committed.")
            else:
                QMessageBox.warning(self, "Git Error", "Commit message is required.")
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "Git Error", "Failed to commit changes.")

    def git_status(self):
        if not self.current_file:
            QMessageBox.warning(self, "Git Error", "No file is currently open.")
            return
        repo_dir = os.path.dirname(self.current_file)
        try:
            status_output = subprocess.check_output(["git", "status"], cwd=repo_dir, text=True)
            QMessageBox.information(self, "Git Status", status_output)
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "Git Error", "Failed to retrieve Git status.")

    def show_about_dialog(self):
        QMessageBox.about(self, "About Code Editor", "Code Editor v1.0\n\nA simple code editor with syntax highlighting, Git integration, and more.")

    # Placeholder methods for actions
    def undo_action(self):
        editor = self.get_current_editor()
        if editor:
            editor.undo()

    def redo_action(self):
        editor = self.get_current_editor()
        if editor:
            editor.redo()

    def cut_action(self):
        editor = self.get_current_editor()
        if editor:
            editor.cut()

    def copy_action(self):
        editor = self.get_current_editor()
        if editor:
            editor.copy()

    def paste_action(self):
        editor = self.get_current_editor()
        if editor:
            editor.paste()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeEditor()
    window.show()
    sys.exit(app.exec_())
