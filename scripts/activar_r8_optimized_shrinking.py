#!/usr/bin/env python3
"""
Activa android.r8.optimizedResourceShrinking=true en gradle.properties.
- --dry-run: solo muestra el cambio.
- --yes:     aplica con os.replace atomico.
- Aborta si la linea no existe o el valor no es exactamente 'false'.
"""
import argparse, os, sys
from pathlib import Path

GP = Path("gradle.properties")
ANCHOR = "android.r8.optimizedResourceShrinking=false"
NEW    = "android.r8.optimizedResourceShrinking=true"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    if not GP.is_file():
        sys.exit("ABORT: no existe " + str(GP))

    text = GP.read_text(encoding="utf-8")
    occurrences = text.count(ANCHOR)

    if occurrences == 0:
        sys.exit("ABORT: ancla no encontrada: '" + ANCHOR + "'")
    if occurrences > 1:
        sys.exit("ABORT: ancla aparece " + str(occurrences) + " veces (esperaba 1)")

    # validar que 'true' no exista ya (por si acaso)
    if NEW in text:
        sys.exit("ABORT: ya estaba en 'true'")

    new_text = text.replace(ANCHOR, NEW, 1)

    # sanity: mismas lineas, +0/-0
    old_lines = text.count("\n")
    new_lines = new_text.count("\n")
    if old_lines != new_lines:
        sys.exit("ABORT: cambio en cantidad de lineas (" + str(old_lines) + " -> " + str(new_lines) + ")")

    # diff para humano
    print("[DIFF]")
    for i, line in enumerate(text.splitlines(), 1):
        if ANCHOR in line:
            print("  - " + line)
    for i, line in enumerate(new_text.splitlines(), 1):
        if NEW in line:
            print("  + " + line)

    if args.dry_run:
        print("[DRY-RUN] no se escribio nada")
        return

    if not args.yes:
        print("Falto --yes. Nada modificado.")
        return

    tmp = GP.with_suffix(".properties.tmp")
    tmp.write_text(new_text, encoding="utf-8")
    os.replace(tmp, GP)
    print("[OK] " + str(GP) + " actualizado")

    # validar post
    if NEW not in GP.read_text(encoding="utf-8"):
        sys.exit("ABORT POST: no se aplico")
    print("[OK] verificacion post: " + NEW)

if __name__ == "__main__":
    main()
