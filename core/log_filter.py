from typing import List, Optional
from datetime import datetime
from .log_entry import LogEntry, LogLevel


class LogFilter:
    @classmethod
    def filter_by_level(cls, entries: List[LogEntry], levels: List[LogLevel]) -> List[LogEntry]:
        return [entry for entry in entries if entry.level in levels]
    
    @classmethod
    def filter_by_time_range(cls, entries: List[LogEntry], start_time: Optional[datetime], end_time: Optional[datetime]) -> List[LogEntry]:
        filtered = []
        for entry in entries:
            if entry.timestamp is None:
                continue
            
            if start_time and entry.timestamp < start_time:
                continue
            
            if end_time and entry.timestamp > end_time:
                continue
            
            filtered.append(entry)
        return filtered
    
    @classmethod
    def filter_by_keyword(cls, entries: List[LogEntry], keyword: str, case_sensitive: bool = False) -> List[LogEntry]:
        keyword = keyword.strip()
        if not keyword:
            return entries
        
        filtered = []
        for entry in entries:
            if case_sensitive:
                if keyword in entry.message:
                    filtered.append(entry)
            else:
                if keyword.lower() in entry.message.lower():
                    filtered.append(entry)
        return filtered
    
    @classmethod
    def extract_chat_messages(cls, entries: List[LogEntry]) -> List[LogEntry]:
        chat_keywords = ['<', '>', '[CHAT]', 'message']
        filtered = []
        for entry in entries:
            if any(keyword in entry.message for keyword in chat_keywords):
                filtered.append(entry)
        return filtered
    
    @classmethod
    def extract_player_commands(cls, entries: List[LogEntry]) -> List[LogEntry]:
        command_patterns = [r'issued server command:', r'Command:', r'!']
        filtered = []
        for entry in entries:
            if any(re.search(pattern, entry.message) for pattern in command_patterns):
                filtered.append(entry)
        return filtered


import re
