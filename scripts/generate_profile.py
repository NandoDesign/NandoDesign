#!/usr/bin/env python3
"""Gera assets/profile.svg: uma única caixa com todo o conteúdo do perfil.

Os dados de contribuição e de perfil vêm da API do GitHub, então o arquivo é
regenerado automaticamente pelo workflow .github/workflows/update-profile.yml.
Requer um token (GITHUB_TOKEN no Actions, ou `gh auth token` localmente).
"""

import base64
import datetime
import html
import json
import os
import subprocess
import sys
import urllib.request

USER = "NandoDesign"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "profile.svg")
LOGO = os.path.join(ROOT, "assets", "logo.png")

F = "Helvetica Neue, Helvetica, Arial, sans-serif"
W = 1200
BLUE, INK, GREY, LINE, SOFT = "#0057FF", "#191919", "#707070", "#ECECEC", "#F9F9F9"
COVER = "#F0F0F0"  # fundo das capas de projeto no Behance
TAN = "#A58A6E"    # tom bege do pôster do projeto "Portifólio" (estimado visualmente)
PLATE = "#6F6F6F"  # cinza do pôster (estimado visualmente)
TABS = ["Sobre", "Trabalhos", "Stack", "Foco", "Formação", "GitHub", "Contato"]
PORTFOLIO_URL = "https://www.behance.net/NandoDesign-real"
GITHUB_URL = f"https://github.com/{USER}"
EMAIL = "nandopv12@gmail.com"

# ---------------------------------------------------------------- conteúdo
SOBRE = [
    "Estudante de Engenharia de Software com background em Design Gráfico,",
    "explorando a interseção entre desenvolvimento, interfaces e experiência do usuário.",
    "Meu foco é construir produtos digitais combinando código bem estruturado,",
    "pensamento visual e atenção à experiência.",
]
PROJETOS = [
    ("01", "Portfólio de desenhos à mão", "Desenho"),
    ("02", "Portfólio", "Portfólio"),
    ("03", "Saturno", "Ilustração"),
]
STACK = [
    ("FRONT-END", [("HTML5", "#E34F26", "#FFFFFF"), ("CSS3", "#1572B6", "#FFFFFF"), ("JavaScript", "#F7DF1E", INK)]),
    ("DESIGN & PRODUTO", [("Figma", "#F24E1E", "#FFFFFF"), ("Illustrator", "#FF9A00", INK), ("Photoshop", "#31A8FF", INK),
                          ("Premiere Pro", "#9999FF", INK), ("After Effects", "#9999FF", INK)]),
    ("WORKFLOW", [("Git", "#F05032", "#FFFFFF"), ("GitHub", "#181717", "#FFFFFF"), ("VS Code", "#007ACC", "#FFFFFF")]),
]
FLUXO = [("Software Engineering", 200), ("Visual Design", 180), ("Interfaces", 160), ("User Experience", 180), ("Digital Products", 200)]
OPS = ["+", "→", "→", "→"]
FOCO_LINHAS = [
    "Design — hierarquia visual, tipografia, motion design e UX",
    "Engenharia — código limpo, componentização e performance",
    "Objetivo — interfaces que funcionam de forma impecável para quem usa",
]
FORMACAO = [
    ("Bacharelado em Engenharia de Software", "PUC Minas", "2026 — 2029"),
    ("Design Gráfico & Motion", "Escola ZION", "Em andamento"),
]
CONTATO = [
    "Estou aberto a oportunidades, projetos colaborativos e conversas",
    "sobre tecnologia, design e produtos digitais.",
]


def esc(s):
    return html.escape(s, quote=False)


# ---------------------------------------------------------------- dados
def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not t:
        t = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
    if not t:
        sys.exit("Nenhum token: defina GITHUB_TOKEN ou faça `gh auth login`.")
    return t


QUERY = """query($login:String!){ user(login:$login){
  followers{totalCount} repositories(ownerAffiliations:OWNER, privacy:PUBLIC){totalCount}
  contributionsCollection{ totalCommitContributions contributionCalendar{
    totalContributions weeks{ contributionDays{ date contributionCount } } } } } }"""


