# Guard rules

The guard is a conservative deterministic filter for candidate investigative utterances.

- In `reconstruction`, a concrete location that is not already present in user-supported case data is blocked with `MD_G_RECON_NEW_LOCATION`.
- In `search_planning`, a new concrete location may be proposed explicitly as a physical search suggestion; it must not be phrased as a recovered memory or known fact.
- Claims that assert false memory, diagnose a forgetting mechanism, present a calibrated location probability, convert failed search into memory evidence, or treat a superficial check as proof of absence are blocked with stable `MD_G_*` codes.

The RU/EN lexical coverage is intentionally bounded and conservative. Passing this helper does not prove an utterance is semantically safe in every phrasing.

Generic Claude Code/Codex skill hosts do not expose a repository-controlled mandatory pre-send interception hook. Therefore this helper mechanically proves behavior only for candidates submitted to it. Production skills must invoke it where specified, and host-level compliance is additionally covered by adversarial evals and review. The project must not claim that every model utterance is technically intercepted in `0.1.0`.
