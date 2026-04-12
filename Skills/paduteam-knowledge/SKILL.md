---
name: paduteam-knowledge
description: >
  Ingère un transcript de vidéo PaduTeam et met à jour la base de connaissances Obsidian.
  Crée ou enrichit les fiches: vidéos, individus, organisations, concepts, enjeux — toutes interconnectées par des wikilinks [[nom]].
  Les fiches sont stockées dans les dossiers à la racine du vault (Videos/, Individus/, Organisations/, Concepts/, Enjeux/).
  Utiliser cette skill dès que l'utilisateur fournit un transcript PaduTeam et veut alimenter le vault,
  ou quand il demande d'analyser/ingérer/traiter une vidéo PaduTeam pour le vault Obsidian.
  Déclencher aussi quand l'utilisateur dit "ingérer", "ajouter au vault", "créer les fiches", "mettre à jour les fiches",
  "analyser cette vidéo pour Obsidian", ou toute demande combinant un transcript PaduTeam et la base de connaissances.
  IMPORTANT: cette skill remplace paduteam-fiche pour la génération de fiches.
date created: Tuesday, March 31st 2026, 10:29:39 am
date modified: Thursday, April 2nd 2026, 10:27:49 am
---

# Skill : Ingestion PaduTeam → Knowledge Vault

## Vue d'ensemble

Cette skill prend un transcript de vidéo PaduTeam (fichier .md dans le dossier Transcripts) et produit/met à jour un ensemble de fiches Obsidian interconnectées dans les dossiers à la racine du vault. Elle génère 5 types de fiches: vidéos, individus, organisations, concepts, enjeux.

L'objectif est de construire un graphe de connaissances navigable dans Obsidian, reflétant fidèlement les analyses et la vision du monde de la PaduTeam.

## Chemins du vault

```
Graphiked/
├── Sources/
│   ├── Inventaire PaduTeam.md          ← table des vidéos
│   └── Transcripts/                     ← transcripts bruts (.md)
│       └── TITRE DE LA VIDÉO.md
├── Videos/                              ← 1 fiche par vidéo ingérée
├── Individus/                           ← 1 fiche par personne
├── Organisations/                       ← 1 fiche par parti/asso/média
├── Concepts/                            ← 1 fiche par concept analytique
└── Enjeux/                              ← 1 fiche par combat stratégique récurrent
```

**Chemin exact sur le disque (Windows) :** `C:\Users\uboil\Documents\Obsidian\Perso\4. Jeux\Notes\Graphiked`

**Accès au vault en début de session :** Utiliser immédiatement `request_cowork_directory` avec le chemin exact ci-dessus — ne jamais demander à l'utilisateur où se trouve le vault, ne jamais ouvrir un sélecteur de dossier. Le vault sera alors monté à `/sessions/.../mnt/Graphiked`.

## Qui est la PaduTeam

Chaîne YouTube marxiste-communiste francophone. Trois membres récurrents:
- **Padu** (Pas Dühring) — Pédopsychiatre, créateur, marxiste-léniniste, provocateur
- **Chris** — Cadre industrie, fondateur de la revue *Positions*, théoricien, concepteur du "Saint Graphique"
- **Zoé** (Docteur Zoé / @Dr_Zoé_YT) — Médecin généraliste, féministe matérialiste

Concepts clés récurrents: **Saint Graphique** (matrice ACM PCS INSEE, axe exploitation × domination), **Moïsation**, analyse en blocs sociaux, soutien critique à LFI.

---

## Principe fondamental

**Capturer fidèlement les analyses de la PaduTeam, pas les challenger ni les nuancer.** Même quand leurs positions sont radicales ou partisanes, les restituer telles quelles. Signaler quand une analyse est spéculative ou quand ils reconnaissent eux-mêmes une incertitude, mais ne pas corriger, ne pas modérer, ne pas ajouter de "cependant".

---

## Taxonomie des tags

Le vault utilise un système de tags structuré sur 5 axes. **Ne pas utiliser de tag `paduteam`** — tout le vault est PaduTeam, c'est redondant.

### Hashtags inline après le frontmatter

Après le frontmatter YAML (lignes fermées par `---`), les fiches Knowledge doivent inclure une ligne de **hashtags structurés** avant le titre `# Titre`. Ces hashtags permettent la visualisation du graphe de connaissances dans Obsidian.

