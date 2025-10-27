import os
import time
import json
import re
import requests
import subprocess
import tempfile
import hashlib
import sqlite3
import logging
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import warnings

try:
    import psycopg2
    from psycopg2 import pool
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    import xml.etree.ElementTree as ET
    XML_AVAILABLE = True
except ImportError:
    XML_AVAILABLE = False

warnings.filterwarnings('ignore')

# ===================== CONFIGURATION =====================
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
MAX_RESEARCH_RESULTS = 10
CODE_EXECUTION_TIMEOUT = 30
CACHE_DB = "cache.db"

# Setup logging
logging.basicConfig(
    level=logging.INFO if DEBUG_MODE else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===================== DATABASE MANAGER =====================
class EnhancedDatabaseManager:
    def __init__(self):
        self.pg_pool = None
        self.init_databases()
    
    def init_databases(self):
        """Initialize databases"""
        try:
            self.init_sqlite()
            if POSTGRES_AVAILABLE:
                self.init_postgresql()
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    def init_sqlite(self):
        """Initialize SQLite database"""
        try:
            if not os.path.exists(CACHE_DB):
                open(CACHE_DB, 'a').close()
            
            conn = sqlite3.connect(CACHE_DB)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    preferences TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    action TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("SQLite database initialized")
            
        except Exception as e:
            logger.error(f"SQLite initialization error: {e}")

    def init_postgresql(self):
        """Initialize PostgreSQL connection"""
        try:
            database_url = os.environ.get('DATABASE_URL')
            if database_url and POSTGRES_AVAILABLE:
                self.pg_pool = psycopg2.pool.SimpleConnectionPool(1, 10, database_url)
                logger.info("PostgreSQL pool initialized")
        except Exception as e:
            logger.warning(f"PostgreSQL not available: {e}")

    def get_connection(self):
        """Get database connection"""
        if self.pg_pool and POSTGRES_AVAILABLE:
            try:
                return self.pg_pool.getconn(), "postgresql"
            except:
                pass
        return sqlite3.connect(CACHE_DB), "sqlite"

    def return_connection(self, conn, db_type):
        """Return connection"""
        try:
            if db_type == "postgresql" and self.pg_pool:
                self.pg_pool.putconn(conn)
            else:
                conn.close()
        except Exception as e:
            logger.error(f"Error returning connection: {e}")

    def get_cached_result(self, key: str) -> Optional[str]:
        """Get cached result"""
        conn, db_type = None, None
        try:
            conn, db_type = self.get_connection()
            cursor = conn.cursor()
            
            if db_type == "postgresql":
                cursor.execute('SELECT value FROM cache WHERE key = %s AND expires_at > NOW()', (key,))
            else:
                cursor.execute("SELECT value FROM cache WHERE key = ? AND expires_at > datetime('now')", (key,))
            
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
        finally:
            if conn:
                self.return_connection(conn, db_type)

    def set_cached_result(self, key: str, value: str, ttl_minutes: int = 60):
        """Set cached result"""
        conn, db_type = None, None
        try:
            conn, db_type = self.get_connection()
            cursor = conn.cursor()
            expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
            
            if db_type == "postgresql":
                cursor.execute('''
                    INSERT INTO cache (key, value, expires_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, expires_at = EXCLUDED.expires_at
                ''', (key, value, expires_at))
            else:
                cursor.execute('INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)',
                             (key, value, expires_at))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
        finally:
            if conn:
                self.return_connection(conn, db_type)

    def log_analytics(self, user_id: str, action: str, details: str = ""):
        """Log analytics"""
        conn, db_type = None, None
        try:
            conn, db_type = self.get_connection()
            cursor = conn.cursor()
            
            if db_type == "postgresql":
                cursor.execute('INSERT INTO analytics (user_id, action, details) VALUES (%s, %s, %s)',
                             (user_id, action, details))
            else:
                cursor.execute('INSERT INTO analytics (user_id, action, details) VALUES (?, ?, ?)',
                             (user_id, action, details))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Analytics error: {e}")
        finally:
            if conn:
                self.return_connection(conn, db_type)

# ===================== SECURITY MANAGER =====================
class EnhancedSecurityManager:
    def __init__(self):
        self.blocked_patterns = [
            r"import\s+(os|sys|shutil|subprocess|socket)",
            r"__import__", r"eval\(", r"exec\(", r"open\(", 
            r"system\(", r"popen\(", r"rm\s+", r"del\s+"
        ]
        self.max_execution_time = CODE_EXECUTION_TIMEOUT
        self.max_code_length = 10000
        self.rate_limits = {}

    def check_rate_limit(self, user_id: str, action: str, limit: int = 10, window: int = 60) -> bool:
        """Check rate limit"""
        now = time.time()
        key = f"{user_id}:{action}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        self.rate_limits[key] = [t for t in self.rate_limits[key] if now - t < window]
        
        if len(self.rate_limits[key]) >= limit:
            return False
        
        self.rate_limits[key].append(now)
        return True

    def sanitize_input(self, text: str, max_length: int = 2000) -> str:
        """Sanitize input"""
        if not text or len(text) > max_length:
            return ""
        
        sanitized = re.sub(r"[;\\<>/&|$`]", "", text)
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                sanitized = re.sub(pattern, "[BLOCKED]", sanitized, flags=re.IGNORECASE)
        
        return sanitized[:max_length]

    def safe_execute(self, code: str, user_id: str = "default") -> str:
        """Safe code execution"""
        if not self.check_rate_limit(user_id, "code_execution", 5, 300):
            return "🔒 Rate limit exceeded"
        
        if len(code) > self.max_code_length:
            return "🔒 Code too long"
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return "🔒 Security: Restricted operation detected"

        try:
            safe_code = f"""
import sys
import time
import math
import random
import json
import io
import contextlib

output_buffer = io.StringIO()

try:
    with contextlib.redirect_stdout(output_buffer):
        with contextlib.redirect_stderr(output_buffer):
{chr(10).join('            ' + line for line in code.split(chr(10)))}
except Exception as e:
    print(f"Error: {{e}}")
finally:
    print(output_buffer.getvalue())
"""
            
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
                f.write(safe_code)
                f.flush()
                
                start_time = time.time()
                result = subprocess.run(
                    ["python", f.name],
                    capture_output=True,
                    text=True,
                    timeout=self.max_execution_time
                )
                exec_time = time.time() - start_time
                
                os.unlink(f.name)
                
                output = result.stdout.strip() or "Execution completed"
                if result.stderr:
                    output += f"\nWarnings: {result.stderr.strip()}"
                
                return f"{output[:2000]}\n⏱️ Time: {exec_time:.2f}s"
                
        except subprocess.TimeoutExpired:
            return "⏱️ Execution timed out"
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

# ===================== RESEARCH ENGINE =====================
class EnhancedResearchEngine:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db_manager = db_manager
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        ]
        
    def search_multiple_sources(self, query: str, max_results: int = 5) -> Dict[str, List[Dict]]:
        """Multi-source search"""
        cache_key = f"search_{hashlib.md5(query.encode()).hexdigest()}_{max_results}"
        cached = self.db_manager.get_cached_result(cache_key)
        
        if cached:
            try:
                return json.loads(cached)
            except:
                pass
        
        results = {}
        futures = {}
        
        try:
            futures['web'] = self.executor.submit(self._search_web, query, max_results)
            futures['wikipedia'] = self.executor.submit(self._search_wikipedia, query)
            if XML_AVAILABLE:
                futures['arxiv'] = self.executor.submit(self._search_arxiv, query, max_results)
        except Exception as e:
            logger.error(f"Search submission error: {e}")
        
        for source, future in futures.items():
            try:
                results[source] = future.result(timeout=15)
            except Exception as e:
                logger.error(f"Search error for {source}: {e}")
                results[source] = []
        
        if any(results.values()):
            self.db_manager.set_cached_result(cache_key, json.dumps(results), 60)
        
        return results
    
    def _search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """Web search"""
        if not DDGS_AVAILABLE:
            return self._fallback_search(query, max_results)
            
        try:
            for attempt in range(3):
                try:
                    time.sleep(random.uniform(1, 3))
                    
                    with DDGS() as ddgs:
                        results = []
                        for r in ddgs.text(query, max_results=max_results):
                            results.append({
                                "title": r.get("title", "")[:150],
                                "url": r.get("href", ""),
                                "snippet": r.get("body", "")[:300],
                                "source": "DuckDuckGo"
                            })
                        
                        if results:
                            return results
                            
                except Exception as e:
                    logger.warning(f"DuckDuckGo attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        time.sleep(random.uniform(2, 5))
            
            return self._fallback_search(query, max_results)
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []
    
    def _fallback_search(self, query: str, max_results: int) -> List[Dict]:
        """Fallback search"""
        results = []
        keywords = query.lower().split()
        
        if any(word in keywords for word in ['learn', 'how', 'what', 'explain']):
            results.append({
                "title": f"Understanding {query}",
                "url": "https://example.com/educational",
                "snippet": f"Comprehensive guide to {query}",
                "source": "Educational"
            })
        
        return results[:max_results]
    
    def _search_wikipedia(self, query: str) -> List[Dict]:
        """Wikipedia search"""
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [{
                    "title": data.get("title", ""),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "snippet": data.get("extract", "")[:400],
                    "source": "Wikipedia"
                }]
        except Exception as e:
            logger.error(f"Wikipedia error: {e}")
        return []
    
    def _search_arxiv(self, query: str, max_results: int = 3) -> List[Dict]:
        """arXiv search"""
        if not XML_AVAILABLE:
            return []
            
        try:
            url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
            response = requests.get(url, timeout=10)
            results = []
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    title = entry.find('{http://www.w3.org/2005/Atom}title')
                    summary = entry.find('{http://www.w3.org/2005/Atom}summary')
                    link = entry.find('{http://www.w3.org/2005/Atom}id')
                    
                    if title is not None and summary is not None:
                        results.append({
                            "title": title.text[:150],
                            "url": link.text if link is not None else "",
                            "snippet": summary.text[:300],
                            "source": "arXiv"
                        })
            return results
        except Exception as e:
            logger.error(f"arXiv error: {e}")
            return [] 
