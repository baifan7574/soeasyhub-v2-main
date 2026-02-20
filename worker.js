/**
 * soeasyhub-v2 Cloudflare Worker (Production Grade - V2.7)
 * Fix: Inline Template & Config Handling
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
            --dark: #0f172a;
            --text: #334155;
            --light-bg: #f8fafc;
        }

        body {
            margin: 0;
            font-family: 'Inter', sans-serif;
            background: var(--light-bg);
            color: var(--text);
            line-height: 1.8;
        }

        /* ===== HEADER ===== */
        .header {
            background: white;
            border-bottom: 1px solid #e2e8f0;
            position: sticky;
            top: 0;
            z-index: 50;
            padding: 15px 0;
        }

        .nav-inner {
            max-width: 900px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-weight: 800;
            font-size: 1.2rem;
            color: var(--dark);
            text-decoration: none;
        }

        .logo span {
            color: var(--primary);
        }

        .back-link {
            font-size: 0.9rem;
            color: #64748b;
            text-decoration: none;
            font-weight: 500;
        }

        .back-link:hover {
            color: var(--primary);
        }

        /* ===== MAIN CONTENT ===== */
        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
        }

        .paper {
            background: white;
            padding: 50px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: 1px solid #f1f5f9;
        }

        /* ===== TITLES ISOLATION ===== */
        h1 {
            font-size: 2.2rem;
            line-height: 1.3;
            color: var(--dark);
            margin-bottom: 10px;
            letter-spacing: -0.02em;
        }

        .audit-meta {
            font-size: 0.9rem;
            color: #94a3b8;
            margin-bottom: 30px;
            display: flex;
            gap: 15px;
            font-weight: 500;
        }

        .meta-tag {
            background: #f1f5f9;
            padding: 2px 10px;
            border-radius: 4px;
            color: #475569;
        }

        /* ===== CONTENT STYLING ===== */
        .content {
            font-size: 1.05rem;
            color: #334155;
        }

        .content h2 {
            font-size: 1.5rem;
            margin-top: 40px;
            margin-bottom: 20px;
            color: var(--dark);
            border-left: 4px solid var(--primary);
            padding-left: 15px;
        }

        .content h3 {
            font-size: 1.2rem;
            margin-top: 30px;
            color: #1e293b;
            font-weight: 600;
        }

        .content ul {
            padding-left: 20px;
            margin-bottom: 20px;
        }

        .content li {
            margin-bottom: 10px;
        }

        .content strong {
            color: var(--dark);
            font-weight: 600;
        }

        .content a {
            color: var(--primary);
            text-decoration: underline;
            text-decoration-color: rgba(249, 115, 22, 0.3);
            text-underline-offset: 3px;
        }

        .content a:hover {
            text-decoration-color: var(--primary);
        }

        /* ===== ACTION BOX ===== */
        .action-box {
            background: linear-gradient(135deg, #fffbeb 0%, #fff7ed 100%);
            border: 1px solid #fed7aa;
            border-radius: 12px;
            padding: 30px;
            margin: 40px 0;
            text-align: center;
        }

        .action-title {
            font-weight: 700;
            color: #9a3412;
            margin-bottom: 10px;
            font-size: 1.2rem;
        }

        .action-text {
            color: #c2410c;
            margin-bottom: 25px;
            font-size: 0.95rem;
        }

        .btn-download {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            background: #ea580c;
            color: white;
            padding: 16px 40px;
            border-radius: 50px;
            font-weight: 700;
            font-size: 1.1rem;
            text-decoration: none;
            transition: 0.2s;
            box-shadow: 0 10px 15px -3px rgba(234, 88, 12, 0.3);
        }

        .btn-download:hover {
            background: #c2410c;
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgba(234, 88, 12, 0.4);
        }

        .secure-badge {
            margin-top: 15px;
            font-size: 0.8rem;
            color: #94a3b8;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }

        /* ===== ADS ===== */
        .ad-slot {
            background: #f8fafc;
            border: 2px dashed #e2e8f0;
            border-radius: 8px;
            margin: 40px 0;
            padding: 20px;
            text-align: center;
            color: #cbd5e1;
            font-size: 0.9rem;

            display: {
                    {
                    ADS_DISPLAY
                }
            }

            ;
            /* Controlled by worker */
        }

        /* ===== FOOTER ===== */
        .footer {
            text-align: center;
            padding: 60px 0;
            color: #94a3b8;
            font-size: 0.85rem;
        }

        @media (max-width: 640px) {
            .paper {
                padding: 25px;
            }

            h1 {
                font-size: 1.8rem;
            }

            .btn-download {
                width: 100%;
                box-sizing: border-box;
            }
        }
    </style>
</head>

<body>
    <div class="header">
        <div class="nav-inner">
            <a href="/" class="logo">SoEasyHub <span>v2</span></a>
            <a href="/" class="back-link">← All Audits</a>
        </div>
    </div>

    <div class="container">
        <div class="paper">
            <div class="audit-meta">
                <span class="meta-tag">2026 Edition</span>
                <span class="meta-tag">Verified Source</span>
                <span class="meta-tag">PDF Ready</span>
            </div>
            <h1>{{TITLE}}</h1>

            <div class="content">
                {{CONTENT}}

                <!-- MONETIZATION LOCK -->
                <div class="action-box">
                    <div class="action-title">📥 Need the Official PDF Report?</div>
                    <div class="action-text">Get the complete 2026 application package, including step-by-step SOPs, fee
                        breakdowns, and direct contact list.</div>
                    <a href="{{PDF_LINK}}" class="btn-download">
                        Download Full Audit Report ($29.90)
                    </a>
                    <div class="secure-badge">🔒 Secure Payment via Payhip • Instant Delivery</div>
                </div>

                <!-- AD PLACEHOLDER -->
                <div class="ad-slot">Sponsored Content Space</div>
            </div>
        </div>
    </div>

    <div class="footer">
        © 2026 SoEasyHub Compliance Network.<br>Official 3rd-Party Audit. Not affiliated with government agencies.
    </div>
</body>

</html>`;

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
        
        // Prioritize SUPABASE_SERVICE_ROLE_KEY if available (Production), else SUPABASE_KEY (Local/Dev)
        const SB_KEY = env.SUPABASE_SERVICE_ROLE_KEY || env.SUPABASE_KEY;

        if (!SB_KEY) return new Response("Error: Config missing (SUPABASE_KEY/SERVICE_ROLE_KEY)", { status: 500 });

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

                // 2. Use Inlined Template
                let html = HTML_TEMPLATE;

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
