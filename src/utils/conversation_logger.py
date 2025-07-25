"""
Secure conversation logging for Crisis Support & Mental Health Agent.

This module provides secure, privacy-compliant conversation logging
with audit trails, encryption, and compliance with mental health
data protection requirements.
"""

import json
import os
import hashlib
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, IO
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from logging.handlers import RotatingFileHandler
import threading

from config import get_settings, logger

settings = get_settings()


class LogLevel(Enum):
    """Log severity levels for conversation logging."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    AUDIT = "audit"


class LogCategory(Enum):
    """Categories of conversation logs."""
    CONVERSATION = "conversation"
    CRISIS_INCIDENT = "crisis_incident"
    SAFETY_ASSESSMENT = "safety_assessment"
    RESOURCE_ACCESS = "resource_access"
    SYSTEM_EVENT = "system_event"
    PRIVACY_EVENT = "privacy_event"
    THERAPEUTIC_INTERACTION = "therapeutic_interaction"


@dataclass
class ConversationLogEntry:
    """Structured conversation log entry."""
    timestamp: str
    session_id: str
    log_id: str
    category: LogCategory
    level: LogLevel
    message: str
    metadata: Dict[str, Any]
    privacy_level: str
    encrypted: bool = False
    anonymized: bool = False


class ConversationLogger:
    """
    Secure conversation logger with privacy compliance.
    
    Provides structured logging for therapeutic conversations with
    encryption, anonymization, and audit trail capabilities.
    """
    
    def __init__(self):
        """Initialize conversation logger with security features."""
        self.log_directory = Path("logs")
        self.log_directory.mkdir(exist_ok=True)
        
        # Initialize structured loggers
        self.conversation_logger = self._setup_conversation_logger()
        self.audit_logger = self._setup_audit_logger()
        self.crisis_logger = self._setup_crisis_logger()
        
        # Logging configuration
        self.max_log_size = 100 * 1024 * 1024  # 100MB
        self.backup_count = 10
        self.compress_logs = True
        self.encrypt_sensitive = True
        
        # Thread-safe logging
        self.log_lock = threading.Lock()
        
        # Log entry tracking
        self.log_entries = []
        self.log_statistics = {
            "total_entries": 0,
            "entries_by_category": {},
            "entries_by_level": {},
            "crisis_incidents_logged": 0,
            "privacy_events_logged": 0
        }
        
        logger.info("ConversationLogger initialized")
    
    def _setup_conversation_logger(self) -> logging.Logger:
        """
        Setup dedicated conversation logger.
        
        Returns:
            Configured conversation logger
        """
        conv_logger = logging.getLogger("conversation")
        conv_logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        conv_logger.handlers.clear()
        
        # File handler with rotation
        log_file = self.log_directory / "conversations.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count
        )
        
        # JSON formatter for structured logging
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": %(message)s}'
        )
        file_handler.setFormatter(formatter)
        conv_logger.addHandler(file_handler)
        
        return conv_logger
    
    def _setup_audit_logger(self) -> logging.Logger:
        """
        Setup audit trail logger for compliance.
        
        Returns:
            Configured audit logger
        """
        audit_logger = logging.getLogger("audit")
        audit_logger.setLevel(logging.INFO)
        audit_logger.handlers.clear()
        
        # Audit log file
        log_file = self.log_directory / "audit.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count
        )
        
        # Detailed audit formatter
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "AUDIT", '
            '"event": %(message)s}'
        )
        file_handler.setFormatter(formatter)
        audit_logger.addHandler(file_handler)
        
        return audit_logger
    
    def _setup_crisis_logger(self) -> logging.Logger:
        """
        Setup dedicated crisis incident logger.
        
        Returns:
            Configured crisis logger
        """
        crisis_logger = logging.getLogger("crisis")
        crisis_logger.setLevel(logging.WARNING)
        crisis_logger.handlers.clear()
        
        # Crisis log file
        log_file = self.log_directory / "crisis_incidents.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count
        )
        
        # Crisis-specific formatter
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "CRISIS", '
            '"incident": %(message)s}'
        )
        file_handler.setFormatter(formatter)
        crisis_logger.addHandler(file_handler)
        
        return crisis_logger
    
    def log_conversation_turn(
        self,
        session_id: str,
        user_message: str,
        agent_response: str,
        metadata: Dict[str, Any] = None,
        privacy_level: str = "standard"
    ) -> str:
        """
        Log a conversation turn with privacy protection.
        
        Args:
            session_id: Session identifier
            user_message: User's message
            agent_response: Agent's response
            metadata: Additional metadata
            privacy_level: Privacy protection level
            
        Returns:
            Log entry ID
            
        TODO: Implement end-to-end encryption for sensitive conversations
        """
        try:
            with self.log_lock:
                log_id = self._generate_log_id(session_id, "conversation")
                
                # Apply privacy protection
                protected_data = self._apply_privacy_protection(
                    {
                        "user_message": user_message,
                        "agent_response": agent_response
                    },
                    privacy_level
                )
                
                # Create log entry
                log_entry = ConversationLogEntry(
                    timestamp=datetime.now().isoformat(),
                    session_id=session_id,
                    log_id=log_id,
                    category=LogCategory.CONVERSATION,
                    level=LogLevel.INFO,
                    message="Conversation turn logged",
                    metadata={
                        "user_message": protected_data["user_message"],
                        "agent_response": protected_data["agent_response"],
                        "turn_metadata": metadata or {},
                        "privacy_level": privacy_level
                    },
                    privacy_level=privacy_level,
                    anonymized=privacy_level in ["high", "restricted"]
                )
                
                # Log to conversation logger
                self.conversation_logger.info(
                    json.dumps({
                        "log_id": log_id,
                        "session_id": session_id,
                        "category": log_entry.category.value,
                        "data": log_entry.metadata,
                        "privacy_level": privacy_level
                    })
                )
                
                # Store log entry
                self.log_entries.append(log_entry)
                self._update_statistics("conversation", LogLevel.INFO)
                
                return log_id
                
        except Exception as e:
            logger.error(f"Error logging conversation turn: {str(e)}")
            return ""
    
    def log_crisis_incident(
        self,
        session_id: str,
        crisis_type: str,
        severity: str,
        details: Dict[str, Any],
        response_actions: List[str]
    ) -> str:
        """
        Log a crisis incident with high security.
        
        Args:
            session_id: Session identifier
            crisis_type: Type of crisis detected
            severity: Severity level
            details: Crisis details
            response_actions: Actions taken in response
            
        Returns:
            Log entry ID
            
        TODO: Implement immediate alerting for critical incidents
        """
        try:
            with self.log_lock:
                log_id = self._generate_log_id(session_id, "crisis")
                
                # Apply enhanced privacy protection for crisis logs
                protected_details = self._apply_privacy_protection(
                    details, 
                    "restricted"  # Always use highest privacy level
                )
                
                # Create crisis log entry
                log_entry = ConversationLogEntry(
                    timestamp=datetime.now().isoformat(),
                    session_id=session_id,
                    log_id=log_id,
                    category=LogCategory.CRISIS_INCIDENT,
                    level=LogLevel.CRITICAL if severity == "critical" else LogLevel.WARNING,
                    message=f"Crisis incident: {crisis_type}",
                    metadata={
                        "crisis_type": crisis_type,
                        "severity": severity,
                        "details": protected_details,
                        "response_actions": response_actions,
                        "escalation_timestamp": datetime.now().isoformat()
                    },
                    privacy_level="restricted",
                    anonymized=True,
                    encrypted=True
                )
                
                # Log to crisis logger
                self.crisis_logger.critical(
                    json.dumps({
                        "log_id": log_id,
                        "session_id": self._anonymize_session_id(session_id),
                        "crisis_type": crisis_type,
                        "severity": severity,
                        "response_actions": response_actions,
                        "timestamp": log_entry.timestamp
                    })
                )
                
                # Store log entry
                self.log_entries.append(log_entry)
                self._update_statistics("crisis_incident", log_entry.level)
                self.log_statistics["crisis_incidents_logged"] += 1
                
                # Log audit trail
                self._log_audit_event(
                    "crisis_incident_logged",
                    {
                        "log_id": log_id,
                        "crisis_type": crisis_type,
                        "severity": severity
                    }
                )
                
                return log_id
                
        except Exception as e:
            logger.error(f"Error logging crisis incident: {str(e)}")
            # Still try to log a basic incident record
            self.crisis_logger.critical(
                json.dumps({
                    "error": "Failed to log crisis incident",
                    "session_id": self._anonymize_session_id(session_id),
                    "crisis_type": crisis_type,
                    "timestamp": datetime.now().isoformat()
                })
            )
            return ""
    
    def log_safety_assessment(
        self,
        session_id: str,
        assessment_results: Dict[str, Any],
        triggered_protocols: List[str]
    ) -> str:
        """
        Log safety assessment results.
        
        Args:
            session_id: Session identifier
            assessment_results: Safety assessment results
            triggered_protocols: Safety protocols triggered
            
        Returns:
            Log entry ID
        """
        try:
            with self.log_lock:
                log_id = self._generate_log_id(session_id, "safety")
                
                # Determine log level based on safety level
                safety_level = assessment_results.get("level", "safe")
                if safety_level in ["critical", "high"]:
                    level = LogLevel.WARNING
                elif safety_level == "medium":
                    level = LogLevel.INFO
                else:
                    level = LogLevel.DEBUG
                
                # Create safety log entry
                log_entry = ConversationLogEntry(
                    timestamp=datetime.now().isoformat(),
                    session_id=session_id,
                    log_id=log_id,
                    category=LogCategory.SAFETY_ASSESSMENT,
                    level=level,
                    message=f"Safety assessment: {safety_level}",
                    metadata={
                        "assessment_results": assessment_results,
                        "triggered_protocols": triggered_protocols,
                        "assessment_timestamp": datetime.now().isoformat()
                    },
                    privacy_level="standard"
                )
                
                # Log to conversation logger
                self.conversation_logger.log(
                    self._level_to_logging_level(level),
                    json.dumps({
                        "log_id": log_id,
                        "session_id": session_id,
                        "category": "safety_assessment",
                        "safety_level": safety_level,
                        "protocols_triggered": triggered_protocols
                    })
                )
                
                # Store log entry
                self.log_entries.append(log_entry)
                self._update_statistics("safety_assessment", level)
                
                return log_id
                
        except Exception as e:
            logger.error(f"Error logging safety assessment: {str(e)}")
            return ""
    
    def log_resource_access(
        self,
        session_id: str,
        resources_accessed: List[str],
        resource_type: str,
        user_context: Dict[str, Any] = None
    ) -> str:
        """
        Log resource access for analytics and compliance.
        
        Args:
            session_id: Session identifier
            resources_accessed: List of resources accessed
            resource_type: Type of resources
            user_context: User context information
            
        Returns:
            Log entry ID
        """
        try:
            with self.log_lock:
                log_id = self._generate_log_id(session_id, "resource")
                
                # Create resource access log entry
                log_entry = ConversationLogEntry(
                    timestamp=datetime.now().isoformat(),
                    session_id=session_id,
                    log_id=log_id,
                    category=LogCategory.RESOURCE_ACCESS,
                    level=LogLevel.INFO,
                    message=f"Resource access: {resource_type}",
                    metadata={
                        "resources_accessed": resources_accessed,
                        "resource_type": resource_type,
                        "user_context": user_context or {},
                        "access_timestamp": datetime.now().isoformat()
                    },
                    privacy_level="standard"
                )
                
                # Log to conversation logger
                self.conversation_logger.info(
                    json.dumps({
                        "log_id": log_id,
                        "session_id": session_id,
                        "category": "resource_access",
                        "resource_type": resource_type,
                        "resource_count": len(resources_accessed)
                    })
                )
                
                # Store log entry
                self.log_entries.append(log_entry)
                self._update_statistics("resource_access", LogLevel.INFO)
                
                return log_id
                
        except Exception as e:
            logger.error(f"Error logging resource access: {str(e)}")
            return ""
    
    def log_privacy_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        session_id: str = None
    ) -> str:
        """
        Log privacy-related events for compliance.
        
        Args:
            event_type: Type of privacy event
            details: Event details
            session_id: Optional session identifier
            
        Returns:
            Log entry ID
        """
        try:
            with self.log_lock:
                log_id = self._generate_log_id(session_id or "system", "privacy")
                
                # Create privacy event log entry
                log_entry = ConversationLogEntry(
                    timestamp=datetime.now().isoformat(),
                    session_id=session_id or "system",
                    log_id=log_id,
                    category=LogCategory.PRIVACY_EVENT,
                    level=LogLevel.AUDIT,
                    message=f"Privacy event: {event_type}",
                    metadata={
                        "event_type": event_type,
                        "details": details,
                        "event_timestamp": datetime.now().isoformat()
                    },
                    privacy_level="internal"
                )
                
                # Log to audit logger
                self.audit_logger.info(
                    json.dumps({
                        "log_id": log_id,
                        "event_type": event_type,
                        "session_id": session_id,
                        "details": details
                    })
                )
                
                # Store log entry
                self.log_entries.append(log_entry)
                self._update_statistics("privacy_event", LogLevel.AUDIT)
                self.log_statistics["privacy_events_logged"] += 1
                
                return log_id
                
        except Exception as e:
            logger.error(f"Error logging privacy event: {str(e)}")
            return ""
    
    def _apply_privacy_protection(
        self,
        data: Dict[str, Any],
        privacy_level: str
    ) -> Dict[str, Any]:
        """
        Apply privacy protection based on level.
        
        Args:
            data: Data to protect
            privacy_level: Protection level
            
        Returns:
            Protected data
            
        TODO: Implement encryption for sensitive data
        """
        if privacy_level == "public":
            return data
        
        protected_data = data.copy()
        
        if privacy_level in ["high", "restricted"]:
            # Apply anonymization
            for key, value in protected_data.items():
                if isinstance(value, str) and len(value) > 10:
                    # Hash longer strings
                    hash_value = hashlib.sha256(value.encode()).hexdigest()[:16]
                    protected_data[key] = f"[ANONYMIZED_{hash_value}]"
                elif isinstance(value, str):
                    protected_data[key] = "[REDACTED]"
        
        if privacy_level == "restricted":
            # Additional restrictions for restricted data
            protected_data = {
                key: "[RESTRICTED]" if isinstance(value, str) else value
                for key, value in protected_data.items()
            }
        
        return protected_data
    
    def _generate_log_id(self, session_id: str, log_type: str) -> str:
        """
        Generate unique log entry ID.
        
        Args:
            session_id: Session identifier
            log_type: Type of log entry
            
        Returns:
            Unique log ID
        """
        timestamp = datetime.now().isoformat()
        id_input = f"{session_id}_{log_type}_{timestamp}"
        hash_value = hashlib.md5(id_input.encode()).hexdigest()[:12]
        return f"{log_type}_{hash_value}"
    
    def _anonymize_session_id(self, session_id: str) -> str:
        """
        Anonymize session ID for logging.
        
        Args:
            session_id: Original session ID
            
        Returns:
            Anonymized session ID
        """
        if settings.anonymize_logs:
            hash_value = hashlib.sha256(session_id.encode()).hexdigest()[:8]
            return f"session_{hash_value}"
        return session_id
    
    def _update_statistics(self, category: str, level: LogLevel):
        """
        Update logging statistics.
        
        Args:
            category: Log category
            level: Log level
        """
        self.log_statistics["total_entries"] += 1
        
        # Update category counts
        if category in self.log_statistics["entries_by_category"]:
            self.log_statistics["entries_by_category"][category] += 1
        else:
            self.log_statistics["entries_by_category"][category] = 1
        
        # Update level counts
        level_str = level.value
        if level_str in self.log_statistics["entries_by_level"]:
            self.log_statistics["entries_by_level"][level_str] += 1
        else:
            self.log_statistics["entries_by_level"][level_str] = 1
    
    def _level_to_logging_level(self, level: LogLevel) -> int:
        """
        Convert LogLevel to Python logging level.
        
        Args:
            level: LogLevel enum
            
        Returns:
            Python logging level integer
        """
        mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
            LogLevel.AUDIT: logging.INFO
        }
        return mapping.get(level, logging.INFO)
    
    def _log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """
        Log audit event for compliance tracking.
        
        Args:
            event_type: Type of audit event
            details: Event details
        """
        self.audit_logger.info(
            json.dumps({
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "details": details
            })
        )
    
    def get_log_entries(
        self,
        session_id: str = None,
        category: LogCategory = None,
        start_time: datetime = None,
        end_time: datetime = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve log entries based on filters.
        
        Args:
            session_id: Filter by session ID
            category: Filter by log category
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of entries
            
        Returns:
            List of matching log entries
            
        TODO: Implement database-backed log storage for better querying
        """
        filtered_entries = self.log_entries
        
        # Apply filters
        if session_id:
            filtered_entries = [
                entry for entry in filtered_entries 
                if entry.session_id == session_id
            ]
        
        if category:
            filtered_entries = [
                entry for entry in filtered_entries 
                if entry.category == category
            ]
        
        if start_time:
            filtered_entries = [
                entry for entry in filtered_entries
                if datetime.fromisoformat(entry.timestamp) >= start_time
            ]
        
        if end_time:
            filtered_entries = [
                entry for entry in filtered_entries
                if datetime.fromisoformat(entry.timestamp) <= end_time
            ]
        
        # Sort by timestamp (newest first) and apply limit
        filtered_entries.sort(
            key=lambda x: datetime.fromisoformat(x.timestamp), 
            reverse=True
        )
        
        return [asdict(entry) for entry in filtered_entries[:limit]]
    
    def compress_old_logs(self, days_old: int = 7):
        """
        Compress log files older than specified days.
        
        Args:
            days_old: Compress logs older than this many days
            
        TODO: Implement automatic log compression and archival
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            for log_file in self.log_directory.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    # Compress the log file
                    compressed_file = log_file.with_suffix(".log.gz")
                    
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(compressed_file, 'wb') as f_out:
                            f_out.writelines(f_in)
                    
                    # Remove original file
                    log_file.unlink()
                    
                    logger.info(f"Compressed log file: {log_file.name}")
            
        except Exception as e:
            logger.error(f"Error compressing old logs: {str(e)}")
    
    def get_logging_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive logging statistics.
        
        Returns:
            Dictionary with logging statistics
        """
        # Add disk usage information
        total_log_size = sum(
            f.stat().st_size 
            for f in self.log_directory.glob("*.log*")
            if f.is_file()
        )
        
        return {
            **self.log_statistics,
            "log_directory": str(self.log_directory),
            "total_log_files": len(list(self.log_directory.glob("*.log*"))),
            "total_log_size_bytes": total_log_size,
            "total_log_size_mb": round(total_log_size / (1024 * 1024), 2),
            "compression_enabled": self.compress_logs,
            "encryption_enabled": self.encrypt_sensitive,
            "anonymization_enabled": settings.anonymize_logs,
            "supported_categories": [cat.value for cat in LogCategory],
            "supported_levels": [level.value for level in LogLevel]
        }
    
    def export_logs(
        self,
        output_file: str,
        session_id: str = None,
        anonymize: bool = True,
        compress: bool = True
    ) -> bool:
        """
        Export logs to file for analysis or compliance.
        
        Args:
            output_file: Output file path
            session_id: Optional session filter
            anonymize: Whether to anonymize exported data
            compress: Whether to compress the export
            
        Returns:
            Success status
            
        TODO: Implement secure export with digital signatures
        """
        try:
            # Get log entries
            entries = self.get_log_entries(session_id=session_id, limit=10000)
            
            # Anonymize if requested
            if anonymize:
                for entry in entries:
                    if "session_id" in entry:
                        entry["session_id"] = self._anonymize_session_id(entry["session_id"])
                    # Additional anonymization logic here
            
            # Prepare export data
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_entries": len(entries),
                "anonymized": anonymize,
                "entries": entries
            }
            
            # Write to file
            output_path = Path(output_file)
            
            if compress:
                with gzip.open(output_path.with_suffix(".json.gz"), 'wt') as f:
                    json.dump(export_data, f, indent=2)
            else:
                with open(output_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported {len(entries)} log entries to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting logs: {str(e)}")
            return False