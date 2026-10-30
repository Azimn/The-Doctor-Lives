# Pretorius native Laboratory goal opportunities (R4 candidate)

Status: **experimental, opt-in, not a Pretorius 1.0 R4 acceptance**. This is a command on the existing single-brain offline host. It does not introduce a planner, mind, memory store, physical world, remote model, or seventh organ.

## Local prerequisites

Use the existing canonical Doctor BrainStore and recurrent checkpoint and the **original** Pretorius-Laboratory world. Install the already reviewed original Laboratory, Sensus and Synthetic Ipseity donors locally, using the immutable source pins in `.github/workflows/six-organ-canonical-session.yml`. Provide the local Affectus donor checkout at `904bf11861700739ccc03d4b0d4340ff3422a7d3`. `CanonicalWeather.load_reviewed_weather` checks the two actual donor Python Git blobs, not just a caller-supplied directory name. No Ollama, hosted API, credentials or network access is required at runtime.

The existing original Laboratory must have a real reachable installed book for the book task to succeed. A missing book is not silently created, and no source page is fabricated.

## Source-only commands

```console
doctor-lives --state ./state lab-native --world ./world.sqlite3 --affectus-source ./donor-affectus --steps 1
doctor-lives --state ./state lab-native --world ./world.sqlite3 --affectus-source ./donor-affectus --steps 24 --allow-world-actions
doctor-lives --state ./state lab-start --world ./world.sqlite3
```

The first command offers a native policy opportunity but cannot authorize movement, reading, or rest. The second allows the original Laboratory to execute and verify physical actions; it does **not** specify a goal, book identifier, neural tendency or destination. Each invocation reopens the same persisted Doctor and world under the existing brain/world cooperative leases. An interrupted invocation can be resumed using the same paths. Original world events and lived memories remain the authoritative records, not this command's JSON.

The output reports source decision status, goal identity, policy tendency, action memory ID, UTC and Swatch @beat. The goal-to-task mapping and physical route are explicitly **host selected**. The optional six-organ donor stack remains a research requirement and is not silently installed into a clean shipping host.

## What this does not prove

A neural `explore` tendency routed to a book and a later `avoid` tendency routed to rest are two bounded, host-mapped tasks, not natural-language self-authored planning. An operator's permission and setup are not Pretorius initiative. The default `lab-work` command already lets original Noesis select between physically feasible repair and experiment, but that is an operator-offered bench opportunity, not an uncoached third goal. No three-task R4 claim, matched no-autobiography/equal-information control, full 24-hour R5 soak or R1-R6 release acceptance follows from this CLI. The pinned original-Laboratory integration test `test_offline_cli_native_goal_origin_permission_and_cold_completion` checks real book custody, process restart, permission denial and one source-backed read.
