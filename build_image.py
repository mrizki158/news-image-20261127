#!/usr/bin/env python3
"""Render entry.png for make.fun news-image-20261127.

Flat editorial illustration drawn with PIL shapes only. No photos, no
network, no randomness. Deterministic: the same bytes on every run.

Structure follows the proven winner template: serif date masthead, UTC
strip + numbers strip at the top, 3 illustrated leads with number
banners, 10 fully illustrated tiles, a verification badge on every
story, a world map with pins, a dense 3-column index and a DATE CHECK
box. 37 stories, 9 regions, 12 fields, all first reported on
Friday 27 November 2026.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 24
CW = W - 2 * M

PAPER = (248, 244, 236)
INK = (22, 35, 63)
NAVY = (22, 35, 63)
RED = (179, 39, 30)
TEAL = (15, 118, 110)
GREEN = (27, 122, 61)
BLUE = (29, 78, 216)
AMBER = (180, 83, 9)
CREAM = (234, 227, 210)
STRIP = (233, 226, 208)
GREY = (90, 96, 110)
SKY = (214, 231, 244)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

REGION_COLORS = {
    "North America": (29, 78, 216),
    "South America": (5, 150, 105),
    "Western Europe": (124, 58, 237),
    "Eastern Europe": (220, 38, 38),
    "Middle East": (234, 88, 12),
    "East Asia": (8, 145, 178),
    "Southeast Asia": (101, 163, 13),
    "Oceania": (15, 118, 110),
    "Africa": (180, 83, 9),
}
BADGE_COLORS = {
    "OFFICIAL": (27, 122, 61),
    "CONFIRMED": (29, 78, 216),
    "REPORTED": (180, 83, 9),
}


def F(path, size):
    return ImageFont.truetype(path, size)


def rr(d, x, y, w, h, r, fill, outline=None, width=1):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill,
                        outline=outline, width=width)


def circ(d, cx, cy, r, fill=None, outline=None, width=1):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
              outline=outline, width=width)


def poly(d, pts, fill, outline=None):
    d.polygon(pts, fill=fill, outline=outline)


def wrap_text(text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if font.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, path, size, max_w, max_lines, min_size=8):
    """Shrink font until text fits in max_lines; returns (font, lines)."""
    while size >= min_size:
        f = F(path, size)
        lines = wrap_text(text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    f = F(path, min_size)
    return f, wrap_text(text, f, max_w)[:max_lines]


def trunc(text, font, max_w):
    if font.getlength(text) <= max_w:
        return text
    while text and font.getlength(text + "\u2026") > max_w:
        text = text[:-1]
    return text + "\u2026"


def draw_tracked(d, cx, y, text, font, fill, tracking=3):
    total = sum(font.getlength(c) for c in text) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking


def badge(d, x, y, kind):
    f = F(SANS_B, 9)
    w = int(f.getlength(kind)) + 10
    rr(d, x, y, w, 13, 3, BADGE_COLORS[kind])
    d.text((x + 5, y + 2), kind, font=f, fill=(255, 255, 255))
    return w


def chip(d, x, y, text, bg=NAVY):
    f = F(SANS_B, 10)
    w = int(f.getlength(text)) + 10
    rr(d, x, y, w, 15, 3, bg)
    d.text((x + 5, y + 2), text, font=f, fill=(255, 255, 255))
    return w


def pin_num(d, cx, cy, num):
    circ(d, cx, cy, 8, NAVY, outline=(255, 255, 255), width=1)
    f = F(SANS_B, 9)
    t = str(num)
    d.text((cx - f.getlength(t) / 2, cy - 5), t, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- data ---

UTC_EVENTS = [
    ("01:00", "NZ final count: hung parliament 65\u201365"),
    ("01:24", "Drone attack reported in Ukraine"),
    ("01:30", "China: industrial profits +20.1% (NBS)"),
    ("01:52", "Lagos crash: 6 burnt to death, 12 hurt"),
    ("03:00", "Kenya unveils Sh30bn road-safety plan"),
    ("04:03", "Trump open to nuclear talks with Putin, Xi"),
    ("11:00", "Black Friday: US stores open; markets close 1pm ET"),
]

NUMBERS = [
    ("65\u201365", "NZ SEATS SPLIT"),
    ("+20.1%", "CHINA FACTORY PROFITS"),
    ("$350BN", "JAPAN DEFENCE PLAN"),
    ("67", "HOMEPLUS STORES SHUT"),
    ("\u20ac25BN", "UKRAINE 2027 GAP"),
    ("48", "PATRIOT MISSILES HELD UP"),
]

LEADS = [
    {
        "num": 1, "region": "Oceania", "badge": "OFFICIAL",
        "banner": "65\u201365", "banner_color": TEAL,
        "headline": "New Zealand hung: 65\u201365",
        "fact": "Final count leaves both blocs one seat short of a majority; the Opportunity Party holds the balance.",
        "illus": "nz",
    },
    {
        "num": 2, "region": "East Asia", "badge": "OFFICIAL",
        "banner": "+20.1%", "banner_color": RED,
        "headline": "China factory profits jump 20.1%",
        "fact": "October industrial profits surge year on year, the strongest in months, Beijing's statistics bureau says.",
        "illus": "china",
    },
    {
        "num": 3, "region": "Eastern Europe", "badge": "CONFIRMED",
        "banner": "48", "banner_color": NAVY,
        "headline": "Zelensky: US too slow on Patriots",
        "fact": "48 interceptor missiles still unapproved; Kyiv faces a \u20ac25bn funding gap for 2027.",
        "illus": "zelensky",
    },
]

TILES = [
    {"num": 4, "region": "East Asia", "badge": "CONFIRMED", "chip": "$350BN",
     "headline": "Japan plans $350bn defence build-up",
     "fact": "Five-year plan from FY2027; below the 80tn yen officials sought.",
     "illus": "japan"},
    {"num": 5, "region": "East Asia", "badge": "CONFIRMED", "chip": "67",
     "headline": "Homeplus shuts all 67 stores",
     "fact": "Cash-strapped chain suspends hypermarkets under court rehabilitation.",
     "illus": "homeplus"},
    {"num": 6, "region": "Western Europe", "badge": "OFFICIAL", "chip": "\u20ac1.78TN",
     "headline": "EU budget summit ends with no deal",
     "fact": "Talks run past midnight; next attempt 17 December.",
     "illus": "eu"},
    {"num": 7, "region": "South America", "badge": "CONFIRMED", "chip": "17",
     "headline": "US sanctions 17 Venezuelan officials",
     "fact": "OFAC targets officials over drug trafficking and election fraud claims.",
     "illus": "venezuela"},
    {"num": 8, "region": "Eastern Europe", "badge": "REPORTED", "chip": "2",
     "headline": "Russia hits two Ukraine bridges",
     "fact": "Overnight Geran strikes reported on Dnipro and Zaporizhzhia crossings.",
     "illus": "bridges"},
    {"num": 9, "region": "North America", "badge": "CONFIRMED", "chip": "25,000",
     "headline": "Trump: Putin wants the war to end",
     "fact": "25,000 lives a month lost, he says; backs Russia's return to the G7.",
     "illus": "trump"},
    {"num": 10, "region": "Western Europe", "badge": "OFFICIAL", "chip": "ECB",
     "headline": "Spain's de Cos to lead the ECB",
     "fact": "Euro leaders back him to succeed Christine Lagarde.",
     "illus": "ecb"},
    {"num": 11, "region": "Southeast Asia", "badge": "CONFIRMED", "chip": "3 TONNES",
     "headline": "Military planes smuggled 3t of meth",
     "fact": "Six charged in Shah Alam over 96.64kg at an air force base.",
     "illus": "malaysia"},
    {"num": 12, "region": "Middle East", "badge": "CONFIRMED", "chip": "CAESAR",
     "headline": "Syria hails move to lift US sanctions",
     "fact": "Congress moves to repeal the Caesar Act; Riyadh welcomes it.",
     "illus": "syria"},
    {"num": 13, "region": "Oceania", "badge": "CONFIRMED", "chip": "3 STATES",
     "headline": "Severe storms bear down on SE Australia",
     "fact": "Heavy rain, damaging winds and large hail from tonight into Saturday.",
     "illus": "storms"},
]

INDEX = [
    ("Western Europe", "OFFICIAL", "24 states back extra Ukraine loan",
     "Bulgaria joins only the non-military part; decision returns in December."),
    ("East Asia", "CONFIRMED", "Asia shares mixed; Hong Kong leads",
     "Tech and China earnings lift HK; Taiwan +200 pts in morning trade."),
    ("North America", "CONFIRMED", "US markets reopen, close early",
     "NYSE and Nasdaq shut at 1pm ET; stores open 6am; REI stays closed."),
    ("Oceania", "REPORTED", "Bushfires: new advice for Palana",
     "Two emergency warnings remain on Flinders Island; watch and act at Mount Boyes."),
    ("East Asia", "CONFIRMED", "57% call Yoon's martial law insurrection",
     "Gallup Korea: President Lee's approval 41%, up one point."),
    ("East Asia", "CONFIRMED", "Woman caught trying to cross to the North",
     "Troops detain a woman in her 30s in Gangwon Province."),
    ("East Asia", "CONFIRMED", "Seoul targets AI-assisted exam cheating",
     "300+ cheating cases reported within a week of the entrance exam."),
    ("East Asia", "CONFIRMED", "Two navy submarines damaged",
     "Two 1,800-ton boats damaged in separate incidents, navy says."),
    ("East Asia", "CONFIRMED", "Police search justice ministry",
     "Raid over an alleged leak about ex-justice minister nominee Kim Seung-won."),
    ("East Asia", "CONFIRMED", "'White Blast' tops box office again",
     "Ninth straight day at No. 1; about 578,000 admissions since 18 Nov."),
    ("Africa", "REPORTED", "Six burnt to death in Lagos crash",
     "12 injured in the road accident, reported at 01:52 GMT."),
    ("Africa", "REPORTED", "Kenya unveils Sh30bn road-safety plan",
     "Plan aims to curb crashes; announced at 03:00 GMT."),
    ("Africa", "REPORTED", "Fake emergency calls hit 57m in 2025",
     "Nigeria's telecom regulator counts 57 million fake calls this year."),
    ("Africa", "REPORTED", "IEBC rejects rules for 94 parties",
     "Kenya's electoral body rejects nomination rules for 94 political parties."),
    ("Africa", "REPORTED", "REFFA revives hope for Ghana film",
     "Producer Selassie Ibrahim's festival draws praise for the industry."),
    ("Africa", "REPORTED", "20 Ugandans repatriated from Myanmar",
     "Citizens brought home from scam compounds, Daily Nation reports."),
    ("Southeast Asia", "CONFIRMED", "Malaysia passes RM510bn Budget 2027",
     "RM376.8bn operating, RM83bn development; now to the Senate and King."),
    ("Southeast Asia", "REPORTED", "Nvidia said to halt server shipments",
     "Shipments to Malaysia, Singapore, Thailand and Indonesia paused amid US export controls."),
    ("Southeast Asia", "CONFIRMED", "Malaysia seeks 19% tariff ceiling",
     "US talks run to early 2027 over Section 301 claims."),
    ("North America", "REPORTED", "Trump open to nuclear talks with Putin, Xi",
     "Trilateral disarmament talks floated in a Forbes interview."),
    ("Africa", "REPORTED", "Ghana MP questions frozen-funds transfer",
     "Afenyo-Markin presses the OSP over alleged movement of frozen funds."),
    ("Africa", "REPORTED", "Benin unveils 2027 budget of 5,295bn FCFA",
     "Draft budget tabled for 2027; economic and social council to review."),
    ("Africa", "REPORTED", "Tanzania's $1bn carbon ambition",
     "Daily Nation reports a billion-dollar carbon plan."),
    ("Africa", "REPORTED", "East Africa risks hosting AFCON without cashing in",
     "Daily Nation warns the region may miss the tournament's payoff."),
]

DATE_CHECK_LEFT = (
    "LEFT OUT \u2014 earlier news, not today: Kim's nuke order (26 Nov) \u00b7 "
    "Asia rebound, Taiex +3.05% (26 Nov) \u00b7 Thanksgiving nor'easter (26 Nov) \u00b7 "
    "Egypt tanker fire, 31 dead (25\u201326 Nov) \u00b7 Bank of Korea rate 3.25% (26 Nov) \u00b7 "
    "COP31 collapse (22 Nov) \u00b7 Bangkok refinery blast (26 Nov) \u00b7 "
    "Guinea-Bissau vote delay (26 Nov)."
)
DATE_CHECK_NOTYET = (
    "NOT YET \u2014 still to come: Taiwan local elections (Sat 28 Nov) \u00b7 "
    "Spain election (Sun) \u00b7 F1 Qatar GP practice (Fri evening) \u00b7 "
    "Serbia presidential vote (27 Dec) \u00b7 India GDP (30 Nov) \u00b7 "
    "EU budget retry (17 Dec)."
)

MAP_LAND = [
    [(8, 14), (58, 10), (72, 18), (66, 40), (48, 52), (30, 48), (14, 34), (6, 26)],
    [(58, 58), (78, 56), (88, 72), (78, 96), (64, 92), (56, 74)],
    [(112, 12), (132, 8), (140, 20), (130, 30), (114, 26)],
    [(112, 36), (138, 34), (144, 58), (132, 84), (118, 72), (110, 52)],
    [(140, 8), (236, 8), (240, 34), (214, 48), (186, 44), (160, 36), (142, 24)],
    [(196, 74), (226, 72), (230, 88), (200, 90)],
]
# (local x, y, pin number) inside the map box
MAP_PINS = [
    (238, 94, 1), (212, 26, 2), (142, 16, 3), (230, 30, 4), (220, 30, 5),
    (116, 16, 6), (52, 58, 7), (152, 24, 8), (24, 28, 9), (126, 24, 10),
    (198, 56, 11), (158, 32, 12), (222, 86, 13),
]
MAP_LEGEND = [
    "1 Wellington  2 Beijing  3 Kyiv  4 Tokyo  5 Seoul  6 Brussels  7 Caracas",
    "8 Dnipro  9 Washington  10 Frankfurt  11 Kuala Lumpur  12 Damascus  13 Melbourne",
]


# ------------------------------------------------------- illustrations ---

def illus_nz(d, x, y, w, h):
    """Wellington parliament + two equal 65-seat bars."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + 88, x + w, y + h], fill=(122, 162, 92))
    # parliament building: white block + dome + flag
    d.rectangle([x + 18, y + 40, x + 108, y + 88], fill=(250, 250, 248))
    d.pieslice([x + 38, y + 16, x + 88, y + 52], 180, 360, fill=(250, 250, 248))
    d.rectangle([x + 60, y + 8, x + 66, y + 22], fill=(90, 96, 110))
    poly(d, [(x + 66, y + 8), (x + 84, y + 13), (x + 66, y + 18)], fill=RED)
    for cx in (30, 52, 74, 96):
        d.rectangle([x + cx, y + 56, x + cx + 8, y + 72], fill=(120, 150, 190))
    # two equal bars
    f = F(SANS_B, 15)
    d.rectangle([x + 128, y + 26, x + w - 14, y + 50], fill=TEAL)
    d.text((x + 136, y + 29), "65", font=f, fill=(255, 255, 255))
    d.text((x + 168, y + 30), "COALITION", font=F(SANS_B, 10),
           fill=(255, 255, 255))
    d.rectangle([x + 128, y + 56, x + w - 14, y + 80], fill=RED)
    d.text((x + 136, y + 59), "65", font=f, fill=(255, 255, 255))
    d.text((x + 168, y + 60), "LEFT BLOC", font=F(SANS_B, 10),
           fill=(255, 255, 255))
    d.text((x + 128, y + 88), "130 SEATS IN PARLIAMENT",
           font=F(SANS_B, 10), fill=(60, 66, 80))


