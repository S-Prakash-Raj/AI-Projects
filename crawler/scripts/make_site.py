from pathlib import Path

N=500
out = Path("site")
out.mkdir(exist_ok=True)
for i in range(N):
    targets = [(i * 7 + 1) % N, (i * 13 + 5) % N, (i + 1) % N]
    links = "".join(f'<a href="/page{j}.html">p{j}</a>' for j in targets)
    (out / f"page{i}.html").write_text(f"<html><body>{links}</body></html>")