"""
Database module for storing chat history
Uses SQLite for persistent storage
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import json

class ChatDatabase:
    def __init__(self, db_path: str = "yuna_chats.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create chats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    
    # ===== CHAT OPERATIONS =====
    
    def create_chat(self, chat_id: str, title: str) -> Dict:
        """Create a new chat"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO chats (id, title) VALUES (?, ?)",
            (chat_id, title)
        )
        
        conn.commit()
        conn.close()
        
        return {"id": chat_id, "title": title}
    
    def get_all_chats(self) -> List[Dict]:
        """Get all chats ordered by most recent"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, created_at, updated_at 
            FROM chats 
            ORDER BY updated_at DESC
        """)
        
        chats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return chats
    
    def get_chat(self, chat_id: str) -> Optional[Dict]:
        """Get a specific chat"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, title, created_at, updated_at FROM chats WHERE id = ?",
            (chat_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_chat_title(self, chat_id: str, title: str) -> bool:
        """Update chat title"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE chats SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title, chat_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat and all its messages"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Delete messages first
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        
        # Delete chat
        cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    # ===== MESSAGE OPERATIONS =====
    
    def add_message(self, chat_id: str, role: str, content: str) -> Dict:
        """Add a message to a chat"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, role, content)
        )
        
        message_id = cursor.lastrowid
        
        # Update chat's updated_at timestamp
        cursor.execute(
            "UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (chat_id,)
        )
        
        conn.commit()
        conn.close()
        
        return {
            "id": message_id,
            "chat_id": chat_id,
            "role": role,
            "content": content
        }
    
    def get_chat_messages(self, chat_id: str) -> List[Dict]:
        """Get all messages for a chat"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, chat_id, role, content, created_at 
            FROM messages 
            WHERE chat_id = ? 
            ORDER BY id ASC
        """, (chat_id,))
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return messages
    
    def get_chat_with_messages(self, chat_id: str) -> Optional[Dict]:
        """Get a chat with all its messages"""
        chat = self.get_chat(chat_id)
        if not chat:
            return None
        
        messages = self.get_chat_messages(chat_id)
        chat['messages'] = messages
        
        return chat


# Global database instance
db = ChatDatabase()