def illus_china(d, x, y, w, h):
    """Factory + rising profit chart."""
    d.rectangle([x, y, x + w, y + h], fill=(245, 236, 214))
    # factory
    d.rectangle([x + 16, y + 62, x + 136, y + h], fill=(60, 70, 90))
    poly(d, [(x + 16, y + 62), (x + 46, y + 44), (x + 76, y + 62),
             (x + 106, y + 44), (x + 136, y + 62)], fill=(60, 70, 90))
    for cx in (28, 52, 76):
        d.rectangle([x + cx, y + 26, x + cx + 12, y + 52], fill=(60, 70, 90))
    for cx, cy, r in ((34, 18, 6), (58, 12, 7), (82, 20, 5)):
        circ(d, x + cx, y + cy, r, fill=(200, 205, 210))
    for wx in (28, 52, 76, 100, 122):
        d.rectangle([x + wx, y + 78, x + wx + 8, y + 92], fill=(250, 210, 90))
    # rising chart
    pts = [(x + 150, y + 92), (x + 190, y + 78), (x + 225, y + 80),
           (x + 258, y + 52), (x + 292, y + 30)]
    d.line(pts, fill=GREEN, width=4)
    poly(d, [(x + 292, y + 30), (x + 282, y + 32), (x + 290, y + 42)],
         fill=GREEN)
    for bx, bh in ((152, 12), (192, 22), (228, 18), (260, 38)):
        d.rectangle([x + bx, y + 104 - bh, x + bx + 18, y + 104],
                    fill=(232, 180, 60))
    d.text((x + 150, y + 6), "OCTOBER", font=F(SANS_B, 11), fill=(90, 96, 110))


