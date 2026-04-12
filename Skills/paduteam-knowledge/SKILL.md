---
name: paduteam-knowledge
description: >
  Orchestre l'ingestion d'un transcript de vidéo PaduTeam dans la base de connaissances Obsidian.
  Coordonne les skills spécialisées : gather-context pour la recherche, puis write-video,
  write-entity, write-concept et write-enjeu pour la rédaction des fiches.
  Gère aussi le workflow git (branche, commit, PR), la vérification ortho et les liens orphelins.
  Déclencher quand l'utilisateur dit "ingérer", "ajouter au vault", "créer les fiches",
  "analyser cette vidéo pour Obsidian", ou toute demande combinant un transcript PaduTeam et la base de connaissances.
date created: Tuesday, March 31st 2026, 10:29:39 am
date modified: Sunday, April 12th 2026, 7:00:00 pm
skill_version: ingest-2026-04-12
---

# Skill : Ingestion PaduTeam → Knowledge Vault (orchestrateur)

## Vue d'ensemble

Cette skill orchestre l'ingestion d'un transcript de vidéo PaduTeam. Elle ne rédige pas directement les fiches — elle coordonne les skills spécialisées qui le font.

**Conventions partagées** (nommage, wikilinks, frontmatter, taxonomie, style, git) : voir `BUILD.md`.

**Skills appelées :**
- `gather-context` — rassemble le contexte vault sur les sujets de la vidéo
- `write-video` — rédige la fiche vidéo
- `write-entity` — rédige/enrichit les fiches individus et organisations
- `write-concept` — rédige/enrichit les fiches concepts
- `write-enjeu` — rédige/enrichit les fiches enjeux

---

## Workflow

### Étape 1 — Sélection de la vidéo

Si l'utilisateur ne fournit ni URL, ni titre, ni transcript :

1. Lire `Sources/Inventaire PaduTeam.md`
2. Parcourir la table du haut (vidéos les plus récentes)
3. Trouver la **première ligne avec transcript mais sans fiche** (colonne 4 non vide, colonne 5 vide)
4. Si toutes les vidéos avec transcript ont une fiche, le signaler

### Étape 2 — Branche git

1. Générer le slug depuis le titre (minuscules, sans accents, tirets, ~50 chars max)
2. `git checkout develop && git pull origin develop`
3. `git checkout -b ingest/<slug>`

### Étape 3 — Lire le transcript

**Toujours chercher dans le vault d'abord** (`Sources/Transcripts/`), avant toute extraction YouTube.

1. Chercher un fichier correspondant au titre (correspondance partielle)
2. Si trouvé → lire directement
3. Si non trouvé → extraire via `paduteam-transcript`, sauvegarder dans `Sources/Transcripts/`

Lire le transcript en entier.

### Étape 4 — Analyser le contenu

Identifier à partir du transcript :

1. **Métadonnées** : titre, date, domaine, `youtube_id` (récupérer depuis l'Inventaire PaduTeam — colonne Lien, extraire l'ID de l'URL `watch?v=`)
2. **Individus** mentionnés significativement
3. **Organisations** mentionnées
4. **Concepts analytiques** utilisés
5. **Enjeux stratégiques** avancés par cette vidéo
6. **Thèses principales** : résumé, projections, mécanismes cause-conséquence

### Étape 5 — Gather context

Appeler `gather-context` avec les sujets principaux de la vidéo (thèmes, enjeux, concepts clés identifiés à l'étape 4).

Le contexte produit dans `Sources/.context-tmp.md` sera utilisé par toutes les skills write-* qui suivent.

### Étape 6 — Lire les fiches existantes

```bash
ls Individus/ && ls Organisations/ && ls Concepts/ && ls Videos/ && ls Enjeux/
```

Pour chaque entité identifiée à l'étape 4, déterminer si la fiche existe ou non.

### Étape 7 — Rédiger les fiches

Appeler les skills spécialisées dans cet ordre :

1. **`write-video`** — Créer la fiche vidéo. Entrée : transcript analysé + contexte.

2. **`write-entity`** — Pour chaque individu et organisation mentionné significativement. Entrée : ce que le transcript dit de l'entité + fiche existante (si applicable) + contexte.

3. **`write-concept`** — Pour chaque concept analytique identifié. Entrée : ce que le transcript dit du concept + fiche existante + contexte.

4. **`write-enjeu`** — Pour chaque enjeu stratégique avancé par la vidéo. Entrée : ce que le transcript apporte à l'enjeu + fiche existante + contexte. **Note** : write-enjeu bénéficie particulièrement du contexte multi-vidéos — c'est la skill qui produit le plus de valeur ajoutée par rapport à l'ancien workflow monolithique.

### Étape 8 — Vérification des liens orphelins

Vérifier que chaque `[[wikilink]]` dans les fiches créées/modifiées pointe vers un fichier existant. Si des liens orphelins restent, créer les fiches manquantes (même minimales via `write-entity` ou `write-concept`).

### Étape 9 — Vérification orthographique des noms

Les transcripts auto-générés produisent des erreurs sur les noms propres :

1. **Repérer** les noms douteux (transcription phonétique, incohérences, noms peu connus)
2. **Croiser avec le vault** : si une fiche existe avec une orthographe différente, utiliser celle du vault
3. **Vérifier par recherche web** les noms qui restent douteux
4. **Corriger** : renommer fichiers + mettre à jour wikilinks et contenu
5. **Rapporter** les corrections (nom erroné → nom corrigé)

Se concentrer sur les noms étrangers et les personnalités secondaires.

### Étape 10 — Mise à jour de l'Inventaire

Mettre à jour `Sources/Inventaire PaduTeam.md` : remplir la colonne **Fiche** avec `[[Titre de la fiche vidéo]]`.

### Étape 11 — Commit, push et PR

Suivre le workflow git défini dans `BUILD.md` :

1. `git status` pour lister les fichiers modifiés
2. `git add` par nom (pas `-A`)
3. Commit structuré :
   ```
   ingest: TITRE ABRÉGÉ DE LA VIDÉO

   Fiches créées: X (liste)
   Fiches enrichies: Y (liste)
   Corrections ortho: Z (liste si applicable)

   Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
   ```
4. `git push -u origin ingest/<slug>`
5. PR vers `develop` avec résumé d'ingestion

### Étape 12 — Résumé à l'utilisateur

Présenter :
- Nombre de fiches créées vs enrichies
- Liste des nouvelles fiches par catégorie
- Fiches existantes enrichies
- Liens orphelins restants (normalement 0)
- Enjeux identifiés ou enrichis
- Corrections orthographiques (nom erroné → nom corrigé)
- **Lien vers la PR** pour review

---

## Feedback système

À la fin de chaque ingestion, évaluer si le transcript a révélé quelque chose qui devrait mettre à jour le système :
- Nouveau thème récurrent non couvert par la taxonomie ?
- Nouveau concept analytique qui mériterait d'être dans `CLAUDE.md` ?
- Nouvel enjeu à ajouter au vocabulaire contrôlé ?
- Correction à apporter aux conventions de `BUILD.md` ?

Si oui, le signaler à l'utilisateur dans le résumé (pas de modification automatique — l'utilisateur décide).
