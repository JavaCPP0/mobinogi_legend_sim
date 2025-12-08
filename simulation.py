# simulation.py
import random
import copy
from config import (
    PARTS,
    PROB_COMMON_TO_RARE,
    PROB_RARE_TO_ELITE,
    PROB_ELITE_TO_EPIC,
    PROB_EPIC_TO_LEGEND,
    COST_ELITE_TO_EPIC,
    COST_EPIC_TO_LEGEND,
    COST_GACHA,
    GACHA_PROB_EPIC,
    GACHA_PROB_ELITE,
    GACHA_PROB_RARE,
    GACHA_PROB_COMMON,
)


def simulate_one_run(start_state: dict, use_gacha: bool, target_parts=None) -> dict:
    """
    start_state 예시:
    {
        "머리":  {"elite": 50, "epic": 0},
        "상의":  {"elite": 40, "epic": 0},
        "하의":  {"elite": 30, "epic": 0},
        "장갑":  {"elite": 40, "epic": 1},
    }

    target_parts:
        - 전설을 '새로' 노릴 부위 목록.
        - None 또는 빈 리스트인 경우: PARTS 전체를 목표로 사용.
        - target_parts에 없는 부위는
          "이미 전설을 갖고 있는 부위" 로 간주하여 legend=1로 시작.

    use_gacha = False:
        - 입력한 엘리트/에픽만 사용.
        - 더 이상 승급 불가 + 아직 target_parts 전설 미완성 → 실패.

    use_gacha = True:
        - 재료가 모자라서 승급을 더 못 하는 순간마다,
          패션 뽑기(가챠)를 1회 돌려 재료 수급.
        - target_parts 전부 전설 완성될 때까지 계속 진행.
    """
    # 목표 부위 설정
    if not target_parts:
        target_parts = PARTS
    else:
        # 방어적으로 복사
        target_parts = list(target_parts)

    state = copy.deepcopy(start_state)

    # 각 부위 상태 초기화
    part_info = {}
    for part in PARTS:
        state[part].setdefault("common", 0)  # 고급
        state[part].setdefault("rare", 0)    # 레어
        state[part].setdefault("elite", 0)
        state[part].setdefault("epic", 0)

        # 목표 부위면 전설 0개에서 시작, 그 외는 이미 전설 보유로 간주
        if part in target_parts:
            state[part]["legend"] = 0
        else:
            state[part]["legend"] = 1  # 이미 전설 보유라고 취급

        part_info[part] = {
            "epic_attempts": 0,    # 엘리트 -> 에픽 승급 시도 횟수
            "legend_attempts": 0,  # 에픽 -> 전설 승급 시도 횟수
        }

    total_cash_spent = 0

    # 가챠 관련 기록
    gacha_pulls = 0
    gacha_parts = {
        part: {"common": 0, "rare": 0, "elite": 0, "epic": 0}
        for part in PARTS
    }

    def all_targets_done() -> bool:
        # 목표로 삼은 부위들만 체크
        return all(state[part]["legend"] >= 1 for part in target_parts)

    # =========================
    # 가챠 OFF 모드
    # =========================
    if not use_gacha:
        while True:
            if all_targets_done():
                return _build_result(True, total_cash_spent, gacha_pulls, gacha_parts, part_info, state)

            # 목표 부위들 중에서 더 이상 행동 가능 여부 체크
            action_possible = False
            for part in target_parts:
                ps = state[part]
                if ps["legend"] >= 1:
                    continue
                if ps["epic"] >= 3 or ps["elite"] >= 3:
                    action_possible = True
                    break

            if not action_possible:
                return _build_result(False, total_cash_spent, gacha_pulls, gacha_parts, part_info, state)

            # 한 라운드: 목표 부위만 돌면서 승급 시도
            for part in target_parts:
                ps = state[part]

                if ps["legend"] >= 1:
                    continue

                # 에픽 → 전설
                if ps["epic"] >= 3:
                    total_cash_spent += COST_EPIC_TO_LEGEND
                    part_info[part]["legend_attempts"] += 1

                    if random.random() < PROB_EPIC_TO_LEGEND:
                        ps["epic"] -= 3
                        ps["legend"] += 1
                    else:
                        ps["epic"] -= 2
                    continue

                # 엘리트 → 에픽
                if ps["elite"] >= 3:
                    total_cash_spent += COST_ELITE_TO_EPIC
                    part_info[part]["epic_attempts"] += 1

                    if random.random() < PROB_ELITE_TO_EPIC:
                        ps["elite"] -= 3
                        ps["epic"] += 1
                    else:
                        ps["elite"] -= 2
                    continue

        # 고급/레어는 이 모드에서는 사용하지 않음

    # =========================
    # 가챠 ON 모드
    # =========================
    while True:
        if all_targets_done():
            return _build_result(True, total_cash_spent, gacha_pulls, gacha_parts, part_info, state)

        progress = False

        # 승급 가능한 건 다 우겨 넣기 (목표 부위만)
        for part in target_parts:
            ps = state[part]

            if ps["legend"] >= 1:
                continue

            # 에픽 → 전설
            while ps["epic"] >= 3 and ps["legend"] < 1:
                total_cash_spent += COST_EPIC_TO_LEGEND
                part_info[part]["legend_attempts"] += 1

                if random.random() < PROB_EPIC_TO_LEGEND:
                    ps["epic"] -= 3
                    ps["legend"] += 1
                else:
                    ps["epic"] -= 2

                progress = True
                if ps["legend"] >= 1:
                    break

            if ps["legend"] >= 1:
                continue

            # 엘리트 → 에픽
            while ps["elite"] >= 3:
                total_cash_spent += COST_ELITE_TO_EPIC
                part_info[part]["epic_attempts"] += 1

                if random.random() < PROB_ELITE_TO_EPIC:
                    ps["elite"] -= 3
                    ps["epic"] += 1
                else:
                    ps["elite"] -= 2

                progress = True

            # 레어 → 엘리트
            while ps["rare"] >= 3:
                if random.random() < PROB_RARE_TO_ELITE:
                    ps["rare"] -= 3
                    ps["elite"] += 1
                else:
                    ps["rare"] -= 2
                progress = True

            # 고급 → 레어
            while ps["common"] >= 3:
                if random.random() < PROB_COMMON_TO_RARE:
                    ps["common"] -= 3
                    ps["rare"] += 1
                else:
                    ps["common"] -= 2
                progress = True

        if all_targets_done():
            continue

        if not progress:
            # 가챠 1회
            total_cash_spent += COST_GACHA
            gacha_pulls += 1

            r = random.random()
            if r < GACHA_PROB_EPIC:
                rarity = "epic"
            elif r < GACHA_PROB_EPIC + GACHA_PROB_ELITE:
                rarity = "elite"
            elif r < GACHA_PROB_EPIC + GACHA_PROB_ELITE + GACHA_PROB_RARE:
                rarity = "rare"
            else:
                rarity = "common"

            # 가챠는 실제 게임처럼 전체 부위에 떨어진다고 가정
            part = random.choice(PARTS)
            state[part][rarity] += 1
            gacha_parts[part][rarity] += 1


def _build_result(success: bool,
                  cash: int,
                  gacha_pulls: int,
                  gacha_parts: dict,
                  part_info: dict,
                  state: dict) -> dict:
    return {
        "success": success,
        "cash": cash,
        "gacha_pulls": gacha_pulls,
        "gacha_parts": gacha_parts,
        "parts": {
            part: {
                "epic_attempts": part_info[part]["epic_attempts"],
                "legend_attempts": part_info[part]["legend_attempts"],
                "success": state[part]["legend"] >= 1,
            }
            for part in PARTS
        },
    }
