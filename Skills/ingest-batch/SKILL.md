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
- Quand un fichier de suivi est utilisé (ex. `FEMINISME.md`), la PR cible une branche thématique dédiée (`theme/<parent>`), pas `develop` directement

---

## Entrée

L'utilisateur fournit l'une des formes suivantes :
- **Un fichier de suivi d'ingestion** (forme recommandée) : ex. `FEMINISME.md`, `GAZA.md`. Le fichier liste plusieurs sous-batches thématiques avec statut (`⏳ en attente`, `✅ fait`, etc.), slug de branche, et liste de vidéos cochables. La skill prend **le premier batch non réalisé** dans l'ordre du fichier (ou l'ordre recommandé s'il est spécifié en fin de fichier), **sauf si l'utilisateur désigne explicitement un batch** (ex: « fais le batch C de FEMINISME.md »).
- **Un sujet** : thème, enjeu, concept (ex: "guerre des gauches", "Palestine", "municipales 2026")
- **Une liste explicite de vidéos** : titres ou slugs
- **Un bloc temporel** : "toutes les vidéos de septembre 2025 sur les gilets jaunes"

Si rien n'est fourni, demander le sujet ou le fichier de suivi — cette skill ne sélectionne pas automatiquement comme `paduteam-knowledge`.

**Note worktree** : cette skill n'a **pas besoin** d'être lancée dans un worktree git. Elle travaille directement dans le répertoire principal sur une branche dédiée. Ne pas créer de worktree pour l'exécuter.

---

## Workflow

### Étape 1 — Identifier le périmètre du batch

1. **Si fichier de suivi fourni** (ex. `FEMINISME.md`) :
   - Lire le fichier en entier
   - Identifier les sous-batches et leur statut. Chaque batch a typiquement un titre (`## Batch A — ...`), un **Statut**, un **Slug branche**, et une liste de vidéos (`- [ ]` / `- [x]`).
   - **Si l'utilisateur a désigné un batch explicitement** (ex. « batch C »), prendre celui-là.
   - **Sinon**, prendre le **premier batch non réalisé** dans l'ordre du fichier (ou dans l'ordre recommandé si la section « Notes et décisions » en définit un).
   - Résoudre chaque vidéo cochable (`- [ ]`) du batch au transcript correspondant dans `Sources/Transcripts/` via `Sources/Inventaire PaduTeam.md`.
   - Retenir le **thème parent** (ex. `feminisme` pour `FEMINISME.md`) — il servira pour la branche parente de merge (voir Étape 3).
2. **Si sujet fourni** :
   - Lire `Sources/Inventaire PaduTeam.md`
   - Grep les transcripts de `Sources/Transcripts/` pour les mots-clés du sujet (3-8 mots-clés + synonymes)
   - Croiser avec l'inventaire pour ne garder que ceux **avec transcript disponible et sans fiche** (colonne Fiche vide)
3. **Si liste explicite** : résoudre chaque entrée au fichier transcript correspondant
4. **Vérifier la taille** : 2-10 vidéos est la cible. Au-delà de 10, proposer à l'utilisateur de scinder.
5. **Présenter la liste** à l'utilisateur pour validation avant de continuer.

### Étape 2 — État du vault (gather-context)

Appeler `gather-context` avec le sujet du batch. Cela produit `Sources/.context-tmp.md` avec l'état actuel du vault sur le sujet (fiches existantes, enjeux liés, entités connues).

**Note** : à ce stade le contexte reflète ce que le vault savait *avant* le batch. Il sera complété par la synthèse batch à l'étape 4.

### Étape 3 — Branche git

**Cas 1 — fichier de suivi (thème parent)** :

Le batch ne merge **pas** vers `develop` directement, mais vers une **branche thématique dédiée** qui agrège tous les sous-batches d'un même fichier de suivi. Cette branche thématique est elle-même mergée vers `develop` à la fin du travail global sur le thème (hors scope de cette skill).

1. Déterminer le **slug thématique parent** à partir du nom du fichier de suivi : `FEMINISME.md` → `theme/feminisme`, `GAZA.md` → `theme/gaza`, etc.
2. `git fetch origin`
3. Vérifier si la branche parente existe :
   - **Si oui** : `git checkout theme/<parent> && git pull origin theme/<parent>` (si suivi distant).
   - **Si non** : la créer à partir de `develop` à jour — `git checkout develop && git pull origin develop && git checkout -b theme/<parent>` — et la pusher (`git push -u origin theme/<parent>`).
4. Si le slug du sous-batch est déjà défini dans le fichier de suivi (champ `Slug branche`), l'utiliser tel quel. Sinon, générer un slug : minuscules, sans accents, tirets, ~40 chars max.
5. Créer la branche de travail depuis la branche parente : `git checkout -b ingest-batch/<slug>` (à partir de `theme/<parent>`).

**Cas 2 — sujet libre ou liste explicite (pas de fichier de suivi)** :

1. Générer un slug thématique (pas un slug vidéo) : minuscules, sans accents, tirets, ~40 chars max. Exemples : `guerre-des-gauches`, `palestine-automne-2025`, `municipales-2026`.
2. `git checkout develop && git pull origin develop`
3. `git checkout -b ingest-batch/<slug>` — dans ce cas la PR cible directement `develop`.

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

### Étape 9 — Mise à jour de l'Inventaire et du fichier de suivi

1. Mettre à jour `Sources/Inventaire PaduTeam.md` : remplir la colonne **Fiche** pour **chacune** des vidéos du batch.
2. **Si un fichier de suivi a été utilisé** (ex. `FEMINISME.md`) : cocher chaque vidéo ingérée (`- [ ]` → `- [x]`) et mettre à jour le **Statut** du sous-batch (`⏳ en attente` → `✅ fait` ou équivalent). Ajouter éventuellement une note courte sur ce qui est sorti du batch (ex. fiches créées majeures).

### Étape 10 — Commit et push

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

**Ne pas créer la PR** — l'utilisateur s'en charge manuellement à la fin. S'arrêter après le push et signaler la branche poussée dans le résumé de l'Étape 11.

### Étape 11 — Résumé à l'utilisateur

Présenter :
- Nombre de vidéos ingérées et cohérence temporelle du batch
- Synthèse batch en quelques puces (thèses récurrentes, évolutions, contradictions)
- Nombre de fiches créées vs enrichies par catégorie
- Enjeux particulièrement enrichis par le batch
- Nom de la branche poussée (la PR sera créée manuellement par l'utilisateur)

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
