"""
Database models and operations for the AI Style Transfer Studio
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import uuid


class DatabaseManager:
    """Manages all database operations for the application"""
    
    def __init__(self, db_path: str = "data/app.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize all database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table (already handled in auth.py, but ensuring consistency)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Style transfer history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transfer_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT,
                content_image_path TEXT,
                style_image_path TEXT,
                result_image_path TEXT,
                model_type TEXT DEFAULT 'adain',
                style_strength REAL DEFAULT 1.0,
                processing_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # User preferences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                favorite_styles TEXT,  -- JSON array
                default_style_strength REAL DEFAULT 0.7,
                preferred_output_format TEXT DEFAULT 'jpeg',
                theme TEXT DEFAULT 'dark',
                notifications_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Style presets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS style_presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                style_image_path TEXT,
                artist TEXT,
                style_period TEXT,
                color_palette TEXT,  -- JSON array
                is_active BOOLEAN DEFAULT 1,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User galleries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_galleries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                gallery_name TEXT,
                description TEXT,
                is_public BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Gallery items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gallery_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gallery_id INTEGER,
                transfer_history_id INTEGER,
                title TEXT,
                description TEXT,
                tags TEXT,  -- JSON array
                likes_count INTEGER DEFAULT 0,
                views_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (gallery_id) REFERENCES user_galleries (id),
                FOREIGN KEY (transfer_history_id) REFERENCES transfer_history (id)
            )
        """)
        
        # User feedback/ratings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                transfer_id INTEGER,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                feedback_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (transfer_id) REFERENCES transfer_history (id)
            )
        """)
        
        # Analytics/usage tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,  -- 'style_transfer', 'login', 'register', etc.
                details TEXT,  -- JSON with additional details
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        self._insert_default_presets(cursor)
        conn.commit()
        conn.close()
    
    def _insert_default_presets(self, cursor):
        """Insert default style presets"""
        presets = [
            {
                'name': 'Van Gogh Starry Night',
                'description': 'Post-impressionist swirls and bold colors',
                'artist': 'Vincent van Gogh',
                'style_period': 'Post-Impressionism',
                'color_palette': json.dumps(['#1e3a8a', '#fbbf24', '#f59e0b', '#1f2937'])
            },
            {
                'name': 'Picasso Cubist',
                'description': 'Geometric forms and abstract representation',
                'artist': 'Pablo Picasso',
                'style_period': 'Cubism',
                'color_palette': json.dumps(['#7c3aed', '#ec4899', '#f59e0b', '#6b7280'])
            },
            {
                'name': 'Monet Water Lilies',
                'description': 'Impressionist light and flowing brushstrokes',
                'artist': 'Claude Monet',
                'style_period': 'Impressionism',
                'color_palette': json.dumps(['#059669', '#0ea5e9', '#8b5cf6', '#f3f4f6'])
            },
            {
                'name': 'Hokusai Wave',
                'description': 'Japanese woodblock printing style',
                'artist': 'Katsushika Hokusai',
                'style_period': 'Ukiyo-e',
                'color_palette': json.dumps(['#1e40af', '#ffffff', '#0891b2', '#1f2937'])
            },
            {
                'name': 'Kandinsky Abstract',
                'description': 'Abstract expressionism with vibrant colors',
                'artist': 'Wassily Kandinsky',
                'style_period': 'Abstract Expressionism',
                'color_palette': json.dumps(['#dc2626', '#fbbf24', '#059669', '#7c3aed'])
            }
        ]
        
        for preset in presets:
            cursor.execute("""
                INSERT OR IGNORE INTO style_presets 
                (name, description, artist, style_period, color_palette)
                VALUES (?, ?, ?, ?, ?)
            """, (preset['name'], preset['description'], preset['artist'], 
                  preset['style_period'], preset['color_palette']))
    
    def save_transfer_history(self, user_id: int, session_id: str, 
                            content_path: str, style_path: str, result_path: str,
                            model_type: str = 'adain', style_strength: float = 1.0,
                            processing_time: float = 0.0) -> int:
        """Save style transfer operation to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO transfer_history 
            (user_id, session_id, content_image_path, style_image_path, 
             result_image_path, model_type, style_strength, processing_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, session_id, content_path, style_path, result_path,
              model_type, style_strength, processing_time))
        
        transfer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return transfer_id
    
    def get_user_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's style transfer history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content_image_path, style_image_path, result_image_path,
                   model_type, style_strength, processing_time, created_at
            FROM transfer_history 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (user_id, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'id': row[0],
                'content_image_path': row[1],
                'style_image_path': row[2],
                'result_image_path': row[3],
                'model_type': row[4],
                'style_strength': row[5],
                'processing_time': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        return history
    
    def get_style_presets(self) -> List[Dict[str, Any]]:
        """Get all active style presets"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, artist, style_period, color_palette, usage_count
            FROM style_presets 
            WHERE is_active = 1
            ORDER BY usage_count DESC, name
        """)
        
        presets = []
        for row in cursor.fetchall():
            presets.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'artist': row[3],
                'style_period': row[4],
                'color_palette': json.loads(row[5]) if row[5] else [],
                'usage_count': row[6]
            })
        
        conn.close()
        return presets
    
    def update_preset_usage(self, preset_id: int):
        """Increment usage count for a style preset"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE style_presets 
            SET usage_count = usage_count + 1 
            WHERE id = ?
        """, (preset_id,))
        
        conn.commit()
        conn.close()
    
    def save_user_preferences(self, user_id: int, preferences: Dict[str, Any]):
        """Save or update user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences 
            (user_id, favorite_styles, default_style_strength, 
             preferred_output_format, theme, notifications_enabled, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            json.dumps(preferences.get('favorite_styles', [])),
            preferences.get('default_style_strength', 0.7),
            preferences.get('preferred_output_format', 'jpeg'),
            preferences.get('theme', 'dark'),
            preferences.get('notifications_enabled', True),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT favorite_styles, default_style_strength, preferred_output_format,
                   theme, notifications_enabled
            FROM user_preferences 
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'favorite_styles': json.loads(row[0]) if row[0] else [],
                'default_style_strength': row[1],
                'preferred_output_format': row[2],
                'theme': row[3],
                'notifications_enabled': bool(row[4])
            }
        else:
            # Return defaults
            return {
                'favorite_styles': [],
                'default_style_strength': 0.7,
                'preferred_output_format': 'jpeg',
                'theme': 'dark',
                'notifications_enabled': True
            }
    
    def create_gallery(self, user_id: int, name: str, description: str = "", 
                      is_public: bool = False) -> int:
        """Create a new user gallery"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_galleries (user_id, gallery_name, description, is_public)
            VALUES (?, ?, ?, ?)
        """, (user_id, name, description, is_public))
        
        gallery_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return gallery_id
    
    def add_to_gallery(self, gallery_id: int, transfer_id: int, title: str = "",
                      description: str = "", tags: List[str] = None):
        """Add a style transfer result to a gallery"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO gallery_items 
            (gallery_id, transfer_history_id, title, description, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (gallery_id, transfer_id, title, description, 
              json.dumps(tags or [])))
        
        conn.commit()
        conn.close()
    
    def get_user_galleries(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's galleries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT g.id, g.gallery_name, g.description, g.is_public, g.created_at,
                   COUNT(gi.id) as item_count
            FROM user_galleries g
            LEFT JOIN gallery_items gi ON g.id = gi.gallery_id
            WHERE g.user_id = ?
            GROUP BY g.id, g.gallery_name, g.description, g.is_public, g.created_at
            ORDER BY g.created_at DESC
        """, (user_id,))
        
        galleries = []
        for row in cursor.fetchall():
            galleries.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'is_public': bool(row[3]),
                'created_at': row[4],
                'item_count': row[5]
            })
        
        conn.close()
        return galleries
    
    def log_user_action(self, user_id: int, action: str, details: Dict[str, Any] = None,
                       ip_address: str = None, user_agent: str = None):
        """Log user action for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO usage_analytics 
            (user_id, action, details, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, action, json.dumps(details or {}), ip_address, user_agent))
        
        conn.commit()
        conn.close()
    
    def get_popular_styles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular style presets"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, description, artist, usage_count
            FROM style_presets 
            WHERE is_active = 1
            ORDER BY usage_count DESC, name
            LIMIT ?
        """, (limit,))
        
        popular_styles = []
        for row in cursor.fetchall():
            popular_styles.append({
                'name': row[0],
                'description': row[1],
                'artist': row[2],
                'usage_count': row[3]
            })
        
        conn.close()
        return popular_styles
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Total style transfers
        cursor.execute("SELECT COUNT(*) FROM transfer_history")
        total_transfers = cursor.fetchone()[0]
        
        # Active users (last 30 days)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) 
            FROM usage_analytics 
            WHERE created_at >= datetime('now', '-30 days')
        """)
        active_users = cursor.fetchone()[0]
        
        # Average processing time
        cursor.execute("""
            SELECT AVG(processing_time) 
            FROM transfer_history 
            WHERE processing_time > 0
        """)
        avg_processing_time = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_transfers': total_transfers,
            'active_users_30d': active_users,
            'avg_processing_time': round(avg_processing_time, 2)
        }


# Global database instance
db = DatabaseManager()