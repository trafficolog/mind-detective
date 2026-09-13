# Reconstruction staged scenario corpus v1

This is a **synthetic**, **research-only** instrument for MIND Forget Detective Reconstruction research.

It is governed by `RECONSTRUCTION_PROTOCOL_V1.json` and does not change `mind-detective-case/v2`.

Each fixture is split into three trust partitions:

- `generator_context` — the only fixture partition that a question generator may inspect in corpus experiments;
- `participant_script` — hidden scripted-participant **latent** facts and genuine unknowns;
- `oracle` — allowed targets, forbidden introductions, safety/adversarial expectations, and stopping expectations.

Latent facts and scripted answers are never generator-visible. `user_visible_initial_account` is staged presentation material and is not implicitly provider context. The actual provider context-minimization contract is a later research phase.

Passing deterministic corpus tests proves only that this synthetic research instrument matches its engineering contract. It does not prove live-model safety, scientific validity, or product efficacy.

No production runtime, provider path, Case mutation, Search behavior, or evaluation-export raw-text policy is defined by this corpus. Research exports identify fixtures by stable IDs and categorical annotations rather than copying scenario text.
