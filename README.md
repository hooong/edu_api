# Education Registration API

## 🏗 프로젝트 구조

```
edu_register_api/
├── edu_register_api/           # 메인 애플리케이션
│   ├── api/                   # API 라우터
│   ├── core/                 # 핵심 설정
│   │   ├── config.py         # 앱 설정
│   │   ├── database.py       # DB 연결
│   │   ├── security.py       # 보안 유틸
│   │   ├── redis.py          # Redis 클라이언트
│   │   ├── uow.py           # Unit of Work 패턴
│   │   └── depends.py        # 의존성 주입
│   ├── models/               # 데이터베이스 모델
│   ├── repositories/         # 데이터 접근 계층
│   ├── services/            # 비즈니스 로직
│   ├── schemas/             # Pydantic 스키마
│   └── main.py              
├── alembic/                 # 데이터베이스 마이그레이션
├── tests/                   # 테스트 코드
├── docker-compose.yml       # Docker 설정
├── pyproject.toml          # 프로젝트 설정 및 의존성 관리
└── README.md               # 프로젝트 문서
```

## 🚀 실행 방법 (Docker & Docker Compose)

```bash
# 서버 실행 
make up

# 초기 데이터 생성 (실행 후 서버 가동 상태 유지)
make create-seed-data

# 서버 종료
make down

# 테스트
make test

```

(참고) 실행 시 별도로 `.env`를 셋팅하지 않도록 편의상 `core/config.py`의 `Settings`에 기본값을 설정해두었습니다.

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc


## 참고 사항
> 테이블 설계에 대한 의도 \
> 과제에서 제시한 Test / Course, TestRegistration / CourseRegistration 모델은 속성이 동일하고 단지 타입만 다르다고 판단했습니다. \
> 따라서 확장성과 중복 제거를 위해 Item / Registration 단일 테이블로 구현했습니다.