def illus_zelensky(d, x, y, w, h):
    """Shield + Patriot missile battery under a night sky."""
    d.rectangle([x, y, x + w, y + h], fill=(58, 72, 110))
    for sx, sy in ((30, 16), (90, 10), (250, 14), (280, 34), (60, 44),
                   (280, 70), (20, 70)):
        circ(d, x + sx, y + sy, 2, fill=(255, 255, 255))
    # shield
    poly(d, [(x + 138, y + 16), (x + 208, y + 16), (x + 208, y + 66),
             (x + 173, y + 98), (x + 138, y + 66)], fill=(30, 90, 180),
         outline=(250, 210, 90))
    d.line([(x + 138, y + 16), (x + 208, y + 16), (x + 208, y + 66),
            (x + 173, y + 98), (x + 138, y + 66), (x + 138, y + 16)],
           fill=(250, 210, 90), width=3)
    # star inside shield
    cx, cy, r = x + 173, y + 52, 16
    star = []
    import math
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr_ = r if i % 2 == 0 else r * 0.45
        star.append((cx + rr_ * math.cos(ang), cy + rr_ * math.sin(ang)))
    poly(d, star, fill=(250, 210, 90))
    # missile battery
    d.rectangle([x + 16, y + 82, x + 116, y + 98], fill=(40, 46, 60))
    for mx in (28, 52, 76, 100):
        d.line([(x + mx, y + 82), (x + mx + 16, y + 46)], fill=(200, 205, 210),
               width=4)
        circ(d, x + mx + 16, y + 46, 3, fill=(250, 210, 90))
    for wx in (32, 62, 92):
        circ(d, x + wx, y + 100, 6, fill=(25, 28, 36))
    d.text((x + 16, y + 6), "AIR DEFENCE", font=F(SANS_B, 11),
           fill=(220, 225, 235))


