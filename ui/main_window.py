from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.entries: List[LogEntry] = []
        self.filtered_entries: List[LogEntry] = []
        self.marked_entries: set = set()
        
        self.setWindowTitle("MCServerLogAnalyser - Minecraft Server Log Analyser")
        self.setMinimumSize(1200, 800)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        self._setup_toolbar(main_layout)
        self._setup_filters(main_layout)
        self._setup_tabs(main_layout)
    
    def _setup_toolbar(self, parent_layout: QVBoxLayout):
        toolbar_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("Import Logs")
        toolbar_layout.addWidget(self.import_btn)
        
        self.clear_btn = QPushButton("Clear")
        toolbar_layout.addWidget(self.clear_btn)
        
        toolbar_layout.addStretch()
        
        parent_layout.addLayout(toolbar_layout)
    
    def _setup_filters(self, parent_layout: QVBoxLayout):
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout()
        
        level_layout = QVBoxLayout()
        level_layout.addWidget(QLabel("Log Levels:"))
        
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
        time_layout.addWidget(QLabel("Time Range:"))
        
        time_range_layout = QHBoxLayout()
        self.start_time_edit = QDateTimeEdit()
        self.start_time_edit.setCalendarPopup(True)
        self.start_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        time_range_layout.addWidget(QLabel("From:"))
        time_range_layout.addWidget(self.start_time_edit)
        
        self.end_time_edit = QDateTimeEdit()
        self.end_time_edit.setCalendarPopup(True)
        self.end_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        time_range_layout.addWidget(QLabel("To:"))
        time_range_layout.addWidget(self.end_time_edit)
        
        self.enable_time_filter = QCheckBox("Enable Time Filter")
        time_layout.addLayout(time_range_layout)
        time_layout.addWidget(self.enable_time_filter)
        
        filter_layout.addLayout(time_layout)
        
        search_layout = QVBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Enter keyword to search...")
        search_layout.addWidget(self.search_edit)
        
        self.search_btn = QPushButton("Search")
        search_layout.addWidget(self.search_btn)
        
        filter_layout.addLayout(search_layout)
        
        filter_group.setLayout(filter_layout)
        parent_layout.addWidget(filter_group)
        
        self.apply_filter_btn = QPushButton("Apply Filters")
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
        self.log_tree.setHeaderLabels(["Line", "Time", "Level", "Message"])
        self.log_tree.setColumnWidth(0, 60)
        self.log_tree.setColumnWidth(1, 120)
        self.log_tree.setColumnWidth(2, 80)
        self.log_tree.setColumnWidth(3, 600)
        
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        
        btn_layout = QHBoxLayout()
        self.mark_btn = QPushButton("Mark Selected")
        self.unmark_btn = QPushButton("Unmark Selected")
        btn_layout.addWidget(self.mark_btn)
        btn_layout.addWidget(self.unmark_btn)
        btn_layout.addStretch()
        
        log_layout.addLayout(btn_layout)
        log_layout.addWidget(self.log_tree)
        
        self.tab_widget.addTab(log_widget, "All Logs")
    
    def _setup_chat_tab(self):
        self.chat_list = QTextEdit()
        self.chat_list.setReadOnly(True)
        self.tab_widget.addTab(self.chat_list, "Chat Messages")
    
    def _setup_commands_tab(self):
        self.commands_list = QTextEdit()
        self.commands_list.setReadOnly(True)
        self.tab_widget.addTab(self.commands_list, "Player Commands")
    
    def _setup_analysis_tab(self):
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.tab_widget.addTab(self.analysis_text, "Runtime Analysis")
    
    def _setup_marked_tab(self):
        self.marked_list = QListWidget()
        self.tab_widget.addTab(self.marked_list, "Marked Entries")
    
    def _connect_signals(self):
        self.import_btn.clicked.connect(self._import_logs)
        self.clear_btn.clicked.connect(self._clear_logs)
        self.apply_filter_btn.clicked.connect(self._apply_filters)
        self.search_btn.clicked.connect(self._apply_filters)
        self.mark_btn.clicked.connect(self._mark_selected)
        self.unmark_btn.clicked.connect(self._unmark_selected)
        self.marked_list.itemDoubleClicked.connect(self._go_to_marked)
    
    def _import_logs(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setNameFilters([
            "All Files (*)",
            "Log Files (*.log)",
            "Text Files (*.txt)",
            "Zip Files (*.zip)",
            "Tar Files (*.tar *.tar.gz *.tgz *.tar.bz2 *.tbz2)"
        ])
        
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, False)
        
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
                    
                    QMessageBox.information(self, "Success", f"Imported {len(self.entries)} log entries.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to import logs: {str(e)}")
    
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
                item.setForeground(2, QBrush(QColor("red")))
            elif entry.level == LogLevel.WARN:
                item.setForeground(2, QBrush(QColor("orange")))
            
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
        
        report = []
        report.append("=== Server Runtime Analysis ===")
        report.append("")
        
        if analysis:
            report.append(f"Start Time: {analysis['start_time']}")
            report.append(f"End Time: {analysis['end_time']}")
            report.append(f"Total Duration: {analysis['duration']}")
            report.append(f"Total Entries: {analysis['total_entries']}")
            report.append("")
        
        if events:
            report.append("=== Start/Stop Events ===")
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
