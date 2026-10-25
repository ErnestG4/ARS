import re, sys, json
data = open(sys.argv[1], 'rb').read().decode('latin-1')
toks = re.findall(r'\[[^\]]*\]|\([^)]*\)|/[^\s/\[\]()]+|[^\s\[\]()]+', data)
stack, num = [], []
M = [1, 0, 0, 1, 0, 0]          # CTM
gstack = []
def mul(a, b):  # a then b: x' = x·a ·b  (PDF row-vector convention: new = a × current)
    return [a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3], a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3],
            a[4]*b[0]+a[5]*b[2]+b[4], a[4]*b[1]+a[5]*b[3]+b[5]]
def app(x, y): return (x*M[0]+y*M[2]+M[4], x*M[1]+y*M[3]+M[5])
circles, texts, lines, cur, path = [], [], [], None, []
tm = None
for t in toks:
    try:
        num.append(float(t)); continue
    except ValueError:
        pass
    if t == 'cm':
        M = mul(num[-6:], M)
    elif t == 'q': gstack.append(M[:])
    elif t == 'Q': M = gstack.pop() if gstack else M
    elif t == 'm':
        path = [('m', num[-2], num[-1])]
    elif t == 'l': path.append(('l', num[-2], num[-1]))
    elif t == 'c': path.append(('c',) + tuple(num[-6:]))
    elif t == 're': path.append(('re',) + tuple(num[-4:]))
    elif t in ('f*', 'f', 'S', 's', 'B', 'b', 'n'):
        cs = [p for p in path if p[0] == 'c']
        if len(cs) == 8 and path[0][0] == 'm':
            xs = [p[5] for p in cs] + [path[0][1]]; ys = [p[6] for p in cs] + [path[0][2]]
            cx, cy = (max(xs)+min(xs))/2, (max(ys)+min(ys))/2
            circles.append(app(cx, cy))
        else:
            for i in range(1, len(path)):
                if path[i][0] == 'l' and path[i-1][0] in ('m', 'l'):
                    lines.append((app(*path[i-1][-2:]), app(path[i][1], path[i][2])))
        path = []
    elif t == 'Tm': tm = num[-6:]
    elif t.startswith('(') or t.startswith('['):
        if tm is not None:
            texts.append((app(tm[4], tm[5]), t[:40]))
    num = [] if t not in ('cm',) else []
json.dump(dict(circles=circles, texts=texts, lines=lines), open(sys.argv[2], 'w'))
print(len(circles), 'circles;', len(texts), 'texts;', len(lines), 'lines')
