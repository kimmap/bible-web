# 프로젝트 규칙

## 코드 수정 후 서버 재시작

코드를 수정할 때마다 반드시 다음을 실행한다:

1. 기존 포트 2323 프로세스 종료
2. 백그라운드로 서버 재시작

```bash
cd /home/opc/bibleAPI && sudo fuser -k 2323/tcp 2>/dev/null; sudo python3 -m http.server 2323 &
```
