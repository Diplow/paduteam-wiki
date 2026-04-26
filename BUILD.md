---
date created: Sunday, April 12th 2026, 6:30:00 pm
date modified: Monday, April 20th 2026, 1:28:00 pm
---
# BUILD.md — Comment le vault est construit

Ce fichier documente **comment** le vault Graphiked est construit et maintenu : l'architecture des skills, les conventions partagées, et le workflow git. Les skills individuelles (dans `Skills/`) décrivent leur workflow spécifique ; ce fichier contient les invariants communs.

---

## Architecture des skills

```
┌──────────────────────────────────────────────────────┐
│  ingest-batch (optionnel)                            │
│  Regroupe N transcripts par sujet, construit une     │
│  synthèse cross-vidéos, puis dispatche vers les       │
│  skills write-* avec ce contexte consolidé.          │
│  Un seul commit / PR pour tout le batch.             │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  ingest-video (orchestrateur principal)               │
│  1. Lit le transcript                                │
│  2. Appelle gather-context pour le sujet             │
│  3. Dispatche vers les skills spécialisées           │
│  4. Gère le git (branche, commit, PR)                │
└───────┬──────────┬──────���───┬──────────┬─────────────┘
        │          │          │          │
        ▼          ▼          ▼          ▼
   write-video  write-entity  write-concept  write-enjeu
   (fiche vidéo) (individu   (fiche concept) (fiche enjeu)
                  ou orga)
```

### Principe central : séparer contexte et écriture

Chaque skill spécialisée (`write-*`) reçoit en entrée :
- Le **contexte** rassemblé par `gather-context` (fiches vault existantes, vidéos liées, entités connexes)
- Les **fiches existantes** pertinentes (déjà lues)
- Les **instructions d'écriture** spécifiques à son type

Elle ne fait **pas** de recherche extensive. Elle prend le contexte pour acquis et se concentre sur la rédaction.

### Skills

