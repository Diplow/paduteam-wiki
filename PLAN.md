# PLAN — Diagnostic et automatisation du vault Graphiked

_Généré le 2026-04-25. Ce fichier décrit l'état du vault et les actions à mener._

---

## 1. Diagnostic des transcripts manquants

### Chiffres bruts

| Élément | Valeur |
|---|---|
| Fichiers dans `Sources/Transcripts/` | **612** (dont ~5 scripts .py + `__pycache__`) |
| Vidéos suivies dans `PADUTEAM_CHRONOLOGIQUE.md` | **426** (batches 01-40, 18 mois) |
| Batches ✅ ingérés | **40** (tous les batches 01-40) |
| Batches ⏳ en attente | **0** |
| Transcripts absents dans batches ingérés | **8** explicitement marqués |

_Note : au moment du diagnostic (worktree créé depuis main), 18 absents étaient identifiés. Sur develop, les batches 34, 37 et 39 ont été complétés depuis — il reste 8 absents._

### Les 8 transcripts manquants (marqués `⚠️ transcript absent` sur develop)

| Batch | Vidéo | Période |
|---|---|---|
| 10 | CHARLIE HEBDO EST-IL RÉACTIONNAIRE ? | 2025-W09-W10 |
| 18 | THAÏS : les VSS l'ont rendue NAZIE !? | 2025-W25-W26 |
| 18 | Les CHÔMEURS sont-ils VRAIMENT des ASSISTÉS ? | 2025-W25-W26 |
| 18 | MÉLENCHON AFFRONTE une HORDE DE BOURGEOIS aux GRANDES GUEULES !! | 2025-W25-W26 |
| 26 | LA GUERRE AU RN EST DÉCLARÉE ?! | 2025-W41-W42 |
| 26 | MACRON VA PARTIR ! LES BANQUIERS VONT LE DÉGAGER | 2025-W41-W42 |
| 26 | SONDAGE ANTI-MÉLENCHON : LES MENSONGES DE L'IFOP VS LA VÉRITÉ DU SAINT GRAPHIQUE | 2025-W41-W42 |
| 30 | BÉGAUDEAU se RIDICULISE sur le DÉTERMINISME et le MARXISME !! | 2025-W49-W50 |

### Analyse du pattern

**Cause probable : délai de génération des sous-titres automatiques YouTube.**

- Les batches 35-39 couvraient février-avril 2026. Les absents des batches 37, 39 et 34 ont depuis été récupérés (commits de complétion sur develop).
- Le batch 39 avait été ingéré le 2026-04-23, soit quelques jours après la publication (YouTube prend 24-72h pour générer les sous-titres FR).
- Le batch 10 (CHARLIE HEBDO, mars 2025) est un cas isolé plus ancien — soit vidéo courte/musicale sans sous-titres, soit dépublicée puis re-uploadée.
- Les batches 26 (oct 2025) et 37 (mars 2026) ont plusieurs absents groupés, ce qui suggère un problème réseau ou rate-limit lors de l'extraction plutôt qu'une absence structurelle de sous-titres.

**Script pour tenter de re-télécharger :**

```bash
python Sources/Transcripts/batch_transcripts.py --dry-run
```

Cela liste les vidéos de l'inventaire sans transcript. Ensuite :

```bash
python Sources/Transcripts/batch_transcripts.py
```

`batch_transcripts.py` (sans flag) tente d'extraire tous les transcripts manquants répertoriés dans l'inventaire. Il s'arrête après 3 échecs consécutifs.

---

## 2. Diagnostic des vidéos récentes et batches en attente

### Batches ingérés sur develop

Tous les 40 batches sont ✅ fait sur develop (batches 35 et 36 mergés le 2026-04-24, contrairement à ce que montrait le worktree de diagnostic). Aucun batch en attente.

### Vidéos sorties après le 20 avril 2026

`PADUTEAM_CHRONOLOGIQUE.md` a été généré le 2026-04-20 et couvre jusqu'au 2026-04-20. Aujourd'hui c'est le 2026-04-25. Il y a probablement **1-3 nouvelles vidéos** publiées cette semaine (rythme PaduTeam : ~3 vidéos/semaine) qui ne sont ni dans l'inventaire ni dans le fichier de suivi.

Pour vérifier :

