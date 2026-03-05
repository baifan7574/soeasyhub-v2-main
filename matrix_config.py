import os
import sys
import platform
import re

class MatrixConfig:
    """
    统一配置大管家 (Unified Configuration Center)
    负责所有脚本的配置加载、环境变量读取、本地Token文件扫描以及日志输出。
    """
    
    # Environment Variable Names
    ENV_SUPABASE_URL = "SUPABASE_URL"
    ENV_SUPABASE_KEY = "SUPABASE_KEY"
    ENV_DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY"
    ENV_GROQ_API_KEY = "GROQ_API_KEY"
    ENV_ZHIPU_API_KEY = "ZHIPU_API_KEY"

    # Local Token File Name
    TOKEN_FILENAME = "Token..txt"

    def __init__(self):
        self._config = {}
        self.is_windows = platform.system() == "Windows"
        self._load_config()

    def _load_config(self):
        """
        加载配置：优先环境变量，其次本地文件
        """
        # 1. 尝试从环境变量加载
        self._load_from_env()

        # 2. 如果关键配置缺失，尝试从本地 Token 文件加载
        if not self.is_valid():
            self.log("[Info] Environment variables incomplete. Scanning for local Token file...", level="INFO")
            self._load_from_file()
        else:
            self.log("[Info] Config loaded fully from environment variables.", level="INFO")

    def _load_from_env(self):
        """从环境变量读取"""
        self._config['url'] = os.environ.get(self.ENV_SUPABASE_URL)
        self._config['key'] = os.environ.get(self.ENV_SUPABASE_KEY)
        self._config['ds_key'] = os.environ.get(self.ENV_DEEPSEEK_API_KEY)
        self._config['groq_key'] = os.environ.get(self.ENV_GROQ_API_KEY)
        self._config['zhipu_key'] = os.environ.get(self.ENV_ZHIPU_API_KEY)

    def _load_from_file(self):
        """扫描并解析本地 Token 文件"""
        search_paths = [
            os.path.join(".agent", self.TOKEN_FILENAME),
            os.path.join("..", ".agent", self.TOKEN_FILENAME),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), ".agent", self.TOKEN_FILENAME),
            # 当前目录下也找找
            os.path.join(os.getcwd(), ".agent", self.TOKEN_FILENAME),
            # 常见位置
            os.path.join("d:/quicktoolshub/rader/美国跨州合规报告/.agent", self.TOKEN_FILENAME)
        ]

        token_path = None
        for p in search_paths:
            if os.path.exists(p):
                token_path = p
                break
        
        if not token_path:
            # 如果没找到文件且环境变量也没配全，只是警告，后续脚本可能会报错
            self.log("[Warn] No local Token file found.", level="WARN")
            return

        self.log(f"[Info] Loading config from local file: {token_path}", level="INFO")
        
        try:
            with open(token_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    
                    # Supabase URL
                    if "Project URL:" in line:
                        self._config['url'] = line.split("Project URL:")[1].split("URL:")[0].strip() # Handle potential double labeling or simple split
                        # Re-parsing carefully as per previous scripts logic
                        if "Project URL:" in line:
                             parts = line.split("Project URL:")
                             if len(parts) > 1: self._config['url'] = parts[1].strip()
                        elif "URL:" in line:
                             self._config['url'] = line.split("URL:")[1].strip()

                    # Supabase Key (Anon or Service Role)
                    if "Secret keys:" in line:
                        keys_part = line.split("keys:")[1].strip()
                        # 有时可能是一长串，有时可能是 key
                        self._config['key'] = keys_part
                    
                    # API Keys
                    if "ZHIPUAPI:" in line:
                        self._config['zhipu_key'] = line.split("ZHIPUAPI:")[1].strip()
                    if "DSAPI:" in line:
                        self._config['ds_key'] = line.split("DSAPI:")[1].strip()
                    if "groqapi" in line.lower(): # Case insensitive check for groq
                         # split by case insensitive 'groqapi:' pattern? 
                         # Simple approach: find index
                         lower_line = line.lower()
                         idx = lower_line.find("groqapi:")
                         if idx != -1:
                             self._config['groq_key'] = line[idx+8:].strip()

                    # Service Role Key specific parsing (JWT looking string)
                    if 'service_role' in line and 'eyJ' in line:
                        parts = line.split()
                        for part in parts:
                            if part.startswith('eyJ'):
                                self._config['service_key'] = part.strip()
            
            # 优先使用 service_key
            if self._config.get('service_key'):
                self._config['key'] = self._config['service_key']

        except Exception as e:
            self.log(f"[Error] Failed to parse Token file: {e}", level="ERROR")

    def is_valid(self):
        """检查核心配置是否存在"""
        return bool(self._config.get('url') and self._config.get('key'))

    @property
    def supabase_url(self):
        return self._config.get('url')

    @property
    def supabase_key(self):
        return self._config.get('key')

    @property
    def deepseek_key(self):
        return self._config.get('ds_key')

    @property
    def groq_key(self):
        return self._config.get('groq_key')

    @property
    def zhipu_key(self):
        return self._config.get('zhipu_key')

    def log(self, message, level="INFO"):
        """统一日志输出，自动过滤不支持的 Emoji (针对 Windows cmd)"""
        if self.is_windows:
            try:
                # 尝试编码打印，如果报错则替换
                print(message)
            except UnicodeEncodeError:
                # 简单过滤 emoji 范围 (粗略)
                # 或者直接忽略错误字符
                clean_msg = message.encode('gbk', 'ignore').decode('gbk')
                print(clean_msg)
        else:
            print(message)

# 全局单例实例
config = MatrixConfig()
