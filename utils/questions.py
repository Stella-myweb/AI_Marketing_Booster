# utils/questions.py - 자가 진단 질문 데이터
# 형식: Python (.py)
# 역할: 질문과 선택지 데이터 구조 정의

# 네이버 스마트 플레이스 마케팅 자가진단 질문 및 평가 시스템

# 자가진단 테스트 - 단계별로 구조화된 질문과 선택지
diagnosis_questions = {
    "인식하게 한다": [
        {
            "id": "keywords_status",
            "question": "대표 키워드 설정 상태",
            "options": [
                {"value": "A", "text": "키워드를 전혀 설정하지 않았다", "score": 1},
                {"value": "B", "text": "1-2개 정도 기본적인 키워드만 설정했다", "score": 2},
                {"value": "C", "text": "업종 관련 키워드 3-5개 정도 설정했다", "score": 3},
                {"value": "D", "text": "다양한 키워드(지역명, 상황, 특징 등)를 체계적으로 설정했다", "score": 4},
                {"value": "E", "text": "경쟁업체 분석을 통해 최적화된 키워드를 지속적으로 관리한다", "score": 5}
            ]
        },
        {
            "id": "description_status",
            "question": "상세 설명 작성 상태",
            "options": [
                {"value": "A", "text": "상세 설명을 작성하지 않았다", "score": 1},
                {"value": "B", "text": "간단한 정보만 기재했다 (1-2문장)", "score": 2},
                {"value": "C", "text": "기본 정보와 매장 특징을 포함해 작성했다", "score": 3},
                {"value": "D", "text": "핵심 키워드를 포함한 자세한 설명과 스토리를 작성했다", "score": 4},
                {"value": "E", "text": "정기적으로 업데이트하며 키워드를 전략적으로 배치했다", "score": 5}
            ]
        },
        {
            "id": "location_accuracy",
            "question": "매장 위치 정보 정확도",
            "options": [
                {"value": "A", "text": "주소만 기재했다", "score": 1},
                {"value": "B", "text": "주소와 간단한 길 안내를 추가했다", "score": 2},
                {"value": "C", "text": "주변 랜드마크와 대중교통 정보를 포함했다", "score": 3},
                {"value": "D", "text": "상세한 찾아오는 길과 주차 정보까지 제공한다", "score": 4},
                {"value": "E", "text": "위치 태그와 내비게이션 연동이 완벽하게 설정되어 있다", "score": 5}
            ]
        },
        {
            "id": "hours_info",
            "question": "영업시간, 휴무일 정보 업데이트",
            "options": [
                {"value": "A", "text": "영업시간 정보가 없거나 부정확하다", "score": 1},
                {"value": "B", "text": "기본적인 영업시간만 등록되어 있다", "score": 2},
                {"value": "C", "text": "영업시간과 휴무일이 정확히 등록되어 있다", "score": 3},
                {"value": "D", "text": "브레이크 타임, 라스트 오더 시간까지 상세히 기재되어 있다", "score": 4},
                {"value": "E", "text": "특별 영업일, 임시 휴무 등의 변동사항도 실시간으로 업데이트한다", "score": 5}
            ]
        }
    ],
    "클릭하게 한다": [
        {
            "id": "image_quality",
            "question": "대표 이미지 품질",
            "options": [
                {"value": "A", "text": "이미지를 등록하지 않았거나 저품질 이미지를 사용 중이다", "score": 1},
                {"value": "B", "text": "기본적인 매장/메뉴 사진이 등록되어 있다", "score": 2},
                {"value": "C", "text": "매장 분위기와 대표 메뉴 사진이 잘 촬영되어 있다", "score": 3},
                {"value": "D", "text": "전문적으로 촬영된 고품질 이미지를 사용하고 있다", "score": 4},
                {"value": "E", "text": "시즌별, 메뉴별 다양한 고품질 이미지를 정기적으로 업데이트한다", "score": 5}
            ]
        },
        {
            "id": "image_diversity",
            "question": "이미지 구성의 다양성",
            "options": [
                {"value": "A", "text": "이미지가 없거나 1-2개만 등록되어 있다", "score": 1},
                {"value": "B", "text": "비슷한 유형의 이미지만 3-5개 정도 있다", "score": 2},
                {"value": "C", "text": "매장 외관, 내부, 메뉴 등 다양한 측면의 이미지가 있다", "score": 3},
                {"value": "D", "text": "전략적으로 구성된 다양한 이미지(공간, 메뉴, 서비스 등)가 있다", "score": 4},
                {"value": "E", "text": "매장의 모든 강점을 보여주는 체계적인 이미지 포트폴리오가 있다", "score": 5}
            ]
        },
        {
            "id": "visual_differentiation",
            "question": "매장 차별점의 시각적 표현",
            "options": [
                {"value": "A", "text": "매장 차별점이 이미지에서 드러나지 않는다", "score": 1},
                {"value": "B", "text": "매장의 기본적인 특징만 확인할 수 있다", "score": 2},
                {"value": "C", "text": "매장의 주요 차별점이 이미지를 통해 어느 정도 드러난다", "score": 3},
                {"value": "D", "text": "매장의 독특한 분위기와 특별한 경험이 이미지에 잘 표현되어 있다", "score": 4},
                {"value": "E", "text": "매장만의 고유한 가치와 스토리가 이미지를 통해 강력하게 전달된다", "score": 5}
            ]
        },
        {
            "id": "title_catchphrase",
            "question": "플레이스 제목과 캐치프레이즈",
            "options": [
                {"value": "A", "text": "기본 상호명만 있다", "score": 1},
                {"value": "B", "text": "상호명과 간단한 업종 설명이 있다", "score": 2},
                {"value": "C", "text": "매장 특징을 나타내는 간단한 문구가 포함되어 있다", "score": 3},
                {"value": "D", "text": "고객 관심을 끌 수 있는 매력적인 캐치프레이즈가 있다", "score": 4},
                {"value": "E", "text": "차별화된 가치를 명확히 전달하는 강력한 문구가 있다", "score": 5}
            ]
        }
    ],
    "머물게 한다": [
        {
            "id": "menu_detail",
            "question": "메뉴/서비스 정보의 상세도",
            "options": [
                {"value": "A", "text": "메뉴/서비스 정보가 없거나 매우 기본적이다", "score": 1},
                {"value": "B", "text": "메뉴명과 가격 정도만 나열되어 있다", "score": 2},
                {"value": "C", "text": "메뉴 설명과 이미지가 함께 제공된다", "score": 3},
                {"value": "D", "text": "재료, 조리법, 추천 포인트 등 상세한 정보가 있다", "score": 4},
                {"value": "E", "text": "메뉴 스토리, 식재료 출처, 먹는 방법까지 풍부한 정보가 있다", "score": 5}
            ]
        },
        {
            "id": "content_update",
            "question": "콘텐츠 업데이트 주기",
            "options": [
                {"value": "A", "text": "개설 이후 거의 업데이트하지 않았다", "score": 1},
                {"value": "B", "text": "필요할 때만 간헐적으로 업데이트한다", "score": 2},
                {"value": "C", "text": "1-2개월에 한 번 정도 업데이트한다", "score": 3},
                {"value": "D", "text": "2주에 한 번 이상 정기적으로 업데이트한다", "score": 4},
                {"value": "E", "text": "주 1회 이상 새로운 콘텐츠나 소식을 추가한다", "score": 5}
            ]
        },
        {
            "id": "news_events",
            "question": "소식/이벤트 활용도",
            "options": [
                {"value": "A", "text": "소식/이벤트 기능을 사용하지 않는다", "score": 1},
                {"value": "B", "text": "가끔 중요한 공지사항만 올린다", "score": 2},
                {"value": "C", "text": "월 1회 정도 소식이나 이벤트를 게시한다", "score": 3},
                {"value": "D", "text": "정기적으로 다양한 소식과 이벤트를 업데이트한다", "score": 4},
                {"value": "E", "text": "전략적으로 계획된 다양한 콘텐츠를 지속적으로 게시한다", "score": 5}
            ]
        },
        {
            "id": "response_rate",
            "question": "사용자 질문 응답률",
            "options": [
                {"value": "A", "text": "질문에 거의 응답하지 않는다", "score": 1},
                {"value": "B", "text": "일부 질문에만 늦게 응답한다", "score": 2},
                {"value": "C", "text": "대부분의 질문에 1-2일 내에 응답한다", "score": 3},
                {"value": "D", "text": "모든 질문에 24시간 이내 응답한다", "score": 4},
                {"value": "E", "text": "매우 신속하게(몇 시간 이내) 상세히 응답한다", "score": 5}
            ]
        }
    ],
    "연락오게 한다": [
        {
            "id": "reservation",
            "question": "예약 기능 활성화",
            "options": [
                {"value": "A", "text": "예약 기능을 설정하지 않았다", "score": 1},
                {"value": "B", "text": "기본적인 예약 기능만 활성화했다", "score": 2},
                {"value": "C", "text": "예약 기능이 활성화되어 있고 가끔 관리한다", "score": 3},
                {"value": "D", "text": "예약 기능을 적극 활용하고 빠르게 대응한다", "score": 4},
                {"value": "E", "text": "예약 전용 혜택과 함께 완벽하게 관리되고 있다", "score": 5}
            ]
        },
        {
            "id": "phone_system",
            "question": "전화 응대 시스템",
            "options": [
                {"value": "A", "text": "스마트콜을 설정하지 않았다", "score": 1},
                {"value": "B", "text": "스마트콜만 설정해 놓았다", "score": 2},
                {"value": "C", "text": "스마트콜을 영업시간 동안 대체로 응대한다", "score": 3},
                {"value": "D", "text": "스마트콜에 매우 빠르게 응대하고 있다", "score": 4},
                {"value": "E", "text": "스마트콜 응대와 함께 부재 시 콜백 시스템도 갖추고 있다", "score": 5}
            ]
        },
        {
            "id": "coupons",
            "question": "쿠폰/할인 혜택 제공",
            "options": [
                {"value": "A", "text": "쿠폰이나 할인 혜택을 제공하지 않는다", "score": 1},
                {"value": "B", "text": "간헐적으로 간단한 할인 혜택을 제공한다", "score": 2},
                {"value": "C", "text": "정기적인 쿠폰이나 할인 프로모션을 진행한다", "score": 3},
                {"value": "D", "text": "다양한 타겟층을 위한 여러 유형의 혜택을 제공한다", "score": 4},
                {"value": "E", "text": "전략적으로 설계된 단계별 고객 혜택 시스템을 운영한다", "score": 5}
            ]
        },
        {
            "id": "cta",
            "question": "방문/구매 전환 유도 문구",
            "options": [
                {"value": "A", "text": "특별한 전환 유도 문구가 없다", "score": 1},
                {"value": "B", "text": "기본적인 방문/구매 안내만 있다", "score": 2},
                {"value": "C", "text": "명확한 행동 유도 문구가 있다", "score": 3},
                {"value": "D", "text": "혜택과 함께 강력한 행동 유도 문구를 사용한다", "score": 4},
                {"value": "E", "text": "고객 상황별 맞춤형 전환 유도 시스템을 갖추고 있다", "score": 5}
            ]
        }
    ],
    "후속 피드백 받는다": [
        {
            "id": "review_collection",
            "question": "리뷰 수집 활동",
            "options": [
                {"value": "A", "text": "리뷰 수집을 위한 활동을 하지 않는다", "score": 1},
                {"value": "B", "text": "가끔 리뷰를 요청하는 정도다", "score": 2},
                {"value": "C", "text": "영수증 리뷰 이벤트를 진행 중이다", "score": 3},
                {"value": "D", "text": "체계적인 리뷰 수집 시스템을 운영 중이다", "score": 4},
                {"value": "E", "text": "다양한 채널을 통한 종합적인 리뷰 수집 전략을 실행 중이다", "score": 5}
            ]
        },
        {
            "id": "review_management",
            "question": "리뷰 관리와 응대",
            "options": [
                {"value": "A", "text": "리뷰에 거의 응답하지 않는다", "score": 1},
                {"value": "B", "text": "긍정적인 리뷰에만 가끔 응답한다", "score": 2},
                {"value": "C", "text": "대부분의 리뷰에 기본적인 답변을 한다", "score": 3},
                {"value": "D", "text": "모든 리뷰에 개인화된 답변을 남긴다", "score": 4},
                {"value": "E", "text": "리뷰 내용을 분석하고 서비스 개선에 적극 반영한다", "score": 5}
            ]
        },
        {
            "id": "save_alert",
            "question": "저장/알림 받기 유도",
            "options": [
                {"value": "A", "text": "저장/알림 받기를 유도하지 않는다", "score": 1},
                {"value": "B", "text": "기본적인 안내만 있다", "score": 2},
                {"value": "C", "text": "저장/알림 받기를 위한 간단한 혜택을 제공한다", "score": 3},
                {"value": "D", "text": "저장/알림 받기를 위한 특별한 인센티브를 제공한다", "score": 4},
                {"value": "E", "text": "저장/알림 받은 고객을 위한 전용 혜택 시스템이 있다", "score": 5}
            ]
        },
        {
            "id": "regular_customers",
            "question": "단골 고객 관리 프로그램",
            "options": [
                {"value": "A", "text": "특별한 단골 고객 관리를 하지 않는다", "score": 1},
                {"value": "B", "text": "기본적인 단골 고객 혜택만 있다", "score": 2},
                {"value": "C", "text": "정기적인 단골 고객 이벤트를 진행한다", "score": 3},
                {"value": "D", "text": "체계적인 단골 고객 관리 시스템을 운영 중이다", "score": 4},
                {"value": "E", "text": "고객 세그먼트별 차별화된 충성도 프로그램을 운영한다", "score": 5}
            ]
        }
    ]
}

