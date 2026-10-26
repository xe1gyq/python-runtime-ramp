# Verification record

Environment date: 2026-10-26. Local Python 3.12.14, NumPy 2.3.5.
No remote repository was created or configured.

## Passed locally

- Nine correctness comparisons against math.fsum: cpython-list,
  cpython-annotated-list and numpy-dot at (N, seed) = (1, 0), (17, 42),
  (257, -3).
- Three small real CLI executions, one for each available implementation:
  N=1024, iterations=10, warmup=2, seed=42, dtype=float64.
- AST comparison confirms the CPython functions differ only in annotations.
- Instrumented exact order: generate, prepare, reference, preflight kernel,
  validate, two warmup kernels, begin, four measured kernels, end.
- Seven CLI rejection cases: unknown implementation, N zero/negative,
  iterations zero/negative, negative warmup, unsupported dtype.
- Dry run completed with execution and ROI functions replaced by failing
  sentinels: none were called.

These were direct Python assertions using standard-library unittest.mock.
They do not constitute a complete pytest run.

## Not verified in this environment

The complete pytest suite and the three Cython extensions could not be run:
Cython and pytest are absent. The attempted dependency install was blocked by
sandbox proxy access (operation not permitted); the additional network permission
request was interrupted before execution. No dependency install succeeded.

Docker build was attempted:

    docker build -t python-runtime-ramp .

It failed before building because /home/agent/.docker/buildx is read-only.
An explicit managed-daemon health check also failed with operation not permitted
on /var/run/docker.sock. The request for additional socket access was interrupted.
No Docker image was built, and no Docker run or in-image extension import has
been verified. No automatic approval rejection was received; permission requests
were interrupted.

Dockerfile includes the full offline pytest suite during build, including tests
that import all three compiled extensions and select all six CLI implementations.
Run the commands in README.md once Docker and build network access are available.
The Cython-native Docker command is documented, not claimed to have succeeded.

## Actual dry-run output

    PYTHON RUNTIME RAMP — EXPERIMENT PLAN

    Benchmark
      dot

    Implementation
      cpython-list

    Parameters
      N:          4096
      dtype:      float64
      seed:       42
      warmup:     3
      iterations: 100

    OUTSIDE ROI
      generate deterministic logical inputs
      prepare implementation representation
      calculate reference
      preflight correctness check
      warmup x3

    ROI
      ROI_BEGIN
      dot kernel x100
      ROI_END

    AFTER ROI
      no required experimental work

    Dry run only. No kernel executed.

## Small real-run commands executed locally

    PYTHONPATH=src python -m pyramp.cli --benchmark dot --impl cpython-list --n 1024 --iterations 10 --warmup 2 --seed 42 --dtype float64
    PYTHONPATH=src python -m pyramp.cli --benchmark dot --impl cpython-annotated-list --n 1024 --iterations 10 --warmup 2 --seed 42 --dtype float64
    PYTHONPATH=src python -m pyramp.cli --benchmark dot --impl numpy-dot --n 1024 --iterations 10 --warmup 2 --seed 42 --dtype float64

All three completed successfully (silent, status 0).
ROI is currently no-op in src/pyramp/roi.py.
