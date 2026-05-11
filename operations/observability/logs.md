# Logs

## required events

- define the minimum production events that must always be logged

## correlation keys

- define identifiers that allow incident reconstruction across systems

## retention

- define retention and archival expectations by log class

## restricted fields

- identify fields that must be masked, excluded, or specially handled

## sentinel monitoring coverage

- define which runtime, security, quality, and product-health signals Sentinel must observe

## knowledge extraction path

- define how logs flow into summaries, review, memory candidates, and KB update proposals

## memory candidate flow

- logs -> summaries -> review queue -> approved operational memory and KB update candidates
