#!/usr/bin/env python3
"""
NHL Aggregator -- portal builder.

Reads  data/archive.json  and writes  index.html  (a self-contained portal page).
Run this after appending a new edition to the archive each morning:

    python3 scripts/build_portal.py

The generated index.html is fully self-contained (inline CSS + JS, all data
embedded, no live network calls) so it works three ways at once:
  * as the Cowork "nhl-aggregator" portal artifact,
  * as a standalone personal website you can open or host anywhere,
  * offline.

Visual design matches the dark "NHL Morning Briefing" broadcast layout.
"""
import json
import os
import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(BASE, "data", "archive.json")
OUT = os.path.join(BASE, "index.html")


def main():
    with open(ARCHIVE, encoding="utf-8") as f:
        archive = json.load(f)

    editions = archive.get("editions", [])
    editions.sort(key=lambda e: e.get("date", ""), reverse=True)
    archive["editions"] = editions

    data_json = json.dumps(archive, ensure_ascii=False)
    data_json = data_json.replace("</", "<\\/")  # safe inside <script>

    built = datetime.datetime.now().strftime("%b %d, %Y at %I:%M %p")

    html = TEMPLATE.replace("/*DATA*/", data_json).replace("{{BUILT}}", built)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("Built %s with %d edition(s)." % (OUT, len(editions)))


TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>NHL Morning Briefing</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  color-scheme: dark;
  --gold: #B4975A;
  --gold-light: #D4B97A;
  --gold-dim: rgba(180,151,90,0.12);
  --gold-dim2: rgba(180,151,90,0.07);
  --purple: #7C6AE8;
  --purple-light: #A89DF0;
  --purple-dim: rgba(124,106,232,0.12);
  --ink: #0D1117;
  --muted: #6B7A99;
  --muted2: #8895B0;
  --border: rgba(255,255,255,0.08);
  --border2: rgba(255,255,255,0.05);
  --green: #3DC97B;
  --surface: rgba(255,255,255,0.04);
  --surface2: rgba(255,255,255,0.02);
  --display: 'Bebas Neue', 'Oswald', 'Arial Narrow', sans-serif;
  --sans: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --mono: 'DM Mono', 'SF Mono', Menlo, Consolas, monospace;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  background: var(--ink);
  color: #D0D8EC;
  font-family: var(--sans);
  font-weight: 300;
  min-height: 100vh;
  background-image:
    radial-gradient(ellipse 80% 40% at 50% -10%, rgba(180,151,90,0.08) 0%, transparent 60%),
    radial-gradient(ellipse 60% 30% at 80% 100%, rgba(124,106,232,0.06) 0%, transparent 50%);
}
body::before {
  content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image: repeating-linear-gradient(0deg, transparent, transparent 40px,
    rgba(255,255,255,0.012) 40px, rgba(255,255,255,0.012) 41px);
}
.container { max-width: 1100px; margin: 0 auto; padding: 0 24px 60px; position: relative; z-index: 1; }

/* HEADER */
header {
  padding: 32px 0 26px; display: flex; align-items: flex-end; justify-content: space-between;
  gap: 18px; border-bottom: 0.5px solid var(--border); margin-bottom: 24px; flex-wrap: wrap;
}
.header-left h1 {
  font-family: var(--display); font-size: 52px; letter-spacing: 0.04em;
  line-height: 1; color: #fff; margin-bottom: 8px; font-weight: 400;
}
.header-left h1 span { color: var(--gold); }
.header-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.header-date {
  font-family: var(--mono); font-size: 12px; color: var(--muted);
  letter-spacing: 0.06em; text-transform: uppercase;
}
.badge {
  display: inline-flex; align-items: center; font-size: 10.5px; font-weight: 500;
  padding: 3px 10px; border-radius: 20px; letter-spacing: 0.05em; text-transform: uppercase;
}
.badge-vgk { background: var(--gold-dim); color: var(--gold-light); border: 0.5px solid rgba(180,151,90,0.3); }
.badge-pod { background: var(--purple-dim); color: var(--purple-light); border: 0.5px solid rgba(124,106,232,0.3); }
.edition-pick { display: flex; flex-direction: column; gap: 5px; align-items: flex-end; }
.edition-label {
  font-family: var(--mono); font-size: 10px; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--muted);
}
#editionSelect {
  font-family: var(--sans); font-size: 13px; color: #D0D8EC; background: var(--surface);
  border: 0.5px solid var(--border); border-radius: 8px; padding: 8px 12px; cursor: pointer;
}

