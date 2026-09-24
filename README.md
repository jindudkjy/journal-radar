# 기후테크·화학공학 저널 트렌드 레이더

9개 저널(Nature Energy, Nature Climate Change, Nature Chemical Engineering, Nature Sustainability, Joule, Energy & Environmental Science, ACS Energy Letters, AIChE Journal, Chemical Engineering Journal)의 최근 3개월 논문을 **Crossref API**에서 매주 자동으로 모아, 주제별로 분류한 웹페이지를 GitHub Pages에 게시합니다.

## 설정 (10분)

1. GitHub에서 새 저장소를 만들고 이 폴더의 파일을 모두 올립니다 (`.github` 폴더 포함).
2. **Settings → Pages → Build and deployment → Source**를 `GitHub Actions`로 바꿉니다.
3. **Settings → Secrets and variables → Actions → New repository secret**에서 추가합니다.
   - `CROSSREF_MAILTO`: 본인 이메일 (권장. Crossref가 요청자를 식별해 더 안정적으로 응답합니다)
   - `ANTHROPIC_API_KEY`: 선택. 넣으면 Claude가 매주 한국어 트렌드 해설을 작성하고, 없으면 통계 기반 요약이 들어갑니다.
4. **Actions → 저널 트렌드 주간 갱신 → Run workflow**로 첫 실행을 합니다. 끝나면 `https://<아이디>.github.io/<저장소명>/`에서 페이지를 볼 수 있습니다.

이후에는 매주 월요일 오전 7시(KST)에 자동으로 갱신됩니다. 주기는 `.github/workflows/update.yml`의 `cron`에서 바꿀 수 있습니다.

## 로컬에서 실행

```bash
pip install -r requirements.txt
python scripts/build.py --demo   # 네트워크 없이 샘플 데이터로 화면 확인
CROSSREF_MAILTO=you@example.com python scripts/build.py   # 실제 수집
open site/index.html
```

## 고치고 싶을 때

- **저널 추가·삭제, 수집 기간**: `scripts/config.py`의 `JOURNALS`, `WINDOW_DAYS`
- **주제 분류 기준**: `scripts/config.py`의 `TOPICS` 정규식 (제목과 초록에 적용)
- **디자인**: `templates/index.html`

## 참고

- Crossref는 DOI 등록 정보를 쓰므로 출판사 사이트 차단과 상관없이 9개 저널을 모두 받습니다. 다만 초록은 출판사가 제공한 경우에만 들어 있어, 초록이 없는 논문은 제목만으로 분류됩니다.
- Chemical Engineering Journal은 3개월에 수천 편이 나오므로 수집에 몇 분 걸리고, 목록은 200편씩 나눠 보여 줍니다.
- Claude 해설을 켜면 실행할 때마다 API 요금이 조금 발생합니다(주 1회, 요청 1건).
