# AI Education Dashboard

Apple Developer Academy 포트폴리오용 개인화된 학습 패턴 상관관계 분석 시스템입니다.

## 📊 프로젝트 개요

4월부터 8월까지의 ChatGPT 대화 데이터를 심층 분석하여 AI 교육 분야의 학습 패턴 상관관계를 도출하는 시스템입니다. 학습 변수들 간의 관계성과 시간적 패턴을 시각화하여 개인화된 학습 전략 수립을 지원합니다.

## 🎯 분석 기간 및 규모

- **분석 기간**: 2025년 4월 1일 ~ 8월 31일 (5개월)
- **전체 데이터**: 9,543개 ChatGPT 대화 메시지
- **실제 분석 데이터**: 8,730개 (JSONL 파일에서 로드)
- **학습 관련 대화**: 4,305개 (49.3%)
- **생성된 차트**: 1개 (4개 분석 차트 포함)
- **토픽 분류**: 8개 카테고리 (AI/ML, Data, Development, Education, Business, Cloud/Infra, Design, General)
- **주요 토픽**: General (4,922개), AI/ML (1,575개)
- **평균 단어 수**: 710개
- **평균 질문 깊이**: 0.33

## 📊 생성되는 차트

### 📈 Learning Pattern Correlation Analysis (4개 차트)

1. **Learning Variables Correlation Matrix**: 학습에 영향을 미치는 주요 변수들(학습 복잡도, 표현 길이, 질문 깊이, 시간대) 간의 상관관계를 히트맵으로 보여줘서, 어떤 요소들이 함께 변하는지 한눈에 파악할 수 있게 해줍니다.

2. **Hourly Learning Pattern Correlation Changes**: 하루 중 시간대별로 표현 길이와 질문 깊이 간의 상관관계가 어떻게 변하는지 추적해서, 최적의 학습 시간대와 패턴 변화를 분석할 수 있게 해줍니다.

3. **Daily Learning Style Correlation**: 요일별로 학습 스타일의 상관관계를 비교해서, 주중과 주말의 학습 패턴 차이를 파악하고 균형 잡힌 학습 습관을 계획할 수 있게 해줍니다.

4. **Correlation Strength Distribution & Learning Pattern Analysis**: 전체 데이터에서 상관관계의 강도를 분류하여 분포를 보여줘서, 학습 패턴의 일관성과 예측 가능성을 평가할 수 있게 해줍니다.

## 📁 프로젝트 구조

```
ai-education-dashboard/
├── advanced_correlation_analyzer.py  # 메인 상관관계 분석 파일
├── dashboard_creator_en.py          # 기본 대시보드 생성
├── question_level_analyzer_en.py     # 질문 분석 모듈
├── data_loader_en.py                 # 데이터 로딩 모듈
├── main_executor_en.py               # 메인 실행 파일
└── correlation_learning_patterns.png # 생성된 분석 차트
```

## 🚀 실행 방법

```bash
# 데이터 파일 준비 (지원 형식: .csv, .json, .jsonl)
# 예시 파일들:
# - processed_conversations.csv
# - conversations_parsed.jsonl
# - data.json

# 상관관계 분석 차트 생성
python3 -c "
from advanced_correlation_analyzer import AdvancedCorrelationAnalyzer
analyzer = AdvancedCorrelationAnalyzer('../../conversations_parsed.jsonl')
if analyzer.load_data():
    analyzer.create_correlation_dashboard()
    print('✅ correlation_learning_patterns.png 생성 완료!')
"
```

### 📁 지원되는 데이터 형식

| 형식 | 설명 | 예시 |
|---|---|---|
| **CSV** | 콤마로 구분된 표 형식 | Excel, 스프레드시트 |
| **JSON** | 단일 객체 또는 배열 | 설정 파일, 작은 데이터 |
| **JSONL** | 한 줄에 하나의 JSON 객체 | 로그 데이터, 대용량 데이터 |

### 📋 필수 데이터 컬럼

```json
{
  "timestamp": "2025-04-01T10:30:00Z",
  "content": "사용자 메시지 내용",
  "word_count": 25,
  "question_depth": 0.7
}
```

## 🛠️ 적용된 분석 기법

많은 방법론들로 분석을 시도했으나 대부분은 심층적 이해없이 일단 해보고 분석 결과로 신뢰도를 주관적으로 평가하는 방식이었습니다. 유의미한 분석방법은 아래와 같습니다.

### 데이터 분석
상관관계 분석, 시계열 분석, 이동평균 분석, 키워드 기반 분류

### 머신러닝
통계적 상관관계 모델링, 기본 수치 계산, 규칙 기반 분류

### 시각화
히트맵 시각화, Matplotlib 차트 생성, 시간 시리즈 플롯, 막대 차트

## 📈 주요 분석 결과

### 상관관계 분석 결과
- **가장 강한 양의 상관관계**: 표현 길이 ↔ 질문 깊이 (학습 집중도와 표현력이 함께 성장)
- **시간대별 패턴**: 오후 시간대에 상관관계가 더 강하게 나타남
- **요일별 차이**: 주중보다 주말에 더 일관된 학습 패턴 관찰
- **상관관계 강도 분포**: 중간 강도의 상관관계가 60% 이상 차지
- **학습 패턴 일관성**: 0.3-0.7 범위의 상관관계가 가장 많아 안정적인 학습 습관 형성

### 기본 분석 결과
- **최적 학습 시간**: 오후 3시
- **평균 성장률**: 17.6%
- **주요 토픽**: General (범용 학습)
- **일일 평균 질문 깊이**: 0.27
- **주간 평균 질문 깊이**: 0.43
- **학습 관련 대화 비율**: 18% (770개/4,266개)

## 🎓 프로젝트 특징

- **집중 분석**: 상관관계 기반 학습 패턴 심층 분석
- **데이터 기반**: 실질적 ChatGPT 사용 데이터 필터링
- **시각화 중심**: 히트맵과 통계 차트로 직관적 인사이트 제공
- **시간적 분석**: 시간대별/요일별 패턴 변화 추적
- **통계적 rigor**: 피어슨 상관계수 기반 과학적 분석

---

*이 코드는 Apple Developer Academy 포트폴리오의 상관관계 분석 차트를 생성합니다.*
*분석 기간: 2025년 4월-8월 | 분석 데이터: 8,730개 메시지 | 차트: 4개 분석 포함*
