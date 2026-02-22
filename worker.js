/**
 * soeasyhub-v2 Cloudflare Worker (Production Grade - V3.2)
 * Monorepo & Supabase Native Integration
 *
 * Features:
 * - Dynamic Home Grid (Top 100 from DB)
 * - Detail Page Rendering (Markdown -> HTML)
 * - Monetization Hooks (Payhip $29.99)
 * - Dark Mode Styling (Hero Section & Responsive Grid)
 * - Zero Dependencies (Raw Fetch)
 * - AdSense Placeholder (Skill 2 Compliance)
 */

const HTML_TEMPLATE = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}} | SoEasyHub 2026 Audit</title>
    <meta name="description" content="{{DESCRIPTION}}">
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
            --card-bg: #1e293b;
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
            background: rgba(15, 23, 42, 0.9);
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

        /* ===== HERO SECTION ===== */
        .hero {
            text-align: center;
            padding: 80px 20px;
            background: radial-gradient(circle at center, #1e293b 0%, #020617 100%);
            border-bottom: 1px solid var(--border);
            margin-bottom: 40px;
        }

        .hero h1 {
            font-size: 3rem;
            margin: 0 0 20px 0;
            background: linear-gradient(to right, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            color: var(--text-muted);
            font-size: 1.2rem;
            max-width: 600px;
            margin: 0 auto;
        }

        /* ===== GRID LAYOUT ===== */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px 60px 20px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 24px;
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            flex-direction: column;
            text-decoration: none;
            color: inherit;
        }

        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border-color: var(--primary);
        }

        .card-meta {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
        }

        .card-tag {
            background: rgba(249, 115, 22, 0.1);
            color: var(--primary);
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
        }

        .card h3 {
            margin: 0 0 12px 0;
            font-size: 1.25rem;
            line-height: 1.4;
        }

        .card p {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin: 0;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        /* ===== ARTICLE DETAIL ===== */
        .article-container {
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
        }

        .article-content {
            background: var(--card-bg);
            padding: 40px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }

        .article-content h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            line-height: 1.2;
        }

        .article-meta {
            color: var(--text-muted);
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }

        .article-body {
            font-size: 1.1rem;
            line-height: 1.8;
            color: #cbd5e1;
        }
        
        .article-body h2 {
            color: white;
            margin-top: 2rem;
        }
        
        .article-body a {
            color: var(--primary);
        }

        /* ===== MONETIZATION HOOK ===== */
        /* 1. NUCLEAR OPTION: Hide Old Buttons */
        .audit-cta, .promo-box, .cta-container, .payhip-button {
            display: none !important;
        }

        /* 2. NEW MATRIX BUTTON STYLE */
        .matrix-official-btn {
            display: block !important;
            width: 100%;
            max-width: 400px;
            margin: 2rem auto;
            padding: 16px 24px;
            background: #f97316; /* 亮橙色 */
            color: #ffffff !important; /* 强制白字 */
            text-align: center;
            font-weight: 800;
            text-decoration: none;
            border-radius: 8px;
            font-size: 1.1rem;
            box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .matrix-official-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(249, 115, 22, 0.6);
            background: #ea580c;
        }

        /* Legacy styles kept for reference but overridden */
        .payhip-box {
            background: linear-gradient(135deg, rgba(249,115,22,0.1) 0%, rgba(15,23,42,0.3) 100%);
            border: 1px solid var(--primary);
            border-radius: 8px;
            padding: 24px;
            margin: 40px 0;
            text-align: center;
        }

        .payhip-btn {
            display: inline-block;
            background: var(--primary);
            color: white;
            font-weight: 700;
            padding: 12px 30px;
            border-radius: 6px;
            text-decoration: none;
            margin-top: 15px;
            transition: background 0.2s;
            font-size: 1.1rem;
        }

        .payhip-btn:hover {
            background: var(--primary-hover);
        }

        .price-tag {
            font-size: 1.5rem;
            font-weight: 800;
            color: white;
            margin-bottom: 8px;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
            font-size: 0.9rem;
            border-top: 1px solid var(--border);
            margin-top: 60px;
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="nav-inner">
            <a href="/" class="logo">SoEasyHub <span>AUDIT</span></a>
            <div>
                <a href="/" class="back-link">Home</a>
            </div>
        </div>
    </header>

    {{CONTENT}}

    <footer class="footer">
        <p>&copy; 2026 SoEasyHub Audit Systems. All Rights Reserved.</p>
        <p>Disclaimer: Not legal advice. For informational purposes only.</p>
    </footer>
</body>
</html>`;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Supabase Config (from Environment Variables)
    const SUPABASE_URL = env.SUPABASE_URL;
    const SUPABASE_KEY = env.SUPABASE_KEY;

    if (!SUPABASE_URL || !SUPABASE_KEY) {
      return new Response("Configuration Error: Missing Database Credentials", { status: 500 });
    }

    // Helper: Supabase Fetch
    async function supabaseFetch(endpoint, options = {}) {
      const headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": `Bearer ${SUPABASE_KEY}`,
        "Content-Type": "application/json",
        ...options.headers
      };
      const response = await fetch(`${SUPABASE_URL}/rest/v1/${endpoint}`, {
        ...options,
        headers
      });
      if (!response.ok) {
        throw new Error(`Supabase Error: ${response.status} ${response.statusText}`);
      }
      return response.json();
    }

    // === ROUTE 1: HOME PAGE (Grid) ===
    if (path === "/" || path === "/index.html") {
      try {
        // Query: Get top 100 articles (where final_article is not null)
        // Fields: id, slug, keyword, category, last_mined_at
        const data = await supabaseFetch(
          `grich_keywords_pool?select=id,slug,keyword,category,last_mined_at&final_article=not.is.null&order=last_mined_at.desc&limit=100`
        );

        let gridHtml = "";
        
        if (data.length === 0) {
            gridHtml = `<div style="text-align:center; padding: 40px;">No audit reports published yet.</div>`;
        } else {
            gridHtml = `<div class="container">
                <div class="hero">
                    <h1>Regulatory Compliance Hub</h1>
                    <p>Instant access to 2026 state-level reciprocity audits and licensing guides.</p>
                </div>
                <div class="grid">`;

            data.forEach(item => {
                // Infer State from Keyword (Simple Heuristic)
                let state = "US";
                const states = ["California", "Texas", "Florida", "New York", "Illinois", "Ohio", "Georgia", "North Carolina", "Michigan", "New Jersey", "Virginia", "Washington", "Arizona", "Massachusetts", "Tennessee", "Indiana", "Missouri", "Maryland", "Wisconsin", "Colorado", "Minnesota", "South Carolina", "Alabama", "Louisiana", "Kentucky", "Oregon", "Oklahoma", "Connecticut", "Utah", "Iowa", "Nevada", "Arkansas", "Mississippi", "Kansas", "New Mexico", "Nebraska", "Idaho", "West Virginia", "Hawaii", "New Hampshire", "Maine", "Rhode Island", "Montana", "Delaware", "South Dakota", "North Dakota", "Alaska", "Vermont", "Wyoming"];
                
                for (const s of states) {
                    if (item.keyword.toLowerCase().includes(s.toLowerCase())) {
                        state = s;
                        break;
                    }
                }

                const date = item.last_mined_at ? new Date(item.last_mined_at).toLocaleDateString() : "2026-02-20";
                const title = item.keyword.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

                gridHtml += `
                <a href="/p/${item.slug}" class="card">
                    <div class="card-meta">
                        <span class="card-tag">${state.toUpperCase()}</span>
                        <span>${date}</span>
                    </div>
                    <h3>${title}</h3>
                    <p>Comprehensive audit report regarding ${item.keyword} requirements and compliance standards for ${state}.</p>
                </a>`;
            });

            gridHtml += `</div></div>`;
        }

        const html = HTML_TEMPLATE
            .replace('{{TITLE}}', 'Home')
            .replace('{{DESCRIPTION}}', 'Access thousands of regulatory compliance audit reports.')
            .replace('{{METADATA}}', '')
            .replace('{{CONTENT}}', gridHtml);

        return new Response(html, {
          headers: { "Content-Type": "text/html; charset=utf-8" },
        });

      } catch (err) {
        return new Response(`Error loading home: ${err.message}`, { status: 500 });
      }
    }

    // === ROUTE 2: DETAIL PAGE (/p/{slug}) ===
    if (path.startsWith("/p/")) {
      const slug = path.split("/p/")[1];
      
      if (!slug) return new Response("Invalid Slug", { status: 400 });

      try {
        // Query: Get article content
        const data = await supabaseFetch(
            `grich_keywords_pool?select=keyword,final_article,last_mined_at,category&slug=eq.${slug}&limit=1`
        );

        if (data.length === 0) {
            return new Response("Article Not Found", { status: 404 });
        }

        const article = data[0];
        const title = article.keyword.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        const date = article.last_mined_at ? new Date(article.last_mined_at).toLocaleDateString() : "2026-02-20";

        // Monetization Hook
        // UPDATED: Simple CTA Button as requested
        const monetizationBlock = `
        <div class="payhip-box-v2" style="text-align: center; margin: 40px 0;">
            <a href="https://payhip.com/b/qoGLF?product_id=${slug}" class="matrix-official-btn" target="_blank">
              UNLOCK OFFICIAL AUDIT REPORT ($29.99)
            </a>
            <p style="font-size: 0.9rem; margin-top: 10px; color: #94a3b8;">Secure Payment via Stripe/PayPal • Instant PDF Download</p>
        </div>`;

        // Inject Monetization into Content (Top 30% and Bottom)
        let content = article.final_article || "<p>Content pending...</p>";
        
        // Remove existing HTML/Head/Body tags if present (since we wrap it)
        content = content.replace(/<!DOCTYPE html>/gi, '')
                         .replace(/<html.*?>/gi, '')
                         .replace(/<\/html>/gi, '')
                         .replace(/<head>[\s\S]*?<\/head>/gi, '') // Remove head completely
                         .replace(/<body.*?>/gi, '')
                         .replace(/<\/body>/gi, '');

        // === HOT FIX: Remove Old Buttons (Source A) ===
        // Remove <div class="audit-cta"... </div> and <div class="promo-box"... </div>
        // Using a greedy match for the div content might be dangerous if nested, 
        // but assuming standard structure from previous scripts.
        content = content.replace(/<div class="audit-cta"[\s\S]*?<\/div>/gi, '');
        content = content.replace(/<div class="promo-box"[\s\S]*?<\/div>/gi, '');

        // Naive Injection: Find the 3rd <h2> or 3rd <p>
        // Better: Append to end, and insert after first significant block
        const paragraphs = content.split('</p>');
        if (paragraphs.length > 5) {
            // Insert after 30%
            const injectIndex = Math.floor(paragraphs.length * 0.3);
            paragraphs.splice(injectIndex, 0, monetizationBlock);
            content = paragraphs.join('</p>');
        } else {
            content = content + monetizationBlock;
        }
        
        // Append at bottom too if long enough
        if (paragraphs.length > 10) {
            content += monetizationBlock;
        }

        const articleHtml = `
        <div class="article-container">
            <div class="article-content">
                <div class="article-meta">
                    <span>${article.category || 'Compliance'}</span> • <span>${date}</span>
                </div>
                <h1>${title}</h1>
                <div class="article-body">
                    ${content}
                </div>
            </div>
        </div>`;

        const html = HTML_TEMPLATE
            .replace('{{TITLE}}', title)
            .replace('{{DESCRIPTION}}', `Compliance audit for ${title}.`)
            .replace('{{METADATA}}', `<meta name="robots" content="index, follow">`)
            .replace('{{CONTENT}}', articleHtml);

        return new Response(html, {
          headers: { "Content-Type": "text/html; charset=utf-8" },
        });

      } catch (err) {
         return new Response(`Error loading article: ${err.message}`, { status: 500 });
      }
    }

    // === ROUTE 3: SITEMAP.XML ===
    if (path === "/sitemap.xml") {
        try {
            const data = await supabaseFetch(
                `grich_keywords_pool?select=slug,last_mined_at&final_article=not.is.null&limit=1000`
            );
            
            let xml = `<?xml version="1.0" encoding="UTF-8"?>
            <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                <url>
                    <loc>https://soeasyhub.com/</loc>
                    <changefreq>daily</changefreq>
                    <priority>1.0</priority>
                </url>`;
            
            data.forEach(item => {
                xml += `
                <url>
                    <loc>https://soeasyhub.com/p/${item.slug}</loc>
                    <lastmod>${item.last_mined_at ? item.last_mined_at.split('T')[0] : '2026-02-20'}</lastmod>
                    <changefreq>weekly</changefreq>
                    <priority>0.8</priority>
                </url>`;
            });
            
            xml += `</urlset>`;
            
            return new Response(xml, {
                headers: { "Content-Type": "application/xml" }
            });

        } catch (err) {
            return new Response("Error generating sitemap", { status: 500 });
        }
    }

    // Fallback
    return new Response("Not Found", { status: 404 });
  },
};