# 평가 시스템 - 점수 계산 및 레벨 판정
def calculate_score(answers):
    """
    사용자의 응답을 바탕으로 점수를 계산하고 레벨을 판정합니다.
    
    Args:
        answers (dict): 질문 ID를 키로, 선택한, 옵션 값(A-E)을 값으로 하는 사전
        
    Returns:
        dict: 총점, 단계별 점수, 레벨 등의 평가 결과
    """
    total_score = 0
    stage_scores = {}
    
    # 단계별로 점수 계산
    for stage, questions in diagnosis_questions.items():
        stage_score = 0
        for question in questions:
            q_id = question["id"]
            if q_id in answers:
                selected_option = answers[q_id]
                for option in question["options"]:
                    if option["value"] == selected_option:
                        stage_score += option["score"]
                        total_score += option["score"]
                        break
        
        # 단계별 평균 점수 계산 (5점 만점)
        stage_scores[stage] = {
            "raw_score": stage_score,
            "avg_score": round(stage_score / len(questions), 1),
            "max_score": len(questions) * 5
        }
    
    # 전체 평균 점수 계산 (5점 만점)
    total_questions = sum(len(questions) for questions in diagnosis_questions.values())
    avg_score = round(total_score / total_questions, 1)
    
    # 레벨 판정
    level = determine_level(avg_score)
    
    return {
        "total_score": total_score,
        "avg_score": avg_score,
        "max_score": total_questions * 5,
        "level": level,
        "stage_scores": stage_scores
    }

