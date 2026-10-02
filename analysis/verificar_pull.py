import pathlib
import subprocess
import sys

_REPO = pathlib.Path(__file__).resolve().parent
subprocess.run(["git", "fetch", "origin"], cwd=_REPO)
_atras = int(subprocess.run(["git", "rev-list", "--count", "HEAD..@{u}"], cwd=_REPO,
                            capture_output=True, text=True).stdout.strip())
if _atras > 0:
    if input(f"KeplerDF-Datos está {_atras} commits atrás de origin. ¿Quieres continuar? [s/n]: ").strip().lower() != "s":
        sys.exit(0)