| Skill | Rôle | Statut |
|-------|------|--------|
| `gather-context` | Rassembler tout ce que le vault sait sur un sujet donné | v1 |
| `ingest-video` | Orchestrer l'ingestion d'un transcript | v2 (orchestrateur) |
| `write-video` | Rédiger/enrichir une fiche `Videos/` | v1 |
| `write-entity` | Rédiger/enrichir une fiche `Individus/` ou `Organisations/` | v1 |
| `write-concept` | Rédiger/enrichir une fiche `Concepts/` | v1 |
| `write-enjeu` | Rédiger/enrichir une fiche `Enjeux/` (format loadout) | v2 |
| `write-methode` | Promouvoir un concept en méthode (couche d'analyse) | v1 |
| `write-conjoncture` | Promouvoir un concept en conjoncture (diagnostic du moment) | v1 |
| `write-possible` | Promouvoir un concept en possible (horizon défendu) | v1 |
| `write-evenement` | Rédiger/enrichir une fiche `Evenements/` (fait daté) | v1 |
| `ingest-batch` | Ingérer plusieurs transcripts par sujet pour cohérence maximale | v1 |

### Couches d'accès au-dessus des entités

Au-delà des 5 types de fiches « entité » (Vidéos / Individus / Organisations / Concepts / Enjeux), 4 **couches d'accès** rendent navigable la pensée PaduTeam comme projet structuré :

- **Méthodes** (`Methodes/`) — outils d'analyse (matérialisme historique, Le Graphique, analyse en blocs sociaux). Une méthode organise le regard.
- **Conjonctures** (`Conjonctures/`) — diagnostics du moment historique (crise de l'hégémonie US, triple crise du capitalisme, moïsation, extrême-droitisation). Une conjoncture décrit un état structurant.
- **Possibles** (`Possibles/`) — horizons défendus (universalisme matériel, choc d'abondance, désagrégation progressiste de l'empire). Un possible se déploie *vers* un horizon ; un enjeu se mène *contre* un adversaire.
- **Évènements** (`Evenements/{période}/`) — faits datés analysés en profondeur (Guerre USA-Iran 2026, Discours Rubio Munich 2026, Coup CIA contre Mossadegh 1953).

Les 3 premières couches **n'ont pas de fichiers propres** au-delà du MOC + `.base` : les concepts qui en relèvent restent dans `Concepts/` avec un champ `couche` en frontmatter. Méthodes/Conjonctures/Possibles sont donc des *vues* sur Concepts, matérialisées par les `.base`. Les Évènements, en revanche, sont des entités à part entière (nouveau type `evenement`).

---

## Invariants — Règles communes à toutes les skills

### Attribution

**Attribution collective par défaut.** Les analyses sont attribuées à "la PaduTeam", pas à un membre individuel. N'attribuer individuellement que quand c'est explicitement identifiable dans le transcript :
- Segment solo (un seul intervenant)
- Auto-identification ("moi en tant que médecin...")
- Rôle spécifique reconnu ("Chris qui a conçu le Graphique")

### Noms de fichiers

- Pas d'accents ni de caractères spéciaux dans les noms de fichiers
- Les noms accentués sont définis en `aliases` dans le frontmatter
- **Individus** : Prénom Nom (`Jean-Luc Melenchon.md`)
- **Organisations** : Nom officiel complet (`France Insoumise.md`, pas `LFI.md`)
- **Concepts** : Nom descriptif capitalisé (`Eclatement du bloc central.md`)
- **Enjeux** : Nom court du combat (`Plus jamais PS.md`)
- **Vidéos** : Titre abrégé lisible (`COMMENT MELENCHON VA GAGNER EN 2027 AU SECOND TOUR.md`)

### Wikilinks

- `[[Nom Exact du Fichier]]` sans chemin, sans `.md`
- Pour les alias : `[[Nom réel|alias affiché]]` (ex: `[[Parti Communiste Français|PCF]]`)
- Le nom du fichier = le texte du wikilink
- Chaque wikilink doit pointer vers un fichier existant. Si un lien orphelin est créé, créer au minimum une fiche ébauche.

### YAML frontmatter

Toujours inclure au minimum :
- `type` : vidéo / individu / organisation / concept / enjeu / evenement / moc
- `domaine` : 1-2 valeurs parmi politique-intérieure, géopolitique, économie, théorie, société
- `thèmes` : liste de thèmes du vocabulaire contrôlé
- `skill_version` : identifiant de la skill + date (ex: `write-video-2026-04-12`, `ingest-2026-04-12`)

Selon le type :
- **Vidéos** : + `enjeux`, `date`, `youtube_id`
- **Individus** : + `aliases`
- **Organisations** : + `aliases`
- **Concepts** : + `aliases`. *Optionnel* : `couche` (`methode`, `conjoncture`, `possible` — peut être une liste si transverse), `couche_skill_version` (set par la skill avancée), `periode` (pour les conjonctures).
- **Enjeux** : pas de champ supplémentaire spécifique
- **Évènements** : + `date` (YYYY-MM-DD), `periode` (sous-dossier, ex: "2026"), optionnel `date_fin`, `aliases`

### Back-références vers les couches d'accès

Les fiches bas-niveau (Vidéos, Individus, Organisations, Concepts) qui mobilisent un objet de couche supérieure le déclarent en frontmatter. C'est ce qui alimente les `.base` des couches.

```yaml
methodes: [Materialisme historique, Graphique]
conjonctures: [Crise de l hegemonie americaine, Triple crise du capitalisme]
possibles: [Desagregation de l empire americain]
evenements: [Guerre USA-Iran 2026, Enlevement Maduro 2026]
# enjeux: [...] existe déjà pour les vidéos
```

Ne pas remplir ces champs gratuitement — uniquement si la fiche bas-niveau *traite significativement* de la couche. Ce sont les `.base` qui alimentent la navigation par couche : la qualité du back-référencement = la qualité de la navigation.

### Hashtags inline

Après le frontmatter YAML, les fiches incluent une ligne de hashtags structurés avant le titre `# Titre` :

```
#domaine/valeur #thème/valeur #enjeu/valeur
```

Inclure uniquement domaine, thèmes et enjeux (pas format ni statut). Ces hashtags matérialisent les tags comme nœuds du graphe Obsidian.

### Taxonomie des tags

3 axes structurent le tagging :

1. **domaine** — champ d'analyse (politique-intérieure, géopolitique, économie, théorie, société)
2. **thèmes** — sujets spécifiques récurrents. Vocabulaire contrôlé, extensible : `élections`, `anti-impérialisme`, `Palestine`, `Venezuela`, `féminisme`, `racisme-antiracisme`, `ruralité`, `médias-propagande`, `guerre-des-gauches`, `le-Graphique`, `travail`, `écologie`, `répression-justice`, `psychiatrie-psychologie`, `Iran`, `États-Unis`, `Amérique-latine`, `antivalidisme`, `santé`. Ajouter un nouveau thème si un sujet revient dans 2+ vidéos.
3. **enjeux** — combats stratégiques récurrents : `plus-jamais-PS`, `Palestine-libre`, `anti-impérialisme`, `le-Graphique`, `union-populaire`, `campisme-assumé`. Ajouter un nouvel enjeu si un combat revient dans 3+ vidéos avec une position constante.

**Le tag `paduteam` n'est pas utilisé** — tout le vault est PaduTeam par définition.

### Sourcing YouTube

Les fiches vidéo incluent un lien YouTube embarqué en haut (avant le résumé) et des notes de bas de page avec timestamps pour sourcer les points clés.

**Lien embarqué** (en haut de chaque fiche vidéo, après les hashtags, avant le `# Titre`) :
```markdown
[![TITRE](https://img.youtube.com/vi/YOUTUBE_ID/0.jpg)](https://www.youtube.com/watch?v=YOUTUBE_ID)
```

**Notes de bas de page avec timestamp** (dans le corps des fiches — vidéos, entités, concepts, enjeux) :
```markdown
La PaduTeam affirme que le PS est structurellement incapable de rupture[^1].

[^1]: [12:34](https://www.youtube.com/watch?v=YOUTUBE_ID&t=754) — "citation exacte ou résumé du passage"
```

Le `youtube_id` est stocké dans le frontmatter de la fiche vidéo. Pour convertir un timestamp `MM:SS` en secondes pour le paramètre `&t=`, utiliser le helper `Sources/timestamp_to_seconds.py`.

Pour les fiches non-vidéo (entités, concepts, enjeux), les footnotes référencent la vidéo source via son youtube_id — récupéré depuis la fiche vidéo correspondante.

### Style

- Phrases courtes, pas de remplissage
- Fidélité totale à l'analyse PaduTeam
- Ton analytique, pas encyclopédique — restituer la vision de la PaduTeam, pas Wikipedia
- Les jugements de valeur de la PaduTeam font partie de la restitution : ne pas les censurer, ne pas les atténuer
- Si la PaduTeam dit "Hollande est un traître", écrire "Hollande est un traître"

### Volume

Être ambitieux dans la création de fiches. Chaque personne mentionnée significativement, chaque parti cité, chaque mécanisme analytique décrit mérite sa fiche. Il vaut mieux créer une fiche minimale (ébauche) que de laisser un lien orphelin.

---

## Workflow git

Le vault est versionné sur GitHub (`Diplow/paduteam-wiki`).

### Stratégie de branches

```
main              ← production (publication du wiki)
 └── develop      ← intégration (état courant du vault)
      ├── ingest/slug-video        ← ingestion unitaire (1 vidéo)
      └── ingest-batch/slug-sujet  ← ingestion batch (N vidéos d'un même sujet)
```

- **`main`** : état publié du wiki. Jamais de push direct.
- **`develop`** : branche d'intégration. Toutes les ingestions sont mergées ici via PR.
- **`ingest/<slug>`** : branche éphémère pour une ingestion unitaire. Slug = titre de la vidéo en minuscules, sans accents, tirets, tronqué à ~50 chars.
- **`ingest-batch/<slug>`** : branche éphémère pour un batch thématique. Slug = nom du sujet (ex: `guerre-des-gauches`), ~40 chars max. Un seul commit et une seule PR couvrant toutes les vidéos du batch.

### En début d'ingestion

1. Se placer sur develop à jour : `git checkout develop && git pull origin develop`
2. Créer la branche : `git checkout -b ingest/<slug>`

### En fin d'ingestion

1. Stage les fichiers modifiés/créés par nom (pas `git add -A`)
2. Commit avec message structuré :
   ```
   ingest: TITRE ABRÉGÉ DE LA VIDÉO

   Fiches créées: X (liste)
   Fiches enrichies: Y (liste)
   Corrections ortho: Z (liste si applicable)

   Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
   ```
3. Push : `git push -u origin ingest/<slug>`
4. PR vers `develop` avec résumé (fiches créées, enrichies, corrections, liens orphelins)

### Publication (develop → main)

Merge manuel par l'utilisateur. Publication via Obsidian Publish.

---

## Chemins du vault

```
Graphiked/
├── Bienvenue.md                     ← homepage publique (Obsidian Publish)
├── CLAUDE.md                        ← instructions projet (ce qu'est le vault)
├── BUILD.md                         ← ce fichier (comment le vault est construit)
├── Sources/
│   ├── Inventaire PaduTeam.md       ← table des vidéos
│   └── Transcripts/                 ← transcripts bruts (.md)
├── Videos/                          ← 1 fiche par vidéo ingérée
├── Individus/                       ← 1 fiche par personne
├── Organisations/                   ← 1 fiche par parti/asso/média
├── Concepts/                        ← 1 fiche par concept analytique
├── Enjeux/                          ← 1 fiche par combat stratégique (loadout)
├── Methodes/                        ← MOC + .base — vue sur les concepts couche=methode
├── Conjonctures/                    ← MOC + .base — vue sur les concepts couche=conjoncture
├── Possibles/                       ← MOC + .base — vue sur les concepts couche=possible
├── Evenements/                      ← 1 fiche par fait daté, organisé par période
│   ├── 2026/
│   ├── 1950-1979/
│   └── ...
└── Skills/                          ← skills Claude (1 dossier par skill)
```

**Chemin sur le disque :** `C:\Users\uboil\Documents\Obsidian\Graphiked`
**Repo GitHub :** `git@github.com:Diplow/paduteam-wiki.git`
