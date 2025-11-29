# config.py

PARTS = ["머리", "상의", "하의", "장갑"]

# 고급/레어 → 상위 등급
PROB_COMMON_TO_RARE = 0.40   # 고급 3개 -> 레어 1개 성공 확률
PROB_RARE_TO_ELITE = 0.30    # 레어 3개 -> 엘리트 1개 성공 확률

# 엘리트/에픽 → 상위 등급
PROB_ELITE_TO_EPIC = 0.25    # 엘리트 3개 -> 에픽 1개 성공 확률
PROB_EPIC_TO_LEGEND = 0.20   # 에픽 3개 -> 전설 1개 성공 확률

# 승급 비용 (현금)
COST_ELITE_TO_EPIC = 500     # 엘리트 3개 합성 시도당
COST_EPIC_TO_LEGEND = 3000   # 에픽 3개 합성 시도당

# 가챠 설정
COST_GACHA = 2000            # 패션 뽑기 1회 비용

GACHA_PROB_EPIC = 0.02
GACHA_PROB_ELITE = 0.10
GACHA_PROB_RARE = 0.33
GACHA_PROB_COMMON = 0.55