def determine_level(avg_score):
    """
    평균 점수를 바탕으로 레벨을 판정합니다.
    
    Args:
        avg_score (float): 평균 점수 (5점 만점)
        
    Returns:
        dict: 레벨 정보 (이름, 설명 등)
    """
    if avg_score < 1.5:
        return {
            "name": "초보 단계",
            "description": "네이버 플레이스 마케팅의 기초부터 시작해야 합니다. 기본적인 정보 등록과 키워드 설정부터 시작하세요.",
            "next_step": "기본 정보 등록과 대표 키워드 설정에 집중하세요."
        }
    elif avg_score < 2.5:
        return {
            "name": "기초 단계",
            "description": "기본적인 설정은 되어 있으나, 체계적인 관리가 필요합니다. 콘텐츠 품질과 다양성을 높여보세요.",
            "next_step": "이미지 품질 향상과 상세 설명 최적화에 집중하세요."
        }
    elif avg_score < 3.5:
        return {
            "name": "발전 단계",
            "description": "플레이스 마케팅의 기본기가 잘 갖춰져 있습니다. 더 전략적인 접근으로 한 단계 발전시키세요.",
            "next_step": "리뷰 관리와 콘텐츠 업데이트 주기를 개선하세요."
        }
    elif avg_score < 4.5:
        return {
            "name": "전문가 단계",
            "description": "높은 수준의 플레이스 마케팅을 실행하고 있습니다. 세부적인 최적화로 완성도를 높이세요.",
            "next_step": "고객 세그먼트별 전략과 전환율 최적화에 집중하세요."
        }
    else:
        return {
            "name": "마스터 단계",
            "description": "최고 수준의 플레이스 마케팅을 구현하고 있습니다. 지속적인 혁신으로 경쟁 우위를 유지하세요.",
            "next_step": "트렌드 분석과 데이터 기반 의사결정으로 더 발전시키세요."
        }

