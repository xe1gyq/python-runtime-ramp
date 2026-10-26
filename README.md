# python-runtime-ramp

Owner: **xe1gyq**. Repository: https://github.com/xe1gyq/python-runtime-ramp

**Docker defines the workload. The external measurement environment defines how it is observed.**

This single image provides a deterministic, parameterized dot product workload:
dot(a, b) = sum(a[i] * b[i] for i in range(N)).
An external execution and measurement environment runs the image through
ordinary Docker execution. There is no simulator backend, platform abstraction,
EMON, perf, VTune, PMU collection, checkpoint logic, or platform configuration here.

## Research model

    IMPLEMENTATION
          ↓
    EXECUTION MECHANISMS
          ↓
    WORKLOAD BEHAVIOR
          ↓
    EXTERNAL OBSERVATION
          ↓
    MICROARCHITECTURAL SIGNATURE

Workload behavior derives from objects, dynamic operations, interpreter dispatch,
reference counting, pointer-heavy layouts, native scalars, contiguous buffers,
and native/vectorized kernels. This repository creates those mechanisms.

The external measurement environment observes their microarchitectural signatures. Depending on the flow
and target, observations might include instructions, cycles, IPC, branches,
branch misses, MPKI, cache behavior, bandwidth, Top-Down categories, or instruction
mix. This is an illustrative list, not a fixed measurement contract.

The objective is: **Which Python/runtime mechanisms produce which hardware
pressures, and how do those pressures respond to different microarchitectures?**
It goes beyond asking which implementation is fastest.

## Level 0: mechanism ladder

| CLI implementation | Representation | Hot loop and arithmetic |
|---|---|---|
| cpython-list | list of Python float objects | Explicit indexed Python loop; Python multiply/add, dispatch, refcounts |
| cpython-annotated-list | Identical list of float objects | Identical algorithm with ordinary annotations only: negative control |
| cython-untyped-list | Same Python lists/objects | Compiled Cython control; untyped locals, Python object arithmetic |
| cython-typed-loop-list | Same Python lists/objects | Native index/length/double accumulator; list access and multiplication still interact with Python objects; product converts to double |
| cython-native-buffer | Contiguous native float64 buffer via array('d') and memoryview | Typed double loads, multiply/add and native loop; no per-element Python arithmetic |
| numpy-dot | Contiguous NumPy float64 arrays | numpy.dot delegates the loop to a native library kernel |

Annotations do not produce native C data. Cython compilation alone does not
remove all Python-object mechanisms. Cython can optimize iteration/control even
in the untyped stage; inferred native local types are explicitly disabled.
The typed-list stage retains Python multiplication deliberately.
The native-buffer stage changes **both execution semantics and physical data
representation**. Its length check, Python call wrapper, memoryview binding, and
boxed return remain per call; the element loop uses native doubles. It retains
the GIL. NumPy introduces library dispatch and its build-selected kernel.

## Level 1: N and repeated execution

N controls logical/physical working-set size; physical size differs between
lists and native buffers. There are no assumed cache capacities or platform
regimes. The mapping from N to cache-resident or memory-system regimes belongs
to external platform analysis.

**Increasing "iterations" while keeping N fixed can increase temporal reuse and
therefore change the cache behavior. "iterations" extends the ROI but is not
guaranteed to preserve the exact microarchitectural signature.**

Treat N and iterations as independent experimental knobs. Warmup does not
eliminate every cold-state effect. Preflight itself also touches the data.

## Execution contract

1. Parse and validate CLI parameters.
2. Generate one logical pair using a local seeded Python PRNG.
3. Prepare the selected physical representation and import its kernel.
4. Calculate a trusted math.fsum reference.
5. Run the exact selected kernel once and validate (relative tolerance 1e-10,
   absolute tolerance 1e-12); fail before ROI on mismatch.
6. Warm up the same kernel and prepared data the requested number of times.
7. Release staging references and prepare the repetition range.
8. Call roi.begin(), execute the kernel iterations times, call roi.end().
9. No required experimental work follows the end marker.

Inputs are positive dyadic float64 values: randrange(1,1025)/1024.0.
All implementations receive exactly the same logical values for N/seed/dtype.
Products are exactly representable; math.fsum provides a stable independent
accumulation reference. There is no input allocation/conversion within ROI.
Python result objects and arithmetic allocations intrinsic to an implementation
are intentional workload mechanisms. Results remain assigned to a live local.

All ROI marker code lives in **src/pyramp/roi.py**, exposing only begin()/end().
It currently emits **local text markers**, `ROI Begin` and `ROI End`,
with immediate stdout flushing. No external marker adapter is configured.
These two bodies are the only future integration point; use only verified
APIs supplied by the chosen execution environment. The dry-run plan
contains textual marker labels but never calls the marker functions.

