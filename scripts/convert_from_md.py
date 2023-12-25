import json, re
from typing import List, Callable, Tuple

def deUnicodeize(text):
    p = re.compile(r"\\u[0-9a-fA-F]+")
    matches = p.findall(text)
    if matches:
        print("Striping unicode", matches)
        return p.sub(r"", text)
    return text


def replaceQuotes(in_text: str):
    replace_with = {
        '```': (lambda lang: f'<pre class="triple-quote {lang.lower()}">', "</pre>"),
        '`': (lambda _: '<span class="single-quote">', "</span>")
    }
    p = re.compile(r'```(\w+)?\n')
    langs = p.findall(in_text)
    in_text = p.sub('```\n', in_text)
    for (quotes, replaced_by) in replace_with.items():
        lang_ix = 0
        while quotes in in_text:
            if lang_ix < len(langs):
                lang = langs[lang_ix]
            else:
                lang = ""

            # Escape md
            ix = in_text.find(quotes)
            offset = in_text[ix+len(quotes):].find(quotes)
            in_text = in_text[:ix] + in_text[ix:ix+len(quotes)+offset].replace('#', '\\#') + in_text[ix+len(quotes)+offset:]

            # Patch for javascript wasm post
            old_replaced_by = replaced_by
            if "output.value +=" in in_text[ix-len("output.value += "):ix]:
                replaced_by = (lambda _: "\\quote", "\\quote")

            in_text = in_text.replace(quotes, replaced_by[0](lang), 1).replace(quotes, replaced_by[1], 1)
            lang_ix += 2

            # Needed for patch for javascript wasm post
            if old_replaced_by != replaced_by:
                replaced_by = old_replaced_by

    return in_text

def generateMultilineString(in_text: str):
    return [t for t in in_text.split("\n") if t.strip()]

def combineTransformations(transformations: List) -> Callable[[str], str]:
    def foo(text):
        for t in transformations:
            text = t(text)
        return text
    return foo

def instertReplacement(in_text: str, span: Tuple[int, int], replacement: str) -> str:
    return in_text[:span[0]] + replacement + in_text[span[1]:]

def unescapeMd(in_text: str) -> str:
    p = re.compile(r"((\[(.*?)\])(\((http.*?)\)))")
    while p.search(in_text):
        matches = p.search(in_text)
        start, end = matches.span(0)
        _, _, content, _, link = matches.groups()
        in_text = instertReplacement(in_text, (start, end), f'<a target="_blank" href="{link}">{content}</a>')

    # Patch for javascript wasm post
    in_text = in_text.replace("\\quote", "`")

    # Unescape escaped hashes
    return in_text.replace("\\#", "#")

def escapePhp(in_text: str) -> str:
    return in_text.replace("<?php", "")

def createLi(text_line: str) -> str:
    if text_line.startswith("- "):
        return text_line.replace("- ", "<li>", 1)
    return text_line

def convert(md_lines):
    tmp_dict = {}
    headers_types = ["title", "excerpt", "author", "tags"]
    count_dashes = 0
    body_start = None
    for (i, h) in enumerate(md_lines):
        if "---" in h:
            count_dashes += 1
        if count_dashes == 2:
            body_start = i
            break
        for ht in headers_types:
            if str(h).startswith(ht):
                tmp_dict[ht] = h[len(ht)+1:-1].strip()

    text_body = replaceQuotes(''.join(md_lines[body_start+1:]))

    transform = combineTransformations([
        escapePhp,
        unescapeMd,
        generateMultilineString,
    ])

    body = []
    tmp_str = ""
    for l in text_body.splitlines(True):
        if str(l).startswith("####"):
            if tmp_str:
                body += [["div", [], transform(tmp_str)]]
            body += [["h5", [], transform(l[4:].strip())]]
            tmp_str = ""
        elif str(l).startswith("###"):
            if tmp_str:
                body += [["div", [], transform(tmp_str)]]
            body += [["h4", [], transform(l[3:].strip())]]
            tmp_str = ""
        elif str(l).startswith("##"):
            if tmp_str:
                body += [["div", [], transform(tmp_str)]]
            body += [["h3", [], transform(l[2:].strip())]]
            tmp_str = ""
        elif str(l).startswith("#"):
            if tmp_str:
                body += [["div", [], transform(tmp_str)]]
            body += [["h2", [], transform(l[1:].strip())]]
            tmp_str = ""
        else:
            tmp_str += createLi(l)

    if tmp_str:
        body += [["div", [], transform(tmp_str)]]

    return deUnicodeize(f"""
let base = import("../base.gr")

# Create new Post Object
let post = base.Post(
    {tmp_dict.get("title")},
    {tmp_dict.get("excerpt")},
    {tmp_dict.get("author")},
    {json.dumps(tmp_dict.get("tags").strip())},
    {json.dumps(body, indent=4)}
)
""")

def rewrite(count):
    import os
    for f in os.listdir("./_posts")[:count]:
        with open("./_posts/" + f, "r") as inp:
            converted = convert(inp.readlines())
        with open(f"./src/pages/posts/{f[:-3]}.gr", "w") as out:
            out.write(converted)


def main(argv):
    rewrite(int(argv[1]))

if __name__ == "__main__":
    import sys
    main(sys.argv)
