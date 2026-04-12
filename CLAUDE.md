---
date created: Wednesday, April 1st 2026, 5:27:10 pm
date modified: Thursday, April 2nd 2026, 10:27:49 am
---
# Graphiked — Projet de documentation PaduTeam

## Objectif

Construire un graphe de connaissances Obsidian documentant l'univers analytique de la PaduTeam, chaîne YouTube marxiste-communiste francophone. Le vault capture fidèlement leurs analyses sans les challenger.

## Usage du vault

Ce vault sert **deux fonctions** :

1. **Construction** — Ingérer des vidéos PaduTeam pour enrichir la base de connaissances (skill `paduteam-knowledge`)

2. **Consultation** — Répondre aux questions sur la politique française, la géopolitique ou les concepts selon l'angle analytique PaduTeam

**Quand l'utilisateur pose une question** (sur une personnalité, un parti, une élection, un concept...) :
- Chercher d'abord dans `Individus/`, `Organisations/`, `Concepts/`, `Videos/`, `Enjeux/` si des fiches pertinentes existent
- Répondre en restituant l'analyse PaduTeam, pas une analyse externe ou "neutre"
- Citer les sources (fiches, vidéos) quand pertinent
- Si le vault ne contient pas d'info sur le sujet, le signaler plutôt que d'inventer

Le vault est une base de connaissances vivante — l'interroger fait partie de son usage normal.

## Structure

- `Sources/` — Matériau brut (transcripts de vidéos YouTube, inventaire)
- `Videos/` — 1 fiche par vidéo ingérée
- `Individus/` — 1 fiche par personne
- `Organisations/` — 1 fiche par parti/asso/média
- `Concepts/` — 1 fiche par concept analytique
- `Enjeux/` — 1 fiche par combat stratégique récurrent
- `Skills/` — Skills Claude pour automatiser l'ingestion

## Conventions générales

- **Wikilinks**: `[[Nom Exact du Fichier]]` sans chemin, sans .md
- **Aliases**: définis en frontmatter YAML, permettent les liens via `[[Nom réel|alias]]`
- **Langue**: français, ton analytique (pas encyclopédique)
- **Principe fondamental**: restituer la vision PaduTeam telle quelle, sans modérer ni nuancer

## Taxonomie des tags

5 axes structurent le tagging (voir `Skills/paduteam-knowledge/SKILL.md` pour le détail complet):

1. **domaine** — champ d'analyse (politique-intérieure, géopolitique, économie, théorie, société)
2. **thèmes** — sujets spécifiques récurrents (vocabulaire contrôlé, extensible)
3. **format** — série/format vidéo (vidéos uniquement)
4. **enjeux** — combats stratégiques récurrents de la PaduTeam
5. **statut** — niveau de complétude (ébauche, développé, mature)

**Le tag `paduteam` n'est pas utilisé** — tout le vault est PaduTeam par définition.

## Membres de la PaduTeam

- **Padu** (Pas Dühring) — Pédopsychiatre, créateur, marxiste-léniniste
- **Chris** — Cadre industrie, fondateur de *Positions Revue*, concepteur du Saint Graphique
- **Zoé** (Dr Zoé) — Médecin généraliste, féministe matérialiste