No production execution timing, hardware counters, CPU inspection, correctness
checks, reference calculation, JSON serialization, or printing occurs in the
repeated workload section. The marker functions print at the boundaries; their
I/O adds boundary overhead and is not a hardware measurement hook.
Successful real runs print `ROI Begin` followed by `ROI End` and return exit status 0.

## Build and run

Docker compiles all three Cython extensions during build and runs the offline
test suite, including compiled-extension imports. No runtime compiler/network
access is required.

    docker build -t python-runtime-ramp .

In managed environments with a TLS proxy, supply its trusted combined bundle:

    docker build --secret id=proxy_ca,src=/etc/ssl/certs/ca-certificates.crt -t python-runtime-ramp .

Dry run (no kernel execution or data generation):

    docker run --rm python-runtime-ramp \
      --benchmark dot --impl cpython-list --n 4096 \
      --iterations 100 --warmup 3 --seed 42 --dtype float64 --dry-run

Small runs:

    docker run --rm python-runtime-ramp \
      --benchmark dot --impl cpython-list --n 1024 \
      --iterations 10 --warmup 2 --seed 42 --dtype float64

    docker run --rm python-runtime-ramp \
      --benchmark dot --impl cython-native-buffer --n 1024 \
      --iterations 10 --warmup 2 --seed 42 --dtype float64

    docker run --rm python-runtime-ramp \
      --benchmark dot --impl numpy-dot --n 1024 \
      --iterations 10 --warmup 2 --seed 42 --dtype float64

Only float64 is supported; unsupported dtype, implementation or benchmark names
and invalid counts fail explicitly. N/iterations must be positive; warmup may
be zero. Seed is any Python integer. Large N is bounded by available memory.

Local development:

    python -m venv .venv
    .venv/bin/python -m pip install Cython==3.1.2 setuptools==80.9.0 wheel==0.45.1
    .venv/bin/python -m pip install --no-build-isolation -e '.[test]'
    .venv/bin/python -m pytest -q

## Reproducibility and confounders

Image: CPython 3.12.12 on bookworm; NumPy 2.3.5; Cython 3.1.2;
setuptools 80.9.0; wheel 0.45.1; pip 25.3; pytest 8.4.2.
The image disables pip update notices because its pip version is deliberately
pinned; this does not suppress installation errors.
Build metadata in /usr/local/share/pyramp records exact installed Python packages,
Python/compiler versions and NumPy build configuration. The base tag and OS
packages are not digest-locked: this is a pinned application recipe, not a
promise of byte-identical rebuilds. Archive the resulting image digest for
experiments. Transitive test dependencies are recorded at build time.

Compiler flags are -O2 -fno-fast-math -ffp-contract=off, without target-specific
ISA selection. NumPy's kernel dispatch, BLAS implementation, SIMD, reduction
order, Python/Cython versions, allocator behavior, result boxing, call overhead,
GIL behavior, and retained input representation all affect interpretation.
The positive bounded input distribution is intentionally simple and does not
explore cancellation, exceptional values, or general numerical conditioning.

The outer iterations loop remains Python for every implementation. Its overhead
can dominate very small N. The Docker defaults request one BLAS/OpenMP thread
using OPENBLAS_NUM_THREADS, OMP_NUM_THREADS and MKL_NUM_THREADS; record overrides.
Repeated calls can change cache state and runtime state. Preparation/reference
temporarily retain logical and converted arrays, so peak process memory exceeds
the active kernel working set. Allocator retention can persist after staging
references are released. No cache flushing, affinity policy, or cache-capacity
mapping is imposed here.

## Files

    Dockerfile, .dockerignore, pyproject.toml, setup.py, .gitignore
    src/pyramp/{cli,registry,data,validation,roi}.py
    src/pyramp/benchmarks/dot/reference.py
    src/pyramp/benchmarks/dot/cpython_list.py
    src/pyramp/benchmarks/dot/cpython_annotated_list.py
    src/pyramp/benchmarks/dot/cython_untyped_list.pyx
    src/pyramp/benchmarks/dot/cython_typed_loop_list.pyx
    src/pyramp/benchmarks/dot/cython_native_buffer.pyx
    src/pyramp/benchmarks/dot/numpy_dot.py
    tests/{conftest,test_correctness,test_cli,test_dry_run,
           test_roi_boundaries,test_implementations}.py
    README.md, VERIFICATION.md

Package directories also contain __init__.py.

## Future levels — documentation only

- Level 2: parameter sweeps and normalized signatures.
- Level 3: RAMP reduced-anchor validation.
- Level 4: externally managed checkpoint generation.
- Level 5: externally managed comparisons across hardware generations.

The Docker workload and ROI contract should survive these stages.
No simulator abstraction is implemented.