**Format des hashtags inline:**
```
#domaine/valeur #thème/valeur #thème/valeur #enjeu/valeur
```

**Règles:**
- Placer la ligne immédiatement après `---` (le `---` qui ferme le frontmatter)
- Laisser une ligne vide après les hashtags, avant le `# Titre`
- Inclure **uniquement** domaine, thèmes et enjeux (pas format ni statut)
- Format des clés: `domaine/`, `thème/`, `enjeu/` (sans "s")
- Valeurs: reprendre exactement celles du frontmatter YAML
- Un hashtag par thème et enjeu (chacun dans sa propre balise)

**Exemple concret:**
```yaml
---
type: vidéo
domaine: [géopolitique]
thèmes: [Palestine, anti-impérialisme]
format: analyse
enjeux: [Palestine-libre, anti-impérialisme]
date: 2025-11-15
intervenants: [Padu, Chris]
statut: ébauche
---
#domaine/géopolitique #thème/Palestine #thème/anti-impérialisme #enjeu/Palestine-libre #enjeu/anti-impérialisme

# TITRE DE LA VIDÉO
```

**Raison:** Ces hashtags matérialisent les tags du vault en tant que nœuds du graphe Obsidian. Ils facilitent la navigation et permettent de voir rapidement les domaines, thèmes et enjeux sans ouvrir le frontmatter.

---

### Axe 1 : `domaine` (champ frontmatter, 1-2 valeurs)

Le champ d'analyse principal de la fiche. Valeurs possibles:

| Valeur | Description | Exemples |
|--------|-------------|----------|
| `politique-intérieure` | Politique française, élections, partis, stratégie partisane | Mélenchon 2027, guerre des gauches, PS |
| `géopolitique` | Relations internationales, impérialisme, conflits | Venezuela, Palestine, Iran, OTAN |
| `économie` | Analyse économique, travail, néolibéralisme | Choc d'abondance, précarité |
| `théorie` | Cadres analytiques, méthodologie, outils conceptuels | Le Graphique, ACM, Marx, Bourdieu |
| `société` | Questions transversales, sociologie, médias | Féminisme, racisme, psychiatrie, médias |

### Axe 2 : `thèmes` (champ frontmatter, liste)

Sujets spécifiques récurrents. Vocabulaire contrôlé, extensible:

`élections`, `anti-impérialisme`, `Palestine`, `Venezuela`, `féminisme`, `racisme-antiracisme`, `ruralité`, `médias-propagande`, `guerre-des-gauches`, `le-Graphique`, `travail`, `écologie`, `répression-justice`, `psychiatrie-psychologie`, `Iran`, `États-Unis`, `Amérique-latine`

Ajouter un nouveau thème si un sujet revient dans 2+ vidéos et ne correspond à aucun thème existant.

### Axe 3 : `format` (champ frontmatter, vidéos uniquement)

Le format/série de la vidéo:

| Valeur | Description |
|--------|-------------|
| `analyse` | Format par défaut — analyse longue classique |
| `paye-ton-droitard` | React à une vidéo d'un droitard (souvent Padu + Zoé) |
| `recette-de-noel` | Debunk humoristique de figures de droite |
| `seigneurs-des-noisettes` | Saga sur les manœuvres du PS |
| `antitech-resistance` | Série sur l'éco-fascisme et l'écologie réactionnaire |
| `backseat` | Débat avec la chaîne Backseat |
| `entretien` | Interview d'un invité extérieur |
| `react` | Réaction à un contenu (hors paye-ton-droitard) |
| `débat` | Débat contradictoire (hors Backseat) |

### Axe 4 : `enjeux` (champ frontmatter, liste)

Les combats stratégiques récurrents de la PaduTeam — les thèses qu'ils défendent vidéo après vidéo. Chaque enjeu a aussi sa propre fiche dans `Enjeux/`.

Vocabulaire initial:

| Enjeu | Description |
|-------|-------------|
| `plus-jamais-PS` | Le PS est l'ennemi structurel de la gauche de rupture |
| `Palestine-libre` | Centralité de la question palestinienne pour la gauche |
| `anti-impérialisme` | Soutien aux pays résistant à l'hégémonie US |
| `le-Graphique` | Le Saint Graphique comme outil prédictif légitime |
| `union-populaire` | Mélenchon/LFI comme seul véhicule viable de la gauche |
| `campisme-assumé` | Choisir un camp sans "ni-nisme" |