# 개선 전략 제안 - 가장 취약한 영역 식별 및 액션 아이템 제안
def suggest_improvements(result):
    """
    진단 결과를 바탕으로 개선이 필요한 영역과 구체적인 액션 아이템을 제안합니다.
    
    Args:
        result (dict): calculate_score 함수의 반환값
        
    Returns:
        dict: 개선이 필요한 영역과 액션 아이템
    """
    stage_scores = result["stage_scores"]
    
    # 단계별 평균 점수 기준으로 정렬하여 가장 취약한 영역 식별
    sorted_stages = sorted(stage_scores.items(), key=lambda x: x[1]["avg_score"])
    
    # 가장 취약한 3개 영역 선정
    weak_areas = sorted_stages[:3]
    
    improvements = []
    for stage, score_info in weak_areas:
        improvements.append({
            "stage": stage,
            "avg_score": score_info["avg_score"],
            "action_items": get_action_items(stage, score_info["avg_score"])
        })
    
    return {
        "weak_areas": improvements,
        "overall_suggestion": get_overall_suggestion(result["level"]["name"])
    }

def get_action_items(stage, score):
    """
    단계와 점수에 따른 구체적인 액션 아이템을 반환합니다.
    
    Args:
        stage (str): 단계명
        score (float): 해당 단계의 평균 점수
        
    Returns:
        list: 구체적인 액션 아이템 목록
    """
    action_items = {
        "인식하게 한다": {
            "low": [
                "기본 키워드 5개를 설정하고 상세 설명에 핵심 키워드를 포함시키세요.",
                "비즈니스의 핵심 특성을 담은,3-5문장의 상세 설명을 작성하세요.",
                "찾아오는 길에 주변 랜드마크와 대중교통 정보를 추가하세요."
            ],
            "medium": [
                "경쟁업체의 키워드를 분석하고 틈새 키워드를 발굴하세요.",
                "상세 설명에 상황별, 시즌별 키워드를 추가하세요.",
                "위치 정보에 주차 정보와 내비게이션 링크를 추가하세요."
            ],
            "high": [
                "키워드 조합 원리를 활용해 5개 키워드로 100개 이상의 키워드 노출을 확보하세요.",
                "주기적으로 트렌드 키워드를 업데이트하고 성과를 모니터링하세요.",
                "독점 키워드를 발굴하여 경쟁 없는 검색 결과를 확보하세요."
            ]
        },
        "클릭하게 한다": {
            "low": [
                "고화질의 매장 사진과 대표 메뉴 사진을 최소 5장 이상 등록하세요.",
                "다양한 각도와 시간대의 매장 사진을 추가하세요.",
                "비즈니스의 특성을 한 눈에 알 수 있는 캐치프레이즈를 추가하세요."
            ],
            "medium": [
                "시즌별, 특별 이벤트별 사진을 주기적으로 업데이트하세요.",
                "메뉴/서비스의 독특한 특성이 드러나는 사진을 추가하세요.",
                "타겟 고객층에 어필할 수 있는 차별화된 캐치프레이즈를 개발하세요."
            ],
            "high": [
                "전문 사진작가의 도움을 받아 브랜드 이미지와 일관된 시각적 콘텐츠를 제작하세요.",
                "매장의 분위기, 스토리, 철학이 드러나는 시각적 스토리텔링을 구현하세요.",
                "정기적인 A/B 테스트를 통해 클릭률이 가장 높은 이미지와 문구를 선별하세요."
            ]
        },
        "머물게 한다": {
            "low": [
                "모든 메뉴/서비스에 대한 기본적인 설명과 가격 정보를 등록하세요.",
                "한 달에 한 번 이상 새로운 소식이나 이벤트를 등록하세요.",
                "고객 질문에 대해 24시간 이내에 응답하는 체계를 마련하세요."
            ],
            "medium": [
                "메뉴/서비스 설명에 재료, 특징, 추천 포인트 등 상세 정보를 추가하세요.",
                "2주에 한 번 이상 시즌 메뉴, 프로모션 등의 콘텐츠를 업데이트하세요.",
                "자주 묻는 질문과 답변 섹션을 추가하여 고객의 체류시간을 늘리세요."
            ],
            "high": [
                "메뉴/서비스의 스토리텔링과 차별화된 가치 제안을 통해 콘텐츠의 깊이를 더하세요.",
                "주 1회 이상 콘텐츠를 업데이트하고 알림 받기 고객을 위한 독점 콘텐츠를 제공하세요.",
                "고객 피드백과 질문을 분석하여 FAQ와 콘텐츠 개선에 적극 반영하세요."
            ]
        },
        "연락오게 한다": {
            "low": [
                "기본적인 예약 기능을 활성화하고 스마트콜 설정을 완료하세요.",
                "시즌별 할인 쿠폰이나 프로모션을 준비하세요.",
                "방문/구매를 유도하는 명확한 CTA(Call-to-Action) 문구를 추가하세요."
            ],
            "medium": [
                "예약 확인 및 리마인더 시스템을 구축하세요.",
                "첫 방문 고객, 재방문 고객을 위한 차별화된 혜택을 제공하세요.",
                "시간대별, 요일별 특별 프로모션으로 방문 유도를 강화하세요."
            ],
            "high": [
                "예약 고객을 위한 VIP 서비스와 특별 혜택 시스템을 구축하세요.",
                "고객 데이터를 분석하여 개인화된 혜택과 추천을 제공하세요.",
                "고객 여정 단계별 최적화된 CTA와 전환 전략을 개발하세요."
            ]
        },
        "후속 피드백 받는다": {
            "low": [
                "영수증에 리뷰 작성 안내와 혜택을 명시하세요.",
                "모든 리뷰에 48시간 이내 답변을 제공하세요.",
                "매장 내 저장/알림 받기 안내 POP을 설치하세요."
            ],
            "medium": [
                "영수증 QR코드를 통해 네이버 검색-플레이스-리뷰로 이어지는 경로를 안내하세요.",
                "부정적 리뷰에 대해 개선 약속과 함께 보상 시스템을 마련하세요.",
                "저장/알림 받기 고객을 위한 월간 특별 혜택을 제공하세요."
            ],
            "high": [
                "리뷰 데이터를 분석하여 서비스/메뉴 개선에 반영하고 그 결과를 공유하세요.",
                "백링크 경로를 활용한 리뷰 유도 시스템을 최적화하세요.",
                "단골 고객의 선호도와 방문 패턴을 분석한 개인화된 로열티 프로그램을 운영하세요."
            ]
        }
    }
    
    if score < 2.5:
        return action_items[stage]["low"]
    elif score < 4:
        return action_items[stage]["medium"]
    else:
        return action_items[stage]["high"]