def illus_japan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    circ(d, x + 148, y + 18, 11, fill=RED)
    for bx, bh in ((16, 12), (36, 20), (56, 30)):
        d.rectangle([x + bx, y + 42 - bh, x + bx + 14, y + 42],
                    fill=(232, 180, 60))
    poly(d, [(x + 92, y + 30), (x + 118, y + 22), (x + 118, y + 30),
             (x + 104, y + 30), (x + 104, y + 38), (x + 92, y + 38)],
         fill=(240, 240, 240))


def illus_homeplus(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 235, 220))
    d.rectangle([x + 10, y + 10, x + 130, y + 42], fill=(179, 39, 30))
    for ax in range(10, 130, 16):
        d.rectangle([x + ax, y + 10, x + ax + 8, y + 18], fill=(250, 250, 248))
    d.rectangle([x + 20, y + 24, x + 120, y + 42], fill=(140, 145, 150))
    for ly in (29, 34, 39):
        d.line([(x + 20, y + ly), (x + 120, y + ly)], fill=(100, 105, 110),
               width=1)
    d.rectangle([x + 140, y + 12, x + w - 8, y + 40], fill=(60, 70, 90))
    d.text((x + 146, y + 18), "CLOSED", font=F(SANS_B, 11),
           fill=(255, 255, 255))


