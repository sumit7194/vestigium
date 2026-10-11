"""Environment stamp for reproducibility (fleet policy 2026-10-11; adapted from TheBridge 243ec82, extended to this
repo's native stack). Usage: python tools/envstamp.py [out.json]   |   import envstamp; envstamp.stamp() -> dict
Covers: interpreter, platform and macOS version, Python packages, the numpy/scipy BLAS/LAPACK backend, git commit;
NATIVE: rustc/cargo and the iahub Cargo.lock hash, the python-flint (v1) FLINT version, Homebrew FLINT/MPFR/GMP (the
v2 Rust core links these), the Lean toolchain plus the Mathlib commit, and the CAPD pin plus compiler and cmake."""
import hashlib, importlib, json, os, platform, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKGS = ['numpy', 'scipy', 'sympy', 'mpmath', 'flint', 'torch']


def _run(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=60)
        return (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr).strip() else None
    except Exception as e:
        return f"error: {e!r}"


def _sha(path):
    try:
        return hashlib.sha256(open(path, 'rb').read()).hexdigest()
    except Exception:
        return None


def _blas():
    out = {}
    for mod in ('numpy', 'scipy'):
        try:
            cfg = importlib.import_module(mod).show_config(mode='dicts')
            dep = cfg.get('Build Dependencies', {})
            out[mod] = {k: dep.get(k, {}).get('name') for k in ('blas', 'lapack')}
        except Exception as e:
            out[mod] = {'error': repr(e)}
    return out


def _brew(formula):
    try:
        d = json.loads(subprocess.run(['brew', 'info', '--json=v2', formula], capture_output=True, text=True,
                                      timeout=60).stdout)['formulae'][0]
        return d['installed'][0]['version'] if d['installed'] else None
    except Exception:
        return None


def _lean():
    lt = os.path.join(REPO, 'lean/ZiglinCert/lean-toolchain')
    man = os.path.join(REPO, 'lean/ZiglinCert/lake-manifest.json')
    mathlib = None
    try:
        for p in json.load(open(man)).get('packages', []):
            if p.get('name') == 'mathlib':
                mathlib = dict(rev=p.get('rev'), inputRev=p.get('inputRev'), url=p.get('url'))
    except Exception:
        pass
    return dict(toolchain=open(lt).read().strip() if os.path.exists(lt) else None, mathlib=mathlib,
                lake_manifest_sha256=_sha(man))


def stamp():
    v = {}
    for p in PKGS:
        try:
            v[p] = importlib.import_module(p).__version__
        except Exception:
            v[p] = None
    try:
        import flint
        flint_lib = getattr(flint, '__FLINT_VERSION__', None)
    except Exception:
        flint_lib = None
    capd_pins = os.path.join(REPO, 'qsim/capd/PINS.md')
    return dict(
        python=sys.version.split()[0], executable=sys.executable, implementation=platform.python_implementation(),
        platform=platform.platform(), machine=platform.machine(), macos=_run(['sw_vers', '-productVersion']),
        macos_build=_run(['sw_vers', '-buildVersion']), packages=v, blas_lapack=_blas(),
        git=dict(commit=_run(['git', '-C', REPO, 'rev-parse', 'HEAD']),
                 dirty=bool(subprocess.run(['git', '-C', REPO, 'status', '--porcelain'], capture_output=True,
                                           text=True).stdout.strip())),
        native=dict(
            rustc=_run(['rustc', '-V']), cargo=_run(['cargo', '-V']),
            iahub_cargo_lock_sha256=_sha(os.path.join(REPO, 'native/iahub/Cargo.lock')),
            python_flint_bundled_FLINT=flint_lib,
            brew=dict(flint=_brew('flint'), mpfr=_brew('mpfr'), gmp=_brew('gmp'), boost=_brew('boost'),
                      cmake=_brew('cmake')),
            cxx=_run(['c++', '--version']), lean=_lean(),
            capd=dict(commit='2f060980d0685cc9bf88352e08c242197cd7d686',
                      tarball_sha256='9998574057400c7a75f483ba3f3cdb14f8824b28fb62eceacdec5327eda7d909',
                      cmake_flags='-DCAPD_INTERVAL_TYPE=NATIVE -DCAPD_ENABLE_MULTIPRECISION=ON -DCAPD_BUILD_TESTS=ON '
                                  '-DCAPD_BUILD_EXAMPLES=ON (+ Homebrew include/lib paths)',
                      pins_sha256=_sha(capd_pins))))


if __name__ == '__main__':
    s = stamp(); out = json.dumps(s, indent=1); print(out)
    if len(sys.argv) > 1:
        open(sys.argv[1], 'w').write(out + '\n')
