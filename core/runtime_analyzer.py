from typing import List, Tuple
from datetime import datetime, timedelta
from .log_entry import LogEntry


class RuntimeAnalyzer:
    @classmethod
    def analyze_uptime(cls, entries: List[LogEntry]) -> dict:
        if not entries:
            return {}
        
        valid_entries = [e for e in entries if e.timestamp is not None]
        if not valid_entries:
            return {}
        
        sorted_entries = sorted(valid_entries, key=lambda x: x.timestamp)
        
        start_time = sorted_entries[0].timestamp
        end_time = sorted_entries[-1].timestamp
        duration = end_time - start_time
        
        return {
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'total_entries': len(valid_entries)
        }
    
    @classmethod
    def find_start_stop_events(cls, entries: List[LogEntry]) -> List[Tuple[datetime, str]]:
        events = []
        
        start_keywords = ['Starting minecraft server', 'Starting server', 'Done']
        stop_keywords = ['Stopping server', 'Server stopped', 'Shutting down']
        
        for entry in entries:
            if entry.timestamp is None:
                continue
            
            message = entry.message.lower()
            
            for keyword in start_keywords:
                if keyword.lower() in message:
                    events.append((entry.timestamp, 'START'))
                    break
            
            for keyword in stop_keywords:
                if keyword.lower() in message:
                    events.append((entry.timestamp, 'STOP'))
                    break
        
        return sorted(events, key=lambda x: x[0])