def illus_eu(d, x, y, w, h):
    import math
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 140))
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        sx = x + 44 + 15 * math.cos(ang)
        sy = y + 24 + 15 * math.sin(ang)
        circ(d, sx, sy, 2, fill=(250, 210, 90))
    circ(d, x + 132, y + 24, 16, fill=(232, 180, 60))
    d.line([(x + 126, y + 10), (x + 138, y + 38)], fill=(90, 70, 20), width=2)
    d.text((x + 126, y + 13), "\u20ac", font=F(SANS_B, 18), fill=(90, 70, 20))


def illus_venezuela(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(245, 240, 225))
    d.rectangle([x + 16, y + 8, x + 96, y + 40], fill=(255, 255, 255),
                outline=(150, 150, 150))
    for ly in (16, 23, 30):
        d.line([(x + 24, y + ly), (x + 88, y + ly)], fill=(170, 175, 180),
               width=2)
    circ(d, x + 132, y + 24, 15, outline=RED, width=3)
    d.line([(x + 124, y + 16), (x + 140, y + 32)], fill=RED, width=3)
    d.line([(x + 140, y + 16), (x + 124, y + 32)], fill=RED, width=3)
    d.text((x + 152, y + 17), "OFAC", font=F(SANS_B, 12), fill=RED)


def illus_bridges(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 225, 240))
    d.rectangle([x, y + 34, x + w, y + h], fill=(70, 130, 180))
    d.line([(x + 8, y + 40), (x + w - 8, y + 40)], fill=(255, 255, 255),
           width=2)
    # bridge deck + arch
    d.rectangle([x + 8, y + 16, x + w - 8, y + 22], fill=(60, 66, 76))
    d.arc([x + 30, y - 6, x + 150, y + 34], 180, 360, fill=(60, 66, 76),
          width=3)
    # crack + blast star
    d.line([(x + 88, y + 16), (x + 84, y + 22), (x + 92, y + 22)],
           fill=(40, 40, 40), width=2)
    import math
    cx, cy, r = x + 90, y + 8, 10
    star = []
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        rr_ = r if i % 2 == 0 else r * 0.45
        star.append((cx + rr_ * math.cos(ang), cy + rr_ * math.sin(ang)))
    poly(d, star, fill=(250, 180, 40))


