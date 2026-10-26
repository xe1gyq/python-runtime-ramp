import argparse

from pyramp import data, registry, roi, validation
from pyramp.benchmarks.dot import reference


def parser():
    p = argparse.ArgumentParser(description="Python runtime mechanism workload")
    p.add_argument("--benchmark", choices=("dot",), required=True)
    p.add_argument("--impl", choices=registry.IMPLEMENTATIONS, required=True)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--iterations", type=int, required=True)
    p.add_argument("--warmup", type=int, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--dtype", choices=("float64",), required=True)
    p.add_argument("--dry-run", action="store_true")
    return p


def plan(args):
    return f"""PYTHON RUNTIME RAMP — EXPERIMENT PLAN

Benchmark
  {args.benchmark}

Implementation
  {args.impl}

Parameters
  N:          {args.n}
  dtype:      {args.dtype}
  seed:       {args.seed}
  warmup:     {args.warmup}
  iterations: {args.iterations}

OUTSIDE ROI
  generate deterministic logical inputs
  prepare implementation representation
  calculate reference
  preflight correctness check
  warmup x{args.warmup}

ROI
  ROI_BEGIN
  dot kernel x{args.iterations}
  ROI_END

AFTER ROI
  no required experimental work

Dry run only. No kernel executed.
"""


def execute(args):
    logical_a, logical_b = data.generate(args.n, args.seed, args.dtype)
    kernel, a, b = registry.prepare(args.impl, logical_a, logical_b)
    expected = reference.dot(logical_a, logical_b)
    validation.verify(kernel(a, b), expected)
    for _ in range(args.warmup):
        result = kernel(a, b)
    # Discard staging lists for native representations before entering ROI.
    del logical_a, logical_b, expected
    repetitions = range(args.iterations)
    roi.begin()
    for _ in repetitions:
        result = kernel(a, b)
    roi.end()
    return result


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    if args.n <= 0:
        p.error("--n must be positive")
    if args.iterations <= 0:
        p.error("--iterations must be positive")
    if args.warmup < 0:
        p.error("--warmup must be nonnegative")
    if args.dry_run:
        print(plan(args), end="")
        return 0
    execute(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
