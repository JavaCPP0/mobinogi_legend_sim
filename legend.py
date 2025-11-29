import random
import copy

# 확률과 비용 설정
PROB_ELITE_TO_EPIC = 0.25   # 엘리트 3개 -> 에픽 1개 성공 확률
PROB_EPIC_TO_LEGEND = 0.20  # 에픽 3개 -> 전설 1개 성공 확률

COST_ELITE_TO_EPIC = 500    # 엘리트 3개 합성 시도당 현금
COST_EPIC_TO_LEGEND = 3000  # 에픽 3개 합성 시도당 현금

PARTS = ["머리", "상의", "하의", "장갑"]


def simulate_one_run(start_state):
    """
    start_state 예시:
    {
        "머리":  {"elite": 50, "epic": 0},
        "상의":  {"elite": 40, "epic": 0},
        "하의":  {"elite": 30, "epic": 0},
        "장갑":  {"elite": 40, "epic": 1},
    }

    - 엘리트는 입력한 개수까지만 사용 가능 (추가 구매 없음)
    - 3개 합성 규칙:
        성공: 하위 재료 3개 소모, 상위 1개 생성
        실패: 하위 재료 2개만 소모, 1개는 남음
    - 에픽/엘리트가 부족해서 더 이상 합성을 못 하는 순간 종료
    - 4부위 전설 1개씩이면 전체 성공, 아니면 실패
    """
    state = copy.deepcopy(start_state)

    # 각 부위 전설 개수 및 시도 횟수 기록
    part_info = {}
    for part in PARTS:
        state[part]["legend"] = 0
        part_info[part] = {
            "epic_attempts": 0,    # 엘리트 -> 에픽 시도 횟수
            "legend_attempts": 0,  # 에픽 -> 전설 시도 횟수
        }

    total_cash_spent = 0

    def all_parts_done():
        return all(state[part]["legend"] >= 1 for part in PARTS)

    while True:
        # 1) 전설 4부위 완료면 전체 성공
        if all_parts_done():
            return {
                "success": True,
                "cash": total_cash_spent,
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
                "parts": {
                    part: {
                        "epic_attempts": part_info[part]["epic_attempts"],
                        "legend_attempts": part_info[part]["legend_attempts"],
                        "success": state[part]["legend"] >= 1,
                    }
                    for part in PARTS
                },
            }

        # 3) 한 라운드: 각 부위를 한 번씩 돌면서 합성 시도
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

                # 이 부위는 이번 라운드에서 1번만 시도
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

            # 엘리트 < 3, 에픽 < 3 이면 이 부위는 이번 라운드에서 할 게 없음
            # 다음 while 반복에서 전체 상태를 다시 체크


def main():
    print("==== 전설 패션 시뮬레이터 (현금 기준) ====")
    print("각 부위별 현재 보유한 '에픽'과 '엘리트' 개수를 입력해주세요.")
    print("목표: 머리/상의/하의/장갑 전설 1개씩 만들기")
    print("엘리트는 입력하신 수량까지만 사용할 수 있고, 떨어지면 더 이상 합성을 못 합니다.")
    print("실패 시 재료 1개는 남는 규칙이 적용되어 있습니다.")
    print()

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

    for i in range(1, num_runs + 1):
        result = simulate_one_run(start_state)
        results.append(result)

        print(f"{i}회차:")

        for part in PARTS:
            pr = result["parts"][part]
            status = "성공" if pr["success"] else "실패"
            ea = pr["epic_attempts"]
            la = pr["legend_attempts"]
            print(f"{part}: 에픽승급도전횟수:{ea}, 전설승급도전횟수:{la} {status}")

        print(f"사용된 현금: {result['cash']:,.0f}원\n")

        if result["success"]:
            success_cash.append(result["cash"])

    # 요약
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
        print("\n성공한 시뮬레이션이 없습니다. (엘리트 수량이 4부위 전설 완성에는 부족할 수 있습니다.)")


if __name__ == "__main__":
    main()
