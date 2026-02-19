/**
 * soeasyhub-v2 Cloudflare Worker (Production Grade - V2.6)
 * Fix: Aggressive Placeholder Cleanup & Snippet Handling
 */

function markdownToHtml(md) {
    if (!md) return '';
    if (md.trim().startsWith('<')) return md;
    let html = md;
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    html = html.replace(/\n{2,}/g, '</p><p>');
    html = '<p>' + html + '</p>';
    html = html.replace(/<p>\s*<(h[1-3]|ul|li)/g, '<$1');
    html = html.replace(/<\/(h[1-3]|ul|li)>\s*<\/p>/g, '</$1>');
    html = html.replace(/<p>\s*<\/p>/g, '');
    html = html.replace(/\\"/g, '"');
    return html;
}

export default {
    async fetch(request, env) {
        const url = new URL(request.url);
        const path = url.pathname;
        const SB_URL = env.SUPABASE_URL || "https://nbfzhxgkfljeuoncujum.supabase.co";
        const SB_KEY = env.SUPABASE_KEY;

        if (!SB_KEY) return new Response("Error: Config missing", { status: 500 });

        try {
            if (path.startsWith("/p/")) {
                const slug = path.split("/p/")[1];
                const sb_res = await fetch(`${SB_URL}/rest/v1/grich_keywords_pool?slug=eq.${slug}&select=*`, {
                    headers: { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}` }
                });
                const data = await sb_res.json();
                if (!data || data.length === 0) return new Response("Audit Not Found", { status: 404 });

                const record = data[0];
                const title = record.keyword;
                let content = markdownToHtml(record.final_article);

                // 1. Snippet Extraction (If AI output full HTML tags)
                content = content.replace(/<!DOCTYPE.*?>/gi, '');
                content = content.replace(/<html.*?>/gi, '');
                content = content.replace(/<head.*?>.*?<\/head>/gi, '');
                content = content.replace(/<body.*?>/gi, '');
                content = content.replace(/<\/body>/gi, '');
                content = content.replace(/<\/html>/gi, '');

                // 2. Fetch Template
                const tplRes = await fetch("https://raw.githubusercontent.com/baifan7574/soeasyhub-v2-main/main/template.html");
                let html = await tplRes.text();

                // 3. Global Loop-Closed Injection
                const payhipLink = `https://payhip.com/b/qoGLF?product_id=${slug}`;
                
                // Cleanup template of old placeholders
                html = html.replaceAll("{{TITLE}}", title);
                
                // Prepare content (internal replace)
                content = content.replaceAll("{{TITLE}}", title);
                content = content.replaceAll("{{title}}", title);
                content = content.replaceAll("{{PDF_LINK}}", payhipLink);

                // Inject content
                html = html.replace("{{CONTENT}}", content);
                
                // Final sweep of any remaining placeholders
                html = html.replaceAll("{{TITLE}}", title);
                html = html.replaceAll("{{PDF_LINK}}", payhipLink);

                const metaDesc = `Download the 2026 Official ${title} Audit Report. Validated state requirements.`;
                html = html.replace("{{METADATA}}", `<meta name="description" content="${metaDesc}">`);

                return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
            }

            // Fallback to static or home
            return fetch(`https://raw.githubusercontent.com/baifan7574/soeasyhub-v2-main/main${path === '/' ? '/index.html' : path}`);

        } catch (e) {
            return new Response(`System Error: ${e.message}`, { status: 500 });
        }
    }
};