Ajouter un nouvel enjeu si un combat revient dans 3+ vidéos avec une position constante.

### Axe 5 : `statut` (champ frontmatter)

Niveau de complétude de la fiche:

| Valeur | Signification |
|--------|---------------|
| `ébauche` | Fiche créée avec infos minimales (1 seule vidéo source) |
| `développé` | Fiche enrichie par 2-3 vidéos, contenu substantiel |
| `mature` | Fiche riche, plusieurs vidéos sources, analyse complète |

---

## Workflow étape par étape

### Étape 0 — Sélection automatique de la vidéo (si aucune vidéo spécifiée)

Si l'utilisateur ne fournit ni URL YouTube, ni titre de vidéo, ni nom de fichier transcript :

1. Lire `Sources/Inventaire PaduTeam.md`
2. Parcourir la table ligne par ligne en partant du haut (vidéos les plus récentes)
3. Chercher la **première ligne qui a un transcript** (colonne 4 non vide, contient un `[[...]]`) **mais pas de fiche** (colonne 5 vide)
4. Utiliser cette vidéo : extraire le titre et le nom du transcript pour passer à l'étape 1

Si toutes les vidéos avec transcript ont déjà une fiche, le signaler à l'utilisateur et proposer d'extraire un nouveau transcript pour la vidéo la plus récente sans transcript.

### Étape 1 — Localiser et lire le transcript

**Toujours chercher le transcript dans le vault en premier**, avant toute tentative d'extraction YouTube.

Procédure :
1. Lister les fichiers dans `Sources/Transcripts/`
2. Si l'utilisateur a fourni un titre ou une URL YouTube, chercher un fichier dont le nom correspond (correspondance partielle ou mot-clé du titre, ex: "SEXISTE" pour la vidéo "Le GRAPHIQUE est-il vraiment SEXISTE ?")
3. Si un fichier correspondant est trouvé → lire ce fichier directement, **ne pas extraire depuis YouTube**
4. Si aucun fichier ne correspond → utiliser la skill `paduteam-transcript` pour extraire le transcript depuis l'URL YouTube, puis sauvegarder le résultat dans `Sources/Transcripts/`

Lire le transcript en entier. Les transcripts sont structurés avec des timestamps (format "MM:SS" ou texte descriptif) et du texte brut. Le texte est souvent oral, avec des hésitations, des interruptions, du langage familier — c'est normal.

### Étape 2 — Analyser le contenu

En lisant le transcript, identifier:

1. **Métadonnées**: titre, date de tournage (si mentionnée), intervenants (Padu, Chris, Zoé), domaine principal, format de la vidéo
2. **Individus mentionnés**: toute personne nommée, analysée, critiquée ou commentée — pas seulement les protagonistes mais aussi les figures secondaires
3. **Organisations mentionnées**: partis politiques, associations, médias, syndicats, institutions
4. **Concepts analytiques**: tout mécanisme, stratégie, grille de lecture ou terme technique utilisé par la PaduTeam (ex: Saint Graphique, vote caché, polarisation, moïsation, bloc bourgeois, etc.)
5. **Enjeux stratégiques**: quels combats récurrents de la PaduTeam cette vidéo avance-t-elle ?
6. **Résumé de l'analyse**: les thèses principales, les projections, les mécanismes cause-conséquence

### Étape 3 — Lire les fiches existantes

Avant de créer de nouvelles fiches, lister les fiches existantes pour savoir lesquelles existent déjà:

```bash
ls Individus/
ls Organisations/
ls Concepts/
ls Videos/
ls Enjeux/
```

Pour chaque entité identifiée à l'étape 2:
- Si la fiche existe → la lire, puis l'enrichir avec les nouvelles informations
- Si la fiche n'existe pas → la créer

C'est l'étape la plus importante: le vault grandit vidéo après vidéo. Chaque nouvelle ingestion enrichit les fiches existantes.

### Étape 4 — Créer/mettre à jour la fiche vidéo

Créer un fichier `Videos/TITRE ABRÉGÉ.md` avec cette structure:

