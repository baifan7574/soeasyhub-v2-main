/**
 * soeasyhub-v2 Cloudflare Worker (Production Grade - V2.4)
 * Mission: Zero-Server Dynamic Orchestration with Loop Prevention
 * Skills: 06-grich-deployer (Skill 2, 3, 4, 5, 7) + 04-grich-mixer (Skill 4 Patch)
 */

// Lightweight Markdown  HTML converter (runs in Worker)
function markdownToHtml(md) {
    if (!md) return '';
    // If content already looks like HTML, return as-is
    if (md.trim().startsWith('<')) return md;

    let html = md;
    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    // Formatting
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    // Lists & Paragraphs
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    html = html.replace(/\n{2,}/g, '</p><p>');
    html = '<p>' + html + '</p>';
    // Cleanup
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

        // Credentials & Config
        const SB_URL = env.SUPABASE_URL || "https://nbfzhxgkfljeuoncujum.supabase.co";
        const SB_KEY = env.SUPABASE_KEY;
        const ADS_ON = env.ADSENSE_ID ? "block" : "none"; // Skill 2

        if (!SB_KEY) return new Response("Error: SUPABASE_KEY missing.", { status: 500 });

        try {
            // =================================================================
            // ROUTE 1: HOME PAGE (Skill 3: Visual Engine)
            // =================================================================
            if (path === "/" || path === "/index.html") {
                // Fetch Skeleton
                const indexRes = await fetch("https://raw.githubusercontent.com/baifan7574/soeasyhub-v2-main/main/index.html");
                if (!indexRes.ok) throw new Error("GitHub fetch failed");
                let html = await indexRes.text();

                // Fetch Top 50 Refined Records (For Grid)
                const sb_res = await fetch(`${SB_URL}/rest/v1/grich_keywords_pool?is_refined=eq.true&select=slug,keyword,last_mined_at&order=last_mined_at.desc&limit=50`, {
                    headers: { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}` }
                });
                const records = await sb_res.json();

                let gridHtml = '';
                records.forEach(r => {
                    // Skill 3: Auto-Categorization Logic based on keywords
                    let cat = 'other';
                    const kw = r.keyword.toLowerCase();
                    if (kw.includes('med') || kw.includes('nurs') || kw.includes('health') || kw.includes('doctor') || kw.includes('therap')) cat = 'medical';
                    else if (kw.includes('teach') || kw.includes('school') || kw.includes('educa')) cat = 'education';
                    else if (kw.includes('engin') || kw.includes('archit') || kw.includes('contract')) cat = 'engineering';
                    else if (kw.includes('law') || kw.includes('attorney') || kw.includes('bar') || kw.includes('paralegal')) cat = 'legal';
                    else if (kw.includes('cpa') || kw.includes('account') || kw.includes('insur') || kw.includes('tax')) cat = 'finance';

                    gridHtml += `
                    <a href="/p/${r.slug}" class="audit-card" data-category="${cat}">
                        <div class="card-tag">#AUD-${r.slug.substring(0, 3).toUpperCase()}</div>
                        <div class="card-title">${r.keyword}</div>
                        <div class="card-meta">
                            <span class="card-status">Sealed</span>
                            <span class="card-price">$29.90</span>
                        </div>
                    </a>`;
                });

                html = html.replace("<!-- DYNAMIC_GRID -->", gridHtml);
                html = html.replace('<span id="totalCount">131</span>', `<span id="totalCount">${records.length}+</span>`);
                return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
            }

            // =================================================================
            // ROUTE 2: ARTICLE DETAIL (Skill 4: Payhip Lock)
            // =================================================================
            if (path.startsWith("/p/")) {
                const slug = path.split("/p/")[1];

                // Fetch Data
                const sb_res = await fetch(`${SB_URL}/rest/v1/grich_keywords_pool?slug=eq.${slug}&select=*`, {
                    headers: { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}` }
                });
                const data = await sb_res.json();

                if (!data || data.length === 0) {
                    return new Response("Audit Not Found. System logged request.", { status: 404 });
                }

                const record = data[0];
                let content = markdownToHtml(record.final_article) || "<p>Audit content is being finalized...</p>";
                const title = record.keyword;

                // Skill 4: Payhip Link Lock
                const payhipLink = `https://payhip.com/b/qoGLF?product_id=${slug}`;

                // Fetch Template
                const tplRes = await fetch("https://raw.githubusercontent.com/baifan7574/soeasyhub-v2-main/main/template.html");
                let html = await tplRes.text();

                // Generate Standard Button HTML (Skill 4 Patch)
                const buttonHtml = `
                <div style="background:#fff7ed;border:2px dashed #f97316;padding:30px;border-radius:12px;margin:40px 0;text-align:center;">
                    <h3 style="color:#9a3412;margin-top:0;font-size:1.2rem;">🚀 Skip the Labyrinth: Get Your 2026 ${title} Fast-Track Bible</h3>
                    <p style="color:#c2410c;margin-bottom:20px;font-size:0.95rem;">Unlock the full audit report with fee breakdowns, step-by-step SOPs, and direct contact list.</p>
                    <a href="${payhipLink}" style="display:inline-block;background:#ea580c;color:white;padding:16px 40px;border-radius:50px;font-weight:700;text-decoration:none;font-size:1.1rem;box-shadow:0 10px 15px -3px rgba(234,88,12,0.3);">
                        Download Full Audit Report ($29.90)
                    </a>
                    <div style="margin-top:15px;font-size:0.8rem;color:#94a3b8;">🔒 Secure Payment via Payhip • Instant Delivery</div>
                </div>`;

                // Global Replace: Replace placeholder with actual button code
                content = content.replace(/\[BUY_BUTTON_PLACEHOLDER\]/g, buttonHtml);

                // Injection
                html = html.replace("{{TITLE}}", title);
                html = html.replace("{{CONTENT}}", content);
                html = html.replaceAll("{{PDF_LINK}}", payhipLink); // Fallback for template.html static links
                html = html.replace("{{ADS_DISPLAY}}", ADS_ON);

                // SEO
                const metaDesc = `Download the 2026 Official ${title} Audit Report. Validated state requirements, fees, and application SOPs.`;
                html = html.replace("{{METADATA}}", `<meta name="description" content="${metaDesc}">`);

                return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
            }

            // =================================================================
            // ROUTE 3: SUCCESS CALLBACK (Skill 4 & 5: Fulfillment)
            // =================================================================
            if (path === "/success") {
                const productId = url.searchParams.get("product_id"); // Comes from Payhip redirect

                if (!productId) return new Response("Invalid Purchase Link", { status: 400 });

                // Fetch PDF URL from DB
                const sb_res = await fetch(`${SB_URL}/rest/v1/grich_keywords_pool?slug=eq.${productId}&select=pdf_url,content_json`, {
                    headers: { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}` }
                });
                const data = await sb_res.json();

                if (!data || data.length === 0) return new Response("Product Not Found", { status: 404 });

                const record = data[0];
                let pdfUrl = record.pdf_url || (record.content_json && record.content_json.pdf_url_cloud);

                if (pdfUrl) {
                    // INSTANT DISPATCH: Redirect to the PDF file
                    return Response.redirect(pdfUrl, 302);
                } else {
                    // Skill 5: Fallback Message
                    return new Response(`
                    <html>
                        <body style="font-family:sans-serif;text-align:center;padding:50px;">
                            <h1 style="color:#f97316;">Payment Verified!</h1>
                            <p>Your audit report is currently being finalized by our system.</p>
                            <p><strong>Do not close this window.</strong> We are generating your secure download link...</p>
                            <p style="color:#94a3b8;font-size:0.9rem;">(If it takes longer than 1 minute, the link will be emailed to you.)</p>
                        </body>
                    </html>`, {
                        headers: { "Content-Type": "text/html" }
                    });
                }
            }

            // =================================================================
            // ROUTE 4: SITEMAP (Skill 7: SEO)
            // =================================================================
            if (path === "/sitemap.xml") {
                const mapRes = await fetch("https://raw.githubusercontent.com/baifan7574/soeasyhub-v2-main/main/sitemap.xml");
                return new Response(await mapRes.text(), { headers: { "Content-Type": "application/xml" } });
            }

            // Fallback
            return fetch(`https://raw.githubusercontent.com/baifan7574/soeasyhub-v2-main/main${path}`);

        } catch (e) {
            return new Response(`System Error: ${e.message}`, { status: 500 });
        }
    }
};
