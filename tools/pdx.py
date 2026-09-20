"""Small lossless-span reader for the brace-delimited CK3 reference files."""
import re
from dataclasses import dataclass

TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}]|(?:!=|>=|<=|\?=|=|>|<)|[^\s{}=<>!?#"]+')

@dataclass
class Node:
    key: str
    value: object
    start: int
    end: int

def parse(text):
    tokens = [(m.group(), m.start(), m.end()) for m in TOKEN.finditer(text) if not m.group().startswith('#')]
    def block(i):
        out = []
        while i < len(tokens) and tokens[i][0] != '}':
            key, start, end = tokens[i]; i += 1
            if key == '{':
                value, i = block(i)
                end = tokens[i][2]; i += 1
                out.append(Node('', value, start, end))
                continue
            if i < len(tokens) and tokens[i][0] in ('=', '?=', '!=', '<', '>', '>=', '<='):
                i += 1
                if i + 1 < len(tokens) and tokens[i][0] in ('hsv', 'hsv360', 'rgb') and tokens[i + 1][0] == '{':
                    i += 1
                if i < len(tokens) and tokens[i][0] == '{':
                    value, i = block(i + 1)
                    end = tokens[i][2]; i += 1
                else:
                    value, _, end = tokens[i]; i += 1
            else:
                value = None
            out.append(Node(key, value, start, end))
        return out, i
    return block(0)[0]

def get(nodes, key, default=None):
    return next((n.value for n in nodes if n.key == key), default)

def vals(nodes, key):
    return [n.value for n in nodes if n.key == key]

def decode(data):
    try: s = data.decode('utf-8-sig')
    except UnicodeDecodeError: s = data.decode('cp1252')
    return s.replace('\r', '')

def title_tree(archive):
    titles = {}; parents = {}; texts = {}
    def walk(nodes, parent, text):
        for n in nodes:
            if re.fullmatch('[hekdcb]_[^\s{}=:]+', n.key) and isinstance(n.value, list):
                titles[n.key] = n.value; parents[n.key] = parent; texts[n.key] = text[n.start:n.end]
                walk(n.value, n.key, text)
    for path in archive.namelist():
        if path.startswith('game/common/landed_titles/') and path.endswith('.txt'):
            text = decode(archive.read(path)); walk(parse(text), None, text)
    return titles, parents, texts
