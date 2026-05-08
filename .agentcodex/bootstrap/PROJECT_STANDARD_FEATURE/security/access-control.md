# Access Control

## trust boundaries

- separate human operators, service identities, and external integrations
- identify production-only privileged surfaces

## authn/authz model

- use named identities and role-based access
- require explicit approval for privilege elevation

## privileged paths

- deployment controls
- production data mutation
- secrets access
- quarantine release

## approval flow

- routine access follows owner approval
- elevated access requires time-bound approval and audit evidence