```bash
python Sources/Transcripts/batch_transcripts.py --recent 5 --dry-run
```

---

## 3. Plan d'automatisation hebdomadaire

### Objectif

Chaque semaine (ou à la demande), enchaîner automatiquement :
1. Découverte des nouvelles vidéos et extraction de leurs transcripts
2. Mise à jour de l'inventaire et du fichier de suivi chronologique
3. Ingestion des nouveaux batches (création des fiches)

### Étape A — Récupérer les nouveaux transcripts

```bash
# Récupère les 20 dernières vidéos de la chaîne, extrait les manquants, met à jour l'inventaire
python Sources/Transcripts/batch_transcripts.py --recent 20
```

**Ce que ça fait :** appelle `yt-dlp --flat-playlist --playlist-end 20`, compare avec l'inventaire, extrait les sous-titres FR pour les nouvelles vidéos, met à jour `Sources/Inventaire PaduTeam.md`.

**Durée estimée :** 5-10 min (20 × 8s de pause anti-ban).

### Étape B — Mettre à jour le fichier de suivi chronologique

```bash
python Sources/Transcripts/generate_chronological.py
```

**Ce que ça fait :** interroge la chaîne via `yt-dlp`, récupère les dates de publication, regroupe les vidéos en batches de 2 semaines ISO, met à jour `PADUTEAM_CHRONOLOGIQUE.md` en **préservant les statuts ✅ existants**.

**Durée estimée :** 5-15 min (récupère jusqu'à 600 vidéos sans `--flat-playlist`).

**Attention :** `generate_chronological.py --force` écrase tous les statuts — ne l'utiliser que pour régénérer depuis zéro. Sans `--force`, les batches ✅ sont préservés.

### Étape C — Ingérer les nouveaux batches

```bash
python Sources/Transcripts/run_ingest.py
```

**Ce que ça fait :** lit `PADUTEAM_CHRONOLOGIQUE.md`, identifie les batches ⏳, invoque `claude ingest-batch N` pour chacun. Gère automatiquement les rate limits (pause 2h).

**Durée estimée :** 30-60 min par batch (sous-agents Claude par vidéo).

### Enchaînement complet en une commande

Il n'existe pas encore de script d'orchestration. La commande ci-dessous enchaîne les 3 étapes manuellement :

```bash
python Sources/Transcripts/batch_transcripts.py --recent 20 && \
python Sources/Transcripts/generate_chronological.py && \
python Sources/Transcripts/run_ingest.py
```

### Ce qu'il faudrait créer pour une vraie automatisation

Un script `Sources/Transcripts/weekly_update.py` (à créer) qui :
1. Lance `batch_transcripts.py --recent 20`
2. Lance `generate_chronological.py`
3. Lance `run_ingest.py`
4. Écrit un rapport dans `Sources/Transcripts/weekly_update.log`

Ce script permettrait d'utiliser la skill `/schedule` ou `/loop` de Claude Code pour une exécution hebdomadaire automatique.

---

## 4. Actions immédiates recommandées

### Priorité 1 — Retenter les 18 transcripts absents

```bash
python Sources/Transcripts/batch_transcripts.py
```

Attendra ~2-3 semaines après la date de publication pour les vidéos récentes (batch 39) afin que YouTube ait généré les sous-titres. Pour le batch 39 (mi-avril 2026), attendre début mai 2026.

### Priorité 3 — Capter les vidéos de la semaine en cours

```bash
python Sources/Transcripts/batch_transcripts.py --recent 5
```

---

## 5. Récapitulatif des scripts disponibles

| Script | Usage principal | Commande clé |
|---|---|---|
| `batch_transcripts.py` | Extraire transcripts manquants | `--recent 20` ou sans flag |
| `batch_transcripts.py` | Découvrir nouvelles vidéos | `--discover` |
| `batch_transcripts.py` | Tout faire (discover+fix+extract) | `--full` |
| `batch_transcripts.py` | Enrichir fiches Videos/ | `--enrich-fiches` |
| `generate_chronological.py` | Régénérer PADUTEAM_CHRONOLOGIQUE.md | (sans flag) |
| `run_ingest.py` | Ingérer batches en attente | (sans flag) |
| `run_ingest.py` | Ingérer un batch précis | `--batch N` |
| `run_ingest.py` | Ingérer depuis le batch N | `--from N` |
