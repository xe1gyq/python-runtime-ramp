"""Only ROI integration point.

Local text markers; no external ROI API is configured.
Marker output is flushed immediately. It is not a hardware measurement hook.
"""

def begin() -> None:
    print("ROI Begin", flush=True)


def end() -> None:
    print("ROI End", flush=True)
