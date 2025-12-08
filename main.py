# main.py
import re
from config import PARTS
from simulation import simulate_one_run


def ask_target_parts():
    print("어느 부위의 전설을 새로 노리실 건가요?")
    print(f"선택 가능한 부위: {', '.join(PARTS)}")
    print("쉼표(,) 또는 공백으로 구분해서 입력해주세요.")
    print("예시) 상의, 하의  또는  상의 하의")
    print("아무것도 입력하지 않고 Enter를 누르면 4부위 전부를 목표로 합니다.\n")

    raw = input("전설 목표 부위 입력: ").strip()

    if not raw:
        # 전체 부위를 목표로
        return None

    tokens = [t.strip() for t in re.split(r"[,\s]+", raw) if t.strip()]
    targets = []
    for t in tokens:
        if t in PARTS:
            if t not in targets:
                targets.append(t)
        else:
            print(f"경고: '{t}' 는 부위 목록에 없습니다. 무시합니다.")

    if not targets:
        print("유효한 부위가 없어 전체 부위를 목표로 설정합니다.\n")
        return None

    print(f"→ 이번 시뮬레이션의 목표 부위: {', '.join(targets)}\n")
    return targets


def main():
    print("==== 전설 패션 시뮬레이터 (현금 기준) ====")
    print("각 부위별 현재 보유한 '에픽'과 '엘리트' 개수를 입력해주세요.")
    print("실패 시 재료 1개는 남는 규칙이 적용되어 있습니다.")
    print("이미 전설을 보유한 부위는 '목표 부위'에서 제외하면 됩니다.\n")

    # 가챠 사용 여부
    use_gacha_input = input("추가 과금 패션 뽑기를 사용하시겠습니까? (y/N): ").strip().lower()
    use_gacha = use_gacha_input in ("y", "yes")

    if use_gacha:
        print("→ 가챠 모드: 부족한 재료는 패션 뽑기(2,000원/회)로 수급합니다.\n")
    else:
        print("→ 가챠 비사용 모드: 입력한 엘리트/에픽만 사용합니다.\n")

    # 목표 부위 입력
    target_parts = ask_target_parts()

    # 초기 보유 상태 입력 (4부위 모두 입력은 그대로 유지)
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
        result = simulate_one_run(start_state, use_gacha, target_parts)
        results.append(result)

        print(f"{i}회차:")

        for part in PARTS:
            pr = result["parts"][part]
            status = "성공" if pr["success"] else "실패"
            ea = pr["epic_attempts"]
            la = pr["legend_attempts"]
            print(f"{part}: 에픽승급도전횟수:{ea}, 전설승급도전횟수:{la} {status}")

        print(f"사용된 현금: {result['cash']:,.0f}원")

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

        print()

        if result["success"]:
            success_cash.append(result["cash"])
            success_gacha_pulls.append(result["gacha_pulls"])
        else:
            fail_cash.append(result["cash"])
            fail_gacha_pulls.append(result["gacha_pulls"])

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
