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
    <title>{{TITLE}} | SoEasyHub 2026</title>
    <meta name="description" content="{{DESCRIPTION}}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --secondary: #0f172a;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #334155;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --accent: #f59e0b;
            --teacher-bg: #eff6ff;
            --teacher-border: #bfdbfe;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }

        /* ===== NAVBAR ===== */
        .header {
            background: var(--card-bg);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 50;
            padding: 15px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
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
            color: var(--secondary);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .logo span {
            color: white;
            background: var(--primary);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
        }

        .nav-links {
            display: flex;
            gap: 24px;
        }

        .nav-links a {
            color: var(--text);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            transition: color 0.2s;
        }

        .nav-links a:hover {
            color: var(--primary);
        }

        /* ===== FOOTER ===== */
        .footer {
            background: var(--secondary);
            color: #94a3b8;
            padding: 60px 20px;
            margin-top: 60px;
        }

        .footer-inner {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
        }

        .footer h3 {
            color: white;
            margin-bottom: 16px;
            font-size: 1.2rem;
        }

        .footer-links {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }

        .footer-links a {
            color: #cbd5e1;
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .footer-links a:hover {
            color: white;
            text-decoration: underline;
        }

        .footer-disclaimer {
            font-size: 0.8rem;
            line-height: 1.6;
            border-top: 1px solid #334155;
            padding-top: 20px;
            margin-top: 20px;
            grid-column: 1 / -1;
        }

        @media (max-width: 768px) {
            .nav-links { display: none; }
            .footer-inner { grid-template-columns: 1fr; }
        }

        /* ===== COMMON CONTENT STYLES ===== */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .static-page {
            max-width: 800px;
            background: var(--card-bg);
            padding: 40px;
            border-radius: 12px;
            border: 1px solid var(--border);
            margin: 40px auto;
        }

        .static-page h1 { margin-bottom: 24px; color: var(--secondary); }
        .static-page h2 { margin: 24px 0 12px 0; color: var(--secondary); }
        .static-page p { margin-bottom: 16px; }

        /* Inject Page Specific CSS Below */
        {{PAGE_CSS}}
    </style>
</head>
<body>
    <header class="header">
        <div class="nav-inner">
            <a href="/" class="logo">SoEasyHub <span>Compliance</span></a>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/about">About Us</a>
                <a href="/contact">Contact</a>
            </div>
        </div>
    </header>

    {{CONTENT}}

    <footer class="footer">
        <div class="footer-inner">
            <div>
                <h3>SoEasyHub Compliance Network</h3>
                <p style="margin-bottom: 15px;">Navigate State Compliance with Confidence. No Legal Jargon, Just Clear Steps.</p>
                <div class="footer-links">
                    <a href="/privacy">Privacy Policy</a>
                    <a href="/terms">Terms of Service</a>
                    <a href="/contact">Contact Us</a>
                </div>
            </div>
            <div>
                <h3>Our Mission</h3>
                <p>Founded by Bai, an educator, legal expert, and counselor. We are dedicated to making multi-state business compliance transparent, accessible, and stress-free for entrepreneurs across America.</p>
            </div>
            <div class="footer-disclaimer">
                <strong>Disclaimer:</strong> The materials provided on this website are for informational and educational purposes only and do not constitute legal advice. While we strive to ensure the accuracy of our compliance reports, state regulations change frequently. Please consult with a licensed attorney in your local jurisdiction before making business decisions. We use cookies and third-party advertising partners (such as Google AdSense) to support this free resource.
                <br><br>&copy; 2026 SoEasyHub. All Rights Reserved.
            </div>
        </div>
    </footer>
    {{SCRIPTS}}
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

    // === ROUTE 0: Google Search Console Verification ===
    if (path === "/googleleaf4d2d986493bb7e.html") {
      return new Response("google-site-verification: googleleaf4d2d986493bb7e.html", {
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
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
            const pageCss = `
            .hero {
                text-align: center;
                padding: 100px 20px 80px;
                background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
                border-bottom: 1px solid var(--border);
            }
            .hero h1 {
                font-size: 3.5rem;
                font-weight: 800;
                color: var(--secondary);
                margin-bottom: 24px;
                line-height: 1.2;
            }
            .hero p {
                font-size: 1.25rem;
                color: var(--text-muted);
                max-width: 700px;
                margin: 0 auto 40px;
            }
            .search-box {
                max-width: 600px;
                margin: 0 auto;
                position: relative;
            }
            .search-box input {
                width: 100%;
                padding: 20px 24px;
                font-size: 1.1rem;
                border: 2px solid var(--border);
                border-radius: 50px;
                outline: none;
                transition: border-color 0.2s;
            }
            .search-box input:focus {
                border-color: var(--primary);
            }
            .founder-section {
                background: var(--card-bg);
                padding: 80px 20px;
                border-bottom: 1px solid var(--border);
            }
            .founder-inner {
                max-width: 1000px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                gap: 60px;
            }
            .founder-img {
                width: 160px;
                height: 160px;
                border-radius: 50%;
                background: #e2e8f0;
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 4rem;
                color: white;
            }
            .founder-content h2 {
                font-size: 2rem;
                color: var(--secondary);
                margin-bottom: 16px;
            }
            .founder-content p {
                font-size: 1.1rem;
                color: var(--text);
                margin-bottom: 16px;
                line-height: 1.8;
            }
            .founder-content strong {
                color: var(--primary);
            }
            .grid-section {
                background: var(--bg);
                padding: 80px 20px;
            }
            .grid-inner {
                max-width: 1200px;
                margin: 0 auto;
            }
            .grid-title {
                text-align: center;
                margin-bottom: 50px;
                font-size: 2.2rem;
                color: var(--secondary);
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                gap: 24px;
            }
            .card {
                background: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 24px;
                transition: transform 0.2s, box-shadow 0.2s;
                text-decoration: none;
                color: inherit;
                display: flex;
                flex-direction: column;
            }
            .card:hover {
                transform: translateY(-4px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.05);
                border-color: var(--primary);
            }
            .card-meta {
                display: flex;
                justify-content: space-between;
                font-size: 0.85rem;
                color: var(--text-muted);
                margin-bottom: 16px;
            }
            .card-tag {
                background: var(--teacher-bg);
                color: var(--primary);
                padding: 4px 10px;
                border-radius: 6px;
                font-weight: 600;
            }
            .card h3 {
                font-size: 1.25rem;
                color: var(--secondary);
                margin-bottom: 12px;
                line-height: 1.4;
            }
            .card p {
                color: var(--text-muted);
                font-size: 0.95rem;
                line-height: 1.6;
            }
            @media (max-width: 768px) {
                .founder-inner { flex-direction: column; text-align: center; gap: 30px; }
                .hero h1 { font-size: 2.5rem; }
            }
            `;

            gridHtml = `
            <div class="hero">
                <h1>Navigate State Compliance<br>with Confidence.</h1>
                <p>No legal jargon. Just clear, actionable steps for your multi-state licensing and business registration.</p>
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Search for professions... e.g., Counselor, Teacher, CPA">
                </div>
            </div>

            <div class="founder-section">
                <div class="founder-inner">
                    <div class="founder-img">B</div>
                    <div class="founder-content">
                        <h2>Meet Our Founder</h2>
                        <p>Hi, I'm <strong>Bai</strong>. As an educator, legal expert, and licensed counselor, I know firsthand the anxiety that entrepreneurs face when dealing with state regulations. The legal jargon, the hidden fees, the endless paperwork—it's overwhelming.</p>
                        <p>That's why my team and I built SoEasyHub. We combine legal expertise with a teacher's clarity to break down complex state licensing requirements into simple, stress-free guides.</p>
                    </div>
                </div>
            </div>

            <div class="grid-section">
                <div class="grid-inner">
                    <h2 class="grid-title">Latest Compliance Guides</h2>
                    <div class="grid" id="auditGrid">`;

            data.forEach(item => {
                let state = "US";
                const states = ["California", "Texas", "Florida", "New York", "Illinois", "Ohio", "Georgia", "North Carolina", "Michigan", "New Jersey", "Virginia", "Washington", "Arizona", "Massachusetts", "Tennessee", "Indiana", "Missouri", "Maryland", "Wisconsin", "Colorado", "Minnesota", "South Carolina", "Alabama", "Louisiana", "Kentucky", "Oregon", "Oklahoma", "Connecticut", "Utah", "Iowa", "Nevada", "Arkansas", "Mississippi", "Kansas", "New Mexico", "Nebraska", "Idaho", "West Virginia", "Hawaii", "New Hampshire", "Maine", "Rhode Island", "Montana", "Delaware", "South Dakota", "North Dakota", "Alaska", "Vermont", "Wyoming"];
                
                for (const s of states) {
                    if (item.keyword.toLowerCase().includes(s.toLowerCase())) {
                        state = s;
                        break;
                    }
                }

                const date = item.last_mined_at ? new Date(item.last_mined_at).toLocaleDateString('en-US', {month:'short', day:'numeric', year:'numeric'}) : "Feb 20, 2026";
                const title = item.keyword.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

                gridHtml += `
                <a href="/p/${item.slug}" class="card audit-card">
                    <div class="card-meta">
                        <span class="card-tag">${state.toUpperCase()}</span>
                        <span>${date}</span>
                    </div>
                    <h3>${title}</h3>
                    <p>Complete regulatory breakdown for ${item.keyword} across state jurisdictions.</p>
                </a>`;
            });

            gridHtml += `</div>
                </div>
            </div>`;
            
            const scripts = `
            <script>
                document.getElementById('searchInput').addEventListener('input', function(e) {
                    const term = e.target.value.toLowerCase();
                    const cards = document.querySelectorAll('.audit-card');
                    cards.forEach(card => {
                        const text = card.textContent.toLowerCase();
                        card.style.display = text.includes(term) ? '' : 'none';
                    });
                });
            </script>`;

            const html = HTML_TEMPLATE
                .replace('{{TITLE}}', 'Multi-State Business Compliance Guides')
                .replace('{{DESCRIPTION}}', 'SoEasyHub provides clear, stress-free compliance guides for multi-state licensing, built by legal experts and educators.')
                .replace('{{PAGE_CSS}}', pageCss)
                .replace('{{CONTENT}}', gridHtml)
                .replace('{{SCRIPTS}}', scripts);

            return new Response(html, {
              headers: { "Content-Type": "text/html; charset=utf-8" },
            });
        }
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
        const date = article.last_mined_at ? new Date(article.last_mined_at).toLocaleDateString('en-US', {month:'long', day:'numeric', year:'numeric'}) : "February 20, 2026";

        let content = article.final_article || "<p>Content pending...</p>";
        
        // Strip out existing full HTML wrapper from the database content
        content = content.replace(/<!DOCTYPE html>/gi, '')
                         .replace(/<html.*?>/gi, '')
                         .replace(/<\/html>/gi, '')
                         .replace(/<head>[\s\S]*?<\/head>/gi, '')
                         .replace(/<body.*?>/gi, '')
                         .replace(/<\/body>/gi, '');

        // Remove old monetization boxes completely
        content = content.replace(/<div class="monetization-box"[\s\S]*?<\/div>/gi, '')
                         .replace(/<div class="audit-cta"[\s\S]*?<\/div>/gi, '')
                         .replace(/<div class="promo-box"[\s\S]*?<\/div>/gi, '')
                         .replace(/<div class="cta-container"[\s\S]*?<\/div>/gi, '')
                         .replace(/<a href="{{PDF_LINK}}"[\s\S]*?<\/a>/gi, '');

        // Remove "Explore Related Pathways" and all related links at the bottom
        content = content.replace(/<h[234][^>]*>Explore Related Pathways<\/h[234]>[\s\S]*/gi, '');
        content = content.replace(/<h[234][^>]*>Related Pathways<\/h[234]>[\s\S]*/gi, '');

        // Generate the Monetization Button (Restored!)
        const monetizationBlock = `
        <div style="text-align: center; margin: 50px 0; background: #fff7ed; padding: 30px; border-radius: 12px; border: 2px dashed #f97316;">
            <h3 style="color: #ea580c; margin-top: 0; margin-bottom: 15px; font-size: 1.4rem;">Ready to Fast-Track Your Compliance?</h3>
            <a href="https://payhip.com/b/qoGLF?product_id=${slug}" target="_blank" style="display: inline-block; background: #f97316; color: #ffffff !important; font-weight: 800; padding: 18px 36px; border-radius: 8px; text-decoration: none; font-size: 1.15rem; box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4); transition: transform 0.2s;">
              UNLOCK OFFICIAL AUDIT REPORT ($29.99)
            </a>
            <p style="font-size: 0.95rem; margin-top: 15px; margin-bottom: 0; color: #64748b;">Secure Payment via Stripe/PayPal • Instant PDF Download</p>
        </div>`;

        // Inject the payment button into the content (middle and end)
        const paragraphs = content.split('</p>');
        if (paragraphs.length > 5) {
            const injectIndex = Math.floor(paragraphs.length * 0.4);
            paragraphs.splice(injectIndex, 0, monetizationBlock);
            content = paragraphs.join('</p>');
        }
        
        // Always append a payment button at the very bottom
        content += monetizationBlock;

        // Generate the "Teacher's Note" block at the start
        const stateMatch = title.match(/(California|Texas|Florida|New York|Illinois|Ohio|Georgia|North Carolina|Michigan|New Jersey|Virginia|Washington|Arizona|Massachusetts|Tennessee|Indiana|Missouri|Maryland|Wisconsin|Colorado|Minnesota|South Carolina|Alabama|Louisiana|Kentucky|Oregon|Oklahoma|Connecticut|Utah|Iowa|Nevada|Arkansas|Mississippi|Kansas|New Mexico|Nebraska|Idaho|West Virginia|Hawaii|New Hampshire|Maine|Rhode Island|Montana|Delaware|South Dakota|North Dakota|Alaska|Vermont|Wyoming)/i);
        const stateName = stateMatch ? stateMatch[0] : "your state";
        
        const teacherNote = `
        <div class="teacher-note">
            <strong>Quick Note from Bai:</strong> 
            Dealing with compliance in ${stateName} can feel overwhelming, but don't let the paperwork stress you out. Take a deep breath! The process usually takes a few weeks, so grab a cup of coffee, follow the steps below carefully, and you'll be licensed before you know it. We're in this together.
        </div>`;

        // Create the new structure
        const articleHtml = `
        <div class="article-container">
            <div class="article-content">
                <div class="article-category">${article.category || 'Compliance Guide'}</div>
                <h1>${title}</h1>
                
                <div class="author-box">
                    <div class="author-avatar">B</div>
                    <div class="author-info">
                        <div class="author-name">Written by SoEasyHub Research Team</div>
                        <div class="author-role">Legally Reviewed by Bai (Lead Counsel) • Updated ${date}</div>
                    </div>
                </div>

                ${teacherNote}

                <div class="article-body">
                    ${content}
                </div>
            </div>
        </div>`;

        const pageCss = `
        .article-container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
        .article-content { background: var(--card-bg); padding: 50px; border-radius: 16px; border: 1px solid var(--border); box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
        .article-category { color: var(--primary); font-weight: 700; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; margin-bottom: 15px; }
        .article-content h1 { font-size: 2.8rem; color: var(--secondary); margin-bottom: 30px; line-height: 1.2; font-weight: 800; }
        
        .author-box { display: flex; align-items: center; gap: 15px; padding-bottom: 30px; border-bottom: 1px solid var(--border); margin-bottom: 40px; }
        .author-avatar { width: 50px; height: 50px; border-radius: 50%; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; }
        .author-name { font-weight: 700; color: var(--secondary); font-size: 1rem; }
        .author-role { color: var(--text-muted); font-size: 0.85rem; margin-top: 2px; }

        .teacher-note { background: var(--teacher-bg); border-left: 4px solid var(--primary); padding: 20px; border-radius: 0 8px 8px 0; margin-bottom: 40px; color: var(--text); font-size: 1.05rem; line-height: 1.6; }
        .teacher-note strong { color: var(--primary); display: block; margin-bottom: 8px; font-size: 1.1rem; }

        .article-body { font-size: 1.15rem; line-height: 1.8; color: var(--text); }
        .article-body h2 { color: var(--secondary); margin: 40px 0 20px; font-size: 1.8rem; font-weight: 700; }
        .article-body h3 { color: var(--secondary); margin: 30px 0 15px; font-size: 1.4rem; font-weight: 600; }
        .article-body p { margin-bottom: 24px; }
        .article-body ul, .article-body ol { margin: 0 0 24px 24px; padding: 0; }
        .article-body li { margin-bottom: 10px; }
        .article-body a { color: var(--primary); text-decoration: underline; font-weight: 500; }
        .article-body a:hover { color: var(--primary-hover); }
        .article-body table { width: 100%; border-collapse: collapse; margin-bottom: 24px; }
        .article-body th, .article-body td { border: 1px solid var(--border); padding: 12px; text-align: left; }
        .article-body th { background: var(--bg); color: var(--secondary); font-weight: 600; }

        @media (max-width: 768px) {
            .article-content { padding: 30px 20px; }
            .article-content h1 { font-size: 2.2rem; }
        }
        `;

        const html = HTML_TEMPLATE
            .replace('{{TITLE}}', title)
            .replace('{{DESCRIPTION}}', `Detailed legal and compliance guide for ${title}, reviewed by experts.`)
            .replace('{{PAGE_CSS}}', pageCss)
            .replace('{{CONTENT}}', articleHtml)
            .replace('{{SCRIPTS}}', '');

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

    // === ROUTE 4: LEGAL & STATIC PAGES ===
    const staticPages = {
        "/about": {
            title: "About Us | SoEasyHub",
            desc: "Learn about Bai and the team behind SoEasyHub.",
            content: `
            <div class="static-page">
                <h1>About SoEasyHub</h1>
                <p>Welcome to SoEasyHub Compliance Network. We are a dedicated team of legal researchers, educators, and data engineers on a mission to simplify multi-state business compliance.</p>
                <h2>Our Story</h2>
                <p>Founded by Bai—an experienced educator, licensed legal counsel, and psychological counselor—SoEasyHub was born out of a profound understanding of entrepreneurial anxiety. We know that navigating state-by-state regulations can feel like deciphering a foreign language. The stress of missing a deadline or filing the wrong form shouldn't hold your business back.</p>
                <p>That's why we built this platform: to translate complex legal jargon into clear, actionable, stress-free steps.</p>
                <h2>Our Approach (E-E-A-T)</h2>
                <ul>
                    <li><strong>Experience:</strong> Years of handling state reciprocity and licensing applications.</li>
                    <li><strong>Expertise:</strong> Every guide is based on official state board data and legally reviewed.</li>
                    <li><strong>Authoritativeness:</strong> We provide structured, accurate SOPs recognized by industry professionals.</li>
                    <li><strong>Trust:</strong> We prioritize your mental well-being alongside legal compliance, ensuring our guides are not just accurate, but also empathetic.</li>
                </ul>
            </div>`
        },
        "/contact": {
            title: "Contact Us | SoEasyHub",
            desc: "Get in touch with the SoEasyHub team.",
            content: `
            <div class="static-page">
                <h1>Contact Us</h1>
                <p>If you have any questions about our compliance reports, or if you're feeling overwhelmed by the licensing process and need a bit of guidance, we are here for you.</p>
                <h2>Reach Out Directly</h2>
                <p><strong>Email:</strong> <a href="mailto:baifan7574@gmail.com">baifan7574@gmail.com</a></p>
                <p>Our team typically responds within 24-48 business hours. We review all inquiries personally, as we believe every entrepreneur deserves human support.</p>
                <h2>Mailing Address</h2>
                <p>SoEasyHub Compliance Network<br>Legal Research Division<br>(Address provided upon request for official inquiries)</p>
            </div>`
        },
        "/privacy": {
            title: "Privacy Policy | SoEasyHub",
            desc: "Privacy Policy for SoEasyHub.",
            content: `
            <div class="static-page">
                <h1>Privacy Policy</h1>
                <p><em>Last Updated: February 2026</em></p>
                <h2>1. Introduction</h2>
                <p>At SoEasyHub, your privacy is our priority. This policy explains how we collect, use, and protect your information when you visit our site.</p>
                <h2>2. Information We Collect</h2>
                <p>We may collect standard analytics data (like IP addresses, browser types) to improve our site. If you contact us via email, we collect your email address and any information you provide.</p>
                <h2>3. Cookies and Advertising (Google AdSense)</h2>
                <p>We use third-party advertising companies, such as Google, to serve ads when you visit our website. These companies may use cookies (like the DoubleClick cookie) to serve ads based on your prior visits to our website or other websites. You can opt out of personalized advertising by visiting Google Ads Settings.</p>
                <h2>4. Data Security</h2>
                <p>We implement standard security measures to protect your data. However, no internet transmission is 100% secure.</p>
                <h2>5. Contact</h2>
                <p>For privacy inquiries, email us at <a href="mailto:baifan7574@gmail.com">baifan7574@gmail.com</a>.</p>
            </div>`
        },
        "/terms": {
            title: "Terms of Service | SoEasyHub",
            desc: "Terms of Service and Disclaimer for SoEasyHub.",
            content: `
            <div class="static-page">
                <h1>Terms of Service & Disclaimer</h1>
                <p><em>Last Updated: February 2026</em></p>
                <h2>1. Acceptance of Terms</h2>
                <p>By accessing SoEasyHub, you agree to these terms. If you disagree, please do not use our site.</p>
                <h2>2. Educational Purposes Only (Disclaimer)</h2>
                <p><strong>The information provided on SoEasyHub is for educational and informational purposes only and does NOT constitute legal advice.</strong> We are an information aggregator and educational publisher. While our lead counsel reviews content, no attorney-client relationship is formed by using this site. Always consult a local attorney for your specific business needs.</p>
                <h2>3. Intellectual Property</h2>
                <p>The layout, design, and original insights on this site are property of SoEasyHub.</p>
                <h2>4. Limitation of Liability</h2>
                <p>We are not liable for any damages or legal issues arising from the use of our guides. State laws change frequently, and you must verify all requirements with official state boards.</p>
            </div>`
        }
    };

    if (staticPages[path]) {
        const page = staticPages[path];
        const html = HTML_TEMPLATE
            .replace('{{TITLE}}', page.title)
            .replace('{{DESCRIPTION}}', page.desc)
            .replace('{{PAGE_CSS}}', '')
            .replace('{{CONTENT}}', page.content)
            .replace('{{SCRIPTS}}', '');
            
        return new Response(html, {
            headers: { "Content-Type": "text/html; charset=utf-8" },
        });
    }

    // Fallback
    return new Response("Not Found", { status: 404 });
  },
};
