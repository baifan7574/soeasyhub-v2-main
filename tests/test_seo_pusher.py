"""Offline regression checks for the reviewed SoEasyHub SEO publisher.

These tests use only fake HTTP responses and temporary state/report files.
Run from the review directory with: py -m unittest discover -s tests -v
"""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from http.client import HTTPMessage
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seo_pusher as seo


EXPECTED_URLS = (
    "https://soeasyhub.com/p/nursing-license-endorsement-to-texas",
    "https://soeasyhub.com/p/texas-nursing-license-reciprocity-states",
    "https://soeasyhub.com/p/nursing-license-requirements-texas",
)
SECRET_MARKER = "DO_NOT_EXPOSE_RESPONSE_OR_EXCEPTION_91fe7"


def sitemap(urls=EXPECTED_URLS):
    entries = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{entries}</urlset>"
    ).encode("utf-8")


def page(url, *, title="Texas nursing preparation", head="", body=""):
    return (
        "<!doctype html><html><head>"
        f'<link rel="canonical" href="{url}">{head}'
        "</head><body>"
        f"<main><h1>{title}</h1><p>Official instruction checklist.</p>{body}</main>"
        "</body></html>"
    ).encode("utf-8")


def response(body, status=200, headers=None):
    return seo.HttpResponse(
        status=status,
        headers=headers or {"content-type": "text/html; charset=utf-8"},
        body=body,
    )


class FakeFetch:
    """Reject unexpected URLs so a test cannot silently reach a real service."""

    def __init__(self, *, urls=EXPECTED_URLS, submit_status=200):
        self.calls = []
        self.responses = {
            seo.SITEMAP_URL: response(
                sitemap(urls), headers={"content-type": "application/xml"}
            ),
            seo.KEY_URL: response(
                (seo.INDEXNOW_KEY + "\n").encode("ascii"),
                headers={"content-type": "text/plain"},
            ),
            seo.ROBOTS_URL: response(
                f"User-agent: *\nAllow: /\nSitemap: {seo.SITEMAP_URL}\n".encode("utf-8"),
                headers={"content-type": "text/plain"},
            ),
            **{url: response(page(url)) for url in EXPECTED_URLS},
        }
        self.submit_response = response(b"", status=submit_status)

    def __call__(self, url, *, method="GET", payload=None):
        self.calls.append((url, method, deepcopy(payload)))
        if method == "POST":
            if url != "https://api.indexnow.org/indexnow":
                raise AssertionError(f"Unexpected submission destination: {url}")
            result = self.submit_response
        elif method == "GET":
            if url not in self.responses:
                raise AssertionError(f"Unexpected GET destination: {url}")
            result = self.responses[url]
        else:
            raise AssertionError(f"Unexpected HTTP method: {method}")
        if isinstance(result, BaseException):
            raise result
        return result

    @property
    def posts(self):
        return [call for call in self.calls if call[1] == "POST"]


