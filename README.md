# Bible Web Search

이 프로젝트는 웹 브라우저에서 개역개정 성경을 검색하고 읽을 수 있는 간단한 웹 애플리케이션입니다.
별도의 백엔드 서버 없이, 구조화된 JSON 데이터 파일을 로컬에서 읽어와 클라이언트 사이드에서 검색을 수행합니다.

## 🚀 시작하기

이 프로젝트는 정적 웹 호스팅(GitHub Pages 등)에 배포하여 누구나 무료로 사용할 수 있습니다.

### 1. 설치 및 실행

파일을 다운로드 받은 후 `index.html` 파일을 웹 브라우저로 열기만 하면 됩니다.
(Chrome, Safari, Edge 등 최신 브라우저 권장)

### 캐싱 방식

이 앱은 `Service Worker + Cache Storage`를 사용합니다.

- 첫 방문 시 `bible_structured.json`을 다운로드합니다.
- 이후 새로고침에서는 브라우저 캐시를 우선 사용합니다.
- `index.html`과 `favicon.png`도 함께 캐시해서, 네트워크가 끊겨도 앱 화면이 열립니다.
- 성경 데이터 파일도 캐시되므로, 이미 한 번 열었던 환경에서는 오프라인 검색이 가능합니다.

주의: 서비스 워커는 보통 `http://localhost` 또는 HTTPS 환경에서 정상 동작합니다. `file://`로 직접 열면 캐시가 기대대로 동작하지 않을 수 있습니다.

### 2. 데이터 구조 (`bible_structured.json`)

성경 데이터는 `bible_structured.json` 파일에 저장되어 있습니다. 이 파일은 약 3만 1천여 개의 성경 구절을 포함하고 있는 JSON 배열입니다.

#### 데이터 예시

```json
[
  {
    "book": "창",         // 성경 책 약어 (예: 창, 출, 레...)
    "chapter": 1,        // 장
    "verse": 1,          // 절
    "content": "태초에 하나님이 천지를 창조하시니라" // 본문 내용
  },
  {
    "book": "요",
    "chapter": 3,
    "verse": 16,
    "content": "하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니..."
  }
]
```

### 3. 개발자 가이드 (API처럼 사용하기)

이 JSON 파일은 마치 **Read-Only API**처럼 사용할 수 있습니다. 웹, 모바일 앱, 데스크톱 프로그램 등 어디서든 HTTP GET 요청으로 데이터를 가져와 활용하세요.

#### JavaScript (Fetch API)

```javascript
// 데이터 불러오기
async function loadBibleData() {
    try {
        const response = await fetch('./bible_structured.json');
        const data = await response.json();
        console.log(`총 ${data.length}개의 구절을 불러왔습니다.`);
        return data;
    } catch (error) {
        console.error("데이터 로드 실패:", error);
    }
}

// 특정 구절 찾기 예제 (요한복음 3장 16절)
function findVerse(data, book, chapter, verse) {
    return data.find(item => 
        item.book === book && 
        item.chapter === chapter && 
        item.verse === verse
    );
}
```

#### Python (Requests)

```python
import json
import requests

# 로컬 파일로 사용 시
with open('bible_structured.json', 'r', encoding='utf-8') as f:
    bible_data = json.load(f)

# 또는 웹에 호스팅된 파일 사용 시
# url = "YOUR_GITHUB_PAGES_URL/bible_structured.json"
# bible_data = requests.get(url).json()

# 검색 예제
results = [item for item in bible_data if "사랑" in item['content']]
print(f"'사랑'이 포함된 구절 수: {len(results)}")
```

## ⚠️ 주의사항

*   **파일 크기**: JSON 파일은 약 6MB 정도입니다. 모바일 환경에서는 데이터 사용량에 주의가 필요할 수 있으나, 텍스트 데이터이므로 로딩 속도는 매우 빠릅니다.
*   **초기 로딩**: 데이터를 모두 메모리에 로드한 후 검색하므로, 페이지 최초 접속 시 수 초의 로딩 시간이 걸릴 수 있습니다.
*   **캐시 갱신**: `sw.js`의 캐시 버전을 올리면 이전 캐시가 자동으로 정리되고 새 파일이 다시 저장됩니다.

## 📝 라이선스

이 프로젝트의 소스 코드는 자유롭게 사용 가능합니다. 단, 성경 데이터(개역개정)의 저작권은 대한성서공회에 있을 수 있으므로 상업적 이용 시 확인이 필요합니다.
