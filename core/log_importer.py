import os
import zipfile
import tarfile
from datetime import datetime
from pathlib import Path
from typing import List
from .log_parser import LogParser
from .log_entry import LogEntry


class LogImporter:
    @classmethod
    def import_file(cls, file_path: str) -> List[LogEntry]:
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.is_dir():
            return cls._import_directory(path)
        elif path.suffix in ['.log', '.txt']:
            return cls._import_text_file(path)
        elif path.suffix in ['.zip']:
            return cls._import_zip(path)
        elif path.suffix in ['.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2']:
            return cls._import_tar(path)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
    
    @classmethod
    def _import_directory(cls, dir_path: Path) -> List[LogEntry]:
        all_entries = []
        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.log', '.txt']:
                entries = cls._import_text_file(file_path)
                all_entries.extend(entries)
        return all_entries
    
    @classmethod
    def _import_text_file(cls, file_path: Path) -> List[LogEntry]:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        date = cls._extract_date_from_filename(file_path.name)
        return LogParser.parse_file(content, date)
    
    @classmethod
    def _import_zip(cls, zip_path: Path) -> List[LogEntry]:
        all_entries = []
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for file_info in zf.infolist():
                if not file_info.is_dir() and file_info.filename.endswith(('.log', '.txt')):
                    with zf.open(file_info.filename) as f:
                        content = f.read().decode('utf-8', errors='replace')
                    
                    date = cls._extract_date_from_filename(file_info.filename)
                    entries = LogParser.parse_file(content, date)
                    all_entries.extend(entries)
        return all_entries
    
    @classmethod
    def _import_tar(cls, tar_path: Path) -> List[LogEntry]:
        all_entries = []
        mode = 'r:*'
        with tarfile.open(tar_path, mode) as tf:
            for member in tf.getmembers():
                if member.isfile() and member.name.endswith(('.log', '.txt')):
                    f = tf.extractfile(member)
                    if f:
                        content = f.read().decode('utf-8', errors='replace')
                        date = cls._extract_date_from_filename(member.name)
                        entries = LogParser.parse_file(content, date)
                        all_entries.extend(entries)
        return all_entries
    
    @classmethod
    def _extract_date_from_filename(cls, filename: str) -> datetime:
        date_patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{2})-(\d{2})-(\d{4})',
            r'(\d{4})(\d{2})(\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    if len(match.groups()) == 3:
                        if int(match.group(1)) > 1900:
                            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                        else:
                            return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
                except ValueError:
                    pass
        
        return datetime.now()


import re