class SitemapTests(unittest.TestCase):
    def assert_source_error(self, fetch):
        with self.assertRaises(seo.SeoError) as caught:
            seo.get_latest_urls(fetch=fetch)
        self.assertTrue(caught.exception.code)

    def test_exact_reviewed_scope_and_published_path(self):
        self.assertEqual(seo.SITE_ORIGIN, "https://soeasyhub.com")
        self.assertEqual(set(seo.CORE_ARTICLE_URLS), set(EXPECTED_URLS))
        self.assertEqual(len(seo.CORE_ARTICLE_URLS), 3)
        self.assertEqual(seo.SITEMAP_URL, "https://soeasyhub.com/sitemap.xml")

    def test_source_is_live_sitemap_and_extra_urls_do_not_expand_scope(self):
        other_urls = (
            "https://soeasyhub.com/",
            "https://soeasyhub.com/packet",
            "https://soeasyhub.com/p/unreviewed-archive-article",
        )
        fetch = FakeFetch(urls=other_urls + EXPECTED_URLS)
        urls = seo.get_latest_urls(fetch=fetch)
        self.assertEqual(set(urls), set(EXPECTED_URLS))
        self.assertEqual(len(urls), 3)
        self.assertEqual(fetch.calls, [(seo.SITEMAP_URL, "GET", None)])

    def test_duplicate_entries_do_not_duplicate_submissions(self):
        fetch = FakeFetch(urls=EXPECTED_URLS + EXPECTED_URLS)
        urls = seo.get_latest_urls(fetch=fetch)
        self.assertEqual(set(urls), set(EXPECTED_URLS))
        self.assertEqual(len(urls), 3)

    def test_empty_source_is_failure_not_no_changes(self):
        self.assert_source_error(FakeFetch(urls=()))

    def test_missing_core_article_is_failure(self):
        self.assert_source_error(FakeFetch(urls=EXPECTED_URLS[:-1]))

    def test_root_path_cannot_replace_published_article_path(self):
        old_root = EXPECTED_URLS[0].replace("/p/", "/")
        self.assert_source_error(FakeFetch(urls=(old_root,) + EXPECTED_URLS[1:]))

    def test_foreign_host_cannot_replace_core_article(self):
        foreign = EXPECTED_URLS[0].replace("soeasyhub.com", "other.example")
        self.assert_source_error(FakeFetch(urls=(foreign,) + EXPECTED_URLS[1:]))

    def test_foreign_url_is_rejected_even_when_all_core_urls_are_present(self):
        foreign = "https://other.example/p/foreign-article"
        self.assert_source_error(FakeFetch(urls=EXPECTED_URLS + (foreign,)))

    def test_invalid_xml_and_wrong_document_root_are_failures(self):
        invalid_documents = (
            b"<urlset><url><loc>broken",
            b"<html><body>Temporary server message</body></html>",
            b'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>',
            sitemap().replace(b' xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', b""),
        )
        for document in invalid_documents:
            with self.subTest(document=document):
                fetch = FakeFetch()
                fetch.responses[seo.SITEMAP_URL] = response(document)
                self.assert_source_error(fetch)

    def test_503_source_is_failure_even_with_valid_xml_body(self):
        fetch = FakeFetch()
        fetch.responses[seo.SITEMAP_URL] = response(sitemap(), status=503)
        self.assert_source_error(fetch)

    def test_dns_and_timeout_are_reportable_source_failures(self):
        for error in (socket.gaierror("DNS failed"), TimeoutError("timed out")):
            with self.subTest(error=type(error).__name__):
                fetch = FakeFetch()
                fetch.responses[seo.SITEMAP_URL] = error
                self.assert_source_error(fetch)


