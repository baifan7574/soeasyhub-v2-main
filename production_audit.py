from supabase import create_client
import os

def load_config():
    config = {
        'url': os.getenv('SUPABASE_URL'),
        'key': os.getenv('SUPABASE_KEY')
    }
    if not config['url'] or not config['key']:
        try:
            token_path = '.agent/Token..txt'
            if not os.path.exists(token_path): token_path = '../' + token_path
            with open(token_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'Project URL:' in line: config['url'] = line.split('URL:')[1].strip()
                    if 'Secret keys:' in line: config['key'] = line.split('keys:')[1].strip()
        except: pass
    return config

config = load_config()
if not config['url'] or not config['key']:
    raise ValueError("Missing Supabase credentials.")

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
        print(f"Column Name: final_article")
        print(f"Slug: {item['slug']}")
        print(f"Content Length: {len(item['final_article'])} chars")
        print(f"Preview (First 200 chars):")
        print(item['final_article'][:200])
