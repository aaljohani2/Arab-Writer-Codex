#!/usr/bin/env python3
"""Run identical evals through Codex baseline and Codex + $arab-writer.

Records configured model/reasoning separately from observed runtime values.
Requires an authenticated `codex` CLI. No credential is stored in the repo.

A single JSONL may be supplied with --evals. v1.4 linguistic pilot files can be
loaded together with --evals-glob 'evals/linguistic_core_pilot_*.jsonl'.

Skill-isolation protocol:
- discover user/global Arab Writer installations in known Codex skill roots;
- disable those exact SKILL.md paths with session-level `-c skills.config=...`;
- render `codex debug prompt-input` before model calls;
- fail closed if baseline still sees `arab-writer` or candidate cannot see the
  repository-local copy.

This keeps a globally installed Arab Writer from contaminating the baseline
without changing the user's persistent Codex configuration.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/arab-writer"
SKILL_NAME = "arab-writer"


def git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def codex_version():
    try:
        return subprocess.check_output(
            ["codex", "--version"], text=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception:
        return "unknown"


def _unique_paths(paths):
    out = []
    seen = set()
    for raw in paths:
        p = Path(raw).expanduser()
        try:
            key = str(p.resolve(strict=False))
        except OSError:
            key = str(p.absolute())
        if key in seen:
            continue
        seen.add(key)
        out.append(Path(key))
    return out


def known_user_skill_roots():
    """Return likely user/global skill roots without recursively scanning HOME."""
    roots = [
        Path.home() / ".agents/skills",
        Path.home() / ".codex/skills",  # legacy/current compatibility
    ]
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        roots.append(Path(codex_home).expanduser() / "skills")
    return _unique_paths(roots)


def _normalize_explicit_skill_path(raw):
    p = Path(raw).expanduser()
    if p.is_dir():
        p = p / "SKILL.md"
    if not p.is_file():
        raise SystemExit(f"global skill path not found: {p}")
    return p.resolve()


def discover_global_skill_paths(extra_paths=None):
    """Find global/user Arab Writer copies that could contaminate the baseline."""
    found = []
    for root in known_user_skill_roots():
        p = root / SKILL_NAME / "SKILL.md"
        if p.is_file():
            found.append(p.resolve())
    for raw in extra_paths or []:
        found.append(_normalize_explicit_skill_path(raw))
    return _unique_paths(found)


def _toml_string(value):
    # TOML basic strings share the escapes we need here with JSON strings.
    return json.dumps(str(value), ensure_ascii=False)


def skill_disable_override(paths):
    paths = _unique_paths(paths)
    if not paths:
        return None
    entries = ",".join(
        f"{{path={_toml_string(p)},enabled=false}}" for p in paths
    )
    return f"skills.config=[{entries}]"


def _path_markers(path):
    p = Path(path)
    try:
        raw = str(p.resolve(strict=False))
    except OSError:
        raw = str(p.absolute())
    markers = {
        raw,
        raw.replace("\\", "/"),
        raw.replace("\\", "\\\\"),
    }
    return {m.lower() for m in markers if m}


def inspect_skill_prompt(text, local_skill_path=None, global_skill_paths=None):
    """Return only visibility booleans/paths; never persist the rendered prompt."""
    low = text.lower()
    global_visible = []
    for p in global_skill_paths or []:
        if any(marker in low for marker in _path_markers(p)):
            global_visible.append(str(p))

    local_visible = False
    if local_skill_path is not None:
        local_visible = any(
            marker in low for marker in _path_markers(local_skill_path)
        )

    return {
        "skill_named": SKILL_NAME in low,
        "local_path_visible": local_visible,
        "global_paths_visible": global_visible,
    }


def debug_prompt_input(workdir, disabled_skill_paths, timeout=45):
    """Render model-visible prompt input without making a model call."""
    cmd = ["codex", "--cd", str(workdir), "debug", "prompt-input"]
    override = skill_disable_override(disabled_skill_paths)
    if override:
        cmd += ["-c", override]
    cmd += ["Skill isolation probe."]
    p = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    return {
        "returncode": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr[-4000:],
        "command_shape": "codex --cd <workspace> debug prompt-input [session skill disable] <probe>",
    }


def run_skill_isolation_preflight(disabled_skill_paths, timeout=45):
    """Verify that baseline is clean and candidate sees only the local skill."""
    with tempfile.TemporaryDirectory(prefix="aw-preflight-base-") as bd, \
         tempfile.TemporaryDirectory(prefix="aw-preflight-skill-") as sd:
        base = Path(bd)
        cand = Path(sd)
        local_skill = cand / ".agents/skills/arab-writer/SKILL.md"
        local_skill.parent.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL, local_skill.parent)

        br = debug_prompt_input(base, disabled_skill_paths, timeout=timeout)
        if br["returncode"] != 0:
            raise SystemExit(
                "skill-isolation preflight failed while rendering baseline prompt: "
                + br["stderr"]
            )
        bv = inspect_skill_prompt(
            br["stdout"],
            local_skill_path=None,
            global_skill_paths=disabled_skill_paths,
        )
        if bv["skill_named"]:
            raise SystemExit(
                "skill-isolation preflight failed: baseline still sees 'arab-writer'. "
                "A global/plugin copy may exist outside known roots. Pass its SKILL.md "
                "with --global-skill-path and retry."
            )

        cr = debug_prompt_input(cand, disabled_skill_paths, timeout=timeout)
        if cr["returncode"] != 0:
            raise SystemExit(
                "skill-isolation preflight failed while rendering candidate prompt: "
                + cr["stderr"]
            )
        cv = inspect_skill_prompt(
            cr["stdout"],
            local_skill_path=local_skill,
            global_skill_paths=disabled_skill_paths,
        )
        if cv["global_paths_visible"]:
            raise SystemExit(
                "skill-isolation preflight failed: candidate still exposes a disabled "
                f"global Arab Writer path: {cv['global_paths_visible']}"
            )
        if not cv["skill_named"]:
            raise SystemExit(
                "skill-isolation preflight failed: candidate cannot see the local "
                "repository copy of Arab Writer."
            )

        return {
            "verified": True,
            "baseline_skill_visible": bv["skill_named"],
            "candidate_skill_visible": cv["skill_named"],
            "candidate_local_path_visible": cv["local_path_visible"],
            "disabled_global_skill_paths": [str(p) for p in disabled_skill_paths],
            "debug_command_shape": br["command_shape"],
        }


def run_codex(
    workdir: Path,
    prompt: str,
    timeout: int,
    model: str | None,
    reasoning: str | None,
    disabled_skill_paths=None,
):
    out = workdir / "last_message.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "codex",
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "-s",
        "read-only",
        "-C",
        str(workdir),
        "--output-last-message",
        str(out),
    ]
    override = skill_disable_override(disabled_skill_paths or [])
    if override:
        cmd += ["-c", override]
    if model:
        cmd += ["-m", model]
    if reasoning:
        cmd += ["-c", f"model_reasoning_effort={reasoning}"]
    cmd += [prompt]
    started = time.time()
    p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    text = out.read_text(encoding="utf-8") if out.exists() else ""
    return {
        "returncode": p.returncode,
        "seconds": round(time.time() - started, 2),
        "output": text,
        "stderr": p.stderr[-4000:],
        "configured_model": model or "un-pinned",
        "configured_reasoning": reasoning or "un-pinned",
        "observed_model": "unknown",
        "observed_reasoning": "unknown",
        "runtime_verified": False,
        "global_arab_writer_disabled": bool(disabled_skill_paths),
    }


def prompt_for(case, with_skill):
    parts = []
    if with_skill:
        parts.append("$arab-writer")
    parts.append(case["task"])
    if case.get("input"):
        parts.append("\nالنص:\n" + case["input"])
    parts.append(
        "\nأعد الناتج المطلوب فقط دون شرح منهجك، إلا إذا كانت المهمة تطلب تفسيرًا."
    )
    return "\n".join(parts)


def load_eval_files(evals: str | None, evals_glob: str | None):
    if evals and evals_glob:
        raise SystemExit("use either --evals or --evals-glob, not both")
    if evals_glob:
        pattern = evals_glob
        if Path(pattern).is_absolute():
            raise SystemExit("--evals-glob must be repository-relative")
        files = sorted(ROOT.glob(pattern))
        if not files:
            raise SystemExit(f"no eval files matched: {pattern}")
    else:
        p = Path(evals) if evals else ROOT / "tests/evals.jsonl"
        if not p.is_absolute():
            p = ROOT / p
        files = [p]
    for p in files:
        if not p.is_file():
            raise SystemExit(f"eval file not found: {p}")
    return files


def load_cases(files: list[Path]):
    cases = []
    ids = set()
    for p in files:
        for line_no, raw in enumerate(
            p.read_text(encoding="utf-8").splitlines(), 1
        ):
            if not raw.strip():
                continue
            try:
                case = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid JSON in {p}:{line_no}: {exc}") from exc
            case_id = case.get("id")
            if not case_id:
                raise SystemExit(f"missing id in {p}:{line_no}")
            if case_id in ids:
                raise SystemExit(f"duplicate eval id: {case_id}")
            if "task" not in case:
                raise SystemExit(f"missing task for {case_id}")
            ids.add(case_id)
            cases.append(case)
    return cases


def main():
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group()
    group.add_argument(
        "--evals", help="single JSONL eval file; defaults to tests/evals.jsonl"
    )
    group.add_argument(
        "--evals-glob", help="repository-relative glob for multiple JSONL eval files"
    )
    ap.add_argument("--out", default=str(ROOT / "evals/results"))
    ap.add_argument("--limit", type=int)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--model")
    ap.add_argument("--reasoning")
    ap.add_argument(
        "--global-skill-path",
        action="append",
        default=[],
        help=(
            "additional global/user Arab Writer SKILL.md or skill directory to disable; "
            "may be repeated"
        ),
    )
    ap.add_argument(
        "--skip-skill-isolation-preflight",
        action="store_true",
        help=(
            "skip debug prompt verification; not recommended for controlled A/B runs"
        ),
    )
    args = ap.parse_args()

    if not shutil.which("codex"):
        raise SystemExit("codex CLI not found on PATH")

    eval_files = load_eval_files(args.evals, args.evals_glob)
    cases = load_cases(eval_files)
    if args.limit:
        cases = cases[: args.limit]

    global_skill_paths = discover_global_skill_paths(args.global_skill_path)
    if args.skip_skill_isolation_preflight:
        isolation = {
            "verified": False,
            "reason": "explicitly skipped",
            "disabled_global_skill_paths": [str(p) for p in global_skill_paths],
        }
    else:
        isolation = run_skill_isolation_preflight(global_skill_paths)

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "skill_version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "skill_commit": git_commit(),
        "codex_cli_version": codex_version(),
        "configured_model": args.model or "un-pinned",
        "configured_reasoning": args.reasoning or "un-pinned",
        "observed_model": "unknown",
        "observed_reasoning": "unknown",
        "runtime_verification": (
            "NOT VERIFIED unless separate runtime evidence is captured"
        ),
        "eval_sources": [
            str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
            for p in eval_files
        ],
        "cases": len(cases),
        "skill_isolation": isolation,
    }
    (outdir / "run_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    jsonl = outdir / "ab_results.jsonl"
    csvp = outdir / "human_review.csv"
    rows = []
    with jsonl.open("w", encoding="utf-8") as jf:
        for case in cases:
            with tempfile.TemporaryDirectory(prefix="aw-base-") as bd, \
                 tempfile.TemporaryDirectory(prefix="aw-skill-") as sd:
                base = Path(bd)
                cand = Path(sd)
                (cand / ".agents/skills").mkdir(parents=True)
                shutil.copytree(SKILL, cand / ".agents/skills/arab-writer")
                br = run_codex(
                    base,
                    prompt_for(case, False),
                    args.timeout,
                    args.model,
                    args.reasoning,
                    disabled_skill_paths=global_skill_paths,
                )
                cr = run_codex(
                    cand,
                    prompt_for(case, True),
                    args.timeout,
                    args.model,
                    args.reasoning,
                    disabled_skill_paths=global_skill_paths,
                )
                rec = {
                    "id": case["id"],
                    "case": case,
                    "baseline": br,
                    "candidate": cr,
                }
                jf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                jf.flush()
                rows.append(
                    {
                        "id": case["id"],
                        "task": case["task"],
                        "input": case.get("input", ""),
                        "baseline": br["output"],
                        "candidate": cr["output"],
                        "preferred": "",
                        "fidelity_0_2": "",
                        "instruction_0_2": "",
                        "grammar_0_2": "",
                        "mechanics_0_2": "",
                        "naturalness_0_2": "",
                        "organization_0_2": "",
                        "voice_0_2": "",
                        "domain_precision_0_2": "",
                        "overediting": "",
                        "underediting": "",
                        "notes": "",
                    }
                )

    with csvp.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=rows[0].keys() if rows else ["id"]
        )
        w.writeheader()
        w.writerows(rows)

    print(
        f"Wrote {jsonl}, {csvp}, and run_metadata.json from "
        f"{len(eval_files)} eval file(s)"
    )
    if isolation.get("verified"):
        print("Skill isolation: VERIFIED (baseline clean; candidate skill visible)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
