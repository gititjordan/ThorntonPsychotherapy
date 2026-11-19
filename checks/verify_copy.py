import argparse
from html.parser import HTMLParser
from pathlib import Path
import difflib
import json
import re
import subprocess

PAGES = ('index.html', 'about.html', 'privacy.html', 'accessibility.html')
SEO_ATTRS = {'name', 'property', 'content', 'charset', 'rel', 'href', 'type'}

class CopyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.body = False
        self.ignored = []
        self.result = {'copy': [], 'accessibility': [], 'links': [], 'media': [], 'seo': []}

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'body':
            self.body = True
        if tag in ('script', 'style', 'svg', 'title'):
            self.ignored.append(tag)
        if self.body and not self.ignored:
            for name in ('aria-label', 'alt', 'title'):
                if attrs.get(name):
                    self.result['accessibility'].append([tag, name, attrs[name]])
            if tag == 'a' and 'href' in attrs:
                self.result['links'].append(attrs['href'])
            if tag in ('img', 'iframe'):
                self.result['media'].append([tag, attrs.get('src')])
        elif not self.body and (tag == 'meta' or (tag == 'link' and attrs.get('rel') == 'canonical')):
            self.result['seo'].append({key: val for key, val in attrs.items() if key in SEO_ATTRS})

    def handle_endtag(self, tag):
        if self.ignored and tag == self.ignored[-1]:
            self.ignored.pop()

    def handle_data(self, data):
        text = ' '.join(data.split())
        if not text:
            return
        if self.body and not self.ignored:
            self.result['copy'].append(text)
        elif not self.body and self.ignored and self.ignored[-1] == 'title':
            self.result['seo'].append({'title': text})

def capture(source):
    parser = CopyParser()
    parser.feed(source)
    parser.result['structured_data'] = [
        json.loads(block)
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)
    ]
    return parser.result

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('snapshot', type=Path)
    cli.add_argument('--revision')
    cli.add_argument('--repo', type=Path, default=Path.cwd())
    args = cli.parse_args()
    if args.revision:
        with args.snapshot.open('w') as dest:
            json.dump({name: capture(subprocess.check_output(['git', 'show', f'{args.revision}:{name}'], cwd=args.repo, text=True)) for name in PAGES}, dest, ensure_ascii=False, indent=2)
            dest.write('\n')
        return

    expected = json.loads(args.snapshot.read_text())
    # The header Book link was intentionally removed from both pages.
    for name, href in (('index.html', '#book'), ('about.html', 'index.html#book')):
        expected[name]['copy'].remove('Book')
        expected[name]['links'].remove(href)

    # The booking calendar moved to the dedicated Thornton Psychotherapy account.
    original_calendar = 'https://calendly.com/gladys-thornton-anchoringpoint/30min'
    updated_calendar = 'https://calendly.com/gladys-thorntonpsychotherapy/30min'
    for media in expected['index.html']['media']:
        if media[0] == 'iframe' and media[1].startswith(original_calendar + '?'):
            media[1] = media[1].replace(original_calendar, updated_calendar, 1)

    # The practice phone number changed and the footer gained a contact email.
    for page in expected.values():
        page['copy'] = ['(519) 465-6921' if text == '(226) 774-5695' else text for text in page['copy']]
        page['links'] = ['tel:+15194656921' if href == 'tel:+12267745695' else href for href in page['links']]

    email = 'gladys@thorntonpsychotherapy.com'
    for name in ('index.html', 'about.html'):
        page = expected[name]
        page['copy'].insert(page['copy'].index('(519) 465-6921') + 1, email)
        page['links'].insert(page['links'].index('tel:+15194656921') + 1, f'mailto:{email}')

    mismatches = []
    for name in PAGES:
        actual = capture((args.repo / name).read_text())
        for key, values in expected[name].items():
            if values != actual[key]:
                original = json.dumps(values, ensure_ascii=False, indent=2).splitlines()
                revised = json.dumps(actual[key], ensure_ascii=False, indent=2).splitlines()
                mismatches.extend(difflib.unified_diff(original, revised, f'{name} original {key}', f'{name} current {key}', lineterm=''))
    if mismatches:
        print('\n'.join(mismatches))
        raise SystemExit(1)
    print('All four pages match the snapshot after the approved header, booking, and contact changes.')

if __name__ == '__main__':
    main()