def get_overall_suggestion(level):
    """
    전체 레벨에 따른 종합적인 제안을 반환합니다.
    
    Args:
        level (str): 레벨 이름
        
    Returns:
        str: 종합적인 제안
    """
    suggestions = {
        "초보 단계": "플레이스 마케팅의 기초부터 체계적으로 시작하세요. 우선 기본 정보를 충실히 입력하고, 핵심 키워드 설정과 대표 이미지 최적화에 집중하세요. 모바일 환경에서 어떻게 보이는지 항상 체크하고, 일주일에 한 번씩 점진적으로 개선해 나가는 것이 중요합니다.",
        
        "기초 단계": "플레이스의 기본 설정은 잘 되어 있습니다. 이제 콘텐츠의 품질과 다양성을 높이고, 고객 리뷰 수집에 집중하세요. 경쟁업체 분석을 통해 차별화 포인트를 발굴하고, 이를 시각적으로 잘 표현할 수 있는 콘텐츠 전략을 수립하세요. 한 달에 한 번 이상 정기적인 업데이트가 중요합니다.",
        
        "발전 단계": "플레이스 마케팅의 기반이 잘 갖춰져 있습니다. 이제 더 전략적인 접근으로 전환율을 높이는데 집중하세요. 고객 경험을 세분화하여 각 접점에서의 만족도를 높이고, 데이터를 기반으로 한 의사결정을 통해 지속적으로 최적화하세요. 정기적인 콘텐츠 업데이트와 리뷰 관리가 중요합니다.",
        
        "전문가 단계": "높은 수준의 플레이스 마케팅을 실행하고 있습니다. 이제 고객 세그먼트별 맞춤형 전략과 통합 마케팅 접근법으로 더 높은 성과를 창출하세요. 다양한 채널과의 시너지를 극대화하고, 고객 데이터 분석을 통한 개인화된 경험 제공에 집중하세요. 트렌드를 선도하는 혁신적인 접근법을 고민하세요.",
        
        "마스터 단계": "최고 수준의 플레이스 마케팅을 구현하고 있습니다. 지속적인 혁신과 실험을 통해 경쟁 우위를 유지하세요. 고객 인사이트를 깊이 분석하여 새로운 기회를 발굴하고, 브랜드 스토리와 가치를 더욱 효과적으로 전달할 수 있는 전략을 모색하세요. 다른 비즈니스의 벤치마크가 될 수 있는 사례를 만들어가세요."
    }
    
    return suggestions.get(level, "플레이스 마케팅 전략을 단계적으로 구현해 나가세요. 기본 설정부터 고객 경험 최적화까지 체계적인 접근이 중요합니다.")

