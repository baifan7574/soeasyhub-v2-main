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

const FALLBACK_SITEMAP_SLUGS = [
  "about-us-electrician",
  "a-grade-electrical-license-nsw",
  "a-grade-electrical-license-victoria",
  "a-grade-electrical-license-wa",
  "aicpa-gaac-conference",
  "aicpa-gen-ai-toolkit",
  "aicpa-generative-ai-toolkit",
  "aicpa-gpac",
  "allegheny-county-electrical-license",
  "all-electrical-license",
  "allen-county-electrical-license",
  "allentown-electrical-license",
  "allentown-electrical-license-application",
  "allentown-electrical-license-renewal",
  "allentown-pa-electrical-license",
  "apply-for-electrical-license-act",
  "california-board-medical-quality-assurance",
  "california-electrical-license-reciprocity",
  "california-electrician-license-reciprocity",
  "california-electrician-reciprocity",
  "california-electricians-license-reciprocity-map",
  "california-journeyman-electrician-license-reciprocity",
  "california-journeyman-electrician-reciprocity",
  "california-medical-board-members",
  "california-medical-board-regulations",
  "california-medical-reciprocity",
  "california-nursing-home-administrator-license-reciprocity",
  "california-nursing-license-by-reciprocity",
  "california-nursing-license-reciprocity-requirements",
  "california-reciprocal-cpa-license",
  "california-reciprocity-rules",
  "california-teaching-certification-reciprocity",
  "can-i-get-my-electrical-license-online",
  "can-i-teach-in-ny-without-certification",
  "can-i-use-my-california-nursing-license-in-another-state",
  "can-you-teach-in-illinois-without-a-teaching-certificate",
  "cgma-aicpa",
  "cgma-designation-organization-in-partnership-with-aicpa",
  "city-of-allentown-electrical-license",
  "cpa-com-generative-ai-toolkit",
  "cpa-employer-partners",
  "cpa-exam-gpa-requirements",
  "cpa-florida-reciprocity",
  "cpa-license-reciprocity-florida",
  "cpa-license-reciprocity-new-york",
  "cpa-license-reciprocity-texas",
  "cpa-license-transfer-to-illinois",
  "cpa-license-transfer-to-new-york",
  "cpa-reciprocal-license",
  "cpa-reciprocity",
  "cpa-reciprocity-arizona",
  "cpa-reciprocity-by-country",
  "cpa-reciprocity-by-state",
  "cpa-reciprocity-by-state-map",
  "cpa-reciprocity-california",
  "cpa-reciprocity-colorado",
  "cpa-reciprocity-countries",
  "cpa-reciprocity-florida",
  "cpa-reciprocity-georgia",
  "cpa-reciprocity-hawaii",
  "cpa-reciprocity-illinois",
  "cpa-reciprocity-indiana",
  "cpa-reciprocity-international",
  "cpa-reciprocity-in-texas",
  "cpa-reciprocity-kansas",
  "cpa-reciprocity-map",
  "cpa-reciprocity-meaning",
  "cpa-reciprocity-missouri",
  "cpa-reciprocity-new-jersey",
  "cpa-reciprocity-new-york",
  "cpa-reciprocity-north-carolina",
  "cpa-reciprocity-ny",
  "cpa-reciprocity-ohio",
  "cpa-reciprocity-reddit",
  "cpa-reciprocity-rules",
  "cpa-reciprocity-south-carolina",
  "cpa-reciprocity-states",
  "cpa-reciprocity-tennessee",
  "cpa-reciprocity-texas",
  "cpa-reciprocity-utah",
  "cpa-reciprocity-virginia",
  "cpa-recognised-employer-list",
  "cpa-recognised-employer-partner-list",
  "dc-electrical-license-requirements",
  "do-electrician-licenses-transfer-from-state-to-state",
  "do-electricians-have-to-be-licensed-in-illinois",
  "do-electricians-need-a-license-in-illinois",
  "does-a-california-rn-license-transfer-to-other-states",
  "does-an-illinois-teaching-certificate-transfer-to-other-states",
  "does-a-texas-nursing-license-transfer-from-state-to-state",
  "does-a-texas-teaching-certificate-transfer-to-other-states",
  "does-california-have-a-master-electrician-license",
  "does-california-have-medical-license-reciprocity",
  "does-california-have-reciprocity-for-teachers",
  "does-florida-have-reciprocity-for-nurses",
  "does-florida-reciprocate-electrical-license",
  "does-florida-teaching-certificate-transfer-to-other-states",
  "does-ny-have-reciprocity",
  "does-texas-have-cna-reciprocity",
  "do-you-have-to-have-a-teaching-certificate-to-teach-in-texas",
  "do-you-need-a-license-to-do-electrical-work",
  "do-you-need-a-teaching-certificate-to-teach-in-texas",
  "electrical-board-full-form",
  "electrical-board-gland",
  "electrical-board-glue",
  "electrical-board-green",
  "electrical-board-ke-connection",
  "electrical-board-nd",
  "electrical-board-sheet",
  "electrical-board-sheet-price",
  "electrical-board-shifting",
  "electrical-board-shoes",
  "electrical-board-short",
  "electrical-board-short-circuit",
  "electrical-board-skp",
  "electrical-board-small",
  "electrical-board-spacers",
  "electrical-board-spelling",
  "electrical-board-spray",
  "electrical-board-supplier",
  "electrical-board-supply",
  "electrical-board-surge-protector",
  "electrical-board-switch",
  "electrical-board-switch-connection",
  "electrical-board-switch-price",
  "electrical-board-switch-replacement",
  "electrical-board-symbol",
  "electrical-board-system",
  "electrical-certification-germany",
  "electrical-certification-symbols",
  "electrical-c-license-agent",
  "electrical-c-license-dd-address",
  "electrical-c-license-in-andhra-pradesh",
  "electrical-c-license-office-address",
  "electrical-colours-uk",
  "electrical-contractor-license-agent",
  "electrical-contractor-license-andhra-pradesh",
  "electrical-contractor-license-in-nc",
  "electrical-cv-examples",
  "electrical-exam-georgia",
  "electrical-exam-guide",
  "electrical-exam-syllabus",
  "electrical-h-license-qualifications",
  "electrical-journeyman-license-reciprocity",
  "electrical-licence-download-karnataka",
  "electrical-licence-download-west-bengal",
  "electrical-licence-ga",
  "electrical-licence-gst",
  "electrical-licence-gujarat-online",
  "electrical-licence-gujarat-validity",
  "electrical-licence-kaise-banega",
  "electrical-licence-last-date",
  "electrical-licence-legacy",
  "electrical-licence-levels",
  "electrical-licence-lucknow",
  "electrical-licence-skills-maintenance",
  "electrical-licence-syllabus",
  "electrical-licence-types",
  "electrical-license-act",
  "electrical-license-address-change",
  "electrical-license-age",
  "electrical-license-agent",
  "electrical-license-a-grade",
  "electrical-license-alabama",
  "electrical-license-alaska",
  "electrical-license-allowance",
  "electrical-license-a-malta",
  "electrical-license-a-malta-past-papers",
  "electrical-license-andhra-pradesh",
  "electrical-license-application",
  "electrical-license-application-form",
  "electrical-license-application-ga",
  "electrical-license-application-georgia",
  "electrical-license-application-status",
  "electrical-license-application-status-west-bengal",
  "electrical-license-apply",
  "electrical-license-arizona",
  "electrical-license-arkansas",
  "electrical-license-assam",
  "electrical-license-az",
  "electrical-license-board-guindy",
  "electrical-license-board-gujarat",
  "electrical-license-by-state",
  "electrical-license-check-sa",
  "electrical-license-class",
  "electrical-license-d",
  "electrical-license-database",
  "electrical-license-dc",
  "electrical-license-de",
  "electrical-license-definition",
  "electrical-license-delaware",
  "electrical-license-delhi",
  "electrical-license-department",
  "electricallicense-details",
  "electrical-license-documents",
  "electrical-license-download",
  "electrical-license-download-pdf",
  "electrical-license-exam-georgia",
  "electrical-license-exam-guide",
  "electrical-license-exam-guide-aaron-patti",
  "electrical-license-exam-nc",
  "electrical-license-florida-reciprocity",
  "electrical-license-for-all-states",
  "electrical-license-for-sale",
  "electrical-license-for-sale-dallas",
  "electrical-license-for-solar",
  "electrical-license-ga",
  "electrical-license-ga-requirements",
  "electrical-license-ga-test",
  "electrical-license-georgia",
  "electrical-license-georgia-requirements",
  "electrical-license-goa",
  "electrical-license-grade-c",
  "electrical-license-grandfather-clause",
  "electrical-license-gujarat",
  "electrical-license-guyana",
  "electrical-license-how-to-get-grandfathered",
  "electrical-license-in-spanish",
  "electrical-license-lara",
  "electrical-license-level",
  "electrical-license-license",
  "electrical-license-login",
  "electrical-license-long-island",
  "electrical-license-lookup",
  "electrical-license-lookup-colorado",
  "electrical-license-lookup-ct",
  "electrical-license-lookup-ga",
  "electrical-license-lookup-georgia",
  "electrical-license-lookup-ky",
  "electrical-license-lookup-massachusetts",
  "electrical-license-lookup-nc",
  "electrical-license-lookup-oregon",
  "electrical-license-lookup-sc",
  "electrical-license-lookup-texas",
  "electrical-license-louisiana",
  "electrical-license-nc-hours",
  "electrical-license-nc-test",
  "electrical-license-north-dakota",
  "electrical-license-nova-scotia",
  "electrical-license-office-guwahati",
  "electrical-license-pdf",
  "electrical-license-pittsburgh-pa",
  "electrical-license-print-out",
  "electrical-license-qualifications",
  "electrical-license-reciprocal-states",
  "electrical-license-reciprocation",
  "electrical-license-reciprocity-alaska",
  "electrical-license-reciprocity-by-state",
  "electrical-license-reciprocity-by-state-map",
  "electrical-license-reciprocity-by-state-texas",
  "electrical-license-reciprocity-california",
  "electrical-license-reciprocity-colorado",
  "electrical-license-reciprocity-florida",
  "electrical-license-reciprocity-georgia",
  "electrical-license-reciprocity-list",
  "electrical-license-reciprocity-map",
  "electrical-license-reciprocity-massachusetts",
  "electrical-license-reciprocity-north-carolina",
  "electrical-license-reciprocity-texas",
  "electrical-license-reciprocity-utah",
  "electrical-license-reciprocity-virginia",
  "electrical-license-reciprocity-washington-state",
  "electrical-license-referee-statement",
  "electrical-license-renewal",
  "electrical-license-renewal-discount-code",
  "electrical-license-renewal-nc",
  "electrical-license-renewal-nh",
  "electrical-license-renewal-sa",
  "electrical-license-renewal-status",
  "electrical-license-requirements",
  "electrical-license-requirements-ky",
  "electrical-license-sa",
  "electrical-license-sample",
  "electrical-license-saskatchewan",
  "electrical-license-sc",
  "electrical-license-school",
  "electrical-license-school-nyc",
  "electrical-license-school-online",
  "electrical-license-sc-requirements",
  "electrical-license-sd",
  "electrical-license-search",
  "electrical-license-search-florida",
  "electrical-license-search-iowa",
  "electrical-license-search-nc",
  "electrical-license-search-nj",
  "electrical-license-search-nsw",
  "electrical-license-search-nt",
  "electrical-license-search-oregon",
  "electrical-license-search-qld",
  "electrical-license-search-qld-online",
  "electrical-license-search-queensland",
  "electrical-license-search-texas",
  "electrical-license-search-vic",
  "electrical-license-search-wa",
  "electrical-license-seattle",
  "electrical-license-service-nsw",
  "electrical-license-south-carolina",
  "electrical-license-south-dakota",
  "electrical-license-stages",
  "electrical-license-stamp",
  "electrical-license-state-of-florida",
  "electrical-license-state-reciprocity",
  "electrical-license-status",
  "electrical-license-steps",
  "electrical-license-study",
  "electrical-license-study-guide",
  "electrical-license-suffolk-county",
  "electrical-license-supervisor",
  "electrical-license-test-georgia",
  "electrical-license-trade-school",
  "electrical-license-viva-guide",
  "electrical-license-viva-guide-pdf",
  "electrical-license-washington-dc",
  "electrical-license-washington-state",
  "electrical-licensing-dmirs",
  "electrical-licensing-government-department",
  "electrical-licensing-system",
  "electrical-llc-requirements",
  "electrical-sign-license",
  "electrical-specialty-license",
  "electrical-supervisor-license-andhra-pradesh",
  "electrician-apprenticeship-united-kingdom",
  "electrician-bloomsbury",
  "electrician-blue-collar",
  "electrician-bucks",
  "electrician-creed",
  "electrician-cv-example",
  "electrician-diy",
  "electrician-dollar",
  "electrician-drip",
  "electrician-dudley-ma",
  "electrician-dukinfield",
  "electrician-dunnington",
  "electrician-duxford",
  "electrician-dykes",
  "electrician-dymchurch",
  "electrician-eu",
  "electrician-gatwick",
  "electrician-go",
  "electrician-ham",
  "electrician-harlan-ky",
  "electrician-harry",
  "electrician-heacham",
  "electrician-heathrow",
  "electrician-hertz",
  "electrician-in-derry-nh",
  "electrician-in-europe",
  "electrician-in-glasgow-ky",
  "electrician-in-hampton-nh",
  "electrician-in-harrodsburg-ky",
  "electrician-in-medford-ny",
  "electrician-in-ri",
  "electrician-in-ukraine",
  "electrician-in-utah-county",
  "electrician-in-york-maine",
  "electrician-ja",
  "electrician-jamaica-vt",
  "electrician-james",
  "electrician-jamie",
  "electrician-julian",
  "electrician-junior",
  "electrician-jw",
  "electrician-kamas",
  "electrician-ken",
  "electrician-kenny",
  "electrician-kensington-md",
  "electrician-kentucky",
  "electrician-kidbrooke",
  "electrician-kidlington",
  "electrician-kits",
  "electrician-kitty",
  "electrician-leccy",
  "electrician-lecky",
  "electrician-license-california-requirement",
  "electrician-license-florida-requirements",
  "electrician-license-georgia",
  "electrician-license-germany",
  "electrician-license-illinois",
  "electrician-license-illinois-cost",
  "electrician-license-illinois-lookup",
  "electrician-license-illinois-requirements",
  "electrician-license-in-illinois",
  "electrician-license-length",
  "electrician-license-levels",
  "electrician-license-nc",
  "electrician-license-nj-requirements",
  "electrician-license-ny-requirements",
  "electrician-license-nys",
  "electrician-license-reciprocity",
  "electrician-license-requirements-in-florida",
  "electrician-license-requirements-in-texas",
  "electrician-license-requirements-mn",
  "electrician-license-requirements-ny",
  "electrician-license-requirements-nyc",
  "electrician-license-san-diego",
  "electrician-license-saskatchewan",
  "electrician-license-sc",
  "electrician-license-school",
  "electrician-license-school-cost",
  "electrician-license-south-carolina",
  "electrician-license-south-dakota",
  "electrician-license-state-transfer",
  "electrician-license-texas-requirements",
  "electrician-license-transfer",
  "electrician-ltd",
  "electrician-lyman",
  "electrician-lynbrook",
  "electrician-mumsnet",
  "electrician-murray",
  "electrician-musk8",
  "electrician-n1",
  "electrician-n5",
  "electrician-nevada",
  "electrician-nvq",
  "electrician-nw1",
  "electrician-nw10",
  "electrician-nw5",
  "electrician-nw6",
  "electrician-overseas",
  "electrician-oxford-alabama",
  "electrician-oxford-ct",
  "electrician-oxford-ma",
  "electrician-oxford-maine",
  "electrician-oxford-pa",
  "electrician-ozark-al",
  "electrician-ozone-park-ny",
  "electrician-pics",
  "electrician-pimlico",
  "electrician-pv",
  "electrician-qualified",
  "electrician-questions",
  "electrician-reciprocity",
  "electrician-reciprocity-by-state",
  "electrician-reciprocity-map",
  "electrician-requirements-in-illinois",
  "electrician-ri",
  "electrician-roanoke",
  "electrician-ron",
  "electrician-room",
  "electrician-rutland",
  "electrician-shoreditch",
  "electrician-slang",
  "electricians-r-us-ri",
  "electrician-sw4",
  "electrician-sw6",
  "electrician-u",
  "electrician-u-cat5",
  "electrician-u-day",
  "electrician-u-discord",
  "electrician-u-journeyman",
  "electrician-ukiah",
  "electrician-ukiah-ca",
  "electrician-u-llc",
  "electrician-u-membership",
  "electrician-u-neca",
  "electrician-union-ky",
  "electrician-union-nh",
  "electrician-united-kingdom",
  "electrician-upgrades",
  "electrician-ups",
  "electrician-u-review",
  "electrician-us",
  "electrician-usk",
  "electrician-ut",
  "electrician-utah",
  "electrician-u-ups",
  "electrician-u-voltage",
  "electrician-u-website",
  "electrician-uxbridge-ma",
  "electrician-u-youtube",
  "electrician-u-zinsco",
  "electrician-van-uk",
  "electrician-vt",
  "electrician-w1",
  "electrician-warminster-uk",
  "electrician-whitby-uk",
  "electrician-work-uk",
  "electrician-yell",
  "electrician-you",
  "electrician-yt",
  "electrician-z",
  "electrician-ziprecruiter",
  "facebook-electricians",
  "florida-board-of-nursing-reciprocity",
  "florida-board-of-pharmacy-reciprocity",
  "florida-electrician-license-reciprocity",
  "florida-electrician-reciprocity",
  "florida-journeyman-electrical-license-reciprocity",
  "florida-master-electrician-license-reciprocity",
  "florida-medical-reciprocity",
  "florida-nurse-aide-registry",
  "florida-nurse-attacked",
  "florida-nurse-ce-package-30-credit-hours",
  "florida-nurse-ce-renewal-package",
  "florida-nurse-college",
  "florida-nurse-contract",
  "florida-nurse-license",
  "florida-nurse-license-lookup",
  "florida-nurse-practitioner",
  "florida-nurse-practitioner-license-lookup",
  "florida-nurse-practitioner-license-verification",
  "florida-nursery",
  "florida-nursery-mart",
  "florida-nursing-license-reciprocity-states",
  "florida-nursing-site",
  "florida-reciprocal-cpa-license",
  "florida-reciprocity-cpa-license",
  "florida-teaching-certificate-reciprocity-states",
  "frs-electrician",
  "ga-electrical-license",
  "g-electrician",
  "getting-electrical-license-in-nc",
  "gfoa-vs-aga",
  "how-do-i-contact-the-texas-medical-board",
  "how-do-i-transfer-my-teaching-license-to-california",
  "how-do-i-write-a-cv-for-an-electrician",
  "how-do-you-get-electrical-license",
  "how-long-does-it-take-to-get-a-teaching-certificate-in-illinois",
  "how-long-does-it-take-to-get-a-teaching-certificate-in-ny",
  "how-much-to-get-electrical-license",
  "how-to-apply-for-nursing-reciprocity-in-illinois",
  "how-to-apply-for-nursing-reciprocity-in-new-jersey",
  "how-to-apply-reciprocity-for-nurse-in-california",
  "how-to-become-a-certified-teacher-in-ny",
  "how-to-become-a-licensed-electrician-in-illinois",
  "how-to-become-an-electrician-in-illinois",
  "how-to-check-for-electrical-license",
  "how-to-get-a-florida-nursing-license-from-out-of-state",
  "how-to-get-a-teaching-certificate-in-illinois",
  "how-to-get-a-teaching-certificate-in-ny",
  "how-to-get-electrical-license",
  "how-to-get-reciprocity-for-nursing-license-in-new-york",
  "how-to-get-texas-cna-reciprocity",
  "how-to-transfer-new-york-nursing-license-to-florida",
  "how-to-write-a-cv-for-electrician",
  "hw-electrician",
  "illinois-board-of-nursing-reciprocity",
  "illinois-board-of-pharmacy-reciprocity",
  "illinois-board-of-registration-in-medicine",
  "illinois-cpa-reciprocal-license",
  "illinois-electrical-license-reciprocity",
  "illinois-electrician-license-good-in-other-states",
  "illinois-electrician-reciprocity",
  "illinois-journeyman-electrician-license-reciprocity",
  "illinois-license-reciprocity",
  "illinois-master-electrician-license-reciprocity",
  "illinois-medical-license-reciprocity",
  "illinois-medical-reciprocity",
  "illinois-nursing-home-administrator-license-reciprocity",
  "illinois-nursing-license-reciprocity",
  "illinois-nursing-license-via-reciprocity",
  "illinois-nursing-reciprocity",
  "illinois-reciprocal-cpa-license",
  "illinois-reciprocal-teaching-certification",
  "illinois-rn-license-reciprocity",
  "illinois-teaching-certificate-reciprocity",
  "is-florida-a-compact-state-for-nursing-license",
  "is-florida-a-reciprocity-states-for-nursing-license",
  "jib-electrician",
  "jim-the-electrician",
  "ldk-electrical",
  "limited-electrical-license-in-nc",
  "list-of-licensed-electricians-in-texas",
  "list-of-states-with-cna-reciprocity",
  "mass-electrical-license-address-change",
  "medical-board-california-cme-requirements",
  "medical-board-california-license-renewal",
  "medical-board-california-license-verification",
  "medical-board-california-renew",
  "medical-board-california-renewal",
  "medical-board-california-renew-license",
  "medical-board-certification-florida",
  "medical-board-fl",
  "medical-board-florida-complaints",
  "medical-board-for-florida",
  "medical-board-for-florida-osteo",
  "medical-board-for-new-york",
  "medical-board-for-texas",
  "medical-board-il",
  "medical-board-illinois",
  "medical-board-in-florida",
  "medical-board-in-new-jersey",
  "medical-board-in-texas",
  "medical-board-license-texas",
  "medical-board-new-york",
  "medical-board-new-york-license-verification",
  "medical-board-new-york-state",
  "medical-board-of-california-approved-medical-school-list",
  "medical-board-of-california-expert-reviewer-guidelines",
  "medical-board-of-california-expert-reviewer-program",
  "medical-board-of-california-faq",
  "medical-board-of-california-laws",
  "medical-board-of-california-osteopathic",
  "medical-board-of-california-recognized-medical-schools",
  "medical-board-of-california-regulations",
  "medical-board-of-california-renewal",
  "medical-board-of-california-reporting-requirements",
  "medical-board-of-california-requirements",
  "medical-board-of-california-verification",
  "medical-board-of-florida-license",
  "medical-board-of-florida-license-verification",
  "medical-board-of-il",
  "medical-board-of-illinois-complaints",
  "medical-board-of-illinois-license-lookup",
  "medical-board-of-illinois-license-verification",
  "medical-board-of-texas-complaints",
  "medical-board-requirements-by-state",
  "medical-board-respiratory",
  "medical-board-state-of-florida",
  "medical-board-state-of-new-york",
  "medical-board-state-of-texas",
  "medical-board-texas",
  "medical-board-texas-complaints",
  "medical-board-texas-license",
  "medical-board-texas-license-verification",
  "medical-board-tx",
  "medical-card-reciprocity-florida",
  "medical-card-reciprocity-states",
  "medical-license-illinois-requirements",
  "medical-license-reciprocity-between-states",
  "medical-license-reciprocity-by-state",
  "medical-license-reciprocity-california",
  "medical-license-reciprocity-florida",
  "medical-license-reciprocity-international",
  "medical-license-reciprocity-new-jersey",
  "medical-license-reciprocity-new-york",
  "medical-license-reciprocity-states",
  "medical-license-reciprocity-texas",
  "medical-license-reciprocity-wisconsin",
  "medical-license-reciprocity-with-puerto-rico",
  "medical-licensing-reciprocity",
  "medical-licensure-reciprocity",
  "medical-school-reciprocity",
  "mi-electrical-contractors",
  "new-york-electrical-license-reciprocity",
  "new-york-medical-reciprocity",
  "new-york-nursing-license-by-reciprocity",
  "new-york-reciprocity",
  "new-york-reciprocity-application",
  "new-york-reciprocity-cna",
  "new-york-reciprocity-rn",
  "new-york-registered-nurse-license-reciprocity",
  "new-york-state-electrical-license-reciprocity",
  "new-york-state-medical-license-reciprocity",
  "new-york-state-medical-license-requirements",
  "new-york-state-nursing-license-reciprocity",
  "new-york-teaching-certificate-reciprocity",
  "new-york-teaching-certification-reciprocity-states",
  "nj-electrical-license-reciprocity",
  "nursing-license-by-endorsement-new-york",
  "nursing-license-california-endorsement",
  "nursing-license-california-lvn",
  "nursing-license-endorsement-california",
  "nursing-license-endorsement-illinois",
  "nursing-license-endorsement-new-york",
  "nursing-license-endorsement-texas",
  "nursing-license-endorsement-to-california",
  "nursing-license-endorsement-to-florida",
  "nursing-license-endorsement-to-illinois",
  "nursing-license-endorsement-to-new-york",
  "nursing-license-endorsement-to-texas",
  "nursing-license-florida-renewal",
  "nursing-license-florida-transfer",
  "nursing-license-illinois-renewal",
  "nursing-license-illinois-transfer",
  "nursing-license-in-california-requirements",
  "nursing-license-nb",
  "nursing-license-new-york-state",
  "nursing-license-new-york-state-verification",
  "nursing-license-nv",
  "nursing-license-other-states",
  "nursing-license-reciprocal-states",
  "nursing-license-reciprocity",
  "nursing-license-reciprocity-between-states",
  "nursing-license-reciprocity-california",
  "nursing-license-reciprocity-florida",
  "nursing-license-reciprocity-illinois",
  "nursing-license-reciprocity-in-massachusetts",
  "nursing-license-reciprocity-nevada",
  "nursing-license-reciprocity-new-jersey",
  "nursing-license-reciprocity-new-york",
  "nursing-license-reciprocity-nj",
  "nursing-license-reciprocity-pennsylvania",
  "nursing-license-reciprocity-rhode-island",
  "nursing-license-reciprocity-states",
  "nursing-license-reciprocity-texas",
  "nursing-license-reinstatement-illinois",
  "nursing-license-renewal-florida-requirements",
  "nursing-license-renewal-illinois-2022",
  "nursing-license-renewal-illinois-requirements",
  "nursing-license-renewal-in-illinois",
  "nursing-license-renewal-requirements-illinois",
  "nursing-license-renewal-requirements-texas",
  "nursing-license-requirements-california",
  "nursing-license-requirements-florida",
  "nursing-license-requirements-in-illinois",
  "nursing-license-requirements-texas",
  "nursing-license-texas-compact-states",
  "nursing-license-texas-renewal",
  "nursing-license-transfer-to-california",
  "nursing-license-transfer-to-florida",
  "nursing-license-transfer-to-texas",
  "nursing-license-us-to-uk",
  "nursing-license-verification-california-lvn",
  "nursing-license-waiver-california",
  "nursing-reciprocity-california",
  "nursing-reciprocity-florida",
  "nursing-reciprocity-new-york",
  "nursing-reciprocity-texas",
  "nv-rn-license-application",
  "nv-rn-license-renewal-fee",
  "nv-rn-license-renewal-requirements",
  "nyc-cpa-reciprocity",
  "ny-cpa-reciprocity",
  "ny-nj-nursing-license-reciprocity",
  "ny-reciprocity-cpa",
  "ny-teaching-certificate-reciprocity",
  "oregon-electrical-license-address-change",
  "ph-electrician",
  "reciprocity-california-rn-license",
  "reciprocity-nursing-license-in-florida",
  "reciprocity-to-california-board-of-nursing",
  "recognised-employer-partner-cpa",
  "recognised-employer-partners-cpa",
  "r-electrician",
  "renew-rn-license-nv",
  "rn-license-nevada-lookup",
  "rn-license-nys-lookup",
  "rn-license-reciprocity-california",
  "rn-licensure-nevada",
  "rn-nevada-license-renewal",
  "rn-nv-license-lookup",
  "rn-nv-license-verification",
  "sa-electrical-licence-cost",
  "sa-electrical-license",
  "sd-electrical-license-reciprocity",
  "swedish-electrical-a-license",
  "teacher-certification-california-reciprocity",
  "teacher-certification-in-florida-reciprocity",
  "teacher-certification-reciprocity-california",
  "teacher-certification-reciprocity-florida",
  "teacher-certification-reciprocity-new-york",
  "teacher-certification-reciprocity-texas",
  "teaching-certificate-florida-reciprocity",
  "teaching-certificate-florida-requirements",
  "teaching-certificate-il",
  "teaching-certificate-illinois",
  "teaching-certificate-illinois-online",
  "teaching-certificate-illinois-requirements",
  "teaching-certificate-in-new-york",
  "teaching-certificate-in-texas-requirements",
  "teaching-certificate-new-york-state",
  "teaching-certificate-reciprocity",
  "teaching-certificate-reciprocity-alabama",
  "teaching-certificate-reciprocity-by-state",
  "teaching-certificate-reciprocity-by-state-map",
  "teaching-certificate-reciprocity-california",
  "teaching-certificate-reciprocity-map",
  "teaching-certificate-reciprocity-texas",
  "teaching-certificate-reciprocity-washington",
  "teaching-certificate-requirements-florida",
  "teaching-certificate-requirements-illinois",
  "teaching-certificate-state-of-florida",
  "teaching-certificate-texas-renewal",
  "teaching-certification-texas-how-long",
  "teaching-credential-reciprocity-california",
  "teaching-license-illinois-reciprocity",
  "teaching-license-in-florida-reciprocity",
  "teaching-license-reciprocity-california",
  "teaching-license-reciprocity-florida",
  "teaching-license-reciprocity-illinois",
  "teaching-license-reciprocity-in-california",
  "teaching-license-reciprocity-new-york",
  "teaching-license-reciprocity-ny",
  "teaching-license-reciprocity-texas",
  "teaching-reciprocity-florida",
  "teaching-reciprocity-illinois",
  "teaching-reciprocity-in-california",
  "teaching-reciprocity-new-york",
  "teaching-reciprocity-ny",
  "teaching-reciprocity-texas",
  "teaching-reciprocity-with-florida",
  "texas-certification-reciprocity",
  "texas-cpa-reciprocity-application",
  "texas-cpa-reciprocity-california",
  "texas-electrician-reciprocity",
  "texas-journeyman-electrician-license-reciprocity",
  "texas-journeyman-electrician-license-reciprocity-map",
  "texas-master-electrician-license-reciprocity",
  "texas-master-electrician-license-reciprocity-map",
  "texas-medical-board-reciprocity",
  "texas-nursing-home-administrator-license-reciprocity",
  "texas-nursing-license-reciprocity",
  "texas-nursing-license-reciprocity-states",
  "texas-nursing-reciprocity-states",
  "texas-reciprocal-teaching-license",
  "texas-reciprocity-journeyman-electrician",
  "texas-teacher-certification-reciprocal-states",
  "texas-teacher-certification-reciprocity-with-other-states",
  "texas-teaching-certificate-in-other-states",
  "texas-teaching-certificate-reciprocity",
  "texas-teaching-certificate-reciprocity-states",
  "texas-teaching-certificate-transfer-another-state",
  "texas-teaching-reciprocity",
  "texas-teaching-reciprocity-states",
  "uk-electrician-working-in-dubai",
  "u-k-electrician-youtube-channel",
  "u-k-electricity-market",
  "united-kingdom-voltages",
  "what-is-a-electrical-license",
  "what-is-a-grade-electrical-licence",
  "what-is-a-limited-electrical-license",
  "what-is-an-a-grade-electrical-license",
  "what-is-a-reciprocal-cpa-license",
  "what-is-electrical-licence",
  "what-states-accept-an-illinois-teaching-license",
  "what-states-can-i-work-in-with-a-texas-nursing-license",
  "what-states-does-california-electrical-license-reciprocity",
  "what-states-does-california-have-reciprocity-with-electrical-license",
  "what-states-do-florida-electrical-license-reciprocate-with",
  "what-states-have-medical-license-reciprocity",
  "what-states-have-nursing-license-reciprocity",
  "what-states-have-reciprocity-with-florida-nursing-license",
  "what-states-have-reciprocity-with-texas-medical-license",
  "what-states-have-teaching-certification-reciprocity-with-texas",
  "what-states-have-teaching-reciprocity-with-california",
  "what-states-have-teaching-reciprocity-with-florida",
  "what-states-have-teaching-reciprocity-with-new-york",
  "what-states-reciprocate-with-california-electrical-license",
  "what-states-reciprocate-with-texas-electrical-license",
  "what-states-reciprocate-with-texas-journeyman-electrical-license",
  "what-states-reciprocate-with-texas-journeyman-electrician-license",
  "what-states-reciprocity-with-california-electrical-license",
  "what-states-reciprocity-with-florida-electrical-contractors-license",
  "what-states-reciprocity-with-florida-electrical-license",
  "what-states-reciprocity-with-texas-electrical-license",
  "what-states-recognize-california-journeyman-electrician-license",
  "what-states-require-electrical-license",
  "where-is-an-illinois-teaching-certificate-reciprocity",
  "which-states-have-cpa-reciprocity",
  "which-states-have-reciprocity-with-new-york",
  "which-states-have-teaching-license-reciprocity",
  "wireman-license-gujarat",
  "wiremans-license-department-of-labour",
  "wiremans-license-south-africa",
  "wv-cpa",
  "zeb-electrician",
  "ze-electrician",
  "zip-electrician",
];

