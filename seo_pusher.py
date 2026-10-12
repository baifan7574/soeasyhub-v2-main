"""Check reviewed, live articles; optionally notify IndexNow of changed content.

No database reads, Google Indexing API calls, or website deployments. The default
CLI invocation only checks public pages. All network requests have bounded time
and size, and failures result in a nonzero exit with a machine-readable report.
"""

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET


SITE_ORIGIN = "https://soeasyhub.com"
SITEMAP_URL = SITE_ORIGIN + "/sitemap.xml"
ROBOTS_URL = SITE_ORIGIN + "/robots.txt"
CORE_ARTICLE_URLS = (
    SITE_ORIGIN + "/p/nursing-license-endorsement-to-texas",
    SITE_ORIGIN + "/p/texas-nursing-license-reciprocity-states",
    SITE_ORIGIN + "/p/nursing-license-requirements-texas",
)
# Public ownership-verification value, already served by the live Worker.
INDEXNOW_KEY = "822834cd8b83498a90e4fd5ef715fa14"
KEY_URL = SITE_ORIGIN + "/" + INDEXNOW_KEY + ".txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class SeoError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


@dataclass
class HttpResponse:
    status: int
    headers: dict
    body: bytes


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_http(url, *, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"User-Agent": "SoEasyHub-SEO-Health/2.0"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        try:
            response = build_opener(NoRedirect()).open(request, timeout=15)
        except HTTPError as error:
            response = error
        with response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                raise SeoError("response_too_large", "HTTP response exceeded the size limit.")
            return HttpResponse(response.status, _combine_headers(response.headers.items()), body)
    except (URLError, TimeoutError, OSError) as error:
        # Raw exception text and HTTP response bodies can contain sensitive data.
        raise SeoError("transport_error", "HTTP transport failed (" + type(error).__name__ + ").") from None


def _request(fetch, url, **kwargs):
    try:
        return fetch(url, **kwargs)
    except SeoError:
        raise
    except Exception as error:
        raise SeoError("transport_error", "HTTP transport failed (" + type(error).__name__ + ").") from None


def _combine_headers(items):
    headers = {}
    for key, value in items:
        name = key.lower()
        headers[name] = headers[name] + ", " + value if name in headers else value
    return headers


def _headers(response):
    return _combine_headers(response.headers.items())


def _require_200(response, label):
    if response.status != 200:
        raise SeoError("http_error", label + " returned HTTP " + str(response.status) + ".")


def get_latest_urls(fetch=fetch_http):
    """Read the live sitemap; only the three explicitly reviewed guides qualify.

    The historical function name is kept for callers. This no longer means
    arbitrary latest database records. Empty/missing core entries are an error.
    """
    response = _request(fetch, SITEMAP_URL)
    _require_200(response, "Sitemap")
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError:
        raise SeoError("invalid_sitemap", "Sitemap is not valid XML.") from None
    if root.tag != "{" + SITEMAP_NS + "}urlset":
        raise SeoError("invalid_sitemap", "Expected a sitemap urlset with the standard namespace.")
    urls = set()
    entries = root.findall("{" + SITEMAP_NS + "}url")
    if not entries:
        raise SeoError("empty_source", "Sitemap has no URL entries; source health is unproven.")
    for entry in entries:
        locations = entry.findall("{" + SITEMAP_NS + "}loc")
        if len(locations) != 1 or not locations[0].text:
            raise SeoError("invalid_sitemap", "Each sitemap entry must contain one URL.")
        url = locations[0].text.strip()
        parts = urlsplit(url)
        if (parts.scheme != "https" or parts.netloc != "soeasyhub.com"
                or parts.query or parts.fragment or not parts.path.startswith("/")):
            raise SeoError("invalid_sitemap_url", "Sitemap contains a noncanonical or foreign URL.")
        if url in CORE_ARTICLE_URLS:
            urls.add(url)
    if urls != set(CORE_ARTICLE_URLS):
        raise SeoError("scope_mismatch", "Sitemap is missing one or more reviewed core guides.")
    return sorted(urls)


def validate_robots(urls, fetch=fetch_http):
    response = _request(fetch, ROBOTS_URL)
    _require_200(response, "Robots file")
    try:
        text = response.body.decode("utf-8")
    except UnicodeDecodeError:
        raise SeoError("invalid_robots", "Robots file is not UTF-8.") from None
    if not re.search(r"^\s*user-agent\s*:", text, re.IGNORECASE | re.MULTILINE):
        raise SeoError("invalid_robots", "Robots file is missing a user-agent directive.")
    robots = RobotFileParser()
    robots.parse(text.splitlines())
    if SITEMAP_URL not in (robots.site_maps() or []):
        raise SeoError("invalid_robots", "Robots file does not advertise the canonical live sitemap.")
    # Conservative guard: do not resolve conflicting Allow rules or bot groups.
    # Any Disallow that could cover a core guide requires a human robots review.
    # This also handles '*' and terminal '$', unlike RobotFileParser.can_fetch.
    for line in text.splitlines():
        directive = line.split("#", 1)[0].strip()
        if ":" not in directive:
            continue
        name, pattern = directive.split(":", 1)
        pattern = unquote(pattern.strip())
        if name.strip().lower() != "disallow" or not pattern:
            continue
        anchored = pattern.endswith("$")
        if anchored:
            pattern = pattern[:-1]
        expression = "^" + re.escape(pattern).replace(r"\*", ".*") + ("$" if anchored else "")
        if any(re.search(expression, urlsplit(url).path) for url in urls):
            raise SeoError("robots_blocked", "A robots Disallow could block a core guide; review the crawl rules.")


class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonicals = []
        self.noindex = False
        self.in_h1 = False
        self.h1_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonicals.append(attrs.get("href", ""))
        if tag == "meta" and attrs.get("name", "").lower() in ("robots", "googlebot", "bingbot"):
            if re.search(r"\b(noindex|none)\b", attrs.get("content", "").lower()):
                self.noindex = True
        if tag == "h1":
            self.in_h1 = True

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_h1:
            self.h1_text.append(data)


def validate_pages(urls, fetch=fetch_http):
    fingerprints = {}
    for url in urls:
        if url not in CORE_ARTICLE_URLS:
            raise SeoError("scope_mismatch", "Attempted to check an unreviewed article URL.")
        response = _request(fetch, url)
        _require_200(response, "Core guide")
        headers = _headers(response)
        if headers.get("content-type", "").split(";", 1)[0].strip().lower() != "text/html":
            raise SeoError("invalid_page", "Core guide did not return HTML.")
        if re.search(r"\b(noindex|none)\b", headers.get("x-robots-tag", "").lower()):
            raise SeoError("noindex", "Core guide has an indexing block in HTTP headers.")
        try:
            html = response.body.decode("utf-8")
        except UnicodeDecodeError:
            raise SeoError("invalid_page", "Core guide HTML is not UTF-8.") from None
        metadata = PageMetadata()
        metadata.feed(html)
        if metadata.noindex:
            raise SeoError("noindex", "Core guide has an indexing block in HTML metadata.")
        if metadata.canonicals != [url]:
            raise SeoError("canonical_mismatch", "Core guide canonical must match its live /p/ URL exactly.")
        if not "".join(metadata.h1_text).strip() or "{{" in html:
            raise SeoError("invalid_page", "Core guide is empty or contains unresolved placeholders.")
        fingerprints[url] = hashlib.sha256(response.body).hexdigest()
    return fingerprints


def load_state(path):
    if not path.exists():
        return {}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or document.get("version") != 1:
            raise ValueError()
        fingerprints = document["fingerprints"]
        if not isinstance(fingerprints, dict):
            raise ValueError()
        for url, digest in fingerprints.items():
            if (url not in CORE_ARTICLE_URLS or not isinstance(digest, str)
                    or re.fullmatch(r"[0-9a-f]{64}", digest) is None):
                raise ValueError()
        return fingerprints
    except (OSError, ValueError, KeyError, TypeError):
        raise SeoError("invalid_state", "Previous submission state is unreadable or invalid.") from None


def _write_json(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=path.name + ".", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def push_to_bing(urls, fetch=fetch_http):
    """Submit only after validating the existing public ownership key."""
    if not urls or any(url not in CORE_ARTICLE_URLS for url in urls):
        raise SeoError("scope_mismatch", "IndexNow requires reviewed article URLs.")
    verification = _request(fetch, KEY_URL)
    _require_200(verification, "IndexNow verification file")
    if verification.body.strip() != INDEXNOW_KEY.encode("ascii"):
        raise SeoError("key_verification_failed", "IndexNow ownership file did not match the existing public key.")
    response = _request(fetch, INDEXNOW_ENDPOINT, method="POST", payload={
        "host": "soeasyhub.com", "key": INDEXNOW_KEY,
        "keyLocation": KEY_URL, "urlList": urls,
    })
    if response.status not in (200, 202):
        raise SeoError("submission_failed", "IndexNow returned HTTP " + str(response.status) + ".")
    return response.status


def run(*, submit, state_file, report_file, fetch=fetch_http):
    if state_file.resolve() == report_file.resolve():
        # An error report must never overwrite the accepted-submission ledger.
        print(json.dumps({"status": "error", "error_code": "invalid_paths",
                          "error": "State and report files must use different paths."}), file=sys.stderr)
        return 1
    report = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "source": SITEMAP_URL, "scope": "three_reviewed_texas_nursing_guides",
              "mode": "submit_indexnow" if submit else "read_only",
              "status": "error", "google_indexing_api": "not_used_for_articles"}
    phase = "state_read"
    try:
        previous = load_state(state_file)
        report["baseline_present"] = state_file.exists()
        phase = "source_read"
        urls = get_latest_urls(fetch)
        phase = "robots_validation"
        validate_robots(urls, fetch)
        phase = "page_validation"
        fingerprints = validate_pages(urls, fetch)
        changed = [url for url in urls if previous.get(url) != fingerprints[url]]
        report.update({"source_read": "ok", "validated_urls": urls,
                       "changed_urls": changed, "changed_count": len(changed),
                       "submission": "not_attempted"})
        if not submit:
            report["status"] = "healthy_read_only"
        elif not changed:
            report["status"] = "healthy_no_changes"
        else:
            phase = "indexnow_submission"
            status = push_to_bing(changed, fetch)
            report.update({"status": "healthy_submitted", "indexnow_http_status": status,
                           "submission": "accepted" if status == 200 else "accepted_key_validation_pending"})
            phase = "state_write"
            _write_json(state_file, {"version": 1, "fingerprints": fingerprints})
        exit_code = 0
    except SeoError as error:
        report.update({"status": "error", "error_code": error.code,
                       "error": str(error), "failed_phase": phase})
        exit_code = 1
    except Exception as error:
        report.update({"status": "error", "error_code": "unexpected_error",
                       "error": "Operation failed (" + type(error).__name__ + ").", "failed_phase": phase})
        exit_code = 1
    try:
        _write_json(report_file, report)
    except OSError:
        print("SEO health error: unable to write report.", file=sys.stderr)
        return 1
    print(json.dumps(report, sort_keys=True))
    return exit_code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submit-indexnow", action="store_true", help="Explicitly permit an external notification for changed, validated guides.")
    parser.add_argument("--state-file", type=Path, default=Path(".seo/state.json"))
    parser.add_argument("--report-file", type=Path, default=Path(".seo/report.json"))
    args = parser.parse_args(argv)
    return run(submit=args.submit_indexnow, state_file=args.state_file, report_file=args.report_file)


if __name__ == "__main__":
    sys.exit(main())