def fetch():
    # Usa o gh (já presente no runner do Actions e autenticado pelo token).
    env = dict(os.environ, GH_TOKEN=token())
    res = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={USER}"],
                         capture_output=True, text=True, env=env)
    if res.returncode != 0:
        sys.exit(f"Falha ao consultar a API: {res.stderr.strip()}")
    payload = json.loads(res.stdout)
    if payload.get("errors"):
        sys.exit(f"Erro na API: {payload['errors']}")
    return payload["data"]["user"]


# ---------------------------------------------------------------- SVG
def title_block(y, num, title, sub):
    return f'''<rect x="40" y="{y+24}" width="66" height="40" rx="20" fill="{BLUE}"/>
<text x="73" y="{y+50}" text-anchor="middle" font-family="{F}" font-size="16" font-weight="800" letter-spacing="1" fill="#FFFFFF">{num}</text>
<text x="128" y="{y+53}" font-family="{F}" font-size="30" font-weight="800" letter-spacing="-0.5" fill="{INK}">{esc(title)}</text>
<text x="128" y="{y+78}" font-family="{F}" font-size="15" fill="{GREY}">{esc(sub)}</text>
<rect x="128" y="{y+88}" width="0" height="4" rx="2" fill="{BLUE}"><animate attributeName="width" from="0" to="120" dur="0.9s" fill="freeze"/></rect>'''


def chip(x, y, label, fill, color, delay):
    w = round(len(label) * 8.6 + 28)
    s = (f'<g><animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" begin="{delay:.2f}s" dur="0.5s" fill="freeze"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="17" fill="{fill}"/>'
         f'<text x="{x + w / 2}" y="{y + 22}" text-anchor="middle" font-family="{F}" font-size="15" font-weight="700" fill="{color}">{esc(label)}</text></g>')
    return s, w