const HTML_TEMPLATE = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}} | SoEasyHub 2026</title>
    <meta name="description" content="{{DESCRIPTION}}">
    <link rel="canonical" href="{{CANONICAL_URL}}">
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

function toTitleFromSlug(slug) {
  return String(slug || "state compliance guide")
    .replace(/\.html$/i, "")
    .replace(/-/g, " ")
    .replace(/\b\w/g, char => char.toUpperCase());
}

function renderHtml(title, description, canonicalUrl, pageCss, content, scripts = "") {
  return HTML_TEMPLATE
    .replace('{{TITLE}}', title)
    .replace('{{DESCRIPTION}}', description)
    .replace('{{CANONICAL_URL}}', canonicalUrl)
    .replace('{{PAGE_CSS}}', pageCss || '')
    .replace('{{CONTENT}}', content)
    .replace('{{SCRIPTS}}', scripts || '');
}

function fallbackPaymentBlock(slug) {
  const productParam = encodeURIComponent(slug || "compliance-packet");
  return `
    <div class="fallback-paywall">
      <h2>Need the Fast-Track Compliance Packet?</h2>
      <p>The free guide gives you the public overview. The paid packet is designed as a practical checklist for reviewing fees, forms, filing steps, and common mistakes before you submit anything.</p>
      <a href="https://payhip.com/b/qoGLF?product_id=${productParam}" target="_blank" rel="noopener sponsored">Get the Compliance Packet ($29.99)</a>
      <p class="small">Secure checkout via Payhip. Educational material only. This is not legal advice.</p>
    </div>`;
}

