/**
 * soeasyhub-v2 Cloudflare Worker (Production Grade - V2.1)
 * Mission: Zero-Server Dynamic Orchestration with Loop Prevention
 */

export default {
    async fetch(request, env) {
        const url = new URL(request.url);
        const path = url.pathname;

        // Credentials from Environment/Secrets
        const SB_URL = env.SUPABASE_URL || "https://nbfzhxgkfljeuoncujum.supabase.co";
        const SB_KEY = env.SUPABASE_KEY;

        if (!SB_KEY) {
            return new Response("Error: SUPABASE_KEY missing in Worker env.", { status: 500 });
        }

        try {
            // 1. Home Page Logic: Dynamic "Recently Sealed Audits" List
            if (path === "/" || path === "/index.html") {
                // FETCH SKELETON FROM GITHUB (To avoid Worker subrequest loop)
                const indexRes = await fetch("https://raw.githubusercontent.com/baifan7574/soeasyhub-v2-main/main/index.html");
                if (!indexRes.ok) throw new Error("Failed to fetch index skeleton from GitHub.");
                let html = await indexRes.text();

                // Fetch latest 10 refined records from Supabase
                const sb_res = await fetch(`${SB_URL}/rest/v1/grich_keywords_pool?is_refined=eq.true&select=slug,keyword,last_mined_at&order=last_mined_at.desc&limit=10`, {
                    headers: { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}` }
                });
                if (!sb_res.ok) {
                    const errBody = await sb_res.text();
                    throw new Error(`Supabase Fetch Failed (Home) | Status: ${sb_res.status} ${sb_res.statusText} | Body: ${errBody}`);
                }
                const records = await sb_res.json();

                let gridHtml = '';
                records.forEach(r => {
                    gridHtml += `
                    <a href="/p/${r.slug}" class="audit-card">
                        <div style="font-size: 0.7rem; color: #64748b;">#AUD-${r.slug.substring(0, 3).toUpperCase()}</div>
                        <div style="font-weight: bold; margin: 10px 0;">${r.keyword}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">Status: Sealed & Audit Ready</div>
                    </a>`;
                });

                html = html.replace("<!-- DYNAMIC_GRID -->", gridHtml);
                return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
            }

            // 2. Dynamic Article Routing: /p/slug-name
            if (path.startsWith("/p/")) {
                const slug = path.split("/p/")[1];

                // Fetch Data from Supabase
                const sb_res = await fetch(`${SB_URL}/rest/v1/grich_keywords_pool?slug=eq.${slug}&select=*`, {
                    headers: { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}` }
                });
                if (!sb_res.ok) {
                    const errBody = await sb_res.text();
                    throw new Error(`Supabase Fetch Failed (Detail) | Status: ${sb_res.status} ${sb_res.statusText} | Body: ${errBody}`);
                }
                const data = await sb_res.json();

                if (!data || data.length === 0) return new Response("Audit Location Not Found", { status: 404 });

                const record = data[0];
                const article = record.final_article || "<h1>Audit Under Construction...</h1><p>Our auditors are currently processing this request. Estimate: 5 minutes.</p>";
                const title = record.keyword || "Compliance Audit";

                // Robust PDF Extraction
                let pdfUrl = "#";
                if (record.pdf_url) {
                    pdfUrl = record.pdf_url;
                } else if (record.content_json && record.content_json.pdf_url_cloud) {
                    pdfUrl = record.content_json.pdf_url_cloud;
                }

                // FETCH MASTER TEMPLATE FROM GITHUB
                const templateRes = await fetch("https://raw.githubusercontent.com/baifan7574/soeasyhub-v2-main/main/template.html");
                if (!templateRes.ok) throw new Error("Failed to fetch template from GitHub.");
                let html = await templateRes.text();

                // Inject Content & Logic
                html = html.replaceAll("{{PDF_LINK}}", pdfUrl);
                html = html.replace("{{TITLE}}", title)
                    .replace("{{CONTENT}}", article)
                    .replace("{{METADATA}}", `<meta name="description" content="Download the 2026 Official ${title} Audit Report. Complete fee breakdown and application SOP.">`);

                return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
            }

            // Fallback for sitemap or other static files
            if (path === "/sitemap.xml") {
                const sitemapRes = await fetch("https://raw.githubusercontent.com/baifan7574/soeasyhub-v2-main/main/sitemap.xml");
                const xml = await sitemapRes.text();
                return new Response(xml, { headers: { "Content-Type": "application/xml" } });
            }

            // Final fallback: Try to get from Raw GitHub
            return fetch(`https://raw.githubusercontent.com/baifan7574/soeasyhub-v2-main/main${path}`);

        } catch (err) {
            return new Response(`Worker Fatal Error: ${err.message}`, { status: 500 });
        }
    }
};
