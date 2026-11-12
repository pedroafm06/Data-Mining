#!/usr/bin/env python3
"""Build IEEE conference PDF; final mode enforces reviewable submission gates."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_digest(path: Path) -> str:
    """Hash with LF line endings, so a CRLF checkout (Git on Windows) matches the pinned value."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def uncomment(tex: str) -> str:
    return re.sub(r"(?<!\\)%[^\n]*", "", tex)


def word_count(tex: str) -> int:
    text = uncomment(tex)
    text = re.sub(r"\\(?:cite|ref|label|url)\{[^}]*\}", "", text)
    text = re.sub(r"\\[a-zA-Z@]+\*?", "", text)
    return len(re.findall(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", text, re.UNICODE))


def public_repository(url: str) -> dict:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.username or parsed.password:
        raise ValueError("The public repository must have an HTTPS URL without credentials.")
    request_url = url
    github = parsed.netloc.lower() in {"github.com", "www.github.com"}
    if github:
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) < 2:
            raise ValueError("Use a concrete public GitHub repository URL.")
        request_url = "https://api.github.com/repos/" + "/".join(parts[:2])
    elif parsed.netloc.lower() != "colab.research.google.com":
        raise ValueError("The rubric requires public GitHub or Google Colab.")
    request = urllib.request.Request(request_url, headers={"User-Agent": "A2-IEEE-reproducibility-check", "Accept": "application/vnd.github+json" if github else "text/html"})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
        final_url = response.geturl()
        status = response.status
    if status != 200:
        raise ValueError(f"Public URL returned HTTP {status}.")
    if github and json.loads(body).get("private") is not False:
        raise ValueError("The GitHub API did not confirm a public repository.")
    if not github and "accounts.google.com" in final_url:
        raise ValueError("Colab redirected anonymous access to login.")
    return {"requested_url": url, "checked_url": request_url, "status": status, "checked_utc": datetime.now(timezone.utc).isoformat()}


def final_config() -> tuple[dict, dict]:
    config = json.loads((ROOT / "submission_config.json").read_text(encoding="utf-8"))
    for key in ("public_repository_url", "public_repository_checked_utc", "results_file", "results_sha256"):
        if not config.get(key):
            raise ValueError(f"Final blocked: missing {key} in submission_config.json.")
    if config.get("results_reviewed") is not True or config.get("manuscript_ready") is not True:
        raise ValueError("Final blocked: new results and manuscript must be explicitly reviewed.")
    if type(config.get("random_state")) is not int:
        raise ValueError("Final blocked: record the actual integer random_state.")
    results = (ROOT / config["results_file"]).resolve()
    if digest(results) != config["results_sha256"]:
        raise ValueError("Final blocked: reviewed results SHA-256 differs from the source.")
    main = uncomment((ROOT / "main.tex").read_text(encoding="utf-8"))
    if r"\documentclass[conference]{vendor/IEEEtran/IEEEtran}" not in main:
        raise ValueError("Final blocked: retain the official IEEEtran conference class.")
    source_paths = list((ROOT / "sections").glob("*.tex"))
    content = "\n".join(uncomment(p.read_text(encoding="utf-8")) for p in source_paths)
    if re.search(r"PENDENTE|TODO|FIXME|\\pendente\b", content):
        raise ValueError("Final blocked: unresolved content placeholders remain.")
    if re.search(r"\\(?:onecolumn|geometry|setstretch)\b|\\usepackage(?:\[[^\]]*\])?\{(?:geometry|fullpage|setspace)\}", main + content):
        raise ValueError("Final blocked: class layout must remain unchanged.")
    words = word_count((ROOT / "sections/abstract.tex").read_text(encoding="utf-8"))
    if not 100 <= words <= 150:
        raise ValueError(f"Final blocked: abstract has {words} words, required 100–150.")
    return config, public_repository(config["public_repository_url"])


def validate_pdf(path: Path, log_path: Path, *, final: bool) -> dict:
    if shutil.which("pdfinfo"):
        info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True).stdout
        pages = int(re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE).group(1))
    else:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("Install Poppler (pdfinfo) or pypdf to validate PDF pages.") from exc
        pages = len(PdfReader(str(path)).pages)
    if final and not 1 <= pages <= 5:
        raise ValueError(f"Final blocked: {pages} pages; maximum is 5.")
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    problems = [line.strip() for line in log.splitlines() if re.search(r"Overfull \\hbox|Missing character|undefined references|Citation .* undefined|Reference .* undefined", line)]
    if final and problems:
        raise ValueError("Final blocked: layout or reference defects: " + "; ".join(problems))
    return {"pages": pages, "layout_reference_warnings": problems, "abstract_words": word_count((ROOT / "sections/abstract.tex").read_text(encoding="utf-8"))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--draft", action="store_true")
    mode.add_argument("--final", action="store_true")
    mode.add_argument("--smoke", action="store_true", help="Compile a separate IEEE layout smoke check.")
    parser.add_argument("--offline", action="store_true", help="Use only the existing local TeX cache.")
    args = parser.parse_args()
    name = "final" if args.final else "smoke" if args.smoke else "draft"
    config, public_check = final_config() if args.final else ({}, {})
    lock = json.loads((ROOT / "provenance.lock.json").read_text(encoding="utf-8"))
    key = f"{platform.system()}-{platform.machine()}"
    spec = lock.get("tectonic_platforms", {}).get(key, lock["tectonic"])
    binary = ROOT / "work/bin" / spec.get("executable_name", "tectonic")
    if not binary.exists() or digest(binary) != spec["executable_sha256"]:
        raise ValueError("Run python3 tools/bootstrap.py to obtain the pinned verified binary.")
    for relative, expected in lock.get("vendored_files", {}).items():
        if text_digest(ROOT / relative) != expected:
            raise ValueError(f"Vendored official source was modified: {relative}")
    build_dir = ROOT / "work/build" / name
    build_dir.mkdir(parents=True, exist_ok=True)
    if args.smoke:
        paragraph = "Este documento verifica apenas a composição do template oficial IEEEtran em modo de conferência. Não apresenta resultados experimentais nem constitui o artigo final. "
        wrapper = "\\documentclass[conference]{vendor/IEEEtran/IEEEtran}\n\\usepackage[T1]{fontenc}\n\\usepackage[brazil]{babel}\n\\title{Verificação local do template IEEE de conferências}\n\\author{\\IEEEauthorblockN{Equipe do estudo de caso}\\IEEEauthorblockA{Universidade Federal de Goiás}}\n\\begin{document}\\maketitle\n\\begin{abstract}" + paragraph * 2 + "\\end{abstract}\n\\section{Verificação de composição}\n" + "\n\n".join(paragraph * 3 for _ in range(7)) + "\n\\end{document}\n"
    else:
        flag = "\\def\\AiiFinalConfigured{1}" if args.final else "\\def\\AiiDraft{1}"
        url = config.get("public_repository_url", "ENDERECO-PUBLICO-PENDENTE")
        if any(char in url for char in "%#{}\\"):
            raise ValueError("Use a repository URL without escaped characters or fragments.")
        wrapper = flag + "\n\\edef\\PublicRepositoryURL{\\detokenize{" + url + "}}\n\\input{main.tex}\n"
    (build_dir / "driver.tex").write_text(wrapper, encoding="utf-8")
    env = os.environ.copy()
    env["TECTONIC_CACHE_DIR"] = str(ROOT / "work/tectonic-cache")
    env["SOURCE_DATE_EPOCH"] = "1794009600"
    command = [str(binary), "--untrusted", "--keep-logs", "--keep-intermediates", "--outdir", str(build_dir)]
    if lock.get("tex_bundle", {}).get("url"):
        command += ["--bundle", lock["tex_bundle"]["url"]]
    if args.offline:
        command += ["--only-cached"]
    command += ["-"]
    completed = subprocess.run(command, input=wrapper, text=True, encoding="utf-8", errors="replace", cwd=ROOT, env=env, capture_output=True)
    (build_dir / "build.stdout.log").write_text(completed.stdout + completed.stderr, encoding="utf-8")
    print(completed.stdout + completed.stderr)
    if completed.returncode:
        raise SystemExit(completed.returncode)
    bundle_lock = lock.get("tex_bundle", {})
    if bundle_lock.get("content_digest"):
        identity_file = ROOT / bundle_lock["cache_identity_file"]
        if identity_file.read_text(encoding="utf-8").strip() != bundle_lock["content_digest"]:
            raise ValueError("Official TeX bundle identity changed; stopped before publishing the PDF.")
    candidate = build_dir / "texput.pdf"
    qa = validate_pdf(candidate, build_dir / "texput.log", final=args.final)
    destination = ROOT / "output/pdf" / ("Artigo_A2_IEEE.pdf" if args.final else f"a2-{name}.pdf")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate, destination)
    sources = [ROOT / "main.tex", ROOT / "references.bib", ROOT / "submission_config.json", *sorted((ROOT / "sections").glob("*.tex")), *sorted((ROOT / "figures").glob("*")), *sorted((ROOT / "tools").glob("*.py"))]
    manifest = {"mode": name, "created_utc": datetime.now(timezone.utc).isoformat(), "pdf": str(destination.relative_to(ROOT)), "pdf_sha256": digest(destination), "tectonic_sha256": digest(binary), "provenance_lock_sha256": digest(ROOT / "provenance.lock.json"), "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sources if p.is_file()}, "tex_bundle_content_digest": bundle_lock.get("content_digest"), "source_date_epoch": env["SOURCE_DATE_EPOCH"], "config": config, "public_repository_check": public_check, "qa": qa}
    (build_dir / "build-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"pdf": str(destination), **qa}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc))