# 이 모듈을 직접 실행할 때의 테스트 코드
if __name__ == "__main__":
    # 테스트용 응답 데이터
    test_answers = {
        "keywords_status": "C",
        "description_status": "B",
        "location_accuracy": "C",
        "hours_info": "D",
        "image_quality": "B",
        "image_diversity": "C",
        "visual_differentiation": "B",
        "title_catchphrase": "A",
        "menu_detail": "C",
        "content_update": "B",
        "news_events": "A",
        "response_rate": "D",
        "reservation": "B",
        "phone_system": "C",
        "coupons": "B",
        "cta": "A",
        "review_collection": "C",
        "review_management": "B",
        "save_alert": "A",
        "regular_customers": "B"
    }
    
    # 결과 계산
    result = calculate_score(test_answers)
    
    # 개선 제안 가져오기
    improvements = suggest_improvements(result)
    
    # 결과 출력
    print(f"총점: {result['total_score']}/{result['max_score']}")
    print(f"평균 점수: {result['avg_score']}/5")
    print(f"레벨: {result['level']['name']}")
    print(f"설명: {result['level']['description']}")
    print("\n단계별 점수:")
    for stage, score_info in result['stage_scores'].items():
        print(f"- {stage}: {score_info['raw_score']}/{score_info['max_score']} (평균: {score_info['avg_score']})")
    
    print("\n개선이 필요한 영역:")
    for area in improvements['weak_areas']:
        print(f"- {area['stage']} (점수: {area['avg_score']})")
        for i, action in enumerate(area['action_items'], 1):
            print(f"  {i}. {action}")
    
    print(f"\n종합 제안: {improvements['overall_suggestion']}")