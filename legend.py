import random
import copy

# ===== 확률과 비용 설정 =====

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

PARTS = ["머리", "상의", "하의", "장갑"]


def simulate_one_run(start_state, use_gacha: bool):
    """
    start_state 예시:
    {
        "머리":  {"elite": 50, "epic": 0},
        "상의":  {"elite": 40, "epic": 0},
        "하의":  {"elite": 30, "epic": 0},
        "장갑":  {"elite": 40, "epic": 1},
    }

    use_gacha = False:
        - 입력한 엘리트/에픽만 사용.
        - 더 이상 어떤 승급도 못 하고, 4부위 전설이 아니면 실패.

    use_gacha = True:
        - 재료가 모자라서 승급을 더 못 하는 순간마다,
          패션 뽑기(가챠)를 1회 돌려 재료 수급.
        - 4부위 모두 전설이 될 때까지 계속 진행.
    """
    state = copy.deepcopy(start_state)

    # 각 부위 상태 초기화
    part_info = {}
    for part in PARTS:
        state[part].setdefault("common", 0)  # 고급
        state[part].setdefault("rare", 0)    # 레어
        state[part].setdefault("elite", 0)
        state[part].setdefault("epic", 0)
        state[part]["legend"] = 0

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

    def all_parts_done():
        return all(state[part]["legend"] >= 1 for part in PARTS)

    # =========================
    # 가챠 OFF 모드 (기존 로직)
    # =========================
    if not use_gacha:
        while True:
            # 1) 전설 4부위 완료면 전체 성공
            if all_parts_done():
                return {
                    "success": True,
                    "cash": total_cash_spent,
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

            # 2) 더 이상 어떤 행동도 가능한지 체크
            action_possible = False
            for part in PARTS:
                ps = state[part]
                if ps["legend"] >= 1:
                    continue
                if ps["epic"] >= 3 or ps["elite"] >= 3:
                    action_possible = True
                    break

            # 아무 행동도 못 하는데 전설 4부위가 아니면 실패
            if not action_possible:
                return {
                    "success": False,
                    "cash": total_cash_spent,
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

            # 3) 한 라운드: 각 부위를 한 번씩 돌면서 승급 시도
            for part in PARTS:
                ps = state[part]

                # 이미 전설 완성된 부위는 건너뜀
                if ps["legend"] >= 1:
                    continue

                # 우선순위 1: 에픽 3개 이상이면 전설 도전
                if ps["epic"] >= 3:
                    total_cash_spent += COST_EPIC_TO_LEGEND
                    part_info[part]["legend_attempts"] += 1

                    if random.random() < PROB_EPIC_TO_LEGEND:
                        # 성공: 에픽 3개 소모, 전설 1개 생성
                        ps["epic"] -= 3
                        ps["legend"] += 1
                    else:
                        # 실패: 에픽 2개만 소모, 1개는 남음
                        ps["epic"] -= 2

                    continue

                # 우선순위 2: 에픽 부족하면 엘리트로 에픽 만들기
                if ps["elite"] >= 3:
                    total_cash_spent += COST_ELITE_TO_EPIC
                    part_info[part]["epic_attempts"] += 1

                    if random.random() < PROB_ELITE_TO_EPIC:
                        # 성공: 엘리트 3개 소모, 에픽 1개 생성
                        ps["elite"] -= 3
                        ps["epic"] += 1
                    else:
                        # 실패: 엘리트 2개만 소모, 1개는 남음
                        ps["elite"] -= 2

                    continue

            # 고급/레어는 이 모드에서는 사용하지 않음

    # =========================
    # 가챠 ON 모드
    # =========================
    else:
        while True:
            # 1) 이미 다 만들었으면 성공
            if all_parts_done():
                return {
                    "success": True,
                    "cash": total_cash_spent,
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

            # 2) 현재 인벤토리로 할 수 있는 승급을 최대한 수행
            progress = False

            for part in PARTS:
                ps = state[part]

                if ps["legend"] >= 1:
                    continue  # 이미 전설이면 스킵

                # 2-1. 에픽 -> 전설 (전설 1개 만들 때까지)
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
                    continue  # 이 부위는 끝

                # 2-2. 엘리트 -> 에픽
                while ps["elite"] >= 3:
                    total_cash_spent += COST_ELITE_TO_EPIC
                    part_info[part]["epic_attempts"] += 1

                    if random.random() < PROB_ELITE_TO_EPIC:
                        ps["elite"] -= 3
                        ps["epic"] += 1
                    else:
                        ps["elite"] -= 2

                    progress = True

                # 2-3. 레어 -> 엘리트 (비용 없음)
                while ps["rare"] >= 3:
                    if random.random() < PROB_RARE_TO_ELITE:
                        ps["rare"] -= 3
                        ps["elite"] += 1
                    else:
                        ps["rare"] -= 2
                    progress = True

                # 2-4. 고급 -> 레어 (비용 없음)
                while ps["common"] >= 3:
                    if random.random() < PROB_COMMON_TO_RARE:
                        ps["common"] -= 3
                        ps["rare"] += 1
                    else:
                        ps["common"] -= 2
                    progress = True

            # 승급으로 뭔가 진행이 있었는지 확인
            if all_parts_done():
                continue  # while 맨 위에서 성공 처리됨

            if not progress:
                # 3) 더 이상 승급할 게 없으면 가챠 1회 돌려서 재료 수급
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
                    rarity = "common"  # 고급

                # 어떤 부위에 뜨는지는 균등 분배
                part = random.choice(PARTS)
                state[part][rarity] += 1
                gacha_parts[part][rarity] += 1
                # 이후 다시 while 루프를 돌며 승급 시도


def main():
    print("==== 전설 패션 시뮬레이터 (현금 기준) ====")
    print("각 부위별 현재 보유한 '에픽'과 '엘리트' 개수를 입력해주세요.")
    print("목표: 머리/상의/하의/장갑 전설 1개씩 만들기")
    print("실패 시 재료 1개는 남는 규칙이 적용되어 있습니다.")
    print()

    # 가챠 사용 여부
    use_gacha_input = input("추가 과금 패션 뽑기를 사용하시겠습니까? (y/N): ").strip().lower()
    use_gacha = use_gacha_input in ("y", "yes")

    if use_gacha:
        print("→ 가챠 모드: 부족한 재료는 패션 뽑기(2,000원/회)로 수급합니다.\n")
    else:
        print("→ 가챠 비사용 모드: 입력한 엘리트/에픽만 사용합니다.\n")

    start_state = {}
    for part in PARTS:
        while True:
            try:
                epic = int(input(f"{part} 에픽 개수: "))
                elite = int(input(f"{part} 엘리트 개수: "))
                if epic < 0 or elite < 0:
                    print("음수는 입력할 수 없습니다. 다시 입력해주세요.")
                    continue
                start_state[part] = {"epic": epic, "elite": elite}
                break
            except ValueError:
                print("숫자를 입력해주세요.")

    print()
    try:
        n_input = input("시뮬레이션 횟수 (기본값 30, 그냥 Enter): ").strip()
        num_runs = int(n_input) if n_input else 30
    except ValueError:
        num_runs = 30

    print(f"\n시뮬레이션 {num_runs}회 실행...\n")

    results = []
    success_cash = []
    fail_cash = []
    success_gacha_pulls = []
    fail_gacha_pulls = []

    for i in range(1, num_runs + 1):
        result = simulate_one_run(start_state, use_gacha)
        results.append(result)

        print(f"{i}회차:")

        for part in PARTS:
            pr = result["parts"][part]
            status = "성공" if pr["success"] else "실패"
            ea = pr["epic_attempts"]
            la = pr["legend_attempts"]
            print(f"{part}: 에픽승급도전횟수:{ea}, 전설승급도전횟수:{la} {status}")

        print(f"사용된 현금: {result['cash']:,.0f}원")

        # 가챠 모드일 때만 가챠 상세 출력
        if use_gacha:
            print(f"가챠 뽑기 횟수: {result['gacha_pulls']}회")
            gp = result["gacha_parts"]
            for part in PARTS:
                info = gp[part]
                print(
                    f"  {part} 가챠 획득 → "
                    f"고급:{info['common']}, 레어:{info['rare']}, "
                    f"엘리트:{info['elite']}, 에픽:{info['epic']}"
                )

        print()  # 빈 줄

        if result["success"]:
            success_cash.append(result["cash"])
            success_gacha_pulls.append(result["gacha_pulls"])
        else:
            fail_cash.append(result["cash"])
            fail_gacha_pulls.append(result["gacha_pulls"])

    # ===== 요약 출력 =====
    total_success = sum(1 for r in results if r["success"])
    total_fail = num_runs - total_success

    print("===== 요약 =====")
    print(f"총 시뮬레이션 횟수: {num_runs}회")
    print(f"성공: {total_success}회, 실패: {total_fail}회")

    if success_cash:
        avg_cash = sum(success_cash) / len(success_cash)
        min_cash = min(success_cash)
        max_cash = max(success_cash)
        print("\n[성공한 경우 기준 현금 사용량]")
        print(f"  평균: {avg_cash:,.0f}원")
        print(f"  최소: {min_cash:,.0f}원")
        print(f"  최대: {max_cash:,.0f}원")
    else:
        print("\n성공한 시뮬레이션이 없습니다.")

    if fail_cash:
        avg_fail_cash = sum(fail_cash) / len(fail_cash)
        min_fail_cash = min(fail_cash)
        max_fail_cash = max(fail_cash)
        print("\n[실패한 경우 기준 현금 사용량]")
        print(f"  평균: {avg_fail_cash:,.0f}원")
        print(f"  최소: {min_fail_cash:,.0f}원")
        print(f"  최대: {max_fail_cash:,.0f}원")
    else:
        print("\n실패한 시뮬레이션이 없습니다.")

    if use_gacha:
        if success_gacha_pulls:
            avg_gp = sum(success_gacha_pulls) / len(success_gacha_pulls)
            min_gp = min(success_gacha_pulls)
            max_gp = max(success_gacha_pulls)
            print("\n[성공한 경우 기준 가챠 뽑기 횟수]")
            print(f"  평균: {avg_gp:,.1f}회")
            print(f"  최소: {min_gp}회")
            print(f"  최대: {max_gp}회")

        if fail_gacha_pulls:
            avg_fail_gp = sum(fail_gacha_pulls) / len(fail_gacha_pulls)
            min_fail_gp = min(fail_gacha_pulls)
            max_fail_gp = max(fail_gacha_pulls)
            print("\n[실패한 경우 기준 가챠 뽑기 횟수]")
            print(f"  평균: {avg_fail_gp:,.1f}회")
            print(f"  최소: {min_fail_gp}회")
            print(f"  최대: {max_fail_gp}회")


if __name__ == "__main__":
    main()
