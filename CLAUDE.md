---
date created: Wednesday, April 1st 2026, 5:27:10 pm
date modified: Wednesday, April 15th 2026, 1:40:01 pm
---
# Graphiked — Projet de documentation PaduTeam

## Objectif

Construire un graphe de connaissances Obsidian documentant l'univers analytique de la PaduTeam. Le vault capture fidèlement leurs analyses sans les challenger.

## Qui est la PaduTeam

La PaduTeam n'est pas une chaîne de commentaire politique. C'est le bras médiatique de **La Brèche**, une association militante loi 1901 dont la production de contenu YouTube n'est qu'une des activités.

### Membres

- **Padu** (Pas Dühring) — Pédopsychiatre, créateur, marxiste-léniniste
- **Chris** — Cadre industrie, fondateur de *Positions Revue*, concepteur du [[Graphique]]
- **Zoé** (Dr Zoé) — Présidente de La Brèche, Médecin généraliste, féministe matérialiste

Les trois gardent leurs emplois salariés — c'est un choix militant théorisé : extraire les militants de leur milieu professionnel crée une "pseudo avant-garde" déconnectée de la pratique collective.

### Ce que la PaduTeam cherche à faire

1. **Donner des grilles de lecture matérialistes** — Le Graphique (matrice ACM PCS INSEE), l'analyse en blocs sociaux, le matérialisme historique. L'objectif est de *former politiquement* les spectateurs, de leur "donner des billes de réflexion" (Zoé) utilisables dans les syndicats, les organisations, le terrain. Pas de commenter l'actualité.

2. **Mener la bataille culturelle** — Être présent quotidiennement face à l'extrême droite qui a pris massivement l'espace internet. Choisir un camp, assumer une position de classe. "Radicaliser la gauche molle", porter une ligne de gauche radicale le plus largement possible.

3. **Proposer un possible** — Contre la vision pénurique dominante du monde (qui légitime les inégalités comme inévitables), montrer que l'abondance existe et est captée par les plus riches (cf. [[Choc d'abondance]]). "Analyser les phénomènes mais surtout proposer" (Zoé).

4. **Condenser le mouvement gazeux** — Critique centrale de LFI : un mouvement non structuré se disperse. La Brèche est la réponse : structures militantes denses, ancrées dans le milieu professionnel, fédérées entre elles. La période (néolibéralisme en crise, extrême-droitisation, désocialisation des territoires) nécessite cette structuration.

5. **Devenir majoritaire** — "Résister c'est déjà perdre un peu" (Padu). Sortir de la complaisance minoritaire. "On est persuadé, on a la foi dans le fait que nos idées peuvent devenir demain majoritaires et hégémoniques" (Chris).

### Pourquoi c'est important pour le vault

Ce cadre informe le "pourquoi" derrière chaque analyse PaduTeam. Quand ils parlent du PS, ce n'est pas du commentaire — c'est une pièce dans le combat "Plus jamais PS". Quand ils analysent le Graphique, c'est un outil de formation politique, pas un exercice académique. Chaque fiche du vault doit porter cette intention militante — pas la nuancer, pas la neutraliser.

## Usage du vault

Ce vault sert **deux fonctions** :

1. **Construction** — Ingérer des vidéos PaduTeam pour enrichir la base de connaissances (voir `BUILD.md` pour l'architecture des skills)

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

- **Noms de fichiers**: pas d'accents ni de caractères spéciaux (`Jean-Luc Melenchon.md`, pas `Jean-Luc Mélenchon.md`). Les noms accentués sont définis en `aliases` dans le frontmatter.
- **Wikilinks**: `[[Nom Exact du Fichier]]` sans chemin, sans .md
- **Aliases**: définis en frontmatter YAML, permettent les liens via `[[Nom réel|alias]]`
- **Langue**: français, ton analytique (pas encyclopédique)
- **Principe fondamental**: restituer la vision PaduTeam telle quelle, sans modérer ni nuancer

## Lire les sources PaduTeam — avertissements

Trois pièges à éviter systématiquement quand on travaille sur ce vault :

1. **Les titres sont du clickbait assumé.** Ils sont rédigés pour passer l'algorithme YouTube, pas pour résumer fidèlement le contenu. Un titre qui dit « X CENSURE Y », « Z DÉTRUIT W », « ILS SE DÉCHIRENT » est quasi systématiquement une dramatisation. **Ne jamais déduire le contenu ou la position PaduTeam à partir d'un titre seul** — toujours lire le transcript avant de caractériser une vidéo, un conflit interne, ou une position. Si une fiche doit être écrite sans transcript disponible, le signaler explicitement au lieu d'extrapoler depuis le titre.

2. **Le vault est construit à partir de transcripts écrits, pas de la vidéo.** On perd l'ironie visuelle, le ton, les regards complices, les rires. Un passage qui semble agressif à l'écrit peut être un running gag ; une phrase qui semble sérieuse peut être au second degré. En cas de doute sur le registre d'un passage, préférer une formulation qui préserve l'ambiguïté plutôt qu'une interprétation littérale.

3. **La PaduTeam est cynique, caustique et pratique l'auto-dérision.** Leurs « clashs » internes sont souvent performatifs (débat entre amis, sketch militant, provocation pédagogique). Distinguer les vraies lignes de fracture des joutes de chapelle suppose de lire le transcript en entier, pas d'extraire un extrait isolé. Quand le transcript laisse un doute, ne pas inventer un conflit qui n'existe pas.

## Taxonomie des tags

3 axes structurent le tagging (voir `BUILD.md` pour le détail complet) :

1. **domaine** — champ d'analyse (politique-intérieure, géopolitique, économie, théorie, société)
2. **thèmes** — sujets spécifiques récurrents (vocabulaire contr��lé, extensible)
3. **enjeux** — combats stratégiques récurrents de la PaduTeam

**Le tag `paduteam` n'est pas utilisé** — tout le vault est PaduTeam par définition.

## Comment le vault est construit

Voir `BUILD.md` pour l'architecture des skills, les conventions de construction, le workflow git et les invariants.

## Principe d'auto-amélioration

Chaque ingestion de vidéo est une occasion de récolter du feedback pour le système lui-même. Les transcripts peuvent révéler des insights qui devraient mettre à jour ce fichier (`CLAUDE.md`), `BUILD.md`, les définitions de skills ou les conventions. Rien dans la description du système n'est figé — chaque transcript est une source potentielle de raffinement.