/* LEDE */
.lede { margin-bottom: 26px; }
.lede-tag {
  font-family: var(--mono); font-size: 10px; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--gold); margin-bottom: 10px;
}
.lede h2 { font-size: 27px; line-height: 1.25; color: #fff; font-weight: 500; margin-bottom: 10px; }
.lede p { font-size: 15px; line-height: 1.7; color: #b8c3d8; max-width: 820px; }

/* METRICS */
.metrics-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin-bottom: 26px; }
.metric { background: var(--surface); border: 0.5px solid var(--border); border-radius: 12px; padding: 16px 18px; }
.metric.gold-accent { border-left: 2px solid var(--gold); }
.metric-label {
  font-family: var(--mono); font-size: 10px; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 9px;
}
.metric-value {
  font-family: var(--display); font-size: 34px; letter-spacing: 0.04em;
  color: #fff; line-height: 1; margin-bottom: 5px; font-weight: 400;
}
.metric-value.sm { font-size: 21px; padding-top: 3px; line-height: 1.1; }
.metric-sub { font-size: 12px; color: var(--muted2); }

/* TABS */
.tab-row {
  display: flex; gap: 0; border-bottom: 0.5px solid var(--border);
  margin-bottom: 24px; overflow-x: auto;
}
.tab-row::-webkit-scrollbar { display: none; }
.tab {
  font-family: var(--sans); font-size: 13px; font-weight: 400; color: var(--muted);
  background: none; border: none; border-bottom: 2px solid transparent;
  padding: 10px 18px; cursor: pointer; white-space: nowrap; margin-bottom: -1px;
  transition: color 0.15s;
}
.tab:hover { color: #c0c8dc; }
.tab.active { color: #fff; font-weight: 500; border-bottom-color: var(--gold); }
.tab-panel { display: none; }
.tab-panel.active { display: block; }

/* CARDS */
.card {
  background: var(--surface); border: 0.5px solid var(--border);
  border-radius: 14px; padding: 18px 20px; margin-bottom: 14px;
}
.card-gold { border-left: 2px solid var(--gold); border-radius: 0 14px 14px 0; }
.card-purple { border-left: 2px solid var(--purple); border-radius: 0 14px 14px 0; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.two-col .card { margin-bottom: 0; }

.sec-title {
  font-family: var(--mono); font-size: 10px; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 12px;
}

/* SCOREBOARD */
.scoreboard { display: flex; align-items: center; margin-bottom: 10px; }
.sb-side { display: flex; flex-direction: column; align-items: center; flex: 1; }
.sb-abbr {
  font-family: var(--display); font-size: 36px; letter-spacing: 0.08em;
  line-height: 1; font-weight: 400;
}
.sb-abbr.winner-team { color: #fff; }
.sb-abbr.loser-team  { color: var(--muted); }
.sb-venue-tag {
  font-family: var(--mono); font-size: 9.5px; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--muted); margin-top: 5px;
}
.sb-center { display: flex; align-items: center; gap: 10px; padding: 0 18px; }
.sb-score {
  font-family: var(--display); font-size: 54px; letter-spacing: 0.02em;
  line-height: 1; color: #fff; font-weight: 400;
}
.sb-score.dim { color: var(--muted2); }
.sb-sep { color: var(--muted); font-size: 22px; padding-bottom: 4px; }

/* GAME / SERIES */
.game-score {
  font-family: var(--display); font-size: 25px; letter-spacing: 0.03em;
  color: #fff; line-height: 1.15; margin-bottom: 8px; font-weight: 400;
}
.series-teams {
  font-family: var(--display); font-size: 23px; letter-spacing: 0.03em;
  color: #fff; line-height: 1.15; margin-bottom: 9px; font-weight: 400;
}
.snote, .badge-status {
  display: inline-block; font-size: 11px; font-weight: 500; padding: 3px 11px;
  border-radius: 20px; margin-bottom: 11px; letter-spacing: 0.02em;
}
.snote, .badge-status.lead { background: rgba(61,201,123,0.13); color: var(--green);
  border: 0.5px solid rgba(61,201,123,0.3); }
.badge-status.tied { background: var(--surface); color: var(--muted2); border: 0.5px solid var(--border); }
.next-line { font-size: 12.5px; color: var(--muted2); margin-top: 4px; }
.next-line strong { color: #fff; font-weight: 500; }

/* AI / PROSE BLOCKS */
.ai-block { font-size: 14px; line-height: 1.75; color: #b8c3d8; font-weight: 300; }
.ai-block p { margin-bottom: 12px; }
.ai-block p:last-child { margin-bottom: 0; }

/* FACT LIST */
.fact-list { list-style: none; margin: 14px 0 4px; }
.fact-list li {
  font-size: 13px; line-height: 1.55; color: #c0c8dc; padding: 9px 0 9px 18px;
  position: relative; border-top: 0.5px solid var(--border2);
}
.fact-list li::before {
  content: ''; position: absolute; left: 0; top: 15px; width: 6px; height: 6px;
  background: var(--gold); border-radius: 50%;
}

/* SCORING LEADERS */
.scoring-row {
  display: flex; align-items: center; padding: 9px 0; gap: 11px; font-size: 13px;
  border-bottom: 0.5px solid var(--border2);
}
.scoring-row:last-child { border-bottom: none; padding-bottom: 0; }
.scoring-row:first-of-type { padding-top: 2px; }
.scoring-rank {
  color: var(--muted); width: 16px; font-size: 11px; font-family: var(--mono); flex-shrink: 0;
}
.scoring-name { flex: 1; color: #c0c8dc; }
.scoring-name strong { color: #fff; font-weight: 500; display: block; }
.scoring-team-label { color: var(--muted2); font-size: 11px; font-family: var(--mono); }
.scoring-note { color: var(--muted2); font-size: 11.5px; flex: 1.6; line-height: 1.4; }
.scoring-pts {
  font-family: var(--display); font-size: 22px; color: #fff; min-width: 56px;
  text-align: right; letter-spacing: 0.03em;
}

/* ANGLES */
.angle-list { list-style: none; counter-reset: a; margin-top: 4px; }
.angle-list li {
  counter-increment: a; position: relative; padding: 13px 0 13px 38px;
  font-size: 14px; line-height: 1.65; color: #c0c8dc; border-top: 0.5px solid var(--border2);
}
.angle-list li:first-child { border-top: none; }
.angle-list li::before {
  content: counter(a,decimal-leading-zero); position: absolute; left: 0; top: 13px;
  font-family: var(--mono); font-size: 12px; color: var(--purple-light);
  border: 0.5px solid rgba(124,106,232,0.35); border-radius: 6px; padding: 2px 6px;
}

/* NEWS */
.news-item { padding: 14px 0; border-top: 0.5px solid var(--border2); }
.news-item:first-child { border-top: none; padding-top: 2px; }
.news-item h4 { font-size: 15px; line-height: 1.35; color: #fff; font-weight: 500; }
.news-item h4 a { color: inherit; text-decoration: none; }
.news-item h4 a:hover { color: var(--gold-light); }
.news-item p { font-size: 13px; line-height: 1.6; color: var(--muted2); margin-top: 5px; }
.news-item .news-src {
  font-family: var(--mono); font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--gold); margin-top: 6px;
}
.empty { font-size: 13px; color: var(--muted); line-height: 1.6; }

/* INJURIES */
.injury-row {
  display: flex; align-items: flex-start; gap: 14px; padding: 13px 0;
  border-top: 0.5px solid var(--border2);
}
.injury-row:first-child { border-top: none; padding-top: 2px; }
.injury-status {
  font-family: var(--mono); font-size: 10px; font-weight: 500; letter-spacing: 0.06em;
  padding: 3px 10px; border-radius: 20px; white-space: nowrap; flex-shrink: 0; margin-top: 2px;
}
.injury-status.out { background: rgba(220,60,60,0.14); color: #E87070; border: 0.5px solid rgba(220,60,60,0.3); }
.injury-status.dtd { background: rgba(230,160,30,0.14); color: #E8C060; border: 0.5px solid rgba(230,160,30,0.3); }
.injury-status.ir  { background: rgba(220,60,60,0.10); color: #C06060; border: 0.5px solid rgba(220,60,60,0.2); }
.injury-name { flex: 1; }
.injury-name strong { font-size: 14px; color: #fff; font-weight: 500; display: block; margin-bottom: 2px; }
.injury-meta { font-family: var(--mono); font-size: 10.5px; color: var(--muted2); margin-bottom: 4px; letter-spacing: 0.03em; }
.injury-detail { font-size: 12.5px; color: var(--muted2); line-height: 1.55; }

/* TRANSACTIONS */
.txn-item { padding: 13px 0; border-top: 0.5px solid var(--border2); }
.txn-item:first-child { border-top: none; padding-top: 2px; }
.txn-header { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; flex-wrap: wrap; }
.txn-type {
  font-family: var(--mono); font-size: 10px; font-weight: 500; letter-spacing: 0.06em;
  text-transform: uppercase; padding: 2px 9px; border-radius: 20px;
  background: var(--surface); color: var(--muted2); border: 0.5px solid var(--border);
}
.txn-date { font-family: var(--mono); font-size: 10px; color: var(--muted); letter-spacing: 0.04em; }
.txn-headline { font-size: 14px; color: #fff; font-weight: 500; line-height: 1.35; }
.txn-headline a { color: inherit; text-decoration: none; }
.txn-headline a:hover { color: var(--gold-light); }
.txn-detail { font-size: 12.5px; color: var(--muted2); line-height: 1.55; margin-top: 4px; }
.txn-src { font-family: var(--mono); font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--gold); margin-top: 5px; }

/* AM REWIND */
.amr-channel { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; padding-bottom: 14px; border-bottom: 0.5px solid var(--border2); }
.amr-channel-icon {
  width: 42px; height: 42px; border-radius: 50%; background: var(--gold-dim);
  border: 1px solid rgba(180,151,90,0.35); display: flex; align-items: center; justify-content: center;
  font-family: var(--display); font-size: 18px; color: var(--gold-light); flex-shrink: 0; letter-spacing: 0.05em;
}
.amr-channel-info { flex: 1; }
.amr-channel-info strong { font-size: 14px; color: #fff; font-weight: 500; display: block; }
.amr-channel-info span { font-size: 12px; color: var(--muted2); }
.amr-channel-link { font-family: var(--mono); font-size: 11px; color: var(--gold); text-decoration: none; letter-spacing: 0.04em; }
.amr-channel-link:hover { color: var(--gold-light); }
.amr-video { padding: 12px 0; border-top: 0.5px solid var(--border2); }
.amr-video:first-child { border-top: none; }
.amr-video-header { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; flex-wrap: wrap; }
.amr-video-type {
  font-family: var(--mono); font-size: 10px; font-weight: 500; letter-spacing: 0.06em;
  text-transform: uppercase; padding: 2px 9px; border-radius: 20px;
  background: var(--purple-dim); color: var(--purple-light); border: 0.5px solid rgba(124,106,232,0.3);
}
.amr-video-date { font-family: var(--mono); font-size: 10px; color: var(--muted); letter-spacing: 0.04em; }
.amr-video-title { font-size: 14px; color: #fff; font-weight: 500; line-height: 1.35; }
.amr-video-title a { color: inherit; text-decoration: none; }
.amr-video-title a:hover { color: var(--gold-light); }
.amr-video-desc { font-size: 12.5px; color: var(--muted2); line-height: 1.55; margin-top: 4px; }
.amr-comment { padding: 10px 0; border-top: 0.5px solid var(--border2); font-size: 12.5px; }
.amr-comment-author { color: var(--gold-light); font-weight: 500; margin-bottom: 3px; }
.amr-comment-text { color: var(--muted2); line-height: 1.5; }

/* TWEETS */
.tweet-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 0.5px solid var(--border2); }
.tweet-header-icon { width: 38px; height: 38px; border-radius: 50%; background: #1DA1F2; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.tweet-header-info strong { font-size: 14px; color: #fff; font-weight: 500; display: block; }
.tweet-header-info span { font-size: 12px; color: var(--muted2); }
.tweet-no-recent { font-family: var(--mono); font-size: 11px; color: var(--gold); letter-spacing: 0.04em; margin-bottom: 14px; display: block; }
.tweet-item { padding: 12px 0; border-top: 0.5px solid var(--border2); }
.tweet-item:first-of-type { border-top: none; }
.tweet-text { font-size: 14px; color: #e8e8e8; line-height: 1.55; white-space: pre-line; }
.tweet-text a { color: inherit; text-decoration: none; }
.tweet-text a:hover { color: var(--gold-light); }
.tweet-meta { display: flex; align-items: center; gap: 14px; margin-top: 7px; flex-wrap: wrap; }
.tweet-date { font-family: var(--mono); font-size: 10.5px; color: var(--muted); letter-spacing: 0.04em; }
.tweet-stat { font-family: var(--mono); font-size: 10.5px; color: var(--muted2); letter-spacing: 0.03em; }
.tweet-link { font-family: var(--mono); font-size: 10.5px; color: var(--gold); text-decoration: none; letter-spacing: 0.04em; margin-left: auto; }
.tweet-link:hover { color: var(--gold-light); }

/* ROSTER TABLE */
.roster-section-label {
  font-family: var(--mono); font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--muted); margin: 18px 0 8px; padding-bottom: 6px; border-bottom: 0.5px solid var(--border2);
}
.roster-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.roster-table { width: 100%; border-collapse: collapse; font-size: 12px; white-space: nowrap; }
.roster-table thead th {
  font-family: var(--mono); font-size: 9.5px; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--muted); padding: 4px 10px 6px; text-align: right;
  border-bottom: 0.5px solid var(--border);
}
.roster-table thead th:first-child,
.roster-table thead th:nth-child(2),
.roster-table thead th:nth-child(3) { text-align: left; }
.roster-table tbody td {
  padding: 7px 10px; text-align: right; color: #c0c8dc;
  border-bottom: 0.5px solid var(--border2);
  font-family: var(--mono); font-size: 12px;
}
.roster-table tbody td:first-child { color: var(--muted); font-size: 11px; }
.roster-table tbody td:nth-child(2) { text-align: left; color: #fff; font-weight: 500; font-family: var(--sans); }
.roster-table tbody td:nth-child(3) { text-align: left; color: var(--muted2); }
.roster-table tbody tr:last-child td { border-bottom: none; }
.roster-table tbody tr.inj td { opacity: 0.5; }
.roster-table .pts-col { color: var(--gold-light); font-weight: 500; }

/* FOOTER */
footer {
  margin-top: 38px; padding-top: 20px; border-top: 0.5px solid var(--border);
  font-family: var(--mono); font-size: 11px; color: var(--muted);
  letter-spacing: 0.04em; display: flex; justify-content: space-between;
  align-items: center; gap: 14px; flex-wrap: wrap;
}
.sources-row { display: flex; gap: 16px; flex-wrap: wrap; }
.sources-row a { color: var(--muted2); text-decoration: none; transition: color 0.15s; }
.sources-row a:hover { color: var(--gold-light); }

@media (max-width: 700px) {
  .metrics-grid { grid-template-columns: 1fr; }
  .two-col { grid-template-columns: 1fr; }
  .header-left h1 { font-size: 38px; }
  header { align-items: flex-start; }
  .edition-pick { align-items: flex-start; }
  footer { flex-direction: column; align-items: flex-start; }
}
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="header-left">
      <h1>NHL <span>Morning</span> Briefing</h1>
      <div class="header-meta">
        <span class="header-date" id="dateline">&mdash;</span>
        <span class="badge badge-vgk">VGK Broadcast</span>
        <span class="badge badge-pod">Empty Netters</span>
      </div>
    </div>
    <div class="edition-pick">
      <span class="edition-label">Edition</span>
      <select id="editionSelect"></select>
    </div>
  </header>

  <div class="lede" id="lede"></div>
  <div class="metrics-grid" id="metrics"></div>
  <div class="tab-row" id="tabRow"></div>
  <div id="panels"></div>

  <footer>
    <span id="footNote">NHL Morning Briefing &middot; refreshed every morning by 5:00 a.m. PT</span>
    <div class="sources-row">
      <a href="https://www.nhl.com" target="_blank" rel="noopener">NHL.com</a>
      <a href="https://www.espn.com/nhl" target="_blank" rel="noopener">ESPN</a>
      <a href="https://www.dailyfaceoff.com" target="_blank" rel="noopener">Daily Faceoff</a>
      <a href="https://puckpedia.com" target="_blank" rel="noopener">PuckPedia</a>
    </div>
  </footer>
</div>

<script>
const ARCHIVE = /*DATA*/;
const EDITIONS = ARCHIVE.editions || [];
const TABS = [
  ['vgk','Golden Knights'], ['scores','Scores'], ['standings','Standings'],
  ['leaders','Stat Leaders'], ['podcast','Empty Netters'], ['news','News'],
  ['injuries','Injuries'], ['transactions','Transactions'], ['amrewind','The AM Rewind']
];
let activeTab = 'vgk';

function el(id){ return document.getElementById(id); }
function esc(s){ return String(s==null?'':s)
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function vgkIn(s){ return /vegas|golden knights|\bVGK\b/i.test(s||''); }
function fmtLong(d){ return new Date(d+'T12:00:00')
  .toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric',year:'numeric'}); }
function fmtShort(d){ return new Date(d+'T12:00:00')
  .toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'}); }

function metricCard(label,value,sub,small){
  return '<div class="metric gold-accent">'
    + '<div class="metric-label">'+esc(label)+'</div>'
    + '<div class="metric-value'+(small?' sm':'')+'">'+esc(value||'—')+'</div>'
    + (sub?'<div class="metric-sub">'+esc(sub)+'</div>':'')
    + '</div>';
}

function panelVGK(ed){
  const v = ed.vgk || {};
  const notes = (v.notes||[]).map(n=>'<li>'+esc(n)+'</li>').join('');
  let html = '<div class="card card-gold">'
    + '<p class="sec-title">VGK broadcast briefing</p>'
    + (v.series?'<div class="series-teams" style="font-size:18px">'+esc(v.series)+'</div>':'')
    + '<div class="ai-block"><p>'+esc(v.spotlight||'')+'</p></div>'
    + (notes?'<ul class="fact-list">'+notes+'</ul>':'')
    + (v.next?'<div class="next-line">Next up &mdash; <strong>'+esc(v.next)+'</strong>'
        + (v.next_detail?' &middot; '+esc(v.next_detail):'')+'</div>':'')
    + '</div>';

  const r = v.roster || {};
  const fwds = r.forwards || [];
  const defs = r.defense || [];
  const gols = r.goalies || [];

  if(fwds.length || defs.length || gols.length){
    html += '<div class="card" style="margin-top:14px"><p class="sec-title">Roster Stats</p>';

    if(fwds.length){
      html += '<div class="roster-section-label">Forwards</div>'
        + '<div class="roster-wrap"><table class="roster-table"><thead><tr>'
        + '<th>#</th><th>Name</th><th>Pos</th><th>GP</th><th>G</th><th>A</th>'
        + '<th class="pts-col">PTS</th><th>+/-</th><th>PIM</th><th>SOG</th>'
        + '<th>S%</th><th>TOI</th><th>FO%</th><th>HIT</th><th>BLK</th>'
        + '</tr></thead><tbody>';
      fwds.forEach(p => {
        const pm = p.pm != null ? (p.pm >= 0 ? '+' : '') + p.pm : '—';
        html += '<tr'+(p.inj?' class="inj"':'')+'>'
          + '<td>'+esc(p.num)+'</td>'
          + '<td>'+esc(p.name)+(p.inj?' <span style="color:#E87070;font-size:9px;margin-left:4px">INJ</span>':'')+'</td>'
          + '<td>'+esc(p.pos)+'</td>'
          + '<td>'+esc(p.gp)+'</td>'
          + '<td>'+esc(p.g)+'</td>'
          + '<td>'+esc(p.a)+'</td>'
          + '<td class="pts-col">'+esc(p.pts)+'</td>'
          + '<td>'+pm+'</td>'
          + '<td>'+esc(p.pim)+'</td>'
          + '<td>'+esc(p.sog)+'</td>'
          + '<td>'+esc(p.spct)+'</td>'
          + '<td>'+esc(p.toi)+'</td>'
          + '<td>'+(p.fow!=null?esc(p.fow):'—')+'</td>'
          + '<td>'+esc(p.hits)+'</td>'
          + '<td>'+esc(p.blk)+'</td>'
          + '</tr>';
      });
      html += '</tbody></table></div>';
    }

    if(defs.length){
      html += '<div class="roster-section-label">Defense</div>'
        + '<div class="roster-wrap"><table class="roster-table"><thead><tr>'
        + '<th>#</th><th>Name</th><th>Pos</th><th>GP</th><th>G</th><th>A</th>'
        + '<th class="pts-col">PTS</th><th>+/-</th><th>PIM</th><th>SOG</th>'
        + '<th>S%</th><th>TOI</th><th>HIT</th><th>BLK</th>'
        + '</tr></thead><tbody>';
      defs.forEach(p => {
        const pm = p.pm != null ? (p.pm >= 0 ? '+' : '') + p.pm : '—';
        html += '<tr'+(p.inj?' class="inj"':'')+'>'
          + '<td>'+esc(p.num)+'</td>'
          + '<td>'+esc(p.name)+(p.inj?' <span style="color:#E87070;font-size:9px;margin-left:4px">INJ</span>':'')+'</td>'
          + '<td>'+esc(p.pos)+'</td>'
          + '<td>'+esc(p.gp)+'</td>'
          + '<td>'+esc(p.g)+'</td>'
          + '<td>'+esc(p.a)+'</td>'
          + '<td class="pts-col">'+esc(p.pts)+'</td>'
          + '<td>'+pm+'</td>'
          + '<td>'+esc(p.pim)+'</td>'
          + '<td>'+esc(p.sog)+'</td>'
          + '<td>'+esc(p.spct)+'</td>'
          + '<td>'+esc(p.toi)+'</td>'
          + '<td>'+esc(p.hits)+'</td>'
          + '<td>'+esc(p.blk)+'</td>'
          + '</tr>';
      });
      html += '</tbody></table></div>';
    }

    if(gols.length){
      html += '<div class="roster-section-label">Goalies</div>'
        + '<div class="roster-wrap"><table class="roster-table"><thead><tr>'
        + '<th>#</th><th>Name</th><th>GP</th><th class="pts-col">W</th><th>L</th>'
        + '<th>GAA</th><th>SV%</th><th>SO</th><th>TOI</th>'
        + '</tr></thead><tbody>';
      gols.forEach(p => {
        html += '<tr'+(p.inj?' class="inj"':'')+'>'
          + '<td>'+esc(p.num)+'</td>'
          + '<td>'+esc(p.name)+(p.inj?' <span style="color:#E87070;font-size:9px;margin-left:4px">INJ</span>':'')+'</td>'
          + '<td>'+esc(p.gp)+'</td>'
          + '<td class="pts-col">'+esc(p.w)+'</td>'
          + '<td>'+esc(p.l)+'</td>'
          + '<td>'+esc(p.gaa)+'</td>'
          + '<td>'+esc(p.svpct)+'</td>'
          + '<td>'+esc(p.so)+'</td>'
          + '<td>'+esc(p.toi)+'</td>'
          + '</tr>';
      });
      html += '</tbody></table></div>';
    }

    html += '</div>';
  }

  return html;
}

function renderScoreboard(g){
  const hasStructured = g.away_abbr && g.home_abbr && g.away_score != null && g.home_score != null;
  if(!hasStructured) return '<div class="game-score">'+esc(g.matchup)+'</div>';
  const awayWin = g.winner_abbr === g.away_abbr;
  const homeWin = g.winner_abbr === g.home_abbr;
  return '<div class="scoreboard">'
    + '<div class="sb-side">'
      + '<div class="sb-abbr '+(awayWin?'winner-team':'loser-team')+'">'+esc(g.away_abbr)+'</div>'
      + '<div class="sb-venue-tag">Away</div>'
    + '</div>'
    + '<div class="sb-center">'
      + '<div class="sb-score'+(awayWin?'':' dim')+'">'+esc(g.away_score)+'</div>'
      + '<div class="sb-sep">&mdash;</div>'
      + '<div class="sb-score'+(homeWin?'':' dim')+'">'+esc(g.home_score)+'</div>'
    + '</div>'
    + '<div class="sb-side">'
      + '<div class="sb-abbr '+(homeWin?'winner-team':'loser-team')+'">'+esc(g.home_abbr)+'</div>'
      + '<div class="sb-venue-tag">Home</div>'
    + '</div>'
    + '</div>';
}

function panelScores(ed){
  const games = ed.games || [];
  if(!games.length) return '<div class="card"><p class="empty">No games on this slate. '
    + 'Check the Standings tab for the next puck drop.</p></div>';
  return games.map(g => {
    const isVGK = vgkIn(g.matchup) || g.away_abbr==='VGK' || g.home_abbr==='VGK';
    return '<div class="card'+(isVGK?' card-gold':'')+'">'
      + '<p class="sec-title">'+esc(g.context)+'</p>'
      + renderScoreboard(g)
      + (g.series_note?'<span class="snote">'+esc(g.series_note)+'</span>':'')
      + '<div class="ai-block"><p>'+esc(g.detail)+'</p></div>'
      + '</div>';
  }).join('');
}

function panelStandings(ed){
  const series = ed.series || [];
  if(!series.length) return '<div class="card"><p class="empty">No active series or '
    + 'standings groups for this edition.</p></div>';
  return series.map(s => {
    const tied = !s.leader_abbr;
    return '<div class="card'+(vgkIn(s.teams)?' card-gold':'')+'">'
      + '<p class="sec-title">'+esc(s.name)+'</p>'
      + '<div class="series-teams">'+esc(s.teams)+'</div>'
      + '<span class="badge-status'+(tied?' tied':' lead')+'">'+esc(s.status)+'</span>'
      + (s.next?'<div class="next-line">Next &mdash; <strong>'+esc(s.next)+'</strong></div>':'')
      + '</div>';
  }).join('');
}

function panelLeaders(ed){
  const L = ed.leaders || {};
  const cats = Object.keys(L);
  if(!cats.length) return '<div class="card"><p class="empty">No stat leaders for this edition.</p></div>';
  const cards = cats.map(cat => {
    const rows = (L[cat]||[]).map((p,i) =>
      '<div class="scoring-row">'
        + '<span class="scoring-rank">'+(i+1)+'</span>'
        + '<span class="scoring-name"><strong>'+esc(p.name)+'</strong>'
          + '<span class="scoring-team-label">'+esc(p.team||'')
          + (p.team==='VGK'?' &middot; VGK':'')+'</span></span>'
        + '<span class="scoring-note">'+esc(p.note||'')+'</span>'
        + '<span class="scoring-pts">'+esc(p.value)+'</span>'
      + '</div>').join('');
    return '<div class="card"><p class="sec-title">'+esc(cat)+'</p>'+rows+'</div>';
  }).join('');
  return '<div class="two-col">'+cards+'</div>';
}

function panelPodcast(ed){
  const angles = ed.podcast_angles || [];
  let inner = '<p class="sec-title">Empty Netters &mdash; segment intel</p>';
  if(angles.length){
    inner += '<ol class="angle-list">'+angles.map(a=>'<li>'+esc(a)+'</li>').join('')+'</ol>';
  } else {
    inner += '<p class="empty">No segment ideas generated for this edition.</p>';
  }
  let out = '<div class="card card-purple">'+inner+'</div>';

  // Tweets card
  const tweets = ed.tweets || [];
  const now = new Date();
  const cutoff = new Date(now.getTime() - 24*60*60*1000);
  const recent = tweets.filter(t => new Date(t.time) >= cutoff);
  let tw = '<div class="tweet-header">'
    + '<div class="tweet-header-icon">𝕏</div>'
    + '<div class="tweet-header-info"><strong>@EmptyNettersPod</strong><span>Empty Netters Podcast</span></div>'
    + '</div>';
  if(!tweets.length){
    tw += '<p class="empty">No tweets available.</p>';
  } else {
    if(!recent.length){
      tw += '<span class="tweet-no-recent">No posts in the last 24 hrs &mdash; showing most recent</span>';
    }
    tw += tweets.slice(0,5).map(t => {
      const tweetText = t.url
        ? '<a href="'+esc(t.url)+'" target="_blank" rel="noopener">'+esc(t.text)+'</a>'
        : esc(t.text);
      return '<div class="tweet-item">'
        + '<div class="tweet-text">'+tweetText+'</div>'
        + '<div class="tweet-meta">'
        + '<span class="tweet-date">'+esc(t.displayTime)+'</span>'
        + (t.likes ? '<span class="tweet-stat">♥ '+esc(t.likes)+'</span>' : '')
        + (t.retweets ? '<span class="tweet-stat">↺ '+esc(t.retweets)+'</span>' : '')
        + (t.url ? '<a class="tweet-link" href="'+esc(t.url)+'" target="_blank" rel="noopener">View →</a>' : '')
        + '</div>'
        + '</div>';
    }).join('');
  }
  out += '<div class="card" style="margin-top:14px">'+tw+'</div>';
  return out;
}

function panelNews(ed){
  const news = ed.news || [];
  if(!news.length) return '<div class="card"><p class="empty">No league news for this edition.</p></div>';
  const items = news.map(n => {
    const head = n.url
      ? '<a href="'+esc(n.url)+'" target="_blank" rel="noopener">'+esc(n.headline)+'</a>'
      : esc(n.headline);
    return '<div class="news-item"><h4>'+head+'</h4>'
      + '<p>'+esc(n.detail)+'</p>'
      + (n.source?'<div class="news-src">'+esc(n.source)+'</div>':'')
      + '</div>';
  }).join('');
  return '<div class="card">'+items+'</div>';
}

function panelInjuries(ed){
  const injuries = ed.injuries || [];
  if(!injuries.length) return '<div class="card"><p class="empty">No injury reports for this edition.</p></div>';
  const vgkInj = injuries.filter(i=>i.vgk);
  const otherInj = injuries.filter(i=>!i.vgk);
  function renderInj(arr){
    return arr.map(i => {
      const st = (i.status||'').toUpperCase();
      const cls = st==='OUT'?'out':st==='DTD'?'dtd':'ir';
      return '<div class="injury-row">'
        + '<span class="injury-status '+cls+'">'+esc(i.status||'?')+'</span>'
        + '<div class="injury-name">'
          + '<strong>'+esc(i.name)+'</strong>'
          + '<div class="injury-meta">'+esc(i.team)+' &middot; '+esc(i.position)+' &middot; '+esc(i.injury)+'</div>'
          + '<div class="injury-detail">'+esc(i.detail)+'</div>'
        + '</div>'
        + '</div>';
    }).join('');
  }
  let html = '';
  if(vgkInj.length){
    html += '<div class="card card-gold"><p class="sec-title">Golden Knights</p>'+renderInj(vgkInj)+'</div>';
  }
  if(otherInj.length){
    html += '<div class="card"><p class="sec-title">Around the League</p>'+renderInj(otherInj)+'</div>';
  }
  return html;
}

function panelTransactions(ed){
  const txns = ed.transactions || [];
  if(!txns.length) return '<div class="card"><p class="empty">No transactions logged for this edition.</p></div>';
  const vgkTxns = txns.filter(t=>t.vgk);
  const otherTxns = txns.filter(t=>!t.vgk);
  function renderTxn(arr){
    return arr.map(t => {
      const head = t.url
        ? '<a href="'+esc(t.url)+'" target="_blank" rel="noopener">'+esc(t.headline)+'</a>'
        : esc(t.headline);
      return '<div class="txn-item">'
        + '<div class="txn-header">'
          + '<span class="txn-type">'+esc(t.type||'move')+'</span>'
          + '<span class="txn-date">'+esc(t.date)+'</span>'
        + '</div>'
        + '<div class="txn-headline">'+head+'</div>'
        + '<div class="txn-detail">'+esc(t.detail)+'</div>'
        + (t.source?'<div class="txn-src">'+esc(t.source)+'</div>':'')
        + '</div>';
    }).join('');
  }
  let html = '';
  if(vgkTxns.length){
    html += '<div class="card card-gold"><p class="sec-title">Golden Knights</p>'+renderTxn(vgkTxns)+'</div>';
  }
  if(otherTxns.length){
    html += '<div class="card"><p class="sec-title">Around the League</p>'+renderTxn(otherTxns)+'</div>';
  }
  return html;
}

function panelAMRewind(ed){
  const amr = ed.amrewind || {};
  const videos = amr.latest_videos || [];
  const comments = amr.comments || [];
  if(!videos.length && !comments.length){
    return '<div class="card"><p class="empty">No AM Rewind content for this edition.</p></div>';
  }
  const channelHtml = '<div class="amr-channel">'
    + '<div class="amr-channel-icon">AMR</div>'
    + '<div class="amr-channel-info">'
      + '<strong>The AM Rewind</strong>'
      + '<span>'+esc(amr.description||'')+'</span>'
    + '</div>'
    + (amr.channel_url?'<a class="amr-channel-link" href="'+esc(amr.channel_url)+'" target="_blank" rel="noopener">'+esc(amr.channel_handle||'Visit Channel')+'</a>':'')
    + '</div>';
  const videoHtml = videos.map(v => {
    const title = v.url
      ? '<a href="'+esc(v.url)+'" target="_blank" rel="noopener">'+esc(v.title)+'</a>'
      : esc(v.title);
    const typeLabel = (v.type||'').replace(/_/g,' ');
    return '<div class="amr-video">'
      + '<div class="amr-video-header">'
        + '<span class="amr-video-type">'+esc(typeLabel)+'</span>'
        + '<span class="amr-video-date">'+esc(v.published)+'</span>'
      + '</div>'
      + '<div class="amr-video-title">'+title+'</div>'
      + '<div class="amr-video-desc">'+esc(v.description)+'</div>'
      + '</div>';
  }).join('');
  const commentHtml = comments.length
    ? '<div class="card" style="margin-top:14px"><p class="sec-title">Recent Comments</p>'
      + comments.map(c =>
          '<div class="amr-comment">'
          + '<div class="amr-comment-author">'+esc(c.author)+'</div>'
          + '<div class="amr-comment-text">'+esc(c.text)+'</div>'
          + '</div>'
        ).join('')
      + '</div>'
    : '';
  return '<div class="card card-purple">'+channelHtml+videoHtml+'</div>'+commentHtml;
}

const PANELS = { vgk:panelVGK, scores:panelScores, standings:panelStandings,
  leaders:panelLeaders, podcast:panelPodcast, news:panelNews,
  injuries:panelInjuries, transactions:panelTransactions, amrewind:panelAMRewind };

function syncTabs(){
  document.querySelectorAll('.tab').forEach(b =>
    b.classList.toggle('active', b.dataset.tab===activeTab));
  document.querySelectorAll('.tab-panel').forEach(p =>
    p.classList.toggle('active', p.id==='panel-'+activeTab));
}

function renderEdition(ed){
  el('dateline').textContent = fmtLong(ed.date);
  el('lede').innerHTML =
    '<div class="lede-tag">Morning Briefing &nbsp;&mdash;&nbsp; covers '+esc(ed.covers)+'</div>'
    + '<h2>'+esc(ed.headline)+'</h2>'
    + '<p>'+esc(ed.summary)+'</p>';
  const v = ed.vgk || {};
  el('metrics').innerHTML =
    metricCard('VGK · Postseason', v.record, v.record_detail||'Vegas Golden Knights', false)
    + metricCard('VGK · Series', v.series_short, 'Stanley Cup Playoffs', false)
    + metricCard('Next VGK Game', v.next, v.next_detail||'', true);
  el('panels').innerHTML = TABS.map(([id]) =>
    '<div class="tab-panel'+(id===activeTab?' active':'')+'" id="panel-'+id+'">'
    + PANELS[id](ed) + '</div>').join('');
}

(function init(){
  if(!EDITIONS.length){
    el('lede').innerHTML = '<div class="lede-tag">No data yet</div>'
      + '<h2>The aggregator has not run.</h2>'
      + '<p>This portal will fill in on the next scheduled run.</p>';
    el('editionSelect').style.display = 'none';
    return;
  }
  const sel = el('editionSelect');
  EDITIONS.forEach((ed,i) => {
    const o = document.createElement('option');
    o.value = i;
    o.textContent = fmtShort(ed.date) + (i===0?'  ·  latest':'');
    sel.appendChild(o);
  });
  sel.addEventListener('change', () => renderEdition(EDITIONS[+sel.value]));

  el('tabRow').innerHTML = TABS.map(([id,label]) =>
    '<button class="tab'+(id===activeTab?' active':'')+'" data-tab="'+id+'">'
    + label + '</button>').join('');
  el('tabRow').querySelectorAll('.tab').forEach(b =>
    b.addEventListener('click', () => { activeTab = b.dataset.tab; syncTabs(); }));

  el('footNote').textContent =
    'NHL Morning Briefing · ' + EDITIONS.length + ' edition'
    + (EDITIONS.length>1?'s':'') + ' · refreshed every morning by 5:00 a.m. PT · built {{BUILT}}';

  renderEdition(EDITIONS[0]);
})();
</script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
