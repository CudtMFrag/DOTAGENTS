# everything-search skill

Standalone skill for using Windows Everything CLI (`es.exe`) from any agent or shell workflow.

It covers:

- filename/path/extension search
- JSON output for agents
- silent Everything startup
- IPC readiness wait
- query readiness wait
- legacy `1.5a` instance probing
- non-Windows graceful handling

Scripts are optional helpers; the skill itself is plain instructions plus PowerShell commands.
