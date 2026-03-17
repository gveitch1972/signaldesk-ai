def test_smoke():
    import src.app
    assert src.app is not None


def main() -> None:
    test_smoke()
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
