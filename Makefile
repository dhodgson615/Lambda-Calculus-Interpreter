.PHONY: all venv deps typecheck lint build test clean install

PYTHON = .venv/bin/python
PIP    = .venv/bin/pip
MYPY   = .venv/bin/mypy
FLAKE8 = .venv/bin/flake8
PYTEST = .venv/bin/pytest
BLACK  = .venv/bin/black

all: venv deps lint typecheck build test

venv:
	@test -d .venv || python3 -m venv .venv

deps: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install mypy setuptools types-setuptools flake8 pytest

typecheck: venv
	$(MYPY) src/

lint: venv
	$(FLAKE8) src/

format:
	$(BLACK) -l79 src/

build: venv
	$(PYTHON) src/setup.py build_ext --inplace

test: venv
	$(PYTEST) src/

benchmark: venv
	$(PYTEST) src/ --benchmark-only --benchmark-columns=min,mean,max,stddev,rounds,iterations

clean:
	rm -rf build/ dist/ *.egg-info .mypy_cache .pytest_cache
	rm -rf *.so *.c src/*.so src/*.c src/__pycache__/

install: venv deps
	$(PIP) install .