def build(data, logo_b64, today):
    out = []
    y = 0

    # --- hero (fundo, pontos e cartão da logo)
    HERO_H = 336
    out.append(f'''<clipPath id="frame"><rect width="{W}" height="__H__" rx="24"/></clipPath>
<clipPath id="hero"><rect width="{W}" height="{HERO_H}"/></clipPath>
<defs><pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.6" fill="{BLUE}" fill-opacity="0.14"/></pattern>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="{INK}" flood-opacity="0.12"/></filter></defs>
<g clip-path="url(#frame)"><g clip-path="url(#hero)">
<rect width="{W}" height="{HERO_H}" fill="{SOFT}"/>
<rect width="{W}" height="{HERO_H}" fill="url(#dots)"/>
<circle cx="1010" cy="180" r="270" fill="none" stroke="{BLUE}" stroke-opacity="0.07" stroke-width="2"/>
<circle cx="1010" cy="180" r="200" fill="none" stroke="{TAN}" stroke-opacity="0.22" stroke-width="2" stroke-dasharray="4 10"/>
</g></g>''')
    out.append(f'''<g font-family="{F}">
<rect x="72" y="64" width="146" height="34" rx="17" fill="{BLUE}"/>
<text x="145" y="86" text-anchor="middle" font-size="14" font-weight="700" letter-spacing="3" fill="#FFFFFF">PORTFÓLIO</text>
<text x="70" y="168" font-size="64" font-weight="800" letter-spacing="-2" fill="{INK}">Fernando Pereira</text>
<text x="72" y="212" font-size="26" font-weight="600" fill="{INK}">Software Engineering × Product Design</text>
<text x="72" y="248" font-size="18" fill="{GREY}">Interfaces que funcionam, comunicam e fazem sentido.</text>
</g>''')
    out.append(f'''<g transform="translate(880 40)">
<rect x="12" y="12" width="280" height="280" rx="24" fill="{BLUE}" fill-opacity="0.12"/>
<rect x="1" y="1" width="278" height="278" rx="24" fill="#FFFFFF" stroke="{LINE}" stroke-width="2" filter="url(#shadow)"/>
<image x="65" y="18" width="150" height="150" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{logo_b64}"/>
<text x="140" y="214" text-anchor="middle" font-family="{F}" font-size="13" font-weight="700" letter-spacing="3" fill="{GREY}">SOFTWARE × DESIGN</text>
<rect x="110" y="230" width="60" height="4" rx="2" fill="{BLUE}"/>
</g>''')
    y = HERO_H
    out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="2"/>')

    # --- abas (como as abas do Behance: cinza, ativa em preto com linha)
    tx = 40
    for i, t in enumerate(TABS):
        ativa = i == 0
        out.append(f'<text x="{tx}" y="{y + 34}" font-family="{F}" font-size="15" font-weight="600" fill="{INK if ativa else GREY}">{esc(t)}</text>')
        tw = len(t) * 7.8
        if ativa:
            out.append(f'<rect x="{tx}" y="{y + 46}" width="{tw:.0f}" height="2" fill="{INK}"/>')
        tx += tw + 36
    y += 56
    out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="2"/>')

    # --- 01 Sobre
    out.append(title_block(y, "01", "Sobre", "Quem sou e o que construo"))
    cy = y + 124
    out.append(f'<rect x="48" y="{cy - 22}" width="6" height="{len(SOBRE) * 32 + 4}" rx="3" fill="{BLUE}"/>')
    for i, t in enumerate(SOBRE):
        out.append(f'<text x="72" y="{cy + i * 32}" font-family="{F}" font-size="20" fill="{INK}">{esc(t)}</text>')
    y = cy + len(SOBRE) * 32 + 12
    out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="2"/>')

    # --- 02 Trabalhos
    out.append(title_block(y, "02", "Trabalhos", "Projetos publicados no Behance"))
    cy = y + 124
    bw, gap = 360, 20
    for i, (num, t, tag) in enumerate(PROJETOS):
        x = 40 + i * (bw + gap)
        tag_w = len(tag) * 8.2 + 28
        out.append(f'''<g><animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" begin="{0.1 + i*0.1:.2f}s" dur="0.5s" fill="freeze"/>
<defs><linearGradient id="poster{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{TAN}" stop-opacity="0.35"/><stop offset="1" stop-color="{PLATE}" stop-opacity="0.18"/></linearGradient></defs>
<rect x="{x}" y="{cy}" width="{bw}" height="190" rx="4" fill="{COVER}"/>
<rect x="{x}" y="{cy}" width="{bw}" height="96" rx="4" fill="url(#poster{i})"/>
<text x="{x + 24}" y="{cy + 74}" font-family="{F}" font-size="60" font-weight="800" letter-spacing="-2" fill="{BLUE}">{num}</text>
<text x="{x + 24}" y="{cy + 118}" font-family="{F}" font-size="18" font-weight="700" fill="{INK}">{esc(t)}</text>
<rect x="{x + 24}" y="{cy + 134}" width="{tag_w:.0f}" height="28" rx="14" fill="#FFFFFF" stroke="{LINE}" stroke-width="2"/>
<text x="{x + 24 + tag_w/2:.0f}" y="{cy + 153}" text-anchor="middle" font-family="{F}" font-size="13" font-weight="700" fill="{GREY}">{esc(tag)}</text></g>''')
    y = cy + 190 + 16
    out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="2"/>')

    # --- 03 Stack
    out.append(title_block(y, "03", "Stack", "Ferramentas que uso no dia a dia"))
    k = 0
    for gi, (label, chips) in enumerate(STACK):
        gy = y + 124 + gi * 84
        out.append(f'<text x="40" y="{gy + 4}" font-family="{F}" font-size="13" font-weight="700" letter-spacing="2" fill="{GREY}">{esc(label)}</text>')
        x = 40
        for name, fill, color in chips:
            s, w = chip(x, gy + 16, name, fill, color, 0.15 + k * 0.05)
            out.append(s)
            x += w + 10
            k += 1
    y = y + 124 + len(STACK) * 84 + 4
    out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="2"/>')

    # --- 04 Foco
    out.append(title_block(y, "04", "Foco", "Onde meu trabalho se encontra"))
    by = y + 124
    x = 40
    for i, (name, w) in enumerate(FLUXO):
        last = i == len(FLUXO) - 1
        fill, color = (BLUE, "#FFFFFF") if last else (SOFT, INK)
        out.append(f'<rect x="{x}" y="{by}" width="{w}" height="64" rx="16" fill="{fill}" stroke="{LINE}" stroke-width="2"/>'
                   f'<text x="{x + w/2}" y="{by + 38}" text-anchor="middle" font-family="{F}" font-size="16" font-weight="700" fill="{color}">{esc(name)}</text>')
        if i < len(OPS):
            out.append(f'<text x="{x + w + 18}" y="{by + 40}" text-anchor="middle" font-family="{F}" font-size="22" font-weight="700" fill="{BLUE}">{OPS[i]}</text>')
        x += w + 36
    out.append(f'<text x="40" y="{by + 112}" font-family="{F}" font-size="20" font-weight="700" fill="{BLUE}">Design defines the experience. Code makes it real.</text>')
    for i, t in enumerate(FOCO_LINHAS):
        yy = by + 150 + i * 28
        out.append(f'<rect x="40" y="{yy - 11}" width="10" height="10" rx="2" fill="{BLUE}"/>'
                   f'<text x="62" y="{yy}" font-family="{F}" font-size="18" fill="{INK}">{esc(t)}</text>')
    y = by + 150 + len(FOCO_LINHAS) * 28 + 8
    out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="2"/>')

    # --- 05 Formação
    out.append(title_block(y, "05", "Formação", "Trajetória acadêmica"))
    fy = y + 116
    for i, (course, inst, period) in enumerate(FORMACAO):
        yr = fy + i * 72
        out.append(f'<text x="40" y="{yr + 28}" font-family="{F}" font-size="20" font-weight="700" fill="{INK}">{esc(course)}</text>'
                   f'<text x="40" y="{yr + 52}" font-family="{F}" font-size="16" fill="{GREY}">{esc(inst)}</text>'
                   f'<rect x="990" y="{yr + 12}" width="170" height="34" rx="17" fill="{SOFT}" stroke="{LINE}" stroke-width="2"/>'
                   f'<text x="1075" y="{yr + 34}" text-anchor="middle" font-family="{F}" font-size="14" font-weight="700" fill="{INK}">{esc(period)}</text>')
        if i < len(FORMACAO) - 1:
            out.append(f'<line x1="40" y1="{yr + 64}" x2="1160" y2="{yr + 64}" stroke="{LINE}" stroke-width="2"/>')
    y = fy + len(FORMACAO) * 72 + 4
    out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="2"/>')

    # --- 06 GitHub em números
    out.append(title_block(y, "06", "GitHub em números", "Atividade nos últimos 12 meses"))
    cal = data["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    counts = sorted(d["contributionCount"] for wk in weeks for d in wk["contributionDays"] if d["contributionCount"] > 0) or [0]
    q1, q2, q3 = counts[len(counts) // 4], counts[len(counts) // 2], counts[(3 * len(counts)) // 4]
    palette = [LINE, "#C9DDFF", "#7FAEFF", "#2F7BFF", BLUE]

    def level(c):
        if c == 0:
            return 0
        return 1 if c <= q1 else 2 if c <= q2 else 3 if c <= q3 else 4

    tiles = [(str(cal["totalContributions"]), "Contribuições no ano"),
             (str(data["contributionsCollection"]["totalCommitContributions"]), "Commits"),
             (str(data["repositories"]["totalCount"]), "Repositórios públicos"),
             (str(data["followers"]["totalCount"]), "Seguidores")]
    ty = y + 124
    tw = (1120 - 3 * 16) / 4
    for i, (num, label) in enumerate(tiles):
        tx = 40 + i * (tw + 16)
        out.append(f'<g><animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" begin="{0.1 + i*0.08:.2f}s" dur="0.5s" fill="freeze"/>'
                   f'<rect x="{tx:.1f}" y="{ty}" width="{tw:.1f}" height="92" rx="16" fill="{SOFT}" stroke="{LINE}" stroke-width="2"/>'
                   f'<text x="{tx + 20:.1f}" y="{ty + 28}" font-family="{F}" font-size="12" font-weight="700" letter-spacing="1.5" fill="{GREY}">{esc(label.upper())}</text>'
                   f'<text x="{tx + 20:.1f}" y="{ty + 70}" font-family="{F}" font-size="38" font-weight="800" letter-spacing="-1" fill="{INK}">{num}</text></g>')
    hy = ty + 92 + 28
    cell, pitch = 14, 18
    for wi, wk in enumerate(weeks):
        for day in wk["contributionDays"]:
            dow = datetime.date.fromisoformat(day["date"]).weekday()
            row = (dow + 1) % 7
            lvl = level(day["contributionCount"])
            out.append(f'<rect x="{40 + wi * pitch}" y="{hy + row * pitch}" width="{cell}" height="{cell}" rx="3" fill="{palette[lvl]}">'
                       f'<animate attributeName="fill-opacity" from="0.35" to="1" begin="{0.3 + wi * 0.02:.2f}s" dur="0.4s" fill="freeze"/></rect>')
    ly = hy + 7 * pitch + 14
    out.append(f'<text x="40" y="{ly + 12}" font-family="{F}" font-size="13" fill="{GREY}">Menos</text>')
    for i, c in enumerate(palette):
        out.append(f'<rect x="{100 + i*18}" y="{ly}" width="14" height="14" rx="3" fill="{c}"/>')
    out.append(f'<text x="{100 + 5*18 + 6}" y="{ly + 12}" font-family="{F}" font-size="13" fill="{GREY}">Mais</text>')
    y = ly + 14 + 26
    out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="2"/>')

    # --- 07 Contato
    out.append(title_block(y, "07", "Contato", "Vamos conversar"))
    cy = y + 124
    for i, t in enumerate(CONTATO):
        out.append(f'<text x="40" y="{cy + i * 30}" font-family="{F}" font-size="20" fill="{INK}">{esc(t)}</text>')
    y = cy + len(CONTATO) * 30 + 12
    out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="2"/>')

    # --- rodapé
    out.append(f'<text x="{W/2}" y="{y + 40}" text-anchor="middle" font-family="{F}" font-size="15" fill="{GREY}">'
               f'Building at the intersection of <tspan font-weight="700" fill="{INK}">code × design × experience</tspan>.  ·  '
               f'Atualizado automaticamente em {today}</text>')
    total_h = y + 70
    out.append(f'<rect x="1" y="1" width="{W-2}" height="{total_h-2}" rx="24" fill="none" stroke="{LINE}" stroke-width="2"/>')
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{total_h}" viewBox="0 0 {W} {total_h}" '
            f'role="img" aria-label="Perfil de Fernando Pereira">')
    body = "\n".join(out).replace("__H__", str(total_h))
    # moldura branca por baixo de tudo
    base = f'<rect width="{W}" height="{total_h}" rx="24" fill="#FFFFFF"/>'
    return head + "\n" + base + "\n" + body + "\n</svg>\n"


def pill(label, w, fill, color, stroke=None):
    """Botão em pílula, como 'Seguir' e 'Mensagem' no Behance."""
    h = 48
    st = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">\n'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{h/2}" fill="{fill}"{st}/>\n'
            f'<text x="{w/2}" y="{h/2 + 6}" text-anchor="middle" font-family="{F}" font-size="16" font-weight="600" fill="{color}">{esc(label)}</text>\n</svg>\n')


def write_buttons():
    d = os.path.join(ROOT, "assets", "buttons")
    os.makedirs(d, exist_ok=True)
    files = {
        "seguir.svg": pill("Seguir no GitHub", 220, BLUE, "#FFFFFF"),
        "mensagem.svg": pill("Enviar e-mail", 200, "#F5F8FF", BLUE, stroke="#E0EAFF"),
        "portfolio.svg": pill("Ver portfólio no Behance", 260, BLUE, "#FFFFFF"),
    }
    for name, svg in files.items():
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write(svg)


def main():
    data = fetch()
    logo_b64 = base64.b64encode(open(LOGO, "rb").read()).decode()
    today = datetime.date.today().strftime("%d/%m/%Y")
    svg = build(data, logo_b64, today)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    write_buttons()
    print("gerado:", OUT, "| contribuições:", data["contributionsCollection"]["contributionCalendar"]["totalContributions"])


if __name__ == "__main__":
    main()