function renderFallbackHome(reason = "") {
  const pageCss = `
    .fallback-hero { padding: 90px 20px 60px; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); text-align: center; border-bottom: 1px solid var(--border); }
    .fallback-hero h1 { color: var(--secondary); font-size: 3rem; line-height: 1.15; margin-bottom: 18px; font-weight: 800; }
    .fallback-hero p { max-width: 760px; margin: 0 auto 26px; color: var(--text-muted); font-size: 1.15rem; }
    .fallback-search { max-width: 680px; margin: 28px auto 0; }
    .fallback-search input { width: 100%; border: 2px solid var(--border); border-radius: 999px; padding: 18px 22px; font-size: 1rem; outline: none; }
    .fallback-search input:focus { border-color: var(--primary); }
    .fallback-count { max-width: 1100px; margin: 36px auto 0; padding: 0 20px; color: #64748b; font-size: .95rem; }
    .fallback-grid { max-width: 1100px; margin: 50px auto; padding: 0 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }
    .fallback-card { background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 24px; text-decoration: none; color: inherit; box-shadow: 0 4px 12px rgba(15,23,42,.04); }
    .fallback-card h3 { color: var(--secondary); margin-bottom: 10px; }
    .fallback-card p { color: var(--text-muted); }
    .status-note { max-width: 900px; margin: 20px auto; color: #64748b; font-size: .9rem; text-align: center; }
  `;
  const cards = FALLBACK_SITEMAP_SLUGS.map(slug => {
    const title = toTitleFromSlug(slug);
    return `
    <a class="fallback-card audit-card" href="/p/${slug}">
      <h3>${title}</h3>
      <p>Compliance overview, filing checklist, fee review, and common application risks for ${title}.</p>
    </a>`;
  }).join("");

  const content = `
    <section class="fallback-hero">
      <h1>State Compliance Guides That Stay Useful</h1>
      <p>Clear, practical checklists for licensing, renewal, reciprocity, and business compliance. Start with a free guide, then unlock a paid packet when you need a tighter filing checklist.</p>
      ${fallbackPaymentBlock("general-compliance-packet")}
      <div class="fallback-search">
        <input id="archiveSearch" type="search" placeholder="Search ${FALLBACK_SITEMAP_SLUGS.length} compliance guides...">
      </div>
    </section>
    <p class="fallback-count">Local archive mode: showing ${FALLBACK_SITEMAP_SLUGS.length} saved compliance guide URLs while the live database is unavailable.</p>
    <div class="fallback-grid">${cards}</div>
    ${reason ? `<p class="status-note">Live database content is temporarily unavailable, so this stable fallback page is being served.</p>` : ""}`;
  const scripts = `
    <script>
      const archiveSearch = document.getElementById('archiveSearch');
      if (archiveSearch) {
        archiveSearch.addEventListener('input', function(event) {
          const term = event.target.value.toLowerCase();
          document.querySelectorAll('.audit-card').forEach(function(card) {
            card.style.display = card.textContent.toLowerCase().includes(term) ? '' : 'none';
          });
        });
      }
    </script>`;

  return renderHtml(
    "Multi-State Business Compliance Guides",
    "SoEasyHub provides clear compliance guides and paid checklist packets for licensing, renewal, reciprocity, and business filings.",
    "https://soeasyhub.com/",
    pageCss,
    content,
    scripts
  );
}

