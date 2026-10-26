# syntax=docker/dockerfile:1
FROM python:3.12.12-bookworm
LABEL org.opencontainers.image.title="python-runtime-ramp" \
      org.opencontainers.image.authors="xe1gyq" \
      io.pyramp.python="3.12.12" \
      io.pyramp.numpy="2.3.5" \
      io.pyramp.cython="3.1.2"
ENV OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY . .
# Optional combined trust bundle for managed proxy environments; never persisted.
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    python -m pip install --no-cache-dir pip==25.2 setuptools==80.9.0 wheel==0.45.1 Cython==3.1.2 && \
    python -m pip install --no-cache-dir --no-build-isolation '.[test]' && \
    python -m pytest -q && \
    mkdir -p /usr/local/share/pyramp && \
    python -m pip freeze --all > /usr/local/share/pyramp/python-packages.txt && \
    python -VV > /usr/local/share/pyramp/python-version.txt && \
    gcc --version > /usr/local/share/pyramp/compiler-version.txt && \
    python -c "import numpy; numpy.show_config()" > /usr/local/share/pyramp/numpy-config.txt
ENTRYPOINT ["pyramp"]
