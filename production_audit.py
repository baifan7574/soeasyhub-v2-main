from supabase import create_client
import os

def load_config():
    config = {
        'url': os.getenv('SUPABASE_URL'),
        'key': os.getenv('SUPABASE_KEY')
    }
    
    # Fast check for env vars first (Actions mode)
    if config['url'] and config['key']:
        print("✅ Using Environment Variables.")
        return config

    # Fallback for Local Dev
    token_paths = [
        '.agent/Token..txt',
        '../.agent/Token..txt',
        '../../.agent/Token..txt'
    ]
    
    for tp in token_paths:
        if os.path.exists(tp):
            try:
                with open(tp, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'Project URL:' in line: config['url'] = line.split('URL:')[1].strip()
                        if 'Secret keys:' in line: config['key'] = line.split('keys:')[1].strip()
                if config['url'] and config['key']:
                    print(f"✅ Using local Token file: {tp}")
                    return config
            except: pass
            
    return config

config = load_config()
if not config['url'] or not config['key']:
    print("❌ ERROR: Missing Supabase credentials (SUPABASE_URL, SUPABASE_KEY).")
    exit(1)

try:
    sb = create_client(config['url'], config['key'])
    
    # Get counts
    downloaded = sb.table('grich_keywords_pool').select('id', count='exact').eq('is_downloaded', True).execute().count
    refined = sb.table('grich_keywords_pool').select('id', count='exact').eq('is_refined', True).execute().count
    composed = sb.table('grich_keywords_pool').select('id', count='exact').not_.is_('final_article', 'null').execute().count
    
    print(f"--- PRODUCTION LINE AUDIT ---")
    print(f"1. PDF Downloaded (Script 2): {downloaded}")
    print(f"2. Data Refined (Script 3): {refined}")
    print(f"3. Articles Composed (Script 4): {composed}")
    
    if composed > 0:
        print("\n--- SAMPLE COMPOSED ARTICLE ---")
        sample = sb.table('grich_keywords_pool').select('slug', 'keyword', 'final_article').not_.is_('final_article', 'null').limit(1).execute()
        if sample.data:
            item = sample.data[0]
            print(f"Slug: {item['slug']}")
            print(f"Content Length: {len(item['final_article'])} chars")
            print(f"Preview: {item['final_article'][:100]}...")
except Exception as e:
    print(f"❌ Supabase Connection Failed: {e}")
    exit(1)
