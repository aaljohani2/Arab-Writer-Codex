# Installation

## Recommended: `$skill-installer`

Open Codex and invoke:

```text
$skill-installer
```

Ask:

```text
Install the skill from https://github.com/aaljohani2/Arab-Writer-Codex/tree/main/.agents/skills/arab-writer
```

After installation, use `/skills` or type `$arab-writer`.

If Codex does not show a newly installed skill, restart Codex.

## Manual personal installation

Run these commands from the root of a local checkout of this repository. Copy the skill into the personal skills directory (not into an existing `arab-writer` subdirectory).

macOS / Linux / WSL:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R .agents/skills/arab-writer "$HOME/.agents/skills/"
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item -Path ".\.agents\skills\arab-writer" -Destination "$HOME\.agents\skills" -Recurse -Force
```

## Repository-scoped installation

Copy:

```text
.agents/skills/arab-writer
```

into the target repository.

Codex can then discover it when working inside that repository.