def illus_trump(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 235, 232))
    # US flag
    for i in range(4):
        d.rectangle([x + 12, y + 10 + i * 7, x + 72, y + 17 + i * 7],
                    fill=RED if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x + 12, y + 10, x + 34, y + 24], fill=(30, 60, 140))
    # Russian flag
    d.rectangle([x + 112, y + 10, x + 172, y + 19], fill=(255, 255, 255))
    d.rectangle([x + 112, y + 19, x + 172, y + 28], fill=(30, 90, 180))
    d.rectangle([x + 112, y + 28, x + 172, y + 37], fill=RED)
    # podium
    d.rectangle([x + 82, y + 30, x + 104, y + 44], fill=(120, 84, 50))
    d.rectangle([x + 78, y + 28, x + 108, y + 32], fill=(90, 60, 35))


def illus_ecb(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    poly(d, [(x + 28, y + 12), (x + 108, y + 12), (x + 68, y + 2)],
         fill=(250, 250, 248))
    d.rectangle([x + 30, y + 14, x + 106, y + 18], fill=(250, 250, 248))
    for cx in (34, 52, 70, 88):
        d.rectangle([x + cx, y + 18, x + cx + 8, y + 38],
                    fill=(250, 250, 248))
    d.rectangle([x + 28, y + 38, x + 108, y + 42], fill=(250, 250, 248))
    d.text((x + 132, y + 10), "\u20ac", font=F(SANS_B, 28),
           fill=(232, 180, 60))


def illus_malaysia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(180, 210, 235))
    # military plane
    poly(d, [(x + 16, y + 20), (x + 118, y + 16), (x + 132, y + 22),
             (x + 118, y + 28), (x + 16, y + 28)], fill=(90, 96, 110))
    poly(d, [(x + 60, y + 20), (x + 84, y + 6), (x + 92, y + 20)],
         fill=(70, 76, 90))
    poly(d, [(x + 66, y + 28), (x + 88, y + 40), (x + 78, y + 28)],
         fill=(70, 76, 90))
    circ(d, x + 122, y + 22, 3, fill=(250, 210, 90))
    # packages
    for px, py, pw in ((146, 32, 12), (160, 28, 14), (146, 40, 10)):
        d.rectangle([x + px, y + py, x + px + pw, y + py + 8],
                    fill=(150, 105, 55))


def illus_syria(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 235, 220))
    d.rectangle([x + 16, y + 8, x + 100, y + 40], fill=(255, 255, 255),
                outline=(150, 150, 150))
    for ly in (16, 23, 30):
        d.line([(x + 24, y + ly), (x + 92, y + ly)], fill=(170, 175, 180),
               width=2)
    circ(d, x + 134, y + 24, 15, outline=GREEN, width=3)
    d.line([(x + 126, y + 24), (x + 132, y + 30), (x + 144, y + 17)],
           fill=GREEN, width=3)
    # small flag: green / white / black
    d.rectangle([x + 154, y + 12, x + 178, y + 19], fill=(0, 122, 61))
    d.rectangle([x + 154, y + 19, x + 178, y + 26], fill=(255, 255, 255))
    d.rectangle([x + 154, y + 26, x + 178, y + 33], fill=(30, 30, 30))


def illus_storms(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(70, 80, 100))
    for ex, ey, er in ((30, 12, 14), (52, 8, 16), (76, 14, 13)):
        circ(d, x + ex, y + ey, er, fill=(120, 128, 140))
    poly(d, [(x + 100, y + 6), (x + 92, y + 24), (x + 100, y + 24),
             (x + 92, y + 42), (x + 110, y + 20), (x + 102, y + 20)],
         fill=(250, 210, 40))
    for rx in (20, 44, 68, 140, 164):
        d.line([(x + rx, y + 34), (x + rx - 3, y + 44)], fill=(150, 190, 230),
               width=2)
    # Australia outline
    poly(d, [(x + 128, y + 34), (x + 172, y + 30), (x + 180, y + 40),
             (x + 160, y + 46), (x + 136, y + 44)], fill=(210, 180, 120))


ILLUS = {
    "nz": illus_nz, "china": illus_china, "zelensky": illus_zelensky,
    "japan": illus_japan, "homeplus": illus_homeplus, "eu": illus_eu,
    "venezuela": illus_venezuela, "bridges": illus_bridges,
    "trump": illus_trump, "ecb": illus_ecb, "malaysia": illus_malaysia,
    "syria": illus_syria, "storms": illus_storms,
}


# ------------------------------------------------------------ layout ---

