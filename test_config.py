import os
import sys

# Ensure we can import from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from matrix_config import config

def mask_key(key):
    if not key:
        return "Not Set"
    if len(key) < 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"

def test_config_loading():
    print("="*60)
    print("      MATRIX CONFIGURATION CENTER - DIAGNOSTIC TEST      ")
    print("="*60)
    
    print(f"[Supabase URL]   : {config.supabase_url}")
    print(f"[Supabase Key]   : {mask_key(config.supabase_key)}")
    print(f"[DeepSeek Key]   : {mask_key(config.deepseek_key)}")
    print(f"[Groq Key]       : {mask_key(config.groq_key)}")
    print(f"[Zhipu Key]      : {mask_key(config.zhipu_key)}")
    
    print("-" * 60)
    
    if config.is_valid():
        config.log("✅ Configuration Validated: Core systems are ready.")
    else:
        config.log("❌ Configuration Failed: Missing critical Supabase credentials.", level="ERROR")

    # Test Logger with Emoji
    print("-" * 60)
    print("Testing Logger (Emoji handling on Windows):")
    config.log("   [Info] This is a test message with emoji: 🚀 🌟 ✅")

if __name__ == "__main__":
    test_config_loading()