class HttpTransportTests(unittest.TestCase):
    class NetworkResponse:
        def __init__(self, body):
            self.status = 200
            self.headers = {"Content-Type": "text/plain"}
            self.body = body
            self.read_limit = None
            self.closed = False

        def __enter__(self):
            return self

        def __exit__(self, *_):
            self.closed = True

        def read(self, limit):
            self.read_limit = limit
            return self.body[:limit]

    def test_real_wrapper_bounds_timeout_body_and_does_not_follow_redirects(self):
        network_response = self.NetworkResponse(b"Public response")
        opener = Mock()
        opener.open.return_value = network_response
        with patch.object(seo, "build_opener", return_value=opener) as factory:
            actual = seo.fetch_http(seo.SITEMAP_URL)
        self.assertEqual(actual.status, 200)
        self.assertEqual(actual.body, b"Public response")
        self.assertEqual(network_response.read_limit, seo.MAX_RESPONSE_BYTES + 1)
        self.assertTrue(network_response.closed)
        self.assertIsInstance(factory.call_args.args[0], seo.NoRedirect)
        self.assertEqual(opener.open.call_args.kwargs["timeout"], 15)
        self.assertIsNone(
            factory.call_args.args[0].redirect_request(None, None, 302, "Redirect", {}, "https://other.example/")
        )

    def test_post_wrapper_sends_only_the_supplied_json_payload(self):
        payload = {"host": "soeasyhub.com", "urlList": list(EXPECTED_URLS)}
        opener = Mock()
        opener.open.return_value = self.NetworkResponse(b"")
        with patch.object(seo, "build_opener", return_value=opener):
            seo.fetch_http(seo.INDEXNOW_ENDPOINT, method="POST", payload=payload)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.indexnow.org/indexnow")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(json.loads(request.data), payload)
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertIsNone(request.get_header("Authorization"))

    def test_http_error_is_returned_as_a_status_for_health_validation(self):
        opener = Mock()
        opener.open.side_effect = HTTPError(
            seo.SITEMAP_URL, 503, "Unavailable", {"Content-Type": "text/plain"},
            io.BytesIO(SECRET_MARKER.encode()),
        )
        output = io.StringIO()
        with patch.object(seo, "build_opener", return_value=opener), redirect_stdout(output), redirect_stderr(output):
            actual = seo.fetch_http(seo.SITEMAP_URL)
        self.assertEqual(actual.status, 503)
        self.assertNotIn(SECRET_MARKER, output.getvalue())

    def test_transport_exceptions_are_wrapped_without_raw_error_text(self):
        for network_error in (
            URLError(SECRET_MARKER),
            TimeoutError(SECRET_MARKER),
            socket.gaierror(SECRET_MARKER),
        ):
            with self.subTest(error=type(network_error).__name__):
                opener = Mock()
                opener.open.side_effect = network_error
                with patch.object(seo, "build_opener", return_value=opener):
                    with self.assertRaises(seo.SeoError) as caught:
                        seo.fetch_http(seo.SITEMAP_URL)
                self.assertEqual(caught.exception.code, "transport_error")
                self.assertNotIn(SECRET_MARKER, str(caught.exception))

    def test_oversized_response_is_rejected_and_closed(self):
        network_response = self.NetworkResponse(b"x" * (seo.MAX_RESPONSE_BYTES + 1))
        opener = Mock()
        opener.open.return_value = network_response
        with patch.object(seo, "build_opener", return_value=opener):
            with self.assertRaises(seo.SeoError) as caught:
                seo.fetch_http(seo.SITEMAP_URL)
        self.assertEqual(caught.exception.code, "response_too_large")
        self.assertTrue(network_response.closed)

    def test_duplicate_http_robots_headers_preserve_noindex_in_both_orders(self):
        url = EXPECTED_URLS[0]
        for values in (("noindex", "index"), ("index", "noindex")):
            with self.subTest(values=values):
                # HTTPMessage preserves duplicate wire headers, unlike dict().
                headers = HTTPMessage()
                headers.add_header("Content-Type", "text/html; charset=utf-8")
                for value in values:
                    headers.add_header("X-Robots-Tag", value)
                network_response = self.NetworkResponse(page(url))
                network_response.headers = headers
                opener = Mock()
                opener.open.return_value = network_response
                with patch.object(seo, "build_opener", return_value=opener):
                    actual = seo.fetch_http(url)
                fetch = FakeFetch()
                fetch.responses[url] = actual
                with self.assertRaises(seo.SeoError) as caught:
                    seo.validate_pages([url], fetch=fetch)
                self.assertEqual(caught.exception.code, "noindex")