function renderFallbackArticle(slug, reason = "") {
  const title = toTitleFromSlug(slug);
  const pageCss = `
    .fallback-article { max-width: 900px; margin: 48px auto; padding: 0 20px; }
    .fallback-panel { background: #fff; border: 1px solid var(--border); border-radius: 16px; padding: 42px; box-shadow: 0 4px 12px rgba(15,23,42,.04); }
    .fallback-panel h1 { color: var(--secondary); font-size: 2.5rem; line-height: 1.15; margin-bottom: 18px; }
    .fallback-panel h2 { color: var(--secondary); margin-top: 34px; margin-bottom: 12px; }
    .fallback-panel p, .fallback-panel li { font-size: 1.08rem; line-height: 1.75; color: var(--text); }
    .fallback-panel ul { margin: 14px 0 22px 22px; }
    .fallback-note { background: var(--teacher-bg); border-left: 4px solid var(--primary); padding: 18px; border-radius: 0 8px 8px 0; margin: 24px 0; }
    .fallback-paywall { margin: 36px 0; background: #fff7ed; border: 2px dashed #f97316; border-radius: 12px; padding: 28px; text-align: center; }
    .fallback-paywall h2 { margin-top: 0; color: #c2410c; }
    .fallback-paywall a { display: inline-block; margin-top: 16px; background: #f97316; color: white; padding: 16px 28px; border-radius: 8px; font-weight: 800; text-decoration: none; }
    .fallback-paywall .small { margin-top: 12px; font-size: .9rem; color: #64748b; }
    .status-note { color: #64748b; font-size: .9rem; margin-top: 20px; }
  `;
  const content = `
    <article class="fallback-article">
      <div class="fallback-panel">
        <p style="color: var(--primary); font-weight: 800; text-transform: uppercase; letter-spacing: .06em;">Compliance Guide</p>
        <h1>${title}</h1>
        <div class="fallback-note">
          <strong>Research note:</strong> Use this page as an organized starting point. State rules change, and official board pages should be checked before filing.
        </div>
        <p>This guide is built for people who need a plain-English compliance overview before dealing with forms, fees, deadlines, reciprocity rules, or renewal steps.</p>
        <h2>What to Check First</h2>
        <ul>
          <li>Confirm the official state board or agency responsible for this filing.</li>
          <li>Check current application fees, renewal fees, and any non-refundable charges.</li>
          <li>Review required documents, ID checks, transcripts, fingerprints, insurance, or business records.</li>
          <li>Look for deadlines, grace periods, continuing education rules, or state-specific exceptions.</li>
          <li>Save proof of submission and payment before leaving the official portal.</li>
        </ul>
        ${fallbackPaymentBlock(slug)}
        <h2>Important Disclaimer</h2>
        <p>SoEasyHub is an educational publisher and compliance research tool. We do not provide legal advice, professional licensing decisions, or guaranteed outcomes. Always verify requirements with the official agency or a licensed professional.</p>
        ${reason ? `<p class="status-note">Live database article content is temporarily unavailable, so this stable fallback article is being served.</p>` : ""}
      </div>
    </article>`;

  return renderHtml(
    title,
    `Compliance guide and checklist packet for ${title}.`,
    `https://soeasyhub.com/p/${slug}`,
    pageCss,
    content
  );
}

