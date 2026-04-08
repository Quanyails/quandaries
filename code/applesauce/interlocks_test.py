from interlocks import find_interlocks, main

# Crossword taken from: https://www.crosserville.com/archive/puzzle/40715
def test_trunked():
    main(
        words=["AMBULANCECHASER", "ACCESSCODE", "ALLEYCAT", "ALCAPONE", "ALARMCLOCK", "AREACLOSED", "ALBUMCOVER"],
    )

def test_untrunked():
    main(
        words=["CRISSANGEL", "CROSSCHECK", "FIONAAPLLE", "ONTHESAUCE"],
    )

if __name__ == "__main__":
    # test_trunked()
    # test_untrunked()
