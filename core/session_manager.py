"""
会话管理模块
管理多个聊天会话和用户状态
"""
from typing import Dict, Optional
from .models import ChatSession


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
    
    def get_session(self, session_id: str) -> ChatSession:
        """获取或创建会话"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatSession(session_id)
        return self.sessions[session_id]
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(self) -> list:
        """列出所有会话ID"""
        return list(self.sessions.keys())
    
    def get_session_count(self) -> int:
        """获取当前会话数量"""
        return len(self.sessions)


# 全局会话管理器实例
session_manager = SessionManager()