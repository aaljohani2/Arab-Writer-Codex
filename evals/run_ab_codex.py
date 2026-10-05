#!/usr/bin/env python3
"""Run identical evals through Codex baseline and Codex + $arab-writer.

Records configured model/reasoning separately from observed runtime values.
Requires an authenticated `codex` CLI. No credential is stored in the repo.

A single JSONL may be supplied with --evals. v1.4 linguistic pilot files can be
loaded together with --evals-glob 'evals/linguistic_core_pilot_*.jsonl'.

Controlled A/B safeguards:
- discover user/global Arab Writer installations in known Codex skill roots;
- disable those exact SKILL.md paths with session-level `-c skills.config=...`;
- inject a one-run sentinel into the temporary candidate skill description;
- render `codex debug prompt-input` before model calls;
- fail closed unless baseline is clean and candidate exposes that exact sentinel;
- optionally require a clean Git worktree plus pinned model/reasoning;
- support a stratified smoke sample across linguistic families;
- support a blind-proofread prompt that hides per-case diagnostic hints.

This keeps a globally installed Arab Writer from contaminating the baseline
without changing the user's persistent Codex configuration.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/arab-writer"
SKILL_NAME = "arab-writer"
DEFAULT_SMOKE_FAMILIES = ("ORT", "MOR", "SYN", "AGR", "NUM", "PUN", "AMB")
BLIND_PROOFREAD_PROTOCOL = "blind-proofread-v1"
BLIND_PROOFREAD_INSTRUCTION = (
    "دقق النص لغويًا ونحويًا وصرفيًا وإملائيًا وترقيميًا.\n"
    "صحح الأخطاء الحقيقية فقط بأقل تعديل ممكن.\n"
    "لا تغيّر تركيبًا صحيحًا لمجرد تحسين الأسلوب، ولا تستبدل وجهًا عربيًا جائزًا بوجه آخر.\n"
    "إذا كان النص صحيحًا فأعده كما هو."
)


def git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def git_status_porcelain():
    try:
        return subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return None


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


def inject_isolation_sentinel(skill_md: Path, sentinel: str):
    """Append a unique sentinel to the temporary skill description only."""
    text = skill_md.read_text(encoding="utf-8")
    pattern = re.compile(r"(?m)^description:\s*(.+)$")
    match = pattern.search(text)
    if not match:
        raise SystemExit("skill-isolation preflight failed: SKILL.md has no description")
    replacement = f"description: {match.group(1)} Isolation sentinel: {sentinel}."
    text = text[: match.start()] + replacement + text[match.end() :]
    skill_md.write_text(text, encoding="utf-8")


def inspect_skill_prompt(
    text,
    local_skill_path=None,
    global_skill_paths=None,
    sentinel=None,
):
    """Return visibility facts only; never persist the rendered prompt."""
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
        "sentinel_visible": bool(sentinel and sentinel.lower() in low),
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
    """Verify baseline is clean and candidate exposes the exact temp local skill."""
    sentinel = f"AW_ISOLATION_{uuid.uuid4().hex}"
    with tempfile.TemporaryDirectory(prefix="aw-preflight-base-") as bd, \
         tempfile.TemporaryDirectory(prefix="aw-preflight-skill-") as sd:
        base = Path(bd)
        cand = Path(sd)
        local_skill = cand / ".agents/skills/arab-writer/SKILL.md"
        local_skill.parent.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL, local_skill.parent)
        inject_isolation_sentinel(local_skill, sentinel)

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
            sentinel=sentinel,
        )
        if bv["skill_named"] or bv["sentinel_visible"]:
            raise SystemExit(
                "skill-isolation preflight failed: baseline still sees Arab Writer. "
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
            sentinel=sentinel,
        )
        if cv["global_paths_visible"]:
            raise SystemExit(
                "skill-isolation preflight failed: candidate still exposes a disabled "
                f"global Arab Writer path: {cv['global_paths_visible']}"
            )
        if not cv["skill_named"]:
            raise SystemExit(
                "skill-isolation preflight failed: candidate cannot see Arab Writer."
            )
        if not cv["sentinel_visible"]:
            raise SystemExit(
                "skill-isolation preflight failed: candidate sees an Arab Writer, "
                "but not the sentinel-tagged temporary local copy."
            )

        return {
            "verified": True,
            "method": "temporary-description-sentinel",
            "baseline_skill_visible": bv["skill_named"],
            "baseline_sentinel_visible": bv["sentinel_visible"],
            "candidate_skill_visible": cv["skill_named"],
            "candidate_sentinel_visible": cv["sentinel_visible"],
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


def prompt_for(case, with_skill, blind_proofread=False):
    """Build the model-visible prompt without leaking case metadata in blind mode."""
    parts = []
    if with_skill:
        parts.append("$arab-writer")
    if blind_proofread:
        parts.append(BLIND_PROOFREAD_INSTRUCTION)
    else:
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


def select_stratified_smoke(cases, family_order=DEFAULT_SMOKE_FAMILIES):
    """Select one deterministic case from each requested family."""
    first_by_family = {}
    for case in cases:
        family = case.get("family")
        if family in family_order and family not in first_by_family:
            first_by_family[family] = case
    missing = [family for family in family_order if family not in first_by_family]
    if missing:
        raise SystemExit(
            "stratified smoke cannot cover families: " + ", ".join(missing)
        )
    return [first_by_family[family] for family in family_order]


def validate_controlled_run(args, git_status):
    """Fail closed on conditions that would make a formal A/B irreproducible."""
    if not args.controlled:
        return
    problems = []
    if not args.model:
        problems.append("--model is required")
    if not args.reasoning:
        problems.append("--reasoning is required")
    if args.skip_skill_isolation_preflight:
        problems.append("skill isolation preflight cannot be skipped")
    if git_status is None:
        problems.append("git worktree state could not be read")
    elif git_status:
        problems.append(
            "git worktree is dirty; run from a clean checkout/worktree at a fixed commit"
        )
    if problems:
        raise SystemExit("controlled A/B preflight failed: " + "; ".join(problems))


def main():
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group()
    group.add_argument(
        "--evals", help="single JSONL eval file; defaults to tests/evals.jsonl"
    )
    group.add_argument(
        "--evals-glob", help="repository-relative glob for multiple JSONL eval files"
    )
    sample = ap.add_mutually_exclusive_group()
    sample.add_argument("--limit", type=int)
    sample.add_argument(
        "--stratified-smoke",
        action="store_true",
        help="run one deterministic case from each pilot family",
    )
    ap.add_argument("--out", default=str(ROOT / "evals/results"))
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--model")
    ap.add_argument("--reasoning")
    ap.add_argument(
        "--blind-proofread",
        action="store_true",
        help=(
            "hide per-case task/rule hints and use one generic Arabic proofreading "
            "instruction for baseline and candidate"
        ),
    )
    ap.add_argument(
        "--controlled",
        action="store_true",
        help="require clean Git state, pinned model/reasoning, and verified skill isolation",
    )
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
        help="skip debug prompt verification; never use for controlled A/B runs",
    )
    args = ap.parse_args()

    if not shutil.which("codex"):
        raise SystemExit("codex CLI not found on PATH")

    worktree_status = git_status_porcelain()
    validate_controlled_run(args, worktree_status)

    eval_files = load_eval_files(args.evals, args.evals_glob)
    cases = load_cases(eval_files)
    sampling = "full"
    if args.stratified_smoke:
        cases = select_stratified_smoke(cases)
        sampling = "stratified-smoke"
    elif args.limit:
        cases = cases[: args.limit]
        sampling = f"first-{args.limit}"

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
        "git_worktree_clean": worktree_status == "",
        "git_status_available": worktree_status is not None,
        "controlled_run": args.controlled,
        "prompt_mode": BLIND_PROOFREAD_PROTOCOL if args.blind_proofread else "case-task",
        "codex_cli_version": codex_version(),
        "configured_model": args.model or "un-pinned",
        "configured_reasoning": args.reasoning or "un-pinned",
        "observed_model": "unknown",
        "observed_reasoning": "unknown",
        "runtime_verification": (
            "configured runtime is pinned only when --model/--reasoning are supplied; "
            "observed runtime remains unknown unless separate runtime evidence is captured"
        ),
        "eval_sources": [
            str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
            for p in eval_files
        ],
        "sampling": sampling,
        "case_ids": [case["id"] for case in cases],
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
                    prompt_for(case, False, args.blind_proofread),
                    args.timeout,
                    args.model,
                    args.reasoning,
                    disabled_skill_paths=global_skill_paths,
                )
                cr = run_codex(
                    cand,
                    prompt_for(case, True, args.blind_proofread),
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
        print(
            "Skill isolation: VERIFIED "
            "(baseline clean; candidate sentinel-tagged local skill visible)"
        )
    print(
        "Prompt mode: "
        + (BLIND_PROOFREAD_PROTOCOL if args.blind_proofread else "case-task")
    )
    if args.stratified_smoke:
        print("Stratified smoke families: " + ", ".join(DEFAULT_SMOKE_FAMILIES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())