class RobotsTests(unittest.TestCase):
    def assert_blocked(self, rules):
        document = f"{rules}\nSitemap: {seo.SITEMAP_URL}\n"
        fetch = FakeFetch()
        fetch.responses[seo.ROBOTS_URL] = response(
            document.encode(), headers={"content-type": "text/plain"}
        )
        with self.assertRaises(seo.SeoError) as caught:
            seo.validate_robots(list(EXPECTED_URLS), fetch=fetch)
        self.assertEqual(caught.exception.code, "robots_blocked")

    def test_current_public_rules_allow_both_search_engines(self):
        fetch = FakeFetch()
        seo.validate_robots(list(EXPECTED_URLS), fetch=fetch)
        self.assertEqual(fetch.calls, [(seo.ROBOTS_URL, "GET", None)])

    def test_global_and_engine_specific_article_blocks_are_rejected(self):
        documents = (
            f"User-agent: *\nDisallow: /p/\nSitemap: {seo.SITEMAP_URL}\n",
            f"User-agent: Googlebot\nDisallow: /p/\n\nUser-agent: *\nAllow: /\nSitemap: {seo.SITEMAP_URL}\n",
            f"User-agent: Bingbot\nDisallow: /p/\n\nUser-agent: *\nAllow: /\nSitemap: {seo.SITEMAP_URL}\n",
        )
        for document in documents:
            with self.subTest(document=document):
                fetch = FakeFetch()
                fetch.responses[seo.ROBOTS_URL] = response(document.encode())
                with self.assertRaises(seo.SeoError) as caught:
                    seo.validate_robots(list(EXPECTED_URLS), fetch=fetch)
                self.assertEqual(caught.exception.code, "robots_blocked")

    def test_unavailable_or_invalid_robots_cannot_be_reported_healthy(self):
        invalid_responses = (
            response(SECRET_MARKER.encode(), status=503),
            response(b"User-agent: *\nAllow: /\n"),
            response(f"Sitemap: {seo.SITEMAP_URL}\n".encode()),
            response(b"<html><h1>Error</h1></html>"),
            response(b"User-agent: *\nAllow: /\nSitemap: https://other.example/sitemap.xml\n"),
            response(b"\xff\xfe"),
        )
        for robots_response in invalid_responses:
            with self.subTest(status=robots_response.status, body=robots_response.body):
                fetch = FakeFetch()
                fetch.responses[seo.ROBOTS_URL] = robots_response
                with self.assertRaises(seo.SeoError):
                    seo.validate_robots(list(EXPECTED_URLS), fetch=fetch)

    def test_allow_cannot_override_article_disallow_in_either_rule_order(self):
        for rules in (
            "User-agent: *\nAllow: /\nDisallow: /p/",
            "User-agent: *\nDisallow: /p/\nAllow: /",
        ):
            with self.subTest(rules=rules):
                self.assert_blocked(rules)

    def test_wildcards_terminal_anchors_and_percent_encoded_blocks_are_rejected(self):
        for pattern in (
            "/p/*",
            "/p/*texas$",
            "/p/nursing-license-requirements-texas$",
            "/%70/",
            "/p/%6eursing-license-endorsement-to-texas$",
            "/p/*%74exas$",
        ):
            with self.subTest(pattern=pattern):
                self.assert_blocked(f"User-agent: *\nAllow: /\nDisallow: {pattern}")

    def test_duplicate_googlebot_groups_cannot_hide_a_block_in_either_order(self):
        allow_group = "User-agent: Googlebot\nAllow: /"
        blocked_group = "User-agent: Googlebot\nDisallow: /p/"
        for groups in ((allow_group, blocked_group), (blocked_group, allow_group)):
            with self.subTest(groups=groups):
                self.assert_blocked("\n\n".join(groups))

    def test_conservative_check_blocks_matching_disallow_for_any_named_agent(self):
        self.assert_blocked("User-agent: SomeOtherCrawler\nDisallow: /p/\n\nUser-agent: *\nAllow: /")

    def test_unrelated_api_and_redirect_blocks_do_not_block_core_guides(self):
        documents = (
            "User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /go/\nDisallow:",
            "User-agent: *\nDisallow: /api/\nDisallow: /go/\nAllow: /",
            "User-agent: *\nDisallow: /p/$\nDisallow: /p/nursing$\nAllow: /",
        )
        for rules in documents:
            with self.subTest(rules=rules):
                fetch = FakeFetch()
                fetch.responses[seo.ROBOTS_URL] = response(
                    f"{rules}\nSitemap: {seo.SITEMAP_URL}\n".encode(),
                    headers={"content-type": "text/plain"},
                )
                seo.validate_robots(list(EXPECTED_URLS), fetch=fetch)


