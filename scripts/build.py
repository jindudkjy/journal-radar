#!/usr/bin/env python3
"""Crossref에서 최근 3개월 논문을 모아 주제를 분류하고 site/index.html을 생성합니다.

사용법:  python scripts/build.py            # 실제 수집
         python scripts/build.py --demo     # 네트워크 없이 샘플 데이터로 페이지만 확인
환경변수: CROSSREF_MAILTO   (권장) Crossref에 알릴 연락 이메일
          ANTHROPIC_API_KEY (선택) 있으면 Claude가 한국어 트렌드 해설을 작성
          ANTHROPIC_MODEL   (선택) 기본 claude-sonnet-5
"""
import html, json, os, re, sys, time
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from config import JOURNALS, TOPICS, WINDOW_DAYS, RECENT_DAYS, MAX_PER_JOURNAL

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "index.html"
OUT = ROOT / "site" / "index.html"
MAILTO = os.environ.get("CROSSREF_MAILTO", "")
UA = f"journal-trend-radar/1.0 (mailto:{MAILTO})" if MAILTO else "journal-trend-radar/1.0"
TAG = re.compile(r"<[^>]+>")
# 연구 논문이 아닌 항목(정정, 표지, 목차 등) 제외
SKIP = re.compile(r"^(correction|erratum|corrigendum|retraction|author correction|publisher correction|issue information|front cover|back cover|inside (front|back) cover|table of contents|masthead|editorial board|outstanding reviewers)", re.I)
TOPIC_RE = {k: re.compile(v["kw"], re.I) for k, v in TOPICS.items()}


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(TAG.sub("", s or ""))).strip()


def date_of(item):
    for key in ("published-online", "published", "created"):
        p = ((item.get(key) or {}).get("date-parts") or [[]])[0]
        if p and p[0]:
            y, m, d = (list(p) + [1, 1])[:3]
            return date(y, m or 1, d or 1)
    return None


def classify(text):
    tags = [k for k, rx in TOPIC_RE.items() if k != "mat" and rx.search(text)]
    return tags[:3] or ["mat"]


def get(url, params):
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=60)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()["message"]
        except requests.RequestException as e:
            if attempt == 3:
                print(f"  ! 요청 실패: {e}", file=sys.stderr)
                return None
            time.sleep(3 * 2 ** attempt)


def fetch_journal(jkey, since):
    """ISSN 후보를 모두 조회해 DOI 기준으로 합치고, 커서로 페이지를 넘깁니다."""
    j = JOURNALS[jkey]
    seen, rows = set(), []
    for issn in j["issn"]:
        cursor = "*"
        while cursor and len(rows) < MAX_PER_JOURNAL:
            params = {"filter": f"from-created-date:{since.isoformat()},type:journal-article",
                      "rows": 1000, "cursor": cursor,
                      "select": "DOI,title,URL,published-online,published,created,abstract,type"}
            if MAILTO:
                params["mailto"] = MAILTO
            msg = get(f"https://api.crossref.org/journals/{issn}/works", params)
            if not msg:
                break
            items = msg.get("items", [])
            for it in items:
                doi = (it.get("DOI") or "").lower()
                title = clean((it.get("title") or [""])[0])
                d = date_of(it)
                if not doi or doi in seen or not title or SKIP.match(title):
                    continue
                if d and d < since:        # 예전 논문이 늦게 등록된 경우 제외
                    continue
                seen.add(doi)
                text = title + " " + clean(it.get("abstract", ""))[:1500]
                rows.append({"j": jkey, "title": title, "url": f"https://doi.org/{doi}",
                             "date": (d or date.today()).isoformat(), "topics": classify(text)})
            cursor = msg.get("next-cursor") if len(items) == 1000 else None
            time.sleep(1)
    print(f"  {j['name']}: {len(rows)}편")
    return rows


def stats(papers, today):
    cut = (today - timedelta(days=RECENT_DAYS)).isoformat()
    counts, totals = defaultdict(Counter), Counter()
    recent, older, rn, on = Counter(), Counter(), 0, 0
    for p in papers:
        totals[p["j"]] += 1
        is_recent = p["date"] >= cut
        rn += is_recent; on += not is_recent
        for t in p["topics"]:
            counts[p["j"]][t] += 1
            (recent if is_recent else older)[t] += 1
    # 최근 30일 비중 - 이전 기간 비중 (퍼센트포인트)
    momentum = {t: round(100 * (recent[t] / max(rn, 1) - older[t] / max(on, 1)), 1) for t in TOPICS}
    return {"counts": {j: dict(c) for j, c in counts.items()}, "totals": dict(totals), "momentum": momentum}


