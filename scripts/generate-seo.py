#!/usr/bin/env python3
"""Update technical SEO metadata and sitemap; use --check for validation only."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://painclinic.am/"
LANGUAGES = ("hy", "en", "ru")
HOME = {"hy": "index.html", "en": "en.html", "ru": "ru.html"}
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


class Metadata(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.canonicals = []
        self.alternates = {}
        self.redirect = False
        self.language = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.language = attrs.get("lang")
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            self.redirect = True
        if tag == "link":
            rel = attrs.get("rel", "").split()
            if "canonical" in rel:
                self.canonicals.append(attrs.get("href"))
            if "alternate" in rel and "hreflang" in attrs:
                lang = attrs["hreflang"]
                if lang in self.alternates:
                    raise ValueError(f"Duplicate hreflang: {lang}")
                self.alternates[lang] = attrs.get("href")


def canonical(filename):
    return BASE if filename == "index.html" else BASE + filename


def language_group(filename):
    if filename in HOME.values():
        return HOME
    match = re.fullmatch(r"(.+)-(hy|en|ru)\.html", filename)
    if not match:
        raise ValueError(f"No language group for {filename}")
    group = {lang: f"{match[1]}-{lang}.html" for lang in LANGUAGES}
    for target in group.values():
        if not (ROOT / target).is_file():
            raise ValueError(f"Missing translation: {target}")
    return group


def generate():
    outputs = {}
    urls = []
    for path in sorted(ROOT.glob("*.html")):
        source = path.read_text(encoding="utf-8")
        metadata = Metadata(source)
        if metadata.redirect:
            # Keep legacy redirect URLs out of the canonical sitemap.
            continue
        group = language_group(path.name)
        expected_alternates = {lang: canonical(group[lang]) for lang in LANGUAGES}
        if metadata.language not in LANGUAGES or group[metadata.language] != path.name:
            raise ValueError(f"Incorrect HTML language: {path.name}")
        additions = []
        expected_canonical = canonical(path.name)
        if metadata.canonicals and metadata.canonicals != [expected_canonical]:
            raise ValueError(f"Conflicting canonical: {path.name}")
        if not metadata.canonicals:
            additions.append(f'<link rel="canonical" href="{expected_canonical}">')
        for lang, url in expected_alternates.items():
            if lang in metadata.alternates:
                if metadata.alternates[lang] != url:
                    raise ValueError(f"Conflicting hreflang: {path.name}: {lang}")
            else:
                additions.append(f'<link rel="alternate" hreflang="{lang}" href="{url}">')
        if additions:
            source, count = re.subn(r"</head\s*>", lambda _: "\n" + "\n".join(additions) + "\n</head>", source, count=1, flags=re.I)
            if count != 1:
                raise ValueError(f"Missing head: {path.name}")
        outputs[path] = source
        urls.append(expected_canonical)

    ET.register_namespace("", NS)
    sitemap = ET.Element(f"{{{NS}}}urlset")
    for url in urls:
        entry = ET.SubElement(sitemap, f"{{{NS}}}url")
        ET.SubElement(entry, f"{{{NS}}}loc").text = url
    ET.indent(sitemap, space="  ")
    outputs[ROOT / "sitemap.xml"] = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(sitemap, encoding="unicode") + "\n"
    outputs[ROOT / "robots.txt"] = "User-agent: *\nAllow: /\n\nSitemap: " + BASE + "sitemap.xml\n"
    return outputs, len(urls)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated metadata or files are out of date")
    args = parser.parse_args()
    outputs, count = generate()
    changed = [path for path, value in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != value]
    if args.check and changed:
        print("Out of date: " + ", ".join(str(path.relative_to(ROOT)) for path in changed), file=sys.stderr)
        return 1
    if not args.check:
        for path in changed:
            path.write_text(outputs[path], encoding="utf-8")
    print(f"Validated {count} canonical pages and their reciprocal HY/EN/RU language links; {len(changed)} files {'need updating' if args.check else 'updated'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
