from src.queries.market import load_market_stress
from src.queries.fx import load_fx_watchlist
from src.queries.macro import load_macro_trends
from src.queries.regime import load_latest_regime


def main() -> None:
    print("REGIME")
    print(load_latest_regime())

    print("\nMARKET")
    print(load_market_stress())

    print("\nFX")
    print(load_fx_watchlist())

    print("\nMACRO")
    print(load_macro_trends())


if __name__ == "__main__":
    main()