class PageValidationTests(unittest.TestCase):
    def test_case_variant_robots_headers_cannot_hide_noindex_in_either_order(self):
        url = EXPECTED_URLS[0]
        pairs = (("X-Robots-Tag", "NOINDEX"), ("x-robots-tag", "index"))
        for ordered_pairs in (pairs, tuple(reversed(pairs))):
            with self.subTest(ordered_pairs=ordered_pairs):
                headers = {"content-type": "text/html"}
                headers.update(ordered_pairs)
                fetch = FakeFetch()
                fetch.responses[url] = response(page(url), headers=headers)
                with self.assertRaises(seo.SeoError) as caught:
                    seo.validate_pages([url], fetch=fetch)
                self.assertEqual(caught.exception.code, "noindex")

    def test_all_three_pages_are_checked_and_have_stable_sha256_digests(self):
        fetch = FakeFetch()
        first = seo.validate_pages(list(EXPECTED_URLS), fetch=fetch)
        second = seo.validate_pages(list(EXPECTED_URLS), fetch=FakeFetch())
        self.assertEqual(set(first), set(EXPECTED_URLS))
        self.assertEqual(first, second)
        for digest in first.values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(
            {url for url, method, _ in fetch.calls if method == "GET"},
            set(EXPECTED_URLS),
        )

    def test_one_content_change_changes_only_that_page_digest(self):
        original = seo.validate_pages(list(EXPECTED_URLS), fetch=FakeFetch())
        changed_fetch = FakeFetch()
        changed_fetch.responses[EXPECTED_URLS[1]] = response(
            page(EXPECTED_URLS[1], body="<p>Updated preparation step.</p>")
        )
        changed = seo.validate_pages(list(EXPECTED_URLS), fetch=changed_fetch)
        self.assertNotEqual(changed[EXPECTED_URLS[1]], original[EXPECTED_URLS[1]])
        for url in (EXPECTED_URLS[0], EXPECTED_URLS[2]):
            self.assertEqual(changed[url], original[url])

    def test_attribute_order_case_and_nested_heading_are_valid(self):
        url = EXPECTED_URLS[0]
        document = (
            f'<HTML><HEAD><LINK href="{url}" REL="canonical">'
            '</HEAD><BODY><H1><span>Texas</span> nursing guide</H1></BODY></HTML>'
        ).encode("utf-8")
        fetch = FakeFetch()
        fetch.responses[url] = response(
            document, headers={"Content-Type": "text/html; charset=UTF-8"}
        )
        self.assertIn(url, seo.validate_pages([url], fetch=fetch))

    def test_unhealthy_or_unindexable_pages_are_rejected(self):
        url = EXPECTED_URLS[0]
        cases = {
            "503": response(page(url), status=503),
            "redirect": response(page(url), status=301),
            "not-html": response(page(url), headers={"content-type": "application/json"}),
            "missing-content-type": seo.HttpResponse(200, {}, page(url)),
            "wrong-canonical-path": response(page(url.replace("/p/", "/"))),
            "wrong-canonical-host": response(page(url.replace("soeasyhub.com", "other.example"))),
            "missing-canonical": response(b"<html><h1>Texas guide</h1></html>"),
            "header-noindex": response(page(url), headers={
                "content-type": "text/html", "X-Robots-Tag": "NOINDEX, follow"
            }),
            "meta-noindex": response(page(url, head='<meta name="robots" content="noindex,follow">')),
            "googlebot-noindex": response(page(url, head='<meta content="NOINDEX" name="googlebot">')),
            "bingbot-noindex": response(page(url, head='<meta name="bingbot" content="noindex">')),
            "robots-none": response(page(url, head='<meta name="robots" content="none">')),
            "header-none": response(page(url), headers={
                "content-type": "text/html", "x-robots-tag": "googlebot: none"
            }),
            "empty-h1": response(page(url, title="   \n\t")),
            "missing-h1": response(f'<html><head><link rel="canonical" href="{url}"></head><body>Guide</body></html>'.encode()),
            "empty-body": response(b""),
        }
        for label, page_response in cases.items():
            with self.subTest(label=label):
                fetch = FakeFetch()
                fetch.responses[url] = page_response
                with self.assertRaises(seo.SeoError) as caught:
                    seo.validate_pages([url], fetch=fetch)
                self.assertTrue(caught.exception.code)

    def test_page_transport_failure_is_not_a_valid_digest(self):
        fetch = FakeFetch()
        fetch.responses[EXPECTED_URLS[1]] = TimeoutError("timed out")
        with self.assertRaises(seo.SeoError):
            seo.validate_pages(list(EXPECTED_URLS), fetch=fetch)


class RunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="soeasyhub-seo-test-")
        self.addCleanup(self.temp.cleanup)
        self.state_file = Path(self.temp.name) / "state.json"
        self.report_file = Path(self.temp.name) / "report.json"
        self.last_output = ""
        # Any accidental use of the real transport fails before opening a socket.
        guard = patch.object(seo, "build_opener", side_effect=AssertionError("Real network forbidden"))
        guard.start()
        self.addCleanup(guard.stop)

    def execute(self, fetch, *, submit=False):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            result = seo.run(
                submit=submit,
                state_file=self.state_file,
                report_file=self.report_file,
                fetch=fetch,
            )
        self.last_output = output.getvalue()
        return result

    def report(self):
        self.assertTrue(self.report_file.is_file(), "Every run must leave a structured report")
        value = json.loads(self.report_file.read_text(encoding="utf-8"))
        self.assertIsInstance(value, dict)
        return value

    def assert_all_live_reads(self, fetch):
        gets = {url for url, method, _ in fetch.calls if method == "GET"}
        self.assertTrue({seo.SITEMAP_URL, seo.ROBOTS_URL, *EXPECTED_URLS}.issubset(gets))

    def assert_clean_failure(self, fetch, *, submit=False):
        result = self.execute(fetch, submit=submit)
        self.assertNotEqual(result, 0)
        report = self.report()
        self.assertIn("error", report)
        self.assertIsInstance(report["error"], str)
        self.assertTrue(report.get("error_code"))
        self.assertEqual(report["status"], "error")
        self.assertIn(report.get("failed_phase"), {
            "state_read", "source_read", "robots_validation", "page_validation",
            "indexnow_submission", "state_write"
        })
        self.assertNotIn(SECRET_MARKER, self.report_file.read_text(encoding="utf-8"))
        self.assertNotIn(SECRET_MARKER, self.last_output)
        return report

    def test_default_dry_run_checks_live_health_without_post_or_state_write(self):
        fetch = FakeFetch()
        with patch.object(seo, "fetch_http", side_effect=AssertionError("Real HTTP forbidden")):
            result = self.execute(fetch)
        self.assertEqual(result, 0)
        self.assert_all_live_reads(fetch)
        self.assertEqual(fetch.posts, [])
        self.assertFalse(self.state_file.exists())
        report = self.report()
        self.assertEqual(report["status"], "healthy_read_only")
        self.assertEqual(report["submission"], "not_attempted")
        self.assertEqual(report["changed_count"], 3)
        self.assertEqual(set(report["validated_urls"]), set(EXPECTED_URLS))
        self.assertEqual(set(report["changed_urls"]), set(EXPECTED_URLS))

    def test_cli_defaults_to_read_only(self):
        with patch.object(seo, "run", return_value=0) as run:
            self.assertEqual(seo.main([]), 0)
        self.assertIs(run.call_args.kwargs["submit"], False)

    def test_missing_state_is_a_valid_first_run(self):
        self.assertEqual(seo.load_state(self.state_file), {})

    def test_malformed_json_unknown_version_and_wrong_top_level_fail(self):
        for contents in ("{broken", "[]", '{"version":999,"fingerprints":{}}', "null"):
            with self.subTest(contents=contents):
                self.state_file.write_text(contents, encoding="utf-8")
                with self.assertRaises(seo.SeoError) as caught:
                    seo.load_state(self.state_file)
                self.assertTrue(caught.exception.code)

    def test_state_rejects_invalid_fingerprints_and_unreviewed_urls(self):
        cases = (
            {"version": 1, "fingerprints": {EXPECTED_URLS[0]: "not-a-hash"}},
            {"version": 1, "fingerprints": {EXPECTED_URLS[0]: "a" * 63}},
            {"version": 1, "fingerprints": {EXPECTED_URLS[0]: "G" * 64}},
            {"version": 1, "fingerprints": {EXPECTED_URLS[0]: 123}},
            {"version": 1, "fingerprints": {"https://other.example/p/article": "a" * 64}},
            {"version": 1, "fingerprints": []},
            {"version": 1},
        )
        for value in cases:
            with self.subTest(value=value):
                self.state_file.write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaises(seo.SeoError):
                    seo.load_state(self.state_file)

    def test_state_accepts_valid_versioned_fingerprints(self):
        fingerprints = {url: "a" * 64 for url in EXPECTED_URLS}
        self.state_file.write_text(
            json.dumps({"version": 1, "fingerprints": fingerprints}), encoding="utf-8"
        )
        self.assertEqual(seo.load_state(self.state_file), fingerprints)

    def test_submit_200_and_202_record_distinct_success_statuses(self):
        statuses = []
        for http_status in (200, 202):
            with self.subTest(http_status=http_status):
                if self.state_file.exists():
                    self.state_file.unlink()
                fetch = FakeFetch(submit_status=http_status)
                self.assertEqual(self.execute(fetch, submit=True), 0)
                self.assert_all_live_reads(fetch)
                self.assertEqual(len(fetch.posts), 1)
                payload = fetch.posts[0][2]
                self.assertEqual(set(payload["urlList"]), set(EXPECTED_URLS))
                self.assertEqual(payload["host"], "soeasyhub.com")
                self.assertEqual(set(seo.load_state(self.state_file)), set(EXPECTED_URLS))
                report = self.report()
                self.assertEqual(report["status"], "healthy_submitted")
                self.assertEqual(report["changed_count"], 3)
                statuses.append(report["submission"])
        self.assertEqual(statuses, ["accepted", "accepted_key_validation_pending"])
        self.assertNotEqual(statuses[0], statuses[1], "Accepted and pending validation must be distinguishable")

    def test_unchanged_content_still_checks_health_and_reports_no_changes(self):
        self.assertEqual(self.execute(FakeFetch(), submit=True), 0)
        state_before = self.state_file.read_bytes()
        fetch = FakeFetch()
        self.assertEqual(self.execute(fetch, submit=True), 0)
        self.assert_all_live_reads(fetch)
        self.assertEqual(fetch.posts, [])
        self.assertEqual(self.state_file.read_bytes(), state_before)
        self.assertEqual(self.report()["status"], "healthy_no_changes")
        self.assertEqual(self.report()["changed_count"], 0)
        self.assertEqual(self.report()["changed_urls"], [])
        self.assertEqual(self.report()["submission"], "not_attempted")

    def test_only_changed_reviewed_article_is_submitted(self):
        self.assertEqual(self.execute(FakeFetch(), submit=True), 0)
        fetch = FakeFetch()
        changed_url = EXPECTED_URLS[2]
        fetch.responses[changed_url] = response(page(changed_url, body="<p>A new note.</p>"))
        self.assertEqual(self.execute(fetch, submit=True), 0)
        self.assertEqual(len(fetch.posts), 1)
        self.assertEqual(fetch.posts[0][2]["urlList"], [changed_url])

    def test_dry_run_preserves_existing_state_when_content_changed(self):
        self.assertEqual(self.execute(FakeFetch(), submit=True), 0)
        state_before = self.state_file.read_bytes()
        fetch = FakeFetch()
        fetch.responses[EXPECTED_URLS[0]] = response(page(EXPECTED_URLS[0], body="<p>Changed.</p>"))
        self.assertEqual(self.execute(fetch), 0)
        self.assertEqual(fetch.posts, [])
        self.assertEqual(self.state_file.read_bytes(), state_before)

    def test_dns_timeout_and_source_503_are_nonzero_and_sanitized(self):
        for failed_response in (
            socket.gaierror(SECRET_MARKER),
            TimeoutError(SECRET_MARKER),
            response(SECRET_MARKER.encode(), status=503),
        ):
            with self.subTest(failure=type(failed_response).__name__):
                fetch = FakeFetch()
                fetch.responses[seo.SITEMAP_URL] = failed_response
                self.assert_clean_failure(fetch, submit=True)
                self.assertNotIn("changed_count", self.report())
                self.assertEqual(self.report()["failed_phase"], "source_read")
                self.assertEqual(fetch.posts, [])
                self.assertFalse(self.state_file.exists())

    def test_empty_source_is_nonzero_and_not_healthy_no_changes(self):
        fetch = FakeFetch(urls=())
        report = self.assert_clean_failure(fetch, submit=True)
        self.assertNotEqual(report["status"], "healthy_no_changes")
        self.assertNotIn("changed_count", report)
        self.assertEqual(fetch.posts, [])
        self.assertFalse(self.state_file.exists())

    def test_robots_failure_is_nonzero_and_does_not_submit_or_invent_change_count(self):
        fetch = FakeFetch()
        fetch.responses[seo.ROBOTS_URL] = response(SECRET_MARKER.encode(), status=503)
        report = self.assert_clean_failure(fetch, submit=True)
        self.assertEqual(report["failed_phase"], "robots_validation")
        self.assertNotIn("changed_count", report)
        self.assertEqual(fetch.posts, [])
        self.assertFalse(self.state_file.exists())

    def test_page_failure_blocks_entire_submission_and_preserves_state(self):
        self.assertEqual(self.execute(FakeFetch(), submit=True), 0)
        state_before = self.state_file.read_bytes()
        fetch = FakeFetch()
        fetch.responses[EXPECTED_URLS[1]] = response(SECRET_MARKER.encode(), status=503)
        self.assert_clean_failure(fetch, submit=True)
        self.assertNotIn("changed_count", self.report())
        self.assertEqual(self.report()["failed_phase"], "page_validation")
        self.assertEqual(fetch.posts, [])
        self.assertEqual(self.state_file.read_bytes(), state_before)

    def test_submission_failure_never_marks_content_as_successfully_submitted(self):
        for failed_response in (
            response(SECRET_MARKER.encode(), status=403),
            response(SECRET_MARKER.encode(), status=503),
            TimeoutError(SECRET_MARKER),
        ):
            with self.subTest(failure=type(failed_response).__name__):
                fetch = FakeFetch()
                fetch.submit_response = failed_response
                self.assert_clean_failure(fetch, submit=True)
                self.assertEqual(len(fetch.posts), 1)
                self.assertFalse(self.state_file.exists())

    def test_unavailable_or_mismatched_ownership_file_blocks_post(self):
        for key_response in (
            response(SECRET_MARKER.encode(), status=404),
            response(SECRET_MARKER.encode(), status=503),
            response(SECRET_MARKER.encode(), status=200),
            response(b"", status=200),
            TimeoutError(SECRET_MARKER),
        ):
            with self.subTest(failure=type(key_response).__name__):
                fetch = FakeFetch()
                fetch.responses[seo.KEY_URL] = key_response
                self.assert_clean_failure(fetch, submit=True)
                self.assert_all_live_reads(fetch)
                self.assertEqual(self.report()["failed_phase"], "indexnow_submission")
                self.assertEqual(fetch.posts, [])
                self.assertFalse(self.state_file.exists())

    def test_state_write_failure_is_nonzero_even_after_notification_is_accepted(self):
        original_replace = Path.replace
        state_file = self.state_file

        def fail_state_replace(path, target):
            if Path(target) == state_file:
                raise PermissionError(SECRET_MARKER)
            return original_replace(path, target)

        fetch = FakeFetch()
        with patch.object(Path, "replace", fail_state_replace):
            report = self.assert_clean_failure(fetch, submit=True)
        self.assertEqual(report["failed_phase"], "state_write")
        self.assertEqual(report["submission"], "accepted")
        self.assertEqual(len(fetch.posts), 1)
        self.assertFalse(self.state_file.exists())

    def test_same_state_and_report_path_does_not_overwrite_previous_state(self):
        fingerprints = {url: "a" * 64 for url in EXPECTED_URLS}
        self.state_file.write_text(
            json.dumps({"version": 1, "fingerprints": fingerprints}), encoding="utf-8"
        )
        state_before = self.state_file.read_bytes()
        fetch = FakeFetch()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            result = seo.run(
                submit=True, state_file=self.state_file,
                report_file=self.state_file, fetch=fetch
            )
        self.assertNotEqual(result, 0)
        self.assertEqual(self.state_file.read_bytes(), state_before)
        self.assertEqual(fetch.calls, [])

    def test_failed_changed_submission_keeps_previous_state_for_retry(self):
        self.assertEqual(self.execute(FakeFetch(), submit=True), 0)
        state_before = self.state_file.read_bytes()
        fetch = FakeFetch()
        fetch.responses[EXPECTED_URLS[2]] = response(page(EXPECTED_URLS[2], body="<p>Changed.</p>"))
        fetch.submit_response = response(SECRET_MARKER.encode(), status=422)
        self.assert_clean_failure(fetch, submit=True)
        self.assertEqual(self.state_file.read_bytes(), state_before)

    def test_bad_state_is_nonzero_without_any_submission(self):
        self.state_file.write_text("{invalid-json", encoding="utf-8")
        fetch = FakeFetch()
        self.assert_clean_failure(fetch, submit=True)
        self.assertEqual(fetch.posts, [])
        self.assertEqual(self.state_file.read_text(encoding="utf-8"), "{invalid-json")


if __name__ == "__main__":
    unittest.main()