def draw_masthead(d):
    d.rectangle([0, 0, W, 10], fill=NAVY)
    f = F(SERIF, 40)
    text = "FRIDAY 27 NOVEMBER 2026"
    d.text(((W - f.getlength(text)) / 2, 16), text, font=f, fill=INK)
    d.rectangle([M, 62, W - M, 64], fill=RED)
    draw_tracked(d, W / 2, 70, "ONE DAY OF WORLD NEWS, ONE PICTURE",
                 F(SANS_B, 15), INK, tracking=3)
    f2 = F(SANS_B, 13)
    text2 = "37 STORIES \u00b7 9 REGIONS \u00b7 12 FIELDS \u00b7 EVERY ONE FROM THIS FRIDAY"
    d.text(((W - f2.getlength(text2)) / 2, 90), text2, font=f2, fill=RED)
    d.line([(M, 110), (W - M, 110)], fill=(200, 192, 172), width=1)


def draw_strips(d):
    # --- THE DAY IN UTC (left) ---
    x0, y0, w0, h0 = M, 118, 484, 104
    d.rectangle([x0, y0, x0 + w0, y0 + h0], fill=STRIP)
    d.text((x0 + 10, y0 + 6), "THE DAY IN UTC", font=F(SANS_B, 12),
           fill=INK)
    tf, ef = F(MONO_B, 11), F(SANS, 11)
    for i, (t, ev) in enumerate(UTC_EVENTS):
        ry = y0 + 24 + i * 12
        d.text((x0 + 10, ry), t, font=tf, fill=RED)
        d.text((x0 + 56, ry), trunc(ev, ef, w0 - 66), font=ef, fill=INK)
    # --- THE DAY IN NUMBERS (right) ---
    x1 = 516
    d.rectangle([x1, y0, x1 + 484, y0 + h0], fill=NAVY)
    d.text((x1 + 10, y0 + 6), "THE DAY IN NUMBERS", font=F(SANS_B, 12),
           fill=(248, 244, 236))
    colw = 484 / 3
    for i, (num, lab) in enumerate(NUMBERS):
        cx = x1 + colw * (i % 3) + colw / 2
        ry = y0 + 26 + (i // 3) * 44
        nf = F(SANS_B, 21)
        d.text((cx - nf.getlength(num) / 2, ry), num, font=nf,
               fill=(255, 255, 255))
        lf = F(SANS_B, 9)
        d.text((cx - lf.getlength(lab) / 2, ry + 24), lab, font=lf,
               fill=(200, 210, 225))
    d.line([(M, 226), (W - M, 226)], fill=(200, 192, 172), width=1)


def draw_leads(d):
    lw, gap = 312, 16
    for i, lead in enumerate(LEADS):
        x = M + i * (lw + gap)
        y = 230
        # number banner
        d.rectangle([x, y, x + lw, y + 28], fill=lead["banner_color"])
        bf = F(SANS_B, 20)
        d.text((x + (lw - bf.getlength(lead["banner"])) / 2, y + 4),
               lead["banner"], font=bf, fill=(255, 255, 255))
        pin_num(d, x + 14, y + 14, lead["num"])
        # illustration
        ILLUS[lead["illus"]](d, x, y + 28, lw, 118)
        # headline (max 2 lines)
        hf, hlines = fit_lines(lead["headline"], SANS_B, 15, lw, 2, 12)
        hy = y + 150
        for li, ln in enumerate(hlines):
            d.text((x, hy + li * 17), ln, font=hf, fill=INK)
        # fact (max 2 lines)
        ff, flines = fit_lines(lead["fact"], SANS, 11, lw, 2, 10)
        fy = y + 188
        for li, ln in enumerate(flines):
            d.text((x, fy + li * 13), ln, font=ff, fill=(60, 66, 80))
        # badge + region
        bw = badge(d, x, y + 218, lead["badge"])
        rf = F(SANS_B, 9)
        d.text((x + bw + 8, y + 220), lead["region"].upper(), font=rf,
               fill=REGION_COLORS[lead["region"]])


def draw_tiles(d):
    d.text((M, 474), "MORE FROM FRIDAY", font=F(SANS_B, 11), fill=INK)
    d.line([(M + 128, 480), (W - M, 480)], fill=(200, 192, 172), width=1)
    tw, gap = 187, 10
    for i, tile in enumerate(TILES):
        col, row = i % 5, i // 5
        x = M + col * (tw + gap)
        y = 494 + row * 104
        ILLUS[tile["illus"]](d, x, y, tw, 48)
        chip(d, x + 4, y + 4, tile["chip"])
        pin_num(d, x + tw - 10, y + 12, tile["num"])
        hf, hlines = fit_lines(tile["headline"], SANS_B, 11, tw, 2, 10)
        hy = y + 52
        for li, ln in enumerate(hlines):
            d.text((x, hy + li * 12), ln, font=hf, fill=INK)
        bw = badge(d, x, y + 82, tile["badge"])
        rf = F(SANS_B, 9)
        d.text((x + bw + 8, y + 84), tile["region"].upper(), font=rf,
               fill=REGION_COLORS[tile["region"]])


def draw_map(d, x, y):
    d.text((x, y), "WHERE IT HAPPENED", font=F(SANS_B, 12), fill=INK)
    mx, my = x + 8, y + 18
    d.rectangle([mx - 4, my - 4, mx + 252, my + 108], fill=NAVY)
    for land in MAP_LAND:
        pts = [(mx + px, my + py) for px, py in land]
        poly(d, pts, fill=(150, 170, 195))
    for px, py, num in MAP_PINS:
        circ(d, mx + px, my + py, 6, fill=RED, outline=(255, 255, 255),
             width=1)
        nf = F(SANS_B, 7)
        t = str(num)
        d.text((mx + px - nf.getlength(t) / 2, my + py - 4), t, font=nf,
               fill=(255, 255, 255))
    lf = F(SANS, 8)
    for i, ln in enumerate(MAP_LEGEND):
        d.text((x, y + 130 + i * 11), ln, font=lf, fill=(60, 66, 80))


def draw_index(d):
    x0 = 308
    d.text((x0, 710), "ALSO ON FRIDAY 27 NOVEMBER \u2014 THE REST OF THE DAY",
           font=F(SANS_B, 12), fill=INK)
    cols = [308, 542, 776]
    colw = 224
    for ci in range(3):
        for ri in range(8):
            item = INDEX[ci * 8 + ri]
            region, bdg, head, fact = item
            iy = 726 + ri * 23
            cx = cols[ci]
            circ(d, cx + 3, iy + 4, 3, fill=REGION_COLORS[region])
            hf = F(SANS_B, 10)
            if hf.getlength(head) > colw - 12:
                hf = F(SANS_B, 9)
            d.text((cx + 10, iy), trunc(head, hf, colw - 10), font=hf,
                   fill=INK)
            ff = F(SANS, 9)
            bf = F(SANS_B, 8)
            bw = bf.getlength(bdg) + 8
            d.text((cx + 10, iy + 12),
                   trunc(fact, ff, colw - 10 - bw), font=ff,
                   fill=(60, 66, 80))
            d.text((cx + 10 + ff.getlength(
                trunc(fact, ff, colw - 10 - bw)) + 3, iy + 12),
                bdg, font=bf, fill=BADGE_COLORS[bdg])


def draw_date_check(d):
    y0 = 918
    d.rectangle([M, y0, W - M, y0 + 74], fill=STRIP)
    d.text((M + 10, y0 + 6),
           "DATE CHECK \u2014 WHAT WE LEFT OUT, AND WHAT HAS NOT HAPPENED YET",
           font=F(SANS_B, 11), fill=INK)
    f = F(SANS, 10)
    lines = wrap_text(DATE_CHECK_LEFT, f, CW - 20)
    for i, ln in enumerate(lines):
        d.text((M + 10, y0 + 22 + i * 12), ln, font=f, fill=(60, 66, 80))
    ny = y0 + 22 + len(lines) * 12 + 4
    lines2 = wrap_text(DATE_CHECK_NOTYET, f, CW - 20)
    for i, ln in enumerate(lines2):
        d.text((M + 10, ny + i * 12), ln, font=f, fill=(60, 66, 80))


def draw_footer(d):
    f = F(SANS, 9)
    l1 = ("Sources: Reuters \u00b7 BBC \u00b7 AP \u00b7 NBS China \u00b7 Electoral "
          "Commission NZ \u00b7 European Council \u00b7 AJP \u00b7 NST \u00b7 "
          "Daily Nation \u00b7 Vanguard \u00b7 The Standard \u00b7 Punch \u00b7 The Edge")
    d.text(((W - f.getlength(l1)) / 2, 998), l1, font=f, fill=GREY)
    l2 = ("All 37 stories were first reported on Friday 27 November 2026. "
          "Flat illustration drawn with PIL \u2014 no photographs.")
    d.text(((W - f.getlength(l2)) / 2, 1008), l2, font=f, fill=GREY)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_strips(d)
    draw_leads(d)
    draw_tiles(d)
    draw_map(d, M, 704)
    draw_index(d)
    draw_date_check(d)
    draw_footer(d)
    return img


def main():
    img = render()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, format="PNG", optimize=True)
    print(out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
