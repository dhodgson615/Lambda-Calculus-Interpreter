from mypyc.build import mypycify
from setuptools import setup

setup(
    name="lambda_calculus_interpreter",
    ext_modules=mypycify(["src/main.py"]),
)