```markdown
---
type: vidéo
domaine: [valeur1]
thèmes: [thème1, thème2]
format: analyse
enjeux: [enjeu1, enjeu2]
date: YYYY-MM-DD (si identifiable)
intervenants: [Padu, Chris]
statut: ébauche
---
#domaine/valeur1 #thème/thème1 #thème/thème2 #enjeu/enjeu1 #enjeu/enjeu2

# TITRE DE LA VIDÉO

## Résumé
2-4 phrases décrivant le contenu et la thèse principale.

## Thèses et analyses clés
Liste numérotée des mécanismes/analyses principaux, chacun avec un lien vers
le concept correspondant via [[wikilink]].

## Résultats / projections
Si la vidéo contient des chiffres, sondages ou projections: les inclure
dans un tableau markdown.

## Individus mentionnés
[[Nom1]], [[Nom2]], [[Nom3]]...

## Organisations mentionnées
[[Org1]], [[Org2]]...

## Concepts mobilisés
[[Concept1]], [[Concept2]]...

## Enjeux avancés
[[Enjeu1]] — comment cette vidéo fait avancer ce combat
[[Enjeu2]] — ...

## Transcript
[[Nom exact du fichier transcript sans .md]]
```

### Étape 5 — Créer/enrichir les fiches individus

Pour chaque personne mentionnée significativement (pas juste citée en passant), créer ou enrichir `Individus/Nom Complet.md`:

```markdown
---
type: individu
domaine: [politique-intérieure]
thèmes: [thème1, thème2]
quadrant_graphique: "Position si connue"
aliases: [alias1, alias2]
statut: ébauche
---
#domaine/politique-intérieure #thème/thème1 #thème/thème2

# Nom Complet

## Profil synthétique
1-3 phrases: qui est cette personne, quel est son rôle dans les analyses PaduTeam.

## Position dans le [[Saint Graphique]]
Si discutée dans la vidéo: où se situe cette personne sur les axes exploitation/domination.

## Stratégie et trajectoire
Analyse de la PaduTeam sur cette personne: sa stratégie, ses alliances, ses erreurs.

## Relations
- Liens vers d'autres individus et organisations via [[wikilinks]]

## Vidéos où X est analysé
- [[Titre vidéo 1]]
- [[Titre vidéo 2]]
```

**Pour enrichir une fiche existante:**
- Ajouter les nouvelles informations dans les sections pertinentes
- Ajouter la nouvelle vidéo dans "Vidéos où X est analysé"
- Ne pas supprimer les informations existantes, même si elles viennent d'une autre vidéo
- Si une information contredit une analyse précédente, noter les deux (la PaduTeam peut évoluer dans ses analyses)
- Mettre à jour le `statut` si la fiche s'enrichit (ébauche → développé → mature)

### Étape 6 — Créer/enrichir les fiches organisations

Même logique que les individus, dans `Organisations/Nom Organisation.md`:

```markdown
---
type: organisation
domaine: [politique-intérieure]
thèmes: [thème1]
quadrant_graphique: "Position si connue"
aliases: [alias1]
statut: ébauche
---
#domaine/politique-intérieure #thème/thème1

# Nom Organisation

## Position dans le [[Saint Graphique]]
Si discutée: positionnement sociologique.

## Dynamique
Analyse PaduTeam: stratégie, évolution, forces/faiblesses.

## Figures clés
- [[Personne1]] — rôle
- [[Personne2]] — rôle

## Vidéos où l'organisation est analysée
- [[Titre vidéo]]
```

### Étape 7 — Créer/enrichir les fiches concepts

Pour chaque concept analytique utilisé par la PaduTeam, dans `Concepts/Nom du concept.md`:

```markdown
---
type: concept
domaine: [théorie]
thèmes: [thème1]
aliases: [alias1, alias2]
statut: ébauche
---
#domaine/théorie #thème/thème1

# Nom du concept

## Définition
Ce que le concept signifie dans le cadre analytique de la PaduTeam.

## Mécanisme
Comment ça fonctionne: dynamique cause-conséquence.

## Exemples
Applications concrètes mentionnées dans les vidéos.

## Vidéos où le concept est développé
- [[Titre vidéo]]
```

Les concepts sont la catégorie la plus précieuse car ils constituent le cœur de la grille de lecture PaduTeam. Être ambitieux: si un mécanisme est décrit même brièvement, il mérite probablement sa fiche.

### Étape 7b — Créer/enrichir les fiches enjeux

Les enjeux sont les **combats stratégiques récurrents** de la PaduTeam — les positions militantes qu'ils défendent vidéo après vidéo. Un enjeu n'est ni un concept (outil analytique) ni un thème (sujet), c'est une **thèse politique** soutenue avec constance.

