# MIND Detective 0.1.0 Requirements

Это нормативный реестр стабильных P0-контрактов. Статус `active` означает, что требование уже имеет проверяемый control path. Статус `planned` используется только пока соответствующий инкремент implementation plan ещё не реализован; такой статус нельзя интерпретировать как green enforcement.

- `MD-REQ-CASE-01` — один канонический Case Controller владеет детерминированным состоянием кейса. **Status: active.**
- `MD-REQ-STATEMENT-01` — `source` и `statement_type` являются независимыми полями. **Status: active.**
- `MD-REQ-STATEMENT-02` — assistant не может быть источником `recollection`, `habit` или `observation`. **Status: active.**
- `MD-REQ-STATEMENT-03` — vividness/confidence/sensory detail не повышают truth status механически. **Status: active.**
- `MD-REQ-RECONSTRUCT-01` — free account предшествует детальным уточнениям. **Status: active; skill-contract + eval + review.**
- `MD-REQ-RECONSTRUCT-02` — reconstruction questions не вводят неподдержанные конкретные локации. **Status: active.**
- `MD-REQ-RECONSTRUCT-03` — «не помню» остаётся явной неопределённостью. **Status: active.**
- `MD-REQ-TIMELINE-01` — timeline сохраняет unknown intervals и contradictions. **Status: active.**
- `MD-REQ-SEARCH-01` — каждая физическая проверка хранит target, method, result и accessibility state. **Status: active.**
- `MD-REQ-SEARCH-02` — повторные проверки не трактуются как независимое probability evidence. **Status: active.**
- `MD-REQ-SEARCH-03` — конкретные локации допустимы как search suggestions, но не как memories/facts. **Status: active.**
- `MD-REQ-SEARCH-04` — выбирается одно next action без numerical location probability и hidden belief weight. **Status: active.**
- `MD-REQ-SEARCH-05` — superficial и thorough checks различимы в истории. **Status: active.**
- `MD-REQ-RESUME-01` — сохранённый кейс возобновляется без evidence strengthening и потери истории. **Status: active.**
- `MD-REQ-STORE-01` — persistence case-local, explicit и deletable. **Status: active.**
- `MD-REQ-STORE-02` — P0 не делает cross-case learning или hidden aggregation. **Status: active.**
- `MD-REQ-SAFETY-01` — high-risk forgotten actions не входят в ordinary physical-search reasoning. **Status: active.**
- `MD-REQ-CLOSE-01` — outcome фиксирует результат без диагностики forgetting mechanism. **Status: active.**
- `MD-REQ-EVAL-01` — high-risk contracts имеют deterministic tests и adversarial eval scenarios. **Status: active.**
- `MD-REQ-DOCS-01` — ключевые публичные docs RU-primary с EN mirrors. **Status: planned; Task 13.**
- `MD-REQ-RELEASE-01` — один repository SemVer, independent plugin SemVer, один manifest и один publisher. **Status: planned; Task 15.**

`docs/CONTRACT_MATRIX.json` является machine-readable trace map. Green fixture validation не является доказательством live-model semantic behavior или научной валидности продукта.
