# Rule record

Fields of a rule record. The schema is [schema/rule-record.schema.json](../schema/rule-record.schema.json). The last column gives the DSSC rule record field each one comes from.

| Field | Content | DSSC field |
| --- | --- | --- |
| `@id`, `version` | Stable identifier. The DSSC identifier when the rule exists there (`dssc:M2.usage.01`), otherwise `ptx:rule/...` | Identifier |
| `title` | Short name | Title |
| `statement` | One sentence, one obligation, per language | Requirement |
| `strength` | `MUST`, `SHOULD`, `MAY` | Requirement |
| `deonticType` | `obligation`, `prohibition`, `permission` | Type |
| `accountable`, `executor` | DSSC roles: governance authority, data provider, data user, service provider, operator, intermediary, participant | Role it binds |
| `level` | 0 to 3 | Level |
| `parameters` | See below | Level |
| `pattern` | Generic rule pattern: purpose limitation, release threshold, local processing, anonymisation, credential, retention, publication, logging, contract, process, governance (what the rulebook itself must state) | Not in DSSC |
| `parent` | Parent rule and the baseline version it conforms to. `null` at level 0 | Parent rule (field 15) |
| `buildingBlock` | One or two Blueprint 4.0 building blocks | Building block |
| `enforcementClass` | E0 to E3, the minimum the rule requires. A lower level may raise it, never lower it. When the rule can bite in several ways, each expression carries its own class | Enforcement class |
| `assuranceLevel` | L1 to L3, the minimum the rule requires, same logic | Assurance level |
| `control` | Who checks what, when | Control |
| `evidence` | Execution records and who may see them | Evidence |
| `trustFramework` | Scheme, version, accepted issuers, or `none` | Trust framework reference |
| `expressions` | See below | Machine-readable expression |
| `source` | Documents the rule comes from | Source |
| `decisionStatus` | `agreed`, `provisional`, `candidate`, `example`, as in the DSSC register | Status |

Implementation status is not in the record. It goes in a validation record, one per data space and rule, as in the DSSC register.

## Parameters

| Field | Content |
| --- | --- |
| `name` | Parameter name, used in templates as `@{name}` |
| `datatype` | `boolean`, `integer`, `decimal`, `string`, `iri`, `duration`, `list` |
| `case` | What the level of the record does with the value: `open` (left to a lower level), `bounded` (`allowedValues` given), `default` (`value` given, may be changed), `fixed` (`value` given, may not be changed) |
| `setAt` | Level that sets the value |
| `stricter` | Direction a lower level may move the value: `higher`, `lower`, `subset`, or `false` / `true` for a boolean |

## Expressions

| Field | Content |
| --- | --- |
| `type` | `odrl-template`, `credential-requirement`, `shacl-shape`, `contract-clause`, `release-gate`, `monitoring`, `none`, `not-yet-specified` |
| `ref` | Identifier of the artifact where the building block reads it |
| `artifact` | Path of the reference version in this repository |
| `check` | For release gates, the condition in plain form |
| `enforcementClass` | When it differs from the record, for this expression |
| `coverage` | `partial` when the artifact checks only part of the rule |
| `note` | Free text |

`none` is a valid expression: the rule is checked by people, and `control` and `evidence` say how. `not-yet-specified` means an artifact is planned but not written.