Pour chaque enjeu identifié, dans `Enjeux/Nom de l'enjeu.md`:

```markdown
---
type: enjeu
domaine: [politique-intérieure]
thèmes: [thème1, thème2]
statut: ébauche
---
#domaine/politique-intérieure #thème/thème1 #thème/thème2

# Nom de l'enjeu

## Position PaduTeam
1-3 phrases: quelle est la thèse défendue, pourquoi c'est un combat central.

## Arguments récurrents
Les arguments que la PaduTeam mobilise vidéo après vidéo pour défendre cette position.

## Concepts associés
[[Concept1]], [[Concept2]] — les outils analytiques mobilisés pour ce combat.

## Adversaires de cette position
Qui défend la position inverse et pourquoi (selon la PaduTeam).

## Évolution
Comment cette position a évolué au fil des vidéos (si applicable).

## Vidéos clés
- [[Titre vidéo 1]] — pourquoi cette vidéo est importante pour cet enjeu
- [[Titre vidéo 2]] — ...
```

**Quand créer une fiche enjeu :**
- Quand un combat revient dans 3+ vidéos avec une position constante
- Quand la PaduTeam prend explicitement position sur un sujet de manière militante (pas juste analytique)
- Les enjeux existants à ce jour: `plus-jamais-PS`, `Palestine-libre`, `anti-impérialisme`, `le-Graphique`, `union-populaire`, `campisme-assumé`

### Étape 8 — Vérification des liens orphelins

Après avoir créé toutes les fiches, vérifier que chaque `[[wikilink]]` utilisé dans les fiches pointe vers un fichier existant. Obsidian gère les wikilinks par nom de fichier (sans chemin), donc `[[Jean-Luc Mélenchon]]` pointera vers `Individus/Jean-Luc Mélenchon.md` automatiquement.

Lister les wikilinks utilisés et vérifier qu'aucun n'est orphelin. Si des liens orphelins restent, créer les fiches manquantes (même minimales).

### Étape 9 — Vérification orthographique des noms

Les transcripts sont générés automatiquement à partir de la parole, ce qui provoque régulièrement des erreurs sur les noms propres (individus et organisations). Par exemple: "Lucy Castets" au lieu de "Lucie Castets", "Alvinerstein" au lieu de "Alvin Hellerstein", "Oribé" au lieu de "Uribe". Cette étape vise à détecter et corriger ces erreurs avant qu'elles ne se propagent dans tout le vault.

**Procédure:**

1. **Lister les noms douteux.** Passer en revue tous les noms d'individus et d'organisations extraits du transcript. Sont suspects:
   - Les noms que le transcript rend de manière incohérente (orthographe qui varie d'une occurrence à l'autre)
   - Les noms qui "sonnent" comme une transcription phonétique approximative (ex: "Ouibé" pour Uribe, "Guayado" pour Guaidó)
   - Les noms de personnalités peu connues ou étrangères, plus sujets aux erreurs
   - Les noms qui ne correspondent à aucune personne connue tels quels

2. **Croiser avec le vault existant.** Vérifier si un nom similaire existe déjà dans `Individus/` ou `Organisations/`. Si "Lucie Castets.md" existe déjà et que le transcript dit "Lucy Castets", c'est une erreur du transcript — utiliser l'orthographe du vault.

3. **Vérifier par recherche web.** Pour les noms qui restent douteux après le croisement vault (notamment les nouvelles entités), faire une recherche web rapide pour confirmer l'orthographe correcte. Quelques secondes de vérification évitent de polluer le vault avec des fiches mal nommées qui créeront des doublons lors d'ingestions futures.

4. **Corriger.** Si des erreurs sont trouvées:
   - Renommer les fichiers concernés
   - Mettre à jour les wikilinks dans toutes les fiches qui y font référence
   - Mettre à jour le contenu des fiches (titres, mentions dans le texte)

5. **Rapporter.** Inclure dans le résumé final la liste des corrections effectuées (nom erroné → nom corrigé) pour que l'utilisateur puisse vérifier.

**Ne pas sur-corriger:** les noms courants de la politique française (Mélenchon, Macron, Bardella...) ou les membres de la PaduTeam n'ont généralement pas besoin de vérification. Se concentrer sur les noms étrangers, les personnalités secondaires, et les noms qui paraissent phonétiquement douteux.

