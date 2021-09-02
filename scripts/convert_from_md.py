import json, re

def deUnicodeize(text):
    p = re.compile(r"\\u[0-9a-fA-F]+")
    matches = p.findall(text)
    if matches:
        print("Striping unicode", matches)
        return p.sub(r"", text)
    return text


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

    body = []
    tmp_str = ""
    append = False
    for l in md_lines[body_start+1:]:
        if str(l).startswith("####"):
            body += [["h5", [], l[4:].strip()]]
            append = True
        elif str(l).startswith("###"):
            body += [["h4", [], l[3:].strip()]]
            append = True
        elif str(l).startswith("##"):
            body += [["h3", [], l[2:].strip()]]
            append = True
        elif str(l).startswith("#"):
            body += [["h2", [], l[1:].strip()]]
            append = True
        else:
            tmp_str += l

        if append and tmp_str:
            body += [["div", [], tmp_str]]
            append = False
            tmp_str = ""

    return deUnicodeize(f"""
let base = import("../base.gr")

# Create new Post Object
let post = base.Post(
    {tmp_dict.get("title")},
    {tmp_dict.get("excerpt")},
    {tmp_dict.get("author")},
    {json.dumps(list(map(lambda s: s.strip(), tmp_dict.get("tags").split(","))))},
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
