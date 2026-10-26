from setuptools import Extension, setup
from Cython.Build import cythonize

names = ("cython_untyped_list", "cython_typed_loop_list", "cython_native_buffer")
setup(ext_modules=cythonize(
    [Extension(f"pyramp.benchmarks.dot.{name}",
               [f"src/pyramp/benchmarks/dot/{name}.pyx"],
               extra_compile_args=["-O2", "-fno-fast-math", "-ffp-contract=off"])
     for name in names],
    compiler_directives={"language_level": 3, "infer_types": False},
))