### Étape 10 — Mise à jour de l'Inventaire PaduTeam

Après création de la fiche vidéo, mettre à jour `Sources/Inventaire PaduTeam.md` :

1. Chercher la ligne de la vidéo dans le tableau (correspondance par titre)
2. Si la ligne existe : remplir la colonne **Fiche** avec `[[Titre de la fiche vidéo]]` (le nom du fichier créé dans `Videos/`, sans .md)
3. Si la ligne n'existe pas : ajouter une nouvelle ligne en fin de tableau avec Titre, Lien YouTube, Date (si connue), Transcript, et Fiche

Format d'une ligne :
```
| TITRE                          | [YouTube](URL)     | DATE              | [[NOM TRANSCRIPT]]                    | [[NOM FICHE VIDEO]]                   |
```

**Important :** toujours vérifier que la colonne Fiche n'est pas déjà remplie avant d'écrire dedans.

### Étape 11 — Résumé à l'utilisateur

Présenter un résumé de ce qui a été fait:
- Nombre de fiches créées vs enrichies
- Liste des nouvelles fiches par catégorie
- Fiches existantes enrichies
- Liens orphelins restants (normalement 0)
- Enjeux identifiés ou enrichis
- Corrections orthographiques effectuées (nom erroné → nom corrigé)

---

## Règles de wikilinks

- Utiliser `[[Nom Complet]]` pour les individus (ex: `[[Jean-Luc Mélenchon]]`)
- Utiliser `[[Nom Organisation]]` pour les orgas (ex: `[[France Insoumise]]`)
- Utiliser `[[Nom du concept]]` pour les concepts (ex: `[[Saint Graphique]]`)
- Utiliser `[[Nom de l'enjeu]]` pour les enjeux (ex: `[[Plus jamais PS]]`)
- Utiliser `[[Titre abrégé vidéo]]` pour les vidéos
- Pour les alias: `[[Nom réel|alias affiché]]` (ex: `[[Parti Communiste Français|PCF]]`)
- Le nom du fichier = le texte du wikilink (sans le chemin, sans .md)

## Règles de nommage

- **Individus**: Prénom Nom (ex: `Jean-Luc Mélenchon.md`)
- **Organisations**: Nom officiel complet (ex: `France Insoumise.md`, pas `LFI.md`) — utiliser `aliases` en frontmatter pour les acronymes
- **Concepts**: Nom descriptif capitalisé (ex: `Éclatement du bloc central.md`)
- **Enjeux**: Nom court du combat (ex: `Plus jamais PS.md`, `Palestine libre.md`)
- **Vidéos**: Titre abrégé lisible (ex: `COMMENT MÉLENCHON VA GAGNER EN 2027 AU SECOND TOUR.md`)

## YAML frontmatter

Toujours inclure au minimum:
- `type`: vidéo / individu / organisation / concept / enjeu
- `domaine`: 1-2 valeurs parmi politique-intérieure, géopolitique, économie, théorie, société
- `thèmes`: liste de thèmes du vocabulaire contrôlé
- `statut`: ébauche / développé / mature

Selon le type:
- **Vidéos**: + `format`, `enjeux`, `date`, `intervenants`
- **Individus**: + `quadrant_graphique` (si connu), `aliases`
- **Organisations**: + `quadrant_graphique` (si connu), `aliases`
- **Concepts**: + `aliases`
- **Enjeux**: pas de champ supplémentaire spécifique

**Ne pas utiliser le tag `paduteam`** — tout le vault est PaduTeam, c'est redondant.

## Consigne de volume

Être ambitieux dans la création de fiches. Chaque personne mentionnée significativement, chaque parti cité, chaque mécanisme analytique décrit mérite sa fiche. Il vaut mieux créer une fiche minimale (que les futures ingestions enrichiront) que de laisser un lien orphelin. L'objectif est un graphe de connaissances dense et navigable.

## Consigne de style

- Phrases courtes, pas de remplissage
- Fidélité totale à l'analyse PaduTeam
- Ton analytique, pas encyclopédique — restituer la vision de la PaduTeam, pas Wikipedia
- Les jugements de valeur de la PaduTeam font partie de la restitution: ne pas les censurer, ne pas les atténuer
- Si la PaduTeam dit "Hollande est un traître", écrire "Hollande est un traître" — pas "la PaduTeam considère que Hollande pourrait être perçu comme un traître"