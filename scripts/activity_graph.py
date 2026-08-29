"""Render contribution charts (year + month) and the interactive page.

Outputs
  profile/activity.svg        weekly line chart, last 52 full weeks
  profile/activity-month.svg  daily bar chart, last 30 days
  docs/contributions.html     interactive page: month/year toggle, hover tooltips
"""
import json
import os
import re
import urllib.request
from collections import OrderedDict
from datetime import date, timedelta

USER = "Vinay-R-S"
SRC = "https://ghchart.rshah.org/{}".format(USER)

W, H = 940, 230
PAD_L, PAD_R, PAD_T, PAD_B = 44, 22, 54, 34
BG, GRID, LINE, TEXT, MUTED = "#2e3440", "#434c5e", "#88c0d0", "#d8dee9", "#81a1c1"
FONT = "Segoe UI, Ubuntu, Sans-Serif"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fetch_days():
    req = urllib.request.Request(SRC, headers={"User-Agent": "readme-cards"})
    with urllib.request.urlopen(req, timeout=30) as res:
        svg = res.read().decode("utf-8")
    pairs = re.findall(r'data-score="(\d+)"\s+data-date="(\d{4}-\d{2}-\d{2})"', svg)
    if not pairs:
        raise SystemExit("no contribution data in source")
    days = {}
    for score, day in pairs:
        y, m, d = (int(v) for v in day.split("-"))
        days[date(y, m, d)] = int(score)
    return days


def weekly(days):
    weeks = OrderedDict()
    for day in sorted(days):
        start = day - timedelta(days=day.weekday())
        bucket = weeks.setdefault(start, [0, 0])
        bucket[0] += days[day]
        bucket[1] += 1
    items = list(weeks.items())
    if items and items[-1][1][1] < 7:
        items.pop()
    if items and items[0][1][1] < 7:
        items.pop(0)
    return [(start, total) for start, (total, _) in items]


def last_days(days, count=30):
    ordered = sorted(days)
    return [(day, days[day]) for day in ordered[-count:]]


def nice_max(value):
    if value <= 5:
        return 5
    step = 10 ** (len(str(value)) - 1)
    for mult in (1, 1.5, 2, 2.5, 3, 4, 5, 10):
        top = int(step * mult)
        if top >= value:
            return top
    return value


def smooth(points):
    """Catmull-Rom through the points, emitted as cubic beziers."""
    if len(points) < 2:
        return ""
    d = ["M {:.1f} {:.1f}".format(*points[0])]
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i else points[0]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append("C {:.1f} {:.1f}, {:.1f} {:.1f}, {:.1f} {:.1f}".format(
            c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]))
    return " ".join(d)


def chrome(title, note, top):
    """Card background, title and y grid shared by both charts."""
    plot_h = H - PAD_T - PAD_B
    out = ['<svg width="{}" height="{}" viewBox="0 0 {} {}" fill="none" '
           'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{}">'
           .format(W, H, W, H, title),
           '<defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0%" stop-color="{}" stop-opacity="0.38"/>'
           '<stop offset="100%" stop-color="{}" stop-opacity="0"/>'
           '</linearGradient></defs>'.format(LINE, LINE),
           '<rect x="0.5" y="0.5" width="{}" height="{}" rx="8" fill="{}" '
           'stroke="#ffffff" stroke-width="1"/>'.format(W - 1, H - 1, BG),
           '<text x="{}" y="30" fill="{}" font-family="{}" font-size="18" '
           'font-weight="600">{}</text>'.format(PAD_L, LINE, FONT, title),
           '<text x="{}" y="30" text-anchor="end" fill="{}" font-family="{}" '
           'font-size="13">{}</text>'.format(W - PAD_R, MUTED, FONT, note)]
    for frac in (0, 0.5, 1):
        y = PAD_T + plot_h - frac * plot_h
        out.append('<line x1="{}" y1="{:.1f}" x2="{}" y2="{:.1f}" stroke="{}" '
                   'stroke-width="1" stroke-dasharray="3 4"/>'
                   .format(PAD_L, y, W - PAD_R, y, GRID))
        out.append('<text x="{}" y="{:.1f}" text-anchor="end" fill="{}" '
                   'font-family="{}" font-size="11">{}</text>'
                   .format(PAD_L - 8, y + 4, MUTED, FONT, int(round(top * frac))))
    return out


