.PHONY: all sort update

all: sort update postprocess

combine:
    PYTHONPATH=. python combine.py

postprocess:
    PYTHONPATH=. python postprocess.py

sort:
    PYTHONPATH=. python sort.py

test:
    PYTHONPATH=. python crossings_test.py
    PYTHONPATH=. python grid_test.py
    PYTHONPATH=. python grids_test.py
    PYTHONPATH=. python tags_test.py
