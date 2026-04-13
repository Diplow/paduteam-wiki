---
name: ingest-batch
description: >
  Ingère plusieurs transcripts PaduTeam liés à un même sujet en un seul passage, pour produire
  des fiches cohérentes sans redondance. Construit une synthèse cross-vidéos (thèses récurrentes,
  évolutions, contradictions) puis dispatche vers les skills write-* avec ce contexte consolidé.
  Un seul commit et une seule PR par batch. Déclencher quand l'utilisateur dit "ingérer le bloc X",
  "ingérer toutes les vidéos sur Y", "batch ingest", "ingérer la série sur Z", ou quand il fournit
  un sujet couvert par plusieurs transcripts non ingérés.
date created: Monday, April 13th 2026, 12:00:00 pm
date modified: Monday, April 13th 2026, 12:00:00 pm
skill_version: ingest-batch-2026-04-13
---

# Skill : Ingestion Batch par sujet

## Vue d'ensemble

Cette skill ingère **plusieurs transcripts liés à un même sujet** en un seul passage. Elle existe parce qu'ingérer une vidéo à la fois fait perdre la cohérence thématique : si 5 vidéos couvrent la guerre PS/LFI, l'enjeu "Plus jamais PS" doit être écrit avec la vue d'ensemble des 5, pas enrichi incrémentalement avec des redondances.

**Conventions partagées** (nommage, wikilinks, frontmatter, taxonomie, style, git) : voir `BUILD.md`.

**Skills appelées :**
- `gather-context` — état actuel du vault sur le sujet
- `write-video` — fiche vidéo (1 par transcript du batch)
- `write-entity` — individus et organisations
- `write-concept` — concepts analytiques
- `write-enjeu` — enjeux stratégiques (bénéficiaire principal du batch)

**Différences clés avec `paduteam-knowledge` (ingest-video) :**
- Un seul commit et une seule PR pour tout le batch
- Un contexte batch consolidé qui complète le contexte vault de `gather-context`
- Les fiches enjeux/concepts sont écrites une fois, avec la vue d'ensemble — pas enrichies N fois
- Ordre chronologique des vidéos pour que les fiches reflètent l'évolution temporelle

---

## Entrée

L'utilisateur fournit l'une des formes suivantes :
- **Un sujet** : thème, enjeu, concept (ex: "guerre des gauches", "Palestine", "municipales 2026")
- **Une liste explicite de vidéos** : titres ou slugs
- **Un bloc temporel** : "toutes les vidéos de septembre 2025 sur les gilets jaunes"

Si rien n'est fourni, demander le sujet — cette skill ne sélectionne pas automatiquement comme `paduteam-knowledge`.

---

## Workflow

### Étape 1 — Identifier le périmètre du batch

1. **Si sujet fourni** :
   - Lire `Sources/Inventaire PaduTeam.md`
   - Grep les transcripts de `Sources/Transcripts/` pour les mots-clés du sujet (3-8 mots-clés + synonymes)
   - Croiser avec l'inventaire pour ne garder que ceux **avec transcript disponible et sans fiche** (colonne Fiche vide)
2. **Si liste explicite** : résoudre chaque entrée au fichier transcript correspondant
3. **Vérifier la taille** : 2-10 vidéos est la cible. Au-delà de 10, proposer à l'utilisateur de scinder.
4. **Présenter la liste** à l'utilisateur pour validation avant de continuer.

### Étape 2 — État du vault (gather-context)

Appeler `gather-context` avec le sujet du batch. Cela produit `Sources/.context-tmp.md` avec l'état actuel du vault sur le sujet (fiches existantes, enjeux liés, entités connues).

**Note** : à ce stade le contexte reflète ce que le vault savait *avant* le batch. Il sera complété par la synthèse batch à l'étape 4.

### Étape 3 — Branche git

1. Générer un slug thématique (pas un slug vidéo) : minuscules, sans accents, tirets, ~40 chars max. Exemples : `guerre-des-gauches`, `palestine-automne-2025`, `municipales-2026`.
2. `git checkout develop && git pull origin develop`
3. `git checkout -b ingest-batch/<slug>`

### Étape 4 — Lire et synthétiser tous les transcripts

