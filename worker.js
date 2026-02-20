/**
 * soeasyhub-v2 Cloudflare Worker (Production Grade - V3.1)
 * Monorepo & Supabase Native Integration
 * 
 * Features:
 * - Dynamic Home Grid (Top 100)
 * - Detail Page Rendering (Markdown -> HTML)
 * - Monetization Hooks (Payhip $29.99)
 * - Dark Mode Styling
 * - Zero Dependencies (Raw Fetch)
 * - AdSense Placeholder (Skill 2 Compliance)
 */

const HTML_TEMPLATE = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}} | SoEasyHub 2026 Audit</title>
    {{METADATA}}
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #f97316;
            --primary-hover: #ea580c;
            --dark: #0f172a;
            --dark-surface: #1e293b;
            --text: #e2e8f0;
            --text-muted: #94a3b8;
            --bg: #020617;
            --border: #334155;
        }

        body {
            margin: 0;
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }

        /* ===== HEADER ===== */
        .header {
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 50;
            padding: 15px 0;
        }

        .nav-inner {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-weight: 800;
            font-size: 1.5rem;
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .logo span {
            color: var(--primary);
            background: rgba(249, 115, 22, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
        }

        .back-link {
            font-size: 0.9rem;
            color: var(--text-muted);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }

        .back-link:hover {
            color: var(--primary);
        }

        /* ===== HERO SECTION ===== */
        .hero {
            text-align: center;
            padding: 80px 20px;
            background: radial-gradient(circle at center, #1e293b 0%, #020617 100%);
            border-bottom: 1px solid var(--border);
        }

        .hero h1 {
            font-size: 3rem;
            margin: 0 0 20px 0;
            background: linear-gradient(to right, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            font-size: 1.2rem;
            color: var(--text-muted);
            max-width: 600px;
            margin: 0 auto;
        }

        /* ===== GRID LAYOUT ===== */
        .container {
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }

        .card {
            background: var(--dark-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.2s, border-color 0.2s;
            display: flex;
            flex-direction: column;
            text-decoration: none;
            color: inherit;
        }

        .card:hover {
            transform: translateY(-4px);
            border-color: var(--primary);
        }

        .card-tag {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--primary);
            font-weight: 700;
            margin-bottom: 10px;
        }

        .card h3 {
            margin: 0 0 10px 0;
            font-size: 1.2rem;
            line-height: 1.4;
            color: white;
        }

        .card-meta {
            margin-top: auto;
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--text-muted);
            border-top: 1px solid rgba(255,255,255,0.05);
            padding-top: 15px;
        }

        /* ===== DETAIL PAGE ===== */
        .paper {
            background: var(--dark-surface);
            padding: 50px;
            border-radius: 16px;
            border: 1px solid var(--border);
            max-width: 800px;
            margin: 0 auto;
        }

        .audit-meta {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }

        .meta-tag {
            background: rgba(255,255,255,0.05);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            color: var(--text-muted);
            border: 1px solid rgba(255,255,255,0.1);
        }

        h1.article-title {
            font-size: 2.5rem;
            margin-bottom: 30px;
            line-height: 1.2;
        }

        /* Content Styling */
        .content h2 {
            color: white;
            border-left: 4px solid var(--primary);
            padding-left: 15px;
            margin-top: 40px;
        }

        .content h3 {
            color: #e2e8f0;
            margin-top: 30px;
        }

        .content a {
            color: var(--primary);
        }

        .content ul, .content ol {
            padding-left: 20px;
            color: var(--text-muted);
        }
        
        .content li {
            margin-bottom: 8px;
        }

        .content p {
            color: #cbd5e1;
        }

        /* Action Box */
        .action-box {
            background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(15, 23, 42, 0.5) 100%);
            border: 1px solid rgba(249, 115, 22, 0.3);
            border-radius: 12px;
            padding: 30px;
            margin: 50px 0;
            text-align: center;
        }

        .btn-download {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: var(--primary);
            color: white;
            padding: 16px 40px;
            border-radius: 50px;
            font-weight: 700;
            font-size: 1.1rem;
            text-decoration: none;
            transition: 0.2s;
            margin-top: 20px;
        }

        .btn-download:hover {
            background: var(--primary-hover);
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(249, 115, 22, 0.4);
        }

        .secure-badge {
            margin-top: 15px;
            font-size: 0.8rem;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }

        /* AdSense Slot */
        .ad-slot {
            display: {{ADS_DISPLAY}};
            background: rgba(255,255,255,0.02);
            border: 1px dashed var(--border);
            padding: 20px;
            text-align: center;
            margin: 30px 0;
            color: var(--text-muted);
            font-size: 0.8rem;
        }

        .footer {
            text-align: center;
            padding: 60px 0;
            color: var(--text-muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--border);
            margin-top: 80px;
        }

        @media (max-width: 640px) {
            .paper { padding: 20px; }
            h1.article-title { font-size: 1.8rem; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="nav-inner">
            <a href="/" class="logo">SoEasyHub <span>PRO</span></a>
            {{NAV_LINK}}
        </div>
    </div>

    {{BODY_CONTENT}}

    <div class="footer">
        © 2026 SoEasyHub Compliance Network.<br>
        Official 3rd-Party Audit. Not affiliated with government agencies.
    </div>
</body>
</html>
`;

function markdownToHtml(md) {
    if (!md) return '';
    let html = md;
    // Basic Markdown Parsing
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    html = html.replace(/\n{2,}/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    html = '<p>' + html + '</p>';
    // Cleanup
    html = html.replace(/<p>\s*<(h[1-3]|ul|li)/g, '<$1');
    html = html.replace(/<\/(h[1-3]|ul|li)>\s*<\/p>/g, '</$1>');
    html = html.replace(/<p>\s*<\/p>/g, '');
    return html;
}

export default {
    async fetch(request, env) {
        const url = new URL(request.url);
        const path = url.pathname;
        const SB_URL = env.SUPABASE_URL;
        const SB_KEY = env.SUPABASE_KEY;

        if (!SB_URL || !SB_KEY) {
            return new Response("Critical Error: Missing Database Config", { status: 500 });
        }

        const headers = {
            "apikey": SB_KEY,
            "Authorization": `Bearer ${SB_KEY}`,
            "Content-Type": "application/json"
        };

        try {
            // === HOME PAGE ===
            if (path === "/" || path === "/index.html") {
                const sb_res = await fetch(`${SB_URL}/rest/v1/grich_keywords_pool?select=slug,keyword,category,state&final_article=not.is.null&order=is_refined.desc,last_mined_at.desc&limit=100`, { headers });
                
                if (!sb_res.ok) throw new Error(`DB Error: ${sb_res.status}`);
                const articles = await sb_res.json();

                let gridHtml = `<div class="hero">
                    <h1>License Compliance made Simple.</h1>
                    <p>Access 2026 Official Audit Reports for Cross-State Licensing Reciprocity.</p>
                </div>
                <div class="container"><div class="grid">`;

                articles.forEach(art => {
                    const category = art.category !== 'Uncategorized' ? art.category : (art.state || 'General');
                    gridHtml += `
                    <a href="/p/${art.slug}" class="card">
                        <div class="card-tag">${category}</div>
                        <h3>${art.keyword}</h3>
                        <div class="card-meta">
                            <span>${art.state || 'US'}</span>
                            <span>2026 Audit</span>
                        </div>
                    </a>`;
                });
                gridHtml += `</div></div>`;

                let html = HTML_TEMPLATE.replace("{{TITLE}}", "Home");
                html = html.replace("{{METADATA}}", `<meta name="description" content="Official 2026 Reciprocity Audit Reports for Nursing, Teaching, Medical, and Trade Licenses across 50 States.">`);
                html = html.replace("{{NAV_LINK}}", "");
                html = html.replace("{{BODY_CONTENT}}", gridHtml);
                html = html.replace("{{ADS_DISPLAY}}", "none"); // No Ads on Home
                
                return new Response(html, { headers: { "content-type": "text/html;charset=UTF-8" } });
            }

            // === DETAIL PAGE ===
            if (path.startsWith("/p/")) {
                const slug = path.split("/p/")[1];
                const sb_res = await fetch(`${SB_URL}/rest/v1/grich_keywords_pool?slug=eq.${slug}&select=*`, { headers });
                
                if (!sb_res.ok) throw new Error(`DB Error: ${sb_res.status}`);
                const data = await sb_res.json();
                
                if (!data || data.length === 0) {
                    return new Response("Audit Report Not Found (Queued for production)", { status: 404 });
                }

                const record = data[0];
                const title = record.keyword;
                const contentHtml = markdownToHtml(record.final_article);
                const payhipLink = `https://payhip.com/b/qoGLF?product_id=${slug}`;

                const detailHtml = `
                <div class="container">
                    <div class="paper">
                        <div class="audit-meta">
                            <span class="meta-tag">Status: Active</span>
                            <span class="meta-tag">Updated: 2026</span>
                            <span class="meta-tag">${record.state || 'Federal'}</span>
                        </div>
                        <h1 class="article-title">${title}</h1>
                        <div class="content">
                            <!-- Ad Slot 1 -->
                            <div class="ad-slot">Sponsored Content</div>
                            
                            ${contentHtml}
                            
                            <!-- MONETIZATION HOOK -->
                            <div class="action-box">
                                <h3 style="color:#f97316; margin-top:0;">📥 Official 2026 Audit Report (PDF)</h3>
                                <p style="color:#cbd5e1;">Get the complete application package including hidden reciprocity rules, fee tables, and direct contact list.</p>
                                <a href="${payhipLink}" class="btn-download">Download Full Report ($29.99)</a>
                                <div class="secure-badge">🔒 Secure Payment via Payhip • Instant Delivery</div>
                            </div>
                        </div>
                    </div>
                </div>`;

                let html = HTML_TEMPLATE.replace("{{TITLE}}", title);
                html = html.replace("{{METADATA}}", `<meta name="description" content="Download the 2026 Official ${title} Audit Report. Validated state requirements.">`);
                html = html.replace("{{NAV_LINK}}", `<a href="/" class="back-link">← All Audits</a>`);
                html = html.replace("{{BODY_CONTENT}}", detailHtml);
                
                // Ads Logic
                const adsDisplay = env.ADSENSE_ID ? "block" : "none";
                html = html.replace("{{ADS_DISPLAY}}", adsDisplay);

                return new Response(html, { headers: { "content-type": "text/html;charset=UTF-8" } });
            }

            // === SITEMAP ===
            if (path === "/sitemap.xml") {
                 const sb_res = await fetch(`${SB_URL}/rest/v1/grich_keywords_pool?select=slug,last_mined_at&final_article=not.is.null&limit=1000`, { headers });
                 const articles = await sb_res.json();
                 
                 let xml = `<?xml version="1.0" encoding="UTF-8"?>
                 <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                    <url><loc>https://soeasyhub.com/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>`;
                 
                 articles.forEach(art => {
                     xml += `<url><loc>https://soeasyhub.com/p/${art.slug}</loc><lastmod>${art.last_mined_at.split('T')[0]}</lastmod><priority>0.8</priority></url>`;
                 });
                 
                 xml += `</urlset>`;
                 return new Response(xml, { headers: { "content-type": "application/xml" } });
            }

            return new Response("Not Found", { status: 404 });

        } catch (e) {
            return new Response(`System Error: ${e.message}`, { status: 500 });
        }
    }
};
