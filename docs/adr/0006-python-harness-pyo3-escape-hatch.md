# ADR-0006 : Python harness for the suzerain CLI, PyO3 escape hatch

- **Statut** : accepted
- **Date** : 2026-04-30
- **Stacks concernées** : * (impacte le code source de suzerain)

## Contexte

Le CLI suzerain pourrait être écrit en Rust pour bénéficier d'une vitesse
brute (cohérence avec `uv`, `ruff`, `ty`). Mais le profil de l'auditeur
est dominé par I/O et invocations subprocess vers les outils tiers
(eux-mêmes en Rust). Le bottleneck réel n'est pas le CPU : c'est le coût
d'évolution des règles, qui sera fréquent au palier 2.

## Décision

Le CLI est écrit en **Python**. Justifications :

- Itération rapide sur les règles (chaque règle = ~10–20 lignes Python).
- Adaptateurs (Python, Node, Go, Rust à venir) vivent dans des sous-modules
  Python : ajouter une stack = créer un dossier, pas recompiler.
- Distribution simple : `uv tool install suzerain`.
- L'utilisateur (Damien) maîtrise déjà l'écosystème Python.

**Porte de sortie explicite** : si `suzerain audit ~/Work/*` dépasse
durablement 30 s à froid (mesuré sur 3 runs consécutifs), profiler avec
`py-spy` ou `cProfile`. Si une règle individuelle est responsable, la
réécrire en extension Rust via PyO3 (intégration locale, pas une
réécriture globale).

## Conséquences

- Toute la pile : Python ≥ 3.13, type hints stricts (ADR-0003), tests
  pytest.
- Pas d'ABI plugin nécessaire pour les adaptateurs.
- Dette assumée : le CLI sera plus lent qu'un équivalent Rust pur. Acceptable
  vu le profil d'usage (audit ponctuel, pas en boucle keystroke).

## Alternatives considérées

- **CLI 100 % Rust** : gain marginal sur le temps total (dominé par
  subprocess), coût massif sur l'agilité.
- **CLI mixte Python + bibliothèque Rust dès V1** : prématuré, ajoute du
  build complexe sans bénéfice prouvé.

## Porte de sortie / révision

- Profiler à chaque major release et tagger les règles > 200 ms comme
  candidates PyO3.
- Si > 5 règles dépassent ce seuil, envisager un sous-projet
  `suzerain-rs` (extension Rust) avant de pousser le palier suivant.