def fallback_insights(papers, st):
    """API 키가 없을 때 통계만으로 만드는 해설."""
    overall = Counter(t for p in papers for t in p["topics"])
    out = []
    for t, n in overall.most_common(3):
        out.append({"t": t, "h": f"{TOPICS[t]['name']} 논문이 {n}편으로 가장 많은 축에 속했습니다",
                    "p": f"수집 논문의 {round(100*n/max(len(papers),1))}%가 이 주제로 분류됐고, 최근 30일 비중은 이전보다 {st['momentum'][t]:+}%p 달라졌습니다."})
    for t, d in sorted(st["momentum"].items(), key=lambda x: -x[1])[:3]:
        if d > 0 and t not in {o["t"] for o in out}:
            out.append({"t": t, "h": f"최근 한 달 {TOPICS[t]['name']} 비중이 늘었습니다",
                        "p": f"직전 기간보다 {d:+}%p 높아졌습니다. 아래 목록에서 이 주제로 걸러 최신 논문을 확인해 보세요."})
    notes = {}
    for j in JOURNALS:
        c = Counter(st["counts"].get(j, {}))
        if c:
            notes[j] = "가장 많이 다룬 주제는 " + ", ".join(TOPICS[t]["name"] for t, _ in c.most_common(2)) + "입니다."
    return out, notes


def claude_insights(papers, st):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    by_j = defaultdict(list)
    for p in sorted(papers, key=lambda p: p["date"], reverse=True):
        if len(by_j[p["j"]]) < 60:
            by_j[p["j"]].append(p["title"])
    prompt = (
        "당신은 화학공학·기후테크 연구 동향 분석가입니다. 아래는 9개 저널의 최근 3개월 논문 제목과 주제 통계입니다.\n"
        "여러 저널에 걸쳐 나타난 구체적 흐름 5~6개와 저널별 한두 문장 요약을 한국어로 작성하세요. "
        "구체적 수치와 기술명을 근거로 들고, 제목에서 확인되지 않는 내용은 쓰지 마세요.\n"
        f"주제 코드: {json.dumps({k: v['name'] for k, v in TOPICS.items()}, ensure_ascii=False)}\n"
        f"저널 코드: {json.dumps({k: v['name'] for k, v in JOURNALS.items()}, ensure_ascii=False)}\n"
        f"통계: {json.dumps(st, ensure_ascii=False)}\n제목: {json.dumps(by_j, ensure_ascii=False)}\n\n"
        '코드블록 없이 JSON만 출력하세요: {"insights":[{"t":"주제코드","h":"한 문장 제목","p":"2~3문장 설명"}],"notes":{"저널코드":"요약"}}'
    )
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", timeout=300, headers={
            "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"), "max_tokens": 4000,
                  "messages": [{"role": "user", "content": prompt}]})
        r.raise_for_status()
        text = "".join(b.get("text", "") for b in r.json()["content"])
        data = json.loads(re.sub(r"```(json)?", "", text).strip())
        return [i for i in data.get("insights", []) if i.get("t") in TOPICS], data.get("notes", {})
    except Exception as e:
        print(f"  ! Claude 해설 생성 실패, 기본 해설로 대체: {e}", file=sys.stderr)
        return None


def demo_papers(today):
    import random
    random.seed(1)
    subjects = ["perovskite tandem solar cells", "sodium-ion battery cathodes", "direct air capture sorbents",
                "seawater electrolysis for hydrogen", "heatwave exposure under warming", "rare-earth separation membranes",
                "PFAS removal from wastewater", "electric vehicle adoption policy", "hydrogel wound therapy", "thermoelectric devices"]
    out = []
    for j in JOURNALS:
        for i in range(random.randint(8, 25)):
            s = random.choice(subjects)
            out.append({"j": j, "title": f"Demo study {i+1} on {s}", "url": "https://doi.org/10.0000/demo",
                        "date": (today - timedelta(days=random.randint(0, WINDOW_DAYS))).isoformat(), "topics": classify(s)})
    return out


def main():
    demo = "--demo" in sys.argv
    today = datetime.now(timezone.utc).date()
    since = today - timedelta(days=WINDOW_DAYS)
    print(f"수집 기간: {since} ~ {today}")
    papers = demo_papers(today) if demo else [p for j in JOURNALS for p in fetch_journal(j, since)]
    if not papers:
        sys.exit("수집된 논문이 없습니다. 네트워크나 Crossref 상태를 확인하세요.")
    st = stats(papers, today)
    res = None if demo else claude_insights(papers, st)
    insights, notes = res if res else fallback_insights(papers, st)
    payload = {
        "generated": today.isoformat(), "since": since.isoformat(), "ai": bool(res), "demo": demo,
        "topics": {k: {"name": v["name"], "color": v["color"]} for k, v in TOPICS.items()},
        "journals": {k: {"name": v["name"], "home": v["home"], "note": notes.get(k, "")} for k, v in JOURNALS.items()},
        "papers": papers, "stats": st, "insights": insights,
    }
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", data), encoding="utf-8")
    print(f"완료: {OUT} ({len(papers)}편)")


if __name__ == "__main__":
    main()
