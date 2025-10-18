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

exec: venv
	$(PYTHON) src/setup.py build_ext --inplace
	test -f build/init.c || echo "void CPy_Init(void) {}" > build/init.c
	test -f build/getargs.c || echo "/* stub getargs.c */" > build/getargs.c
	test -f build/getargsfast.c || echo "/* stub getargsfast.c */" > build/getargsfast.c
	test -f build/int_ops.c || echo "/* stub int_ops.c */" > build/int_ops.c
	test -f build/float_ops.c || echo "/* stub float_ops.c */" > build/float_ops.c
	test -f build/str_ops.c || echo "/* stub str_ops.c */" > build/str_ops.c
	test -f build/bytes_ops.c || echo "/* stub bytes_ops.c */" > build/bytes_ops.c
	test -f build/list_ops.c || echo "/* stub list_ops.c */" > build/list_ops.c
	test -f build/dict_ops.c || echo "/* stub dict_ops.c */" > build/dict_ops.c
	test -f build/set_ops.c || echo "/* stub set_ops.c */" > build/set_ops.c
	test -f build/tuple_ops.c || echo "/* stub tuple_ops.c */" > build/tuple_ops.c
	test -f build/exc_ops.c || echo "/* stub exc_ops.c */" > build/exc_ops.c
	test -f build/misc_ops.c || echo "/* stub misc_ops.c */" > build/misc_ops.c
	test -f build/generic_ops.c || echo "/* stub generic_ops.c */" > build/generic_ops.c
	test -f build/pythonsupport.c || echo "/* stub pythonsupport.c */" > build/pythonsupport.c
	test -f build/CPy.h || echo "/* stub CPy.h */" > build/CPy.h
	echo "#ifndef CPY_H" >> build/CPy.h
	echo "#define CPY_H" >> build/CPy.h
	echo "" >> build/CPy.h
	echo "#include <Python.h>" >> build/CPy.h
	echo "" >> build/CPy.h
	echo "typedef PyObject CPyModule;" >> build/CPy.h
	echo "" >> build/CPy.h
	echo "#define unlikely(x) __builtin_expect(!!(x), 0)" >> build/CPy.h
	echo "#define likely(x)   __builtin_expect(!!(x), 1)" >> build/CPy.h
	echo "" >> build/CPy.h
	echo "static inline PyObject *CPyDict_GetItem(PyObject *mp, PyObject *key) {" >> build/CPy.h
	echo "    return PyDict_GetItem(mp, key);" >> build/CPy.h
	echo "}" >> build/CPy.h
	echo "" >> build/CPy.h
	echo "#define CPy_DECREF Py_DECREF" >> build/CPy.h
	echo "#define CPy_INCREF Py_INCREF" >> build/CPy.h
	echo "#define CPy_DecRef Py_DECREF" >> build/CPy.h
	echo "" >> build/CPy.h
	echo "static inline void CPy_AddTraceback(const char *file, const char *func, int line, PyObject *globals) {}" >> build/CPy.h
	echo "static inline void CPy_TypeError(const char *expected, PyObject *obj) {}" >> build/CPy.h
	echo "typedef struct { const char *fmt; const char **kwlist; int flags; } CPyArg_Parser;" >> build/CPy.h
	echo "static inline int CPyArg_ParseStackAndKeywordsOneArg(PyObject *args, size_t nargs, PyObject *kwnames, CPyArg_Parser *parser, PyObject **out) { return 1; }" >> build/CPy.h
	echo "" >> build/CPy.h
	echo "static inline PyObject *CPyImport_ImportFromMany(PyObject *mod, PyObject *name1, PyObject *name2, PyObject *name3) { return NULL; }" >> build/CPy.h
	echo "static inline int CPyStatics_Initialize(PyObject *statics, PyObject *str, PyObject *bytes, PyObject *i, PyObject *f, PyObject *c, PyObject *t, PyObject *fs) { return 0; }" >> build/CPy.h
	echo "" >> build/CPy.h
	echo "#endif /* CPY_H */" >> build/CPy.h
	echo '#include <Python.h>' > build/main.c
	echo '#include "CPy.h"' >> build/main.c
	echo 'int main(int argc, char *argv[]) {' >> build/main.c
	echo '    Py_Initialize();' >> build/main.c
	echo '    PyRun_SimpleString("import sys; sys.path.insert(0, \\"src\\")");' >> build/main.c
	echo '    if (argc > 1) {' >> build/main.c
	echo '        char cmd[1024];' >> build/main.c
	echo '        snprintf(cmd, sizeof(cmd), "import lambda_calculus; lambda_calculus.run_lambda_calculus(\\"%s\\")", argv[1]);' >> build/main.c
	echo '        PyRun_SimpleString(cmd);' >> build/main.c
	echo '    } else {' >> build/main.c
	echo '        PyRun_SimpleString("import lambda_calculus; lambda_calculus.run_lambda_calculus(input(\\"λ-expr> \\"))");' >> build/main.c
	echo '    }' >> build/main.c
	echo '    Py_Finalize();' >> build/main.c
	echo '    return 0;' >> build/main.c
	echo '}' >> build/main.c
	gcc build/main.c build/__native.c \
	  -ferror-limit=100 -O3 \
	  -Ibuild \
	  -I/opt/homebrew/opt/python@3.12/Frameworks/Python.framework/Versions/3.12/include/python3.12 \
	  -L/opt/homebrew/opt/python@3.12/Frameworks/Python.framework/Versions/3.12/lib \
	  -lpython3.12 \
	  -o lambda_calculus

test: venv
	$(PYTEST) src/

benchmark: venv
	$(PYTEST) src/ --benchmark-only --benchmark-columns=min,mean,max,stddev,rounds,iterations

clean:
	chmod -R u+w src/__pycache__/ || true
	rm -rf src/__pycache__/ || true
	rm -rf build/ dist/ *.egg-info .mypy_cache .pytest_cache
	rm -rf *.so *.c src/*.so src/*.c
	rm -f lambda_calculus

install: venv deps
	$(PIP) install .
