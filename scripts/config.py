"""수집 대상 저널과 주제 분류 규칙. 저널·키워드를 바꾸려면 이 파일만 고치면 됩니다."""

WINDOW_DAYS = 92          # 최근 약 3개월
RECENT_DAYS = 30          # '최근 한 달' 급상승 비교 구간
MAX_PER_JOURNAL = 4000    # CEJ처럼 게재량이 많은 저널의 상한

JOURNALS = {
    "ne":    {"name": "Nature Energy",                  "issn": ["2058-7546"], "home": "https://www.nature.com/nenergy/research-articles"},
    "ncc":   {"name": "Nature Climate Change",          "issn": ["1758-6798", "1758-678X"], "home": "https://www.nature.com/nclimate/research-articles"},
    "nce":   {"name": "Nature Chemical Engineering",    "issn": ["2948-1198"], "home": "https://www.nature.com/natchemeng/research-articles"},
    "nsus":  {"name": "Nature Sustainability",          "issn": ["2398-9629"], "home": "https://www.nature.com/natsustain/research-articles"},
    "joule": {"name": "Joule",                          "issn": ["2542-4351", "2542-4785"], "home": "https://www.cell.com/joule/home"},
        "ees":   {"name": "Energy & Environmental Science", "issn": ["1754-5706", "1754-5692"], "home": "https://pubs.rsc.org/en/journals/journalissues/ee", "rss": ["https://pubs.rsc.org/en/journals/rss/ee", "http://feeds.rsc.org/rss/ee"]},
    "acsel": {"name": "ACS Energy Letters",             "issn": ["2380-8195"], "home": "https://pubs.acs.org/toc/aelccp/current"},
    "aiche": {"name": "AIChE Journal",                  "issn": ["1547-5905", "0001-1541"], "home": "https://aiche.onlinelibrary.wiley.com/journal/15475905"},
    "cej":   {"name": "Chemical Engineering Journal",   "issn": ["1385-8947", "1873-3212"], "home": "https://www.sciencedirect.com/journal/chemical-engineering-journal"},
}

# 제목(+초록)에 대한 정규식. 한 논문이 여러 주제에 걸릴 수 있습니다. 아무것도 안 걸리면 'mat'.
TOPICS = {
    "bat":  {"name": "배터리·에너지저장", "color": "#2F6FD1",
             "kw": r"batter|lithium[- ]ion|li[- ]ion|sodium[- ]ion|na[- ]ion|zinc[- ]ion|zn[- ]ion|anode|cathode|electrolyte|solid[- ]state|redox flow|supercapacit|energy storage|\bsei\b|lithium metal|li[–-]s\b|dendrite"},
    "pv":   {"name": "태양전지", "color": "#D99A00",
             "kw": r"perovskite|photovolta|solar cell|tandem|organic solar|\bopv\b|silicon heterojunction|kesterite|cu\(in,ga\)se|cigs"},
    "h2":   {"name": "수소·수전해", "color": "#1A9E8F",
             "kw": r"hydrogen|water electroly|electrolys|\bher\b|\boer\b|oxygen evolution|hydrogen evolution|water splitting|fuel cell|ammonia synth|nitrogen reduction|e-fuel"},
    "ccus": {"name": "CO₂ 포집·전환", "color": "#5B6B2E",
             "kw": r"co2|co₂|carbon dioxide|carbon capture|direct air capture|\bdac\b|carbon removal|negative emission|sequestration|ccus|\bccs\b|methanation|syngas|electroreduction"},
    "sys":  {"name": "에너지시스템·정책·사회", "color": "#8A4FB5",
             "kw": r"polic|market|cost|economic|grid|power system|energy system|decarboni[sz]ation pathway|scenario|adoption|households?|equity|justice|transition|electric vehicle|\bev\b|shipping|aviation|techno-economic|life[- ]cycle|\blca\b|net[- ]zero|emissions? inventory"},
    "clim": {"name": "기후영향·생태", "color": "#C4473A",
             "kw": r"climate change|warming|heatwave|heat extreme|drought|flood|precipitation|sea[- ]level|glacier|permafrost|ocean|amoc|biodiversity|species|forest|ecosystem|crop yield|migration|adaptation|wildfire"},
    "sep":  {"name": "분리·자원회수·순환", "color": "#2B8BC0",
             "kw": r"separat|membrane|recover|recycl|upcycl|circular|rare[- ]earth|lithium extraction|critical mineral|valori[sz]|waste|adsorbent|sorbent|distillation|extraction"},
    "env":  {"name": "수처리·환경오염", "color": "#3E8E5A",
             "kw": r"wastewater|water treatment|desalinat|pollut|contamina|pfas|pfoa|microplastic|nanoplastic|pm2\.5|persulfate|degradation of|antibiotic|heavy metal|groundwater|evaporat"},
    "bio":  {"name": "바이오·의료", "color": "#C2527E",
             "kw": r"tumou?r|cancer|therap|wound|antibacter|bacteri|drug|biosensor|tissue|mrna|sirna|rna delivery|immun|clinical|medic|bioprint|ferment|microb|enzym"},
    "mat":  {"name": "기타 소재·공정", "color": "#7A7F87", "kw": r"$^"},
}
