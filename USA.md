---
name: USA — suivi d'ingestion
description: Suivi du travail d'ingestion batch des vidéos PaduTeam sur les États-Unis — présidence Trump 2, gauche américaine émergente (DSA/Mamdani), désagrégation de l'empire américain, rapport USA/France sur la question raciale et impérialiste.
date created: Sunday, April 19th 2026, 3:00:00 pm
date modified: Sunday, April 19th 2026, 3:00:00 pm
---
# USA — Suivi d'ingestion

Fichier de travail pour suivre l'ingestion par sous-batches thématiques des transcripts PaduTeam traitant substantiellement de la politique intérieure américaine, de l'impérialisme US (volet interventions internes) et de la gauche américaine émergente. Complémentaire à `GEOPOLITIQUE.md` qui couvre l'angle impérialiste externe (Iran, Venezuela, Ukraine).

**Critère de sélection initial** : titres mentionnant Trump, États-Unis, New York, Californie, Los Angeles, Mamdani, DSA, primaires démocrates, Rubio, Groenland, colonialisme américain — ou analyse PaduTeam des bifurcations internes à la société américaine.

---

## Batch A — Trump et la gauche américaine émergente

**Statut** : ⏳ à rejouer (fiches existantes à enrichir selon nouvelles exigences de finesse analytique)
**Slug branche** : `usa-rejeu-finesse-analytique`

Bloc cohérent couvrant un an et demi de politique américaine vue par la PaduTeam : de la réélection de Trump (nov 2024) à la victoire Mamdani à NYC (nov 2025) puis aux tensions de la Californie (début 2026) et au discours colonial assumé de Rubio (Munich, fév 2026). Le fil : désagrégation de l'empire américain par le bas (NYC/Californie bifurquent à gauche) pendant que Trump/Rubio assument le colonialisme sans masque.

**Note de rejeu** : ce batch a été ingéré une première fois le 2026-04-19 sous l'ancienne architecture `ingest-batch` (lecture monolithique des 6 transcripts + compaction avant écriture). L'analyse comparative fiche Mamdani ↔ transcript a montré une perte analytique substantielle (thèses théoriques manquantes, données chiffrées absentes, mécanismes matérialistes résumés en une ligne). Ce rejeu utilise la nouvelle architecture (un subagent par vidéo, pas de compaction) et vise l'**enrichissement** des fiches existantes selon les exigences de finesse du briefing — pas leur recréation.

- [ ] CE QUE SIGNIFIE VRAIMENT L ELECTION DE TRUMP (nov-déc 2024)
- [ ] NEW YORK BASCULE DANS L'ISLAMO-GAUCHISME COMMENT ZOHRAN MAMDANI A GAGNÉ (4-5 nov 2025)
- [ ] MAMDANI À GAUCHE DE MÉLENCHON (5-6 nov 2025)
- [ ] TRUMP VEUT ANNEXER LE GROENLAND (5 janv 2026)
- [ ] RÉVOLTES À LOS ANGELES VERS UNE RÉPUBLIQUE SOVIÉTIQUE DE CALIFORNIE (début 2026)
- [ ] TRUMP ET RUBIO REGRETTENT LE TEMPS BÉNI DES COLONIES (25 fév 2026)

**Fiches existantes (à enrichir)** : [[CE QUE SIGNIFIE VRAIMENT L ELECTION DE TRUMP]], [[NEW YORK BASCULE DANS L ISLAMO-GAUCHISME COMMENT ZOHRAN MAMDANI A GAGNE]], [[MAMDANI A GAUCHE DE MELENCHON]], [[TRUMP VEUT ANNEXER LE GROENLAND]], [[REVOLTES A LOS ANGELES VERS UNE REPUBLIQUE SOVIETIQUE DE CALIFORNIE]], [[TRUMP ET RUBIO REGRETTENT LE TEMPS BENI DES COLONIES]], [[Desagregation de l empire americain]], [[Gauche de droite]], [[Kamala Harris]], [[Alexandria Ocasio-Cortez]], [[Gavin Newsom]], [[Democratic Socialists of America]], [[Parti Democrate]], [[Anti-imperialisme]], [[Moisation]], [[Pacte raciste]], [[Marco Rubio]], [[Zohran Mamdani]], [[Donald Trump]]

---

## Notes et décisions

- **Ordre de lancement** : chronologique strict (ordre de la liste ci-dessus). Rationale : permet au subagent de la vidéo Mamdani nov-2025 de voir les fiches Concepts/Individus enrichies par la vidéo Trump nov-2024, et ainsi de suite.
- **Exigences de finesse renforcées** (contre-mesure à la perte observée) :
  - ≥2-3 données chiffrées significatives par fiche vidéo (participation, %, populations, loyers, etc.)
  - ≥1 thèse théorique explicitement formulée (pas juste nommée via wikilink) — ex: pour Mamdani « jeunes femmes = classe révolutionnaire » doit apparaître en clair, pas seulement [[Sujet révolutionnaire]]
  - Formulations marquantes citées littéralement avec timestamp quand pertinent
  - Mécanismes (matérialistes, sociologiques, politiques) restitués avec leurs étapes, pas résumés en une ligne
- **Périmètre strict** : ne pas étendre le batch à d'autres vidéos USA lors du rejeu — garder les 6 initiales pour pouvoir comparer proprement avant/après.
- **Enjeu de consolidation** : le subagent final lira les 6 fiches vidéo enrichies pour éventuellement créer/enrichir [[Anti-imperialisme]] (colonialisme assumé Rubio/Groenland), [[Moisation]] (variante américaine), [[Pacte raciste]] (contrat racial US), et potentiellement un nouvel enjeu autour de la désagrégation par bifurcation (NYC + Californie).
