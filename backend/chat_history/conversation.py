import os
import sqlite3

class ConversationHistory:
    def __init__(self):
        self.chat_history_dir = os.getenv('CHAT_HISTORY_DIR', os.path.join(os.path.dirname(__file__), 'chat_history'))
        self.chat_history_db = os.path.join(self.chat_history_dir, 'chat_history.db')
        self._ensure_db_directory()
        self.init_db()

    def _ensure_db_directory(self):
        if not os.path.exists(self.chat_history_dir):
            os.makedirs(self.chat_history_dir)

    def init_db(self):
        conn = sqlite3.connect(self.chat_history_db)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def get_conversation_history(self, session_id):
        conn = sqlite3.connect(self.chat_history_db)
        c = conn.cursor()
        c.execute('SELECT role, content FROM conversation_history WHERE session_id = ?', (session_id,))
        history = c.fetchall()
        conn.close()
        return [{'role': row[0], 'content': row[1]} for row in history]

    def add_to_conversation_history(self, session_id, role, content):
        conn = sqlite3.connect(self.chat_history_db)
        c = conn.cursor()
        c.execute('INSERT INTO conversation_history (session_id, role, content) VALUES (?, ?, ?)', (session_id, role, content))
        conn.commit()
        conn.close()

    def delete_conversation_history(self, session_id):
        conn = sqlite3.connect(self.chat_history_db)
        c = conn.cursor()
        c.execute('DELETE FROM conversation_history WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()

    