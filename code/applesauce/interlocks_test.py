from interlocks import find_interlocks, main

def test_trunks_only():
    main(
        words=["XXAXX", "YAY"],
    )

def test_pair():
    main(
        words=["XXAXX", "YYAYY"],
    )

# Crossword taken from: https://www.crosserville.com/archive/puzzle/40715
def test_trunks_and_branches():
    main(
        words=["AMBULANCECHASER", "ACCESSCODE", "ALLEYCAT", "ALCAPONE", "ALARMCLOCK", "AREACLOSED", "ALBUMCOVER"],
    )

def test_branches():
    main(
        words=["CRISSANGEL", "CROSSCHECK", "FIONAAPLLE", "ONTHESAUCE"],
    )

if __name__ == "__main__":
    test_trunks_only()
    test_pair()
    # test_trunks_and_branches()
    # test_branches()
