import re
from datetime import datetime
from typing import List
from .log_entry import LogEntry, LogLevel


class LogParser:
    TIMESTAMP_PATTERN = r'\[(\d{2}:\d{2}:\d{2})\]'
    LEVEL_PATTERN = r'\[(INFO|DEBUG|WARN|ERROR)\]'
    THREAD_PATTERN = r'\[(.*?)\]'
    
    @classmethod
    def parse_line(cls, line: str, line_number: int, date: datetime = None) -> LogEntry:
        timestamp_match = re.search(cls.TIMESTAMP_PATTERN, line)
        level_match = re.search(cls.LEVEL_PATTERN, line)
        
        timestamp = None
        if timestamp_match:
            time_str = timestamp_match.group(1)
            if date:
                timestamp = datetime.combine(date.date(), datetime.strptime(time_str, "%H:%M:%S").time())
            else:
                timestamp = datetime.strptime(time_str, "%H:%M:%S")
        
        level = LogLevel.INFO
        if level_match:
            try:
                level = LogLevel(level_match.group(1))
            except ValueError:
                pass
        
        thread = "Unknown"
        thread_matches = re.findall(cls.THREAD_PATTERN, line)
        if len(thread_matches) >= 3:
            thread = thread_matches[1]
        
        message = line.strip()
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            thread=thread,
            message=message,
            raw_line=line,
            line_number=line_number
        )
    
    @classmethod
    def parse_file(cls, content: str, date: datetime = None) -> List[LogEntry]:
        entries = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if line.strip():
                entry = cls.parse_line(line, line_num, date)
                entries.append(entry)
        
        return entries
