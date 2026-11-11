#!/usr/bin/env python3
"""
Recorta idiomas de KISS Launcher.
Conserva: values/ (default), values-es, values-en-rGB
Conserva SIEMPRE (no son idiomas): values-night, values-v31,
  values-night-v31, values-sw360dp
Borra el resto con git rm. Reescribe locales_config.xml.
--dry-run: solo muestra que haria.
"""
import argparse, os, subprocess, sys
from pathlib import Path

RES = Path("app/src/main/res")
LOCALES = RES / "xml" / "locales_config.xml"

KEEP_LANGS = {"values", "values-es", "values-en-rGB"}
KEEP_CONFIG = {"values-night", "values-v31", "values-night-v31", "values-sw360dp"}
KEEP = KEEP_LANGS | KEEP_CONFIG

NEW_LOCALES = ["en-US", "es"]

def is_lang_dir(p: Path) -> bool:
    return p.is_dir() and p.name.startswith("values-") and p.name not in KEEP_CONFIG

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    if not RES.is_dir():
        sys.exit("ABORT: no existe " + str(RES))
    if not LOCALES.is_file():
        sys.exit("ABORT: no existe " + str(LOCALES))

    langs = sorted([d for d in RES.iterdir() if is_lang_dir(d)], key=lambda p: p.name)
    to_remove = [d for d in langs if d.name not in KEEP_LANGS]
    to_keep   = [d for d in langs if d.name in KEEP_LANGS]

    print("[INFO] idiomas detectados:", len(langs))
    print("[INFO] conservar:", len(to_keep), "->", [d.name for d in to_keep])
    print("[INFO] borrar:", len(to_remove))
    for d in to_remove:
        files = sum(1 for _ in d.rglob("*") if _.is_file())
        print("   -", d.name, "(", files, "archivos )")

    missing = [k for k in KEEP_LANGS if not (RES / k).is_dir()]
    if missing:
        sys.exit("ABORT: faltan carpetas a conservar: " + str(missing))

    new_xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<locale-config xmlns:android="http://schemas.android.com/apk/res/android">\n'
        + "".join('    <locale android:name="' + l + '" />\n' for l in NEW_LOCALES)
        + '</locale-config>\n'
    )

    if args.dry_run:
        print("\n[DRY-RUN] git rm -r " + " ".join(d.name for d in to_remove))
        print("[DRY-RUN] nuevo locales_config.xml:")
        print(new_xml)
        total = sum(f.stat().st_size for d in to_remove for f in d.rglob('*') if f.is_file())
        print("[DRY-RUN] ahorro estimado:", total, "bytes")
        return

    if not args.yes:
        print("\nFalto --yes. Nada modificado.")
        return

    if to_remove:
        cmd = ["git", "rm", "-r", "-q"] + [str(d) for d in to_remove]
        print("[EXEC]", " ".join(cmd))
        subprocess.run(cmd, check=True)

    tmp = LOCALES.with_suffix(".xml.tmp")
    tmp.write_text(new_xml, encoding="utf-8")
    os.replace(tmp, LOCALES)
    print("[OK]", LOCALES, "reescrito (", len(NEW_LOCALES), "locales )")

    remaining = sorted([d.name for d in RES.iterdir() if is_lang_dir(d)])
    expected = sorted(KEEP_LANGS)
    if remaining != expected:
        sys.exit("ABORT POST: quedaron " + str(remaining) + " esperaba " + str(expected))
    print("[OK] idiomas restantes:", remaining)

if __name__ == "__main__":
    main()
