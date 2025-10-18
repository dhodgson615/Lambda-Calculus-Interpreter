.PHONY: all venv deps typecheck lint build test clean install

PIP    = .venv/bin/pip
MYPY   = .venv/bin/mypy
FLAKE8 = .venv/bin/flake8
BLACK  = .venv/bin/black
ISORT  = .venv/bin/isort
PYTHON = .venv/bin/python
PYTEST = .venv/bin/pytest

all: venv deps lint typecheck build test

venv:
	@test -d .venv || python3 -m venv .venv

deps: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install mypy setuptools types-setuptools flake8 pytest

typecheck: venv
	$(MYPY) --strict src/

lint: venv
	$(MYPY) --strict src/
	$(FLAKE8) src/

format:
	$(BLACK) -l79 src/
	$(ISORT) src/

build: venv
	$(PYTHON) src/setup.py build_ext --inplace
	mv -f *.so src/ 2>/dev/null || true

test: venv
	$(PYTEST) src/

benchmark: venv
	$(PYTEST) src/ --benchmark-only --benchmark-columns=min,mean,max,stddev,rounds,iterations

clean:
	rm -rf build/ dist/ *.egg-info .mypy_cache .pytest_cache
	rm -rf *.so *.c src/*.so src/*.c src/__pycache__/

install: venv deps
	$(PIP) install .
