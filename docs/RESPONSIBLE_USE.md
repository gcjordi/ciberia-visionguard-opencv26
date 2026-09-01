# Responsible Use and Safety

## Intended scope

VisionGuard is a research/demo system for evaluating visual evidence quality before an agent acts. The reference use case is a synthetic restricted-zone event.

## Deliberate exclusions

The MVP does **not** perform:

- face recognition;
- biometric identification;
- identity inference;
- demographic inference;
- emotion recognition;
- intent prediction;
- persistent person tracking across identities.

## Data rights and privacy

The bundled demonstration data is generated synthetically by project code. Uploaded videos are deleted from local temporary storage after analysis by default. S3 persistence is disabled by default and must be explicitly enabled. The reference S3 infrastructure blocks public access, encrypts objects and deletes retained demo evidence after seven days.

For any real-camera deployment, the operator is responsible for lawful basis, notice/consent where required, purpose limitation, retention, access controls and applicable privacy regulation.

## Human control

VisionGuard is designed to **withhold** autonomous action when trust is inadequate. The human-review API records approval or rejection in the trace. A production system should use authenticated reviewers and stronger authorization than the demo endpoint.

## Calibration

VCTS is a composite research heuristic. It is not a calibrated probability of correctness. Thresholds must be validated for each domain and must not be represented as universal safety guarantees.

## Misuse controls

The project should not be positioned as a mass-surveillance tool, an autonomous enforcement system, or a substitute for safety certification. Consequential real-world actions require domain-specific engineering, validation and governance beyond this competition prototype.