def render_year(series):
    top = nice_max(max(total for _, total in series))
    plot_w, plot_h = W - PAD_L - PAD_R, H - PAD_T - PAD_B
    step = plot_w / float(max(len(series) - 1, 1))
    pts = [(PAD_L + i * step, PAD_T + plot_h - (total / float(top)) * plot_h)
           for i, (_, total) in enumerate(series)]
    peak = max(range(len(series)), key=lambda i: series[i][1])

    out = chrome("Contribution Activity",
                 "{} contributions in the last year".format(
                     sum(t for _, t in series)), top)
    out.append('<path d="{} L {:.1f} {:.1f} L {:.1f} {:.1f} Z" fill="url(#fill)"/>'
               .format(smooth(pts), pts[-1][0], PAD_T + plot_h,
                       pts[0][0], PAD_T + plot_h))
    out.append('<path d="{}" fill="none" stroke="{}" stroke-width="2.2" '
               'stroke-linecap="round" stroke-linejoin="round"/>'
               .format(smooth(pts), LINE))
    out.append('<circle cx="{:.1f}" cy="{:.1f}" r="3.5" fill="{}" stroke="{}" '
               'stroke-width="2"/>'.format(pts[peak][0], pts[peak][1], BG, LINE))
    out.append('<text x="{:.1f}" y="{:.1f}" text-anchor="middle" fill="{}" '
               'font-family="{}" font-size="11" font-weight="600">{}</text>'
               .format(min(max(pts[peak][0], PAD_L + 12), W - PAD_R - 12),
                       pts[peak][1] - 10, TEXT, FONT, series[peak][1]))

    seen, last_x = None, None
    for i, (start, _) in enumerate(series):
        if start.month == seen:
            continue
        seen = start.month
        x = PAD_L + i * step
        if last_x is not None and x - last_x < 34:
            continue
        last_x = x
        out.append('<text x="{:.1f}" y="{}" text-anchor="middle" fill="{}" '
                   'font-family="{}" font-size="11">{}</text>'
                   .format(x, H - 12, MUTED, FONT, MONTHS[start.month - 1]))
    out.append('</svg>')
    return "\n".join(out)


def render_month(series):
    top = nice_max(max(total for _, total in series))
    plot_w, plot_h = W - PAD_L - PAD_R, H - PAD_T - PAD_B
    slot = plot_w / float(len(series))
    bar_w = min(slot - 8, 26)

    first, last = series[0][0], series[-1][0]
    note = "{} {} to {} {}".format(MONTHS[first.month - 1], first.day,
                                   MONTHS[last.month - 1], last.day)
    out = chrome("Contribution Activity", note, top)

    for i, (day, total) in enumerate(series):
        cx = PAD_L + i * slot + slot / 2.0
        if total:
            bh = max((total / float(top)) * plot_h, 3)
            out.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" '
                       'rx="3" fill="{}" fill-opacity="0.85"/>'
                       .format(cx - bar_w / 2.0, PAD_T + plot_h - bh, bar_w, bh, LINE))
            out.append('<text x="{:.1f}" y="{:.1f}" text-anchor="middle" fill="{}" '
                       'font-family="{}" font-size="10" font-weight="600">{}</text>'
                       .format(cx, PAD_T + plot_h - bh - 5, TEXT, FONT, total))
        if i % 3 == 0 or i == len(series) - 1:
            out.append('<text x="{:.1f}" y="{}" text-anchor="middle" fill="{}" '
                       'font-family="{}" font-size="10">{}</text>'
                       .format(cx, H - 12, MUTED, FONT, day.day))
    out.append('</svg>')
    return "\n".join(out)


def render_page(days):
    data = [[day.isoformat(), days[day]] for day in sorted(days)]
    template = open(os.path.join("scripts", "contributions.tpl.html"),
                    encoding="utf-8").read()
    return (template
            .replace("__USER__", USER)
            .replace("__DATA__", json.dumps(data, separators=(",", ":"))))


def write(path, body):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    print("wrote {}".format(path))


def main():
    days = fetch_days()
    year = weekly(days)
    if len(year) < 4:
        raise SystemExit("not enough weeks to plot")
    write("profile/activity.svg", render_year(year))
    write("profile/activity-month.svg", render_month(last_days(days, 30)))
    write("docs/contributions.html", render_page(days))


if __name__ == "__main__":
    main()