**Ordre : chronologique** (de la plus ancienne à la plus récente — consulter la colonne Date de l'inventaire).

Pour chaque transcript :
1. Le lire en entier
2. Extraire les éléments analytiques (thèses, mécanismes, entités, citations marquantes avec timestamps)
3. Noter la date et la position de la vidéo dans l'évolution du sujet

Une fois tous les transcripts lus, **construire une synthèse batch** — la sortie principale de cette étape. Elle complète `Sources/.context-tmp.md` en ajoutant une section :

```markdown
## Synthèse batch : {SUJET}

### Vidéos du batch (ordre chronologique)
- {Date} — {Titre} — {youtube_id} — {1 ligne sur l'apport spécifique}
- ...

### Thèses récurrentes (reviennent dans 2+ vidéos)
- **{Thèse}** : présente dans {liste vidéos}. {Résumé consolidé.}
- ...

### Évolutions et inflexions
- {Ce qui a changé entre la vidéo la plus ancienne et la plus récente — virages, durcissements, nuances ajoutées}

### Contradictions ou tensions internes
- {Si une vidéo dit X et une autre dit Y sur le même point, le noter. Ne pas résoudre — restituer.}

### Entités cross-vidéos
- **Individus** : {qui revient dans combien de vidéos, avec quel rôle}
- **Organisations** : idem
- **Concepts** : idem

### Enjeux touchés par le batch
- {Pour chaque enjeu, quels arguments le batch apporte — récurrences, nouveaux arguments, évolutions}
```

Cette synthèse est la valeur ajoutée principale de la skill. Elle est lue par toutes les write-* qui suivent.

### Étape 5 — Lire les fiches existantes

```bash
ls Individus/ && ls Organisations/ && ls Concepts/ && ls Videos/ && ls Enjeux/
```

Pour chaque entité, concept, enjeu repérés dans la synthèse, déterminer si la fiche existe.

### Étape 6 — Rédiger les fiches

**Ordre d'écriture** (différent de ingest-video) :

1. **Enjeux d'abord** — appeler `write-enjeu` pour chaque enjeu touché par le batch. C'est l'étape qui bénéficie le plus de la synthèse. Écrire/enrichir avec la vue d'ensemble : consolidation des arguments récurrents, identification des adversaires/alliés, évolution de la position PaduTeam dans le temps.
2. **Concepts** — appeler `write-concept` pour chaque concept, avec la synthèse. Si un concept revient dans plusieurs vidéos du batch avec des nuances différentes, `write-concept` doit les intégrer toutes.
3. **Entités** — appeler `write-entity` pour chaque individu/organisation significatif. Le batch peut révéler un arc narratif (ex: évolution de la position PaduTeam sur un individu) — le restituer.
4. **Vidéos** — appeler `write-video` pour chaque transcript du batch. Chaque fiche vidéo reste individuelle mais peut référencer les autres vidéos du batch via wikilinks.

**Principe** : les enjeux/concepts/entités sont écrits **une fois** avec la vue d'ensemble, pas N fois incrémentalement. Les fiches vidéo sont écrites N fois (une par transcript) mais en aval, donc elles peuvent pointer vers les fiches enjeux/concepts/entités déjà enrichies.

### Étape 7 — Vérification liens orphelins

Idem ingest-video : parcourir les fiches créées/modifiées, vérifier que chaque `[[wikilink]]` pointe vers un fichier existant. Créer des ébauches pour les liens restants.

### Étape 8 — Vérification orthographique

Idem ingest-video, mais effectuée en une passe sur toutes les fiches du batch.

### Étape 9 — Mise à jour de l'Inventaire

Mettre à jour `Sources/Inventaire PaduTeam.md` : remplir la colonne **Fiche** pour **chacune** des vidéos du batch.

### Étape 10 — Commit, push et PR

**Un seul commit pour tout le batch** :

```
ingest-batch: {SUJET} ({N} vidéos)

Vidéos ingérées:
- {Titre 1}
- {Titre 2}
- ...

Fiches créées: X (liste)
Fiches enrichies: Y (liste)
Corrections ortho: Z (liste si applicable)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

1. `git add` fichier par fichier (pas `-A`)
2. Commit avec le message ci-dessus
3. `git push -u origin ingest-batch/<slug>`
4. PR vers `develop` avec :
   - Liste des vidéos ingérées (titres + dates)
   - Résumé de la synthèse batch
   - Liste des fiches créées par catégorie
   - Liste des fiches enrichies
   - Enjeux touchés

### Étape 11 — Résumé à l'utilisateur

Présenter :
- Nombre de vidéos ingérées et cohérence temporelle du batch
- Synthèse batch en quelques puces (thèses récurrentes, évolutions, contradictions)
- Nombre de fiches créées vs enrichies par catégorie
- Enjeux particulièrement enrichis par le batch
- Lien vers la PR

---

## Règles

- **Ne jamais ingérer en boucle vidéo par vidéo.** Si on se retrouve à appeler `write-enjeu` plusieurs fois pour le même enjeu dans un même batch, c'est un bug : la synthèse batch doit permettre un seul appel par enjeu avec toute l'info.
- **Ordre chronologique.** Les vidéos sont lues dans l'ordre chronologique pour que l'évolution temporelle soit lisible dans la synthèse.
- **Une seule PR.** Même si le batch couvre 10 vidéos, il produit 1 branche, 1 commit, 1 PR. C'est la cohérence thématique qu'on review, pas chaque vidéo isolément.
- **Taille du batch.** 2-10 vidéos. Moins de 2, utiliser `paduteam-knowledge`. Plus de 10, scinder en sous-batches thématiques.
- **Ne pas doublonner avec gather-context.** `gather-context` donne l'état du vault *avant* le batch. La synthèse batch donne ce que les transcripts apportent. Les deux cohabitent dans `.context-tmp.md`.
- **Ne jamais référencer le « batch » dans les fiches.** Le découpage en batches est un artefact du workflow d'ingestion — les lecteurs des fiches (Concepts, Enjeux, Individus, Organisations, Vidéos) n'ont pas accès à cette information et ne peuvent pas comprendre des formulations comme « batch D », « ce batch », « le corpus batch », « cf. batch F », « apports du batch X ». Reformuler en nommant le sujet réel (« l'arc Rima Hassan », « le corpus Gaza », « les vidéos sur le sionisme de gauche », ou simplement supprimer la référence). Cette règle ne s'applique pas aux fichiers de suivi d'ingestion (ex: `GAZA.md`, `FEMINISME.md`) qui sont explicitement des fichiers de travail.

---

## Feedback système

À la fin du batch, évaluer si la synthèse a révélé des éléments qui devraient mettre à jour le système :
- Un thème ou un enjeu qui mérite d'entrer dans la taxonomie de `BUILD.md` ?
- Un concept structurant qui mériterait d'être mentionné dans `CLAUDE.md` ?
- Une contradiction récurrente entre vidéos qui suggère que la position PaduTeam a évolué et que les fiches anciennes doivent être révisées ?

Signaler à l'utilisateur sans modifier automatiquement.