function renderFallbackSitemap() {
  const slugs = FALLBACK_SITEMAP_SLUGS;
  const urls = [
    "https://soeasyhub.com/",
    "https://soeasyhub.com/about",
    "https://soeasyhub.com/contact",
    "https://soeasyhub.com/privacy",
    "https://soeasyhub.com/terms",
    ...slugs.map(slug => `https://soeasyhub.com/p/${slug}`)
  ];
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(url => `  <url><loc>${url}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>`).join("\n")}
</urlset>`;
  return body;
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Supabase Config (from Environment Variables)
    const SUPABASE_URL = env.SUPABASE_URL;
    const SUPABASE_KEY = env.SUPABASE_KEY;

    // Helper: Supabase Fetch
    async function supabaseFetch(endpoint, options = {}) {
      if (!SUPABASE_URL || !SUPABASE_KEY) {
        throw new Error("Missing Database Credentials");
      }
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

    // === ROUTE 0: Google Search Console & Bing IndexNow Verification ===
    if (path === "/googleleaf4d2d986493bb7e.html") {
      return new Response("google-site-verification: googleleaf4d2d986493bb7e.html", {
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    }
    
    if (path === "/822834cd8b83498a90e4fd5ef715fa14.txt") {
      return new Response("822834cd8b83498a90e4fd5ef715fa14", {
        headers: { "Content-Type": "text/plain; charset=utf-8" },
      });
    }

    if (path === "/robots.txt") {
      return new Response(
        "User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: https://soeasyhub.com/sitemap.xml\n",
        { headers: { "Content-Type": "text/plain; charset=utf-8" } }
      );
    }

    // === ROUTE 1: HOME PAGE (Grid) ===
    if (path === "/" || path === "/index.html") {
      try {
        // Query: Get top 100 articles (where final_article is not null)
        // Fields: id, slug, keyword, category, last_mined_at
        const data = await supabaseFetch(
          `grich_keywords_pool?select=id,slug,keyword,category,last_mined_at&final_article=not.is.null&order=last_mined_at.desc&limit=300`
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
                        <p>Hi, I'm <strong>Bai</strong>. As an educator, legal expert, and licensed counselor, I know firsthand the anxiety that entrepreneurs face when dealing with state regulations. The legal jargon, the hidden fees, the endless paperwork鈥攊t's overwhelming.</p>
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
                .replace('{{CANONICAL_URL}}', 'https://soeasyhub.com/')
                .replace('{{PAGE_CSS}}', pageCss)
                .replace('{{CONTENT}}', gridHtml)
                .replace('{{SCRIPTS}}', scripts);

            return new Response(html, {
              headers: { "Content-Type": "text/html; charset=utf-8" },
            });
        }
      } catch (err) {
        return new Response(renderFallbackHome(err.message), {
          headers: { "Content-Type": "text/html; charset=utf-8", "X-SoEasyHub-Fallback": "home" },
        });
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
            <a href="https://payhip.com/b/qoGLF?product_id=${slug}" target="_blank" rel="noopener sponsored" style="display: inline-block; background: #f97316; color: #ffffff !important; font-weight: 800; padding: 18px 36px; border-radius: 8px; text-decoration: none; font-size: 1.15rem; box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4); transition: transform 0.2s;">
              GET THE INDEPENDENT COMPLIANCE PACKET ($29.99)
            </a>
            <p style="font-size: 0.95rem; margin-top: 15px; margin-bottom: 0; color: #64748b;">Secure Payment via Stripe/PayPal 鈥?Instant PDF Download</p>
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
        <blockquote class="teacher-note" cite="https://soeasyhub.com/about">
            <strong>Research Note from Bai:</strong> 
            Compliance in ${stateName} can feel confusing because state-board pages are often scattered. Use this guide as an organized starting point, then verify the current rules with the official board before filing.
        </blockquote>`;

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
                        <div class="author-role">Legally Reviewed by Bai (Lead Counsel) 鈥?Updated ${date}</div>
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

        const descriptionText = `2026 Updated: Complete compliance and reciprocity guide for ${title}. Step-by-step application requirements, fees, and official contact information for out-of-state transfers.`;

        // Generate JSON-LD Schema
        const schemaObj = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title + " - 2026 Compliance Guide",
            "description": descriptionText,
            "author": {
                "@type": "Person",
                "name": "Bai",
                "jobTitle": "Compliance Research Editor"
            },
            "publisher": {
                "@type": "Organization",
                "name": "SoEasyHub"
            },
            "dateModified": article.last_mined_at || new Date().toISOString()
        };
        const schemaString = JSON.stringify(schemaObj);
        const schemaHtml = `<script type="application/ld+json">${schemaString}</script></head>`;

        const html = HTML_TEMPLATE
            .replace('{{TITLE}}', title)
            .replace('{{DESCRIPTION}}', descriptionText)
            .replace('{{CANONICAL_URL}}', `https://soeasyhub.com/p/${slug}`)
            .replace('{{PAGE_CSS}}', pageCss)
            .replace('{{CONTENT}}', articleHtml)
            .replace('{{SCRIPTS}}', '')
            .replace('</head>', schemaHtml);

        return new Response(html, {
          headers: { "Content-Type": "text/html; charset=utf-8" },
        });

      } catch (err) {
         return new Response(renderFallbackArticle(slug, err.message), {
           headers: { "Content-Type": "text/html; charset=utf-8", "X-SoEasyHub-Fallback": "article" },
         });
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
                </url>
                <url>
                    <loc>https://soeasyhub.com/about</loc>
                    <changefreq>monthly</changefreq>
                    <priority>0.5</priority>
                </url>
                <url>
                    <loc>https://soeasyhub.com/contact</loc>
                    <changefreq>monthly</changefreq>
                    <priority>0.5</priority>
                </url>
                <url>
                    <loc>https://soeasyhub.com/privacy</loc>
                    <changefreq>yearly</changefreq>
                    <priority>0.3</priority>
                </url>
                <url>
                    <loc>https://soeasyhub.com/terms</loc>
                    <changefreq>yearly</changefreq>
                    <priority>0.3</priority>
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
            return new Response(renderFallbackSitemap(), {
                headers: { "Content-Type": "application/xml; charset=utf-8", "X-SoEasyHub-Fallback": "sitemap" },
            });
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
                <p>Founded by Bai鈥攁n experienced educator, licensed legal counsel, and psychological counselor鈥擲oEasyHub was born out of a profound understanding of entrepreneurial anxiety. We know that navigating state-by-state regulations can feel like deciphering a foreign language. The stress of missing a deadline or filing the wrong form shouldn't hold your business back.</p>
                <p>That's why we built this platform: to translate complex legal jargon into clear, actionable, stress-free steps.</p>
                <h2>Our Approach (E-E-A-T)</h2>
                <ul>
                    <li><strong>Experience:</strong> We study real state-board forms, public instructions, and filing workflows.</li>
                    <li><strong>Expertise:</strong> Every guide is based on public official-source research and written in plain English.</li>
                    <li><strong>Authoritativeness:</strong> We cite official sources where available and keep guides structured for fast verification.</li>
                    <li><strong>Trust:</strong> We clearly state that our materials are educational and should be checked against the current official board rules.</li>
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
                <p><strong>The information provided on SoEasyHub is for educational and informational purposes only and does NOT constitute legal advice.</strong> We are an information aggregator and educational publisher. No attorney-client relationship is formed by using this site. Always consult a licensed professional for your specific business needs.</p>
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
            .replace('{{CANONICAL_URL}}', `https://soeasyhub.com${path}`)
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

