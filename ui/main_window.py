from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTreeWidget, QTreeWidgetItem,
    QFileDialog, QCheckBox, QLineEdit, QDateTimeEdit, QGroupBox,
    QTabWidget, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QColor, QBrush
from typing import List, Optional
from core.log_entry import LogEntry, LogLevel
from core.log_importer import LogImporter
from core.log_filter import LogFilter
from core.runtime_analyzer import RuntimeAnalyzer
from ui.translations import Translator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tr = Translator()
        self.entries: List[LogEntry] = []
        self.filtered_entries: List[LogEntry] = []
        self.marked_entries: set = set()

        self.setMinimumSize(1200, 800)

        self._setup_ui()
        self._connect_signals()
        self._retranslate()
        self._apply_stylesheet()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        self._setup_toolbar(main_layout)
        self._setup_filters(main_layout)
        self._setup_tabs(main_layout)

    def _setup_toolbar(self, parent_layout: QVBoxLayout):
        self.toolbar_widget = QWidget()
        self.toolbar_widget.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(self.toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        self.import_btn = QPushButton()
        self.import_btn.setObjectName("primary_btn")
        toolbar_layout.addWidget(self.import_btn)

        self.clear_btn = QPushButton()
        self.clear_btn.setObjectName("danger_btn")
        toolbar_layout.addWidget(self.clear_btn)

        toolbar_layout.addStretch()

        self.lang_btn = QPushButton()
        self.lang_btn.setObjectName("lang_btn")
        self.lang_btn.setFixedWidth(90)
        toolbar_layout.addWidget(self.lang_btn)

        parent_layout.addWidget(self.toolbar_widget)

    def _setup_filters(self, parent_layout: QVBoxLayout):
        self.filter_group = QGroupBox()
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(20)

        level_layout = QVBoxLayout()
        self.log_levels_label = QLabel()
        level_layout.addWidget(self.log_levels_label)

        self.info_cb = QCheckBox("INFO")
        self.info_cb.setChecked(True)
        level_layout.addWidget(self.info_cb)

        self.debug_cb = QCheckBox("DEBUG")
        self.debug_cb.setChecked(True)
        level_layout.addWidget(self.debug_cb)

        self.warn_cb = QCheckBox("WARN")
        self.warn_cb.setChecked(True)
        level_layout.addWidget(self.warn_cb)

        self.error_cb = QCheckBox("ERROR")
        self.error_cb.setChecked(True)
        level_layout.addWidget(self.error_cb)

        filter_layout.addLayout(level_layout)

        time_layout = QVBoxLayout()
        self.time_range_label = QLabel()
        time_layout.addWidget(self.time_range_label)

        time_range_layout = QHBoxLayout()
        self.start_time_edit = QDateTimeEdit()
        self.start_time_edit.setCalendarPopup(True)
        self.start_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.from_label = QLabel()
        time_range_layout.addWidget(self.from_label)
        time_range_layout.addWidget(self.start_time_edit)

        self.end_time_edit = QDateTimeEdit()
        self.end_time_edit.setCalendarPopup(True)
        self.end_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.to_label = QLabel()
        time_range_layout.addWidget(self.to_label)
        time_range_layout.addWidget(self.end_time_edit)

        self.enable_time_filter = QCheckBox()
        time_layout.addLayout(time_range_layout)
        time_layout.addWidget(self.enable_time_filter)

        filter_layout.addLayout(time_layout)

        search_layout = QVBoxLayout()
        self.search_label = QLabel()
        search_layout.addWidget(self.search_label)

        self.search_edit = QLineEdit()
        search_layout.addWidget(self.search_edit)

        self.search_btn = QPushButton()
        self.search_btn.setObjectName("search_btn")
        search_layout.addWidget(self.search_btn)

        filter_layout.addLayout(search_layout)

        self.filter_group.setLayout(filter_layout)
        parent_layout.addWidget(self.filter_group)

        self.apply_filter_btn = QPushButton()
        self.apply_filter_btn.setObjectName("apply_filter_btn")
        parent_layout.addWidget(self.apply_filter_btn)

    def _setup_tabs(self, parent_layout: QVBoxLayout):
        self.tab_widget = QTabWidget()

        self._setup_log_tab()
        self._setup_chat_tab()
        self._setup_commands_tab()
        self._setup_analysis_tab()
        self._setup_marked_tab()

        parent_layout.addWidget(self.tab_widget)

    def _setup_log_tab(self):
        self.log_tree = QTreeWidget()
        self.log_tree.setColumnCount(4)
        self.log_tree.setAlternatingRowColors(True)
        self.log_tree.setColumnWidth(0, 60)
        self.log_tree.setColumnWidth(1, 120)
        self.log_tree.setColumnWidth(2, 80)
        self.log_tree.setColumnWidth(3, 600)
        self.log_tree.setRootIsDecorated(False)

        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)

        btn_layout = QHBoxLayout()
        self.mark_btn = QPushButton()
        self.mark_btn.setObjectName("mark_btn")
        self.unmark_btn = QPushButton()
        self.unmark_btn.setObjectName("unmark_btn")
        btn_layout.addWidget(self.mark_btn)
        btn_layout.addWidget(self.unmark_btn)
        btn_layout.addStretch()

        log_layout.addLayout(btn_layout)
        log_layout.addWidget(self.log_tree)

        self.tab_widget.addTab(log_widget, "")

    def _setup_chat_tab(self):
        self.chat_list = QTextEdit()
        self.chat_list.setReadOnly(True)
        self.tab_widget.addTab(self.chat_list, "")

    def _setup_commands_tab(self):
        self.commands_list = QTextEdit()
        self.commands_list.setReadOnly(True)
        self.tab_widget.addTab(self.commands_list, "")

    def _setup_analysis_tab(self):
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.tab_widget.addTab(self.analysis_text, "")

    def _setup_marked_tab(self):
        self.marked_list = QListWidget()
        self.tab_widget.addTab(self.marked_list, "")

    def _connect_signals(self):
        self.import_btn.clicked.connect(self._import_logs)
        self.clear_btn.clicked.connect(self._clear_logs)
        self.apply_filter_btn.clicked.connect(self._apply_filters)
        self.search_btn.clicked.connect(self._apply_filters)
        self.search_edit.returnPressed.connect(self._apply_filters)
        self.mark_btn.clicked.connect(self._mark_selected)
        self.unmark_btn.clicked.connect(self._unmark_selected)
        self.marked_list.itemDoubleClicked.connect(self._go_to_marked)
        self.lang_btn.clicked.connect(self._toggle_language)

    def _toggle_language(self):
        langs = self.tr.languages
        idx = langs.index(self.tr.lang) if self.tr.lang in langs else -1
        new_lang = langs[(idx + 1) % len(langs)]
        self.tr.set_language(new_lang)
        self._retranslate()
        if self.entries:
            self._run_analysis()

    def _retranslate(self):
        tr = self.tr
        self.setWindowTitle(tr.get("window_title"))
        self.import_btn.setText(tr.get("import_logs"))
        self.clear_btn.setText(tr.get("clear"))
        self.lang_btn.setText("English" if tr.lang == "zh" else "中文")

        self.filter_group.setTitle(tr.get("filters"))
        self.log_levels_label.setText(tr.get("log_levels"))
        self.time_range_label.setText(tr.get("time_range"))
        self.from_label.setText(tr.get("from_label"))
        self.to_label.setText(tr.get("to_label"))
        self.enable_time_filter.setText(tr.get("enable_time_filter"))
        self.search_label.setText(tr.get("search_label"))
        self.search_edit.setPlaceholderText(tr.get("search_placeholder"))
        self.search_btn.setText(tr.get("search"))
        self.apply_filter_btn.setText(tr.get("apply_filters"))

        self.tab_widget.setTabText(0, tr.get("all_logs"))
        self.tab_widget.setTabText(1, tr.get("chat_messages"))
        self.tab_widget.setTabText(2, tr.get("player_commands"))
        self.tab_widget.setTabText(3, tr.get("runtime_analysis"))
        self.tab_widget.setTabText(4, tr.get("marked_entries"))

        self.mark_btn.setText(tr.get("mark_selected"))
        self.unmark_btn.setText(tr.get("unmark_selected"))

        self.log_tree.setHeaderLabels([
            tr.get("col_line"),
            tr.get("col_time"),
            tr.get("col_level"),
            tr.get("col_message"),
        ])

        self.info_cb.setText(tr.get("level_info"))
        self.debug_cb.setText(tr.get("level_debug"))
        self.warn_cb.setText(tr.get("level_warn"))
        self.error_cb.setText(tr.get("level_error"))

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #eef1f5;
            }
            QWidget#toolbar {
                background-color: transparent;
            }
            QPushButton {
                padding: 7px 18px;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                min-height: 22px;
                font-weight: 500;
            }
            QPushButton#primary_btn {
                background-color: #1976D2;
                color: white;
            }
            QPushButton#primary_btn:hover {
                background-color: #1565C0;
            }
            QPushButton#primary_btn:pressed {
                background-color: #0D47A1;
            }
            QPushButton#danger_btn {
                background-color: #D32F2F;
                color: white;
            }
            QPushButton#danger_btn:hover {
                background-color: #C62828;
            }
            QPushButton#danger_btn:pressed {
                background-color: #B71C1C;
            }
            QPushButton#lang_btn {
                background-color: #455A64;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#lang_btn:hover {
                background-color: #37474F;
            }
            QPushButton#search_btn {
                background-color: #546E7A;
                color: white;
            }
            QPushButton#search_btn:hover {
                background-color: #455A64;
            }
            QPushButton#apply_filter_btn {
                background-color: #388E3C;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 18px;
                min-height: 24px;
            }
            QPushButton#apply_filter_btn:hover {
                background-color: #2E7D32;
            }
            QPushButton#apply_filter_btn:pressed {
                background-color: #1B5E20;
            }
            QPushButton#mark_btn {
                background-color: #F9A825;
                color: white;
            }
            QPushButton#mark_btn:hover {
                background-color: #F57F17;
            }
            QPushButton#unmark_btn {
                background-color: #78909C;
                color: white;
            }
            QPushButton#unmark_btn:hover {
                background-color: #607D8B;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #CFD8DC;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 14px;
                padding-bottom: 6px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #37474F;
            }
            QTreeWidget {
                border: 1px solid #CFD8DC;
                border-radius: 6px;
                background-color: #ffffff;
                alternate-background-color: #F5F7FA;
                selection-background-color: #BBDEFB;
                selection-color: #212121;
                outline: none;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 4px 0px;
            }
            QTreeWidget::item:hover {
                background-color: #E3F2FD;
            }
            QHeaderView::section {
                background-color: #ECEFF1;
                color: #37474F;
                padding: 6px 8px;
                border: none;
                border-bottom: 2px solid #B0BEC5;
                font-weight: bold;
                font-size: 12px;
            }
            QTabWidget::pane {
                border: 1px solid #CFD8DC;
                border-radius: 6px;
                background-color: #ffffff;
                top: -1px;
            }
            QTabBar::tab {
                padding: 8px 18px;
                margin-right: 3px;
                background-color: #ECEFF1;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-size: 13px;
                color: #546E7A;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #1976D2;
                font-weight: bold;
                border-bottom: 2px solid #1976D2;
            }
            QTabBar::tab:hover:!selected {
                background-color: #E3F2FD;
            }
            QLineEdit, QDateTimeEdit {
                border: 1px solid #CFD8DC;
                border-radius: 5px;
                padding: 6px 10px;
                background-color: #ffffff;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus, QDateTimeEdit:focus {
                border-color: #1976D2;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 13px;
                min-height: 24px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #B0BEC5;
            }
            QCheckBox::indicator:checked {
                background-color: #1976D2;
                border-color: #1976D2;
            }
            QTextEdit {
                border: 1px solid #CFD8DC;
                border-radius: 6px;
                background-color: #ffffff;
                font-size: 13px;
                padding: 6px;
            }
            QListWidget {
                border: 1px solid #CFD8DC;
                border-radius: 6px;
                background-color: #ffffff;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item:hover {
                background-color: #E3F2FD;
            }
            QListWidget::item:selected {
                background-color: #BBDEFB;
                color: #212121;
            }
        """)

    def _import_logs(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, False)
        dialog.setNameFilters([
            "All Files (*)",
            "Log Files (*.log)",
            "Text Files (*.txt)",
            "Zip Files (*.zip)",
            "Tar Files (*.tar *.tar.gz *.tgz *.tar.bz2 *.tbz2)"
        ])

        if dialog.exec():
            selected_files = dialog.selectedFiles()
            if selected_files:
                try:
                    all_entries = []
                    for file_path in selected_files:
                        entries = LogImporter.import_file(file_path)
                        all_entries.extend(entries)

                    self.entries = all_entries
                    self.filtered_entries = all_entries.copy()

                    if self.entries:
                        first_time = self.entries[0].timestamp
                        last_time = self.entries[-1].timestamp

                        if first_time:
                            self.start_time_edit.setDateTime(QDateTime(first_time))
                        if last_time:
                            self.end_time_edit.setDateTime(QDateTime(last_time))

                    self._populate_log_tree()
                    self._extract_content()
                    self._run_analysis()

                    QMessageBox.information(
                        self,
                        self.tr.get("success_title"),
                        self.tr.get("imported_msg").format(len(self.entries))
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        self.tr.get("error_title"),
                        self.tr.get("failed_import_msg").format(str(e))
                    )

    def _clear_logs(self):
        self.entries = []
        self.filtered_entries = []
        self.marked_entries = set()
        self.log_tree.clear()
        self.chat_list.clear()
        self.commands_list.clear()
        self.analysis_text.clear()
        self.marked_list.clear()

    def _apply_filters(self):
        if not self.entries:
            return

        filtered = self.entries.copy()

        selected_levels = []
        if self.info_cb.isChecked():
            selected_levels.append(LogLevel.INFO)
        if self.debug_cb.isChecked():
            selected_levels.append(LogLevel.DEBUG)
        if self.warn_cb.isChecked():
            selected_levels.append(LogLevel.WARN)
        if self.error_cb.isChecked():
            selected_levels.append(LogLevel.ERROR)

        filtered = LogFilter.filter_by_level(filtered, selected_levels)

        if self.enable_time_filter.isChecked():
            start_dt = self.start_time_edit.dateTime().toPyDateTime()
            end_dt = self.end_time_edit.dateTime().toPyDateTime()
            filtered = LogFilter.filter_by_time_range(filtered, start_dt, end_dt)

        keyword = self.search_edit.text()
        if keyword:
            filtered = LogFilter.filter_by_keyword(filtered, keyword)

        self.filtered_entries = filtered
        self._populate_log_tree()

    def _populate_log_tree(self):
        self.log_tree.clear()

        for entry in self.filtered_entries:
            item = QTreeWidgetItem()
            item.setText(0, str(entry.line_number))
            item.setText(1, entry.timestamp.strftime("%H:%M:%S") if entry.timestamp else "")
            item.setText(2, entry.level.value)
            item.setText(3, entry.message)

            if entry.level == LogLevel.ERROR:
                item.setForeground(2, QBrush(QColor("#D32F2F")))
            elif entry.level == LogLevel.WARN:
                item.setForeground(2, QBrush(QColor("#F57C00")))

            if entry.line_number in self.marked_entries:
                item.setBackground(0, QBrush(QColor(255, 255, 200)))

            item.setData(0, Qt.ItemDataRole.UserRole, entry)
            self.log_tree.addTopLevelItem(item)

    def _extract_content(self):
        if not self.entries:
            return

        chat_entries = LogFilter.extract_chat_messages(self.entries)
        self.chat_list.clear()
        for entry in chat_entries:
            self.chat_list.append(entry.message)

        command_entries = LogFilter.extract_player_commands(self.entries)
        self.commands_list.clear()
        for entry in command_entries:
            self.commands_list.append(entry.message)

    def _run_analysis(self):
        if not self.entries:
            return

        analysis = RuntimeAnalyzer.analyze_uptime(self.entries)
        events = RuntimeAnalyzer.find_start_stop_events(self.entries)

        tr = self.tr
        report = []
        report.append(tr.get("analysis_header"))
        report.append("")

        if analysis:
            report.append(tr.get("start_time").format(analysis["start_time"]))
            report.append(tr.get("end_time").format(analysis["end_time"]))
            report.append(tr.get("total_duration").format(analysis["duration"]))
            report.append(tr.get("total_entries").format(analysis["total_entries"]))
            report.append("")

        if events:
            report.append(tr.get("events_header"))
            for time, event_type in events:
                report.append(f"{time} - {event_type}")

        self.analysis_text.setText("\n".join(report))

    def _mark_selected(self):
        for item in self.log_tree.selectedItems():
            entry = item.data(0, Qt.ItemDataRole.UserRole)
            if entry:
                self.marked_entries.add(entry.line_number)
                item.setBackground(0, QBrush(QColor(255, 255, 200)))

                marked_item = QListWidgetItem(f"{entry.line_number}: {entry.message}")
                marked_item.setData(Qt.ItemDataRole.UserRole, entry)
                self.marked_list.addItem(marked_item)

    def _unmark_selected(self):
        for item in self.log_tree.selectedItems():
            entry = item.data(0, Qt.ItemDataRole.UserRole)
            if entry and entry.line_number in self.marked_entries:
                self.marked_entries.remove(entry.line_number)
                item.setBackground(0, QBrush())

                for i in range(self.marked_list.count()):
                    list_item = self.marked_list.item(i)
                    list_entry = list_item.data(Qt.ItemDataRole.UserRole)
                    if list_entry and list_entry.line_number == entry.line_number:
                        self.marked_list.takeItem(i)
                        break

    def _go_to_marked(self, item: QListWidgetItem):
        entry = item.data(Qt.ItemDataRole.UserRole)
        if entry:
            self.tab_widget.setCurrentIndex(0)

            for i in range(self.log_tree.topLevelItemCount()):
                tree_item = self.log_tree.topLevelItem(i)
                tree_entry = tree_item.data(0, Qt.ItemDataRole.UserRole)
                if tree_entry and tree_entry.line_number == entry.line_number:
                    self.log_tree.setCurrentItem(tree_item)
                    self.log_tree.scrollToItem(tree_item)
                    break
