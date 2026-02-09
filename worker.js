/**
 * soeasyhub-v2 Cloudflare Worker (Production Grade)
 * Mission: Zero-Server Dynamic Orchestration
 */

export default {
    async fetch(request, env) {
        const url = new URL(request.url);
        const path = url.pathname;

        // Use secrets from Cloudflare Secrets (env)
        const SB_URL = env.SUPABASE_URL;
        const SB_KEY = env.SUPABASE_KEY;

        // 1. Home Page Logic: Dynamic "Recently Sealed Audits" List
        if (path === "/" || path === "/index.html") {
            const indexRes = await fetch(request); // Fetch the skeleton
            let html = await indexRes.text();

            // Fetch latest 10 refined records
            const sb_res = await fetch(`${SB_URL}/rest/v1/grich_keywords_pool?is_refined=eq.true&select=slug,keyword,created_at&order=created_at.desc&limit=10`, {
                headers: { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}` }
            });
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
            return await renderArticle(slug, SB_URL, SB_KEY);
        }

        return fetch(request);
    }
};

async function renderArticle(slug, SB_URL, SB_KEY) {
    const res = await fetch(`${SB_URL}/rest/v1/grich_keywords_pool?slug=eq.${slug}&select=*`, {
        headers: { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}` }
    });

    const data = await res.json();
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

    // Fetch master template
    const templateRes = await fetch("https://soeasyhub.com/template.html");
    let html = await templateRes.text();

    // Inject Content & Logic
    html = html.replaceAll("{{PDF_LINK}}", pdfUrl); // Replace in all spots including content
    html = html.replace("{{TITLE}}", title)
        .replace("{{CONTENT}}", article)
        .replace("{{METADATA}}", `<meta name="description" content="Download the 2026 Official ${title} Audit Report. Complete fee breakdown and application SOP.">`);

    return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}
