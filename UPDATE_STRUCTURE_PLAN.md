---
date created: Sunday, April 12th 2026, 6:00:00 pm
date modified: Wednesday, April 15th 2026, 1:40:00 pm
---
# Plan de restructuration des skills — Graphiked

> **État : exécuté.** Ce plan décrit la refonte historique du monolithe vers l'architecture actuelle (`gather-context` + `ingest-video` + `write-*` + `ingest-batch`). Les références à `paduteam-knowledge` ci-dessous désignent l'ancien nom de `ingest-video`, renommé le 2026-04-19. Le document est conservé comme trace de conception.

## Problème

La skill `paduteam-knowledge` (aujourd'hui `ingest-video`) est un monolithe de ~600 lignes qui fait tout : orchestration git, lecture du transcript, analyse du contenu, et écriture de 5 types de fiches différents. Ça pose trois problèmes :

1. **Pas de séparation contexte / écriture** — La skill fait la recherche ET la rédaction dans le même flux. Résultat : les fiches individus, concepts, enjeux etc. sont écrites avec un contexte partiel (juste le transcript courant + la fiche existante), sans vue d'ensemble sur ce que le vault sait déjà du sujet.

2. **Pas de skill dédiée par type de fiche** — Écrire une fiche enjeu et écrire une fiche individu sont deux tâches très différentes. Un enjeu est un combat récurrent qui se construit à travers de multiples vidéos. Un individu est un profil qui s'enrichit au fil des mentions. La même procédure monolithique ne peut pas bien servir les deux.

3. **Pas de vision multi-vidéos** — Quand on ingère une vidéo isolément, on perd la cohérence thématique. Si 5 vidéos parlent de la guerre PS/LFI, l'enjeu "Plus jamais PS" devrait être documenté avec la vue d'ensemble des 5, pas enrichi incrémentalement avec des redondances.

## Architecture cible

```
┌──────────────────────────────────────────────────────┐
│  ingest-batch (optionnel)                            │
│  Regroupe N transcripts par sujet, construit un      │
│  contexte consolidé, puis appelle ingest-video       │
│  pour chaque vidéo avec ce contexte enrichi          │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  ingest-video (orchestrateur principal)               │
│  1. Lit le transcript                                │
│  2. Appelle gather-context pour le sujet             │
│  3. Dispatche vers les skills spécialisées           │
│  4. Gère le git (branche, commit, PR)                │
└───────┬──────────┬──────────┬──────────┬─────────────┘
        │          │          │          │
        ▼          ▼          ▼          ▼
   write-video  write-entity  write-concept  write-enjeu
   (fiche vidéo) (individu   (fiche concept) (fiche enjeu)
                  ou orga)
```

### Principe central : séparer contexte et écriture

Chaque skill spécialisée (`write-*`) reçoit en entrée :
- Le **contexte** (déjà rassemblé par `gather-context` ou `ingest-batch`)
- Les **fiches existantes** pertinentes (déjà lues)
- Les **instructions d'écriture** spécifiques à son type

Elle n'a **pas** à faire de recherche extensive. Elle prend le contexte pour acquis et se concentre sur la rédaction.

---

## Skills proposées

### 1. `gather-context`

**Rôle** : Rassembler tout ce que le vault sait déjà sur un sujet donné.

**Entrée** : Un sujet (titre de vidéo, nom de concept, nom d'enjeu, etc.)

**Sortie** : Un document structuré contenant :
- Les fiches existantes pertinentes (résumées ou complètes selon la taille)
- Les vidéos déjà ingérées qui touchent au même sujet
- Les entités liées (individus, orgas, concepts)
- Les enjeux concernés

**Pourquoi c'est une skill à part** : Ce travail de recherche dans le vault est le même quel que soit le type de fiche qu'on va écrire. Le factoriser évite que chaque skill spécialisée refasse le même scan.

### 2. `ingest-video` (refonte de `paduteam-knowledge`)

**Rôle** : Orchestrer l'ingestion d'un transcript unique.

**Ce qui change par rapport à aujourd'hui** :
- Ne rédige plus directement les fiches — dispatche vers les skills spécialisées
- Appelle `gather-context` en amont pour donner aux writers un contexte riche
- Conserve la gestion git (branche, commit, PR)
- Conserve la vérification orthographique et les liens orphelins
- Conserve la mise à jour de l'inventaire

**Workflow révisé** :
1. Sélection de la vidéo (inchangé)
2. Lecture du transcript (inchangé)
3. Analyse du contenu → liste des entités, concepts, enjeux identifiés
4. **`gather-context`** sur les sujets principaux de la vidéo
5. Création de la fiche vidéo via **`write-video`**
6. Pour chaque individu/orga significatif → **`write-entity`** avec le contexte
7. Pour chaque concept → **`write-concept`** avec le contexte
8. Pour chaque enjeu → **`write-enjeu`** avec le contexte
9. Vérification liens orphelins + ortho (inchangé)
10. Git : commit, push, PR (inchangé)

### 3. `write-video`

**Rôle** : Rédiger ou mettre à jour une fiche dans `Videos/`.

**Entrée** :
- Transcript analysé (thèses, métadonnées, entités identifiées)
- Contexte vault (via `gather-context`)

**Sortie** : Fiche vidéo complète selon le template actuel.

**Spécificité** : C'est la skill la plus proche de ce que fait le monolithe actuel pour les fiches vidéo. Peu de changement structurel ici.

### 4. `write-entity`

**Rôle** : Rédiger ou enrichir une fiche dans `Individus/` ou `Organisations/`.

**Entrée** :
- Ce que le transcript dit de l'entité
- La fiche existante (si elle existe)
- Le contexte vault pour cette entité

**Sortie** : Fiche individu ou organisation créée/enrichie.

**Spécificité** : Gère la distinction création vs enrichissement. Quand elle enrichit, elle doit intégrer les nouvelles infos sans créer de redondances avec l'existant.

### 5. `write-concept`

**Rôle** : Rédiger ou enrichir une fiche dans `Concepts/`.

**Entrée** :
- Ce que le transcript dit du concept
- La fiche existante (si elle existe)
- Le contexte vault pour ce concept

**Sortie** : Fiche concept créée/enrichie.

**Spécificité** : Les concepts sont le cœur analytique du vault. La skill doit être exigeante sur la clarté de la définition et du mécanisme.

### 6. `write-enjeu`

**Rôle** : Rédiger ou enrichir une fiche dans `Enjeux/`.

**Entrée** :
- Ce que le transcript dit de l'enjeu
- La fiche existante (si elle existe)
- Le contexte vault : **toutes les vidéos** qui touchent à cet enjeu, pas juste la courante

**Sortie** : Fiche enjeu créée/enrichie.

**Spécificité** : C'est la skill qui bénéficie le plus de la séparation contexte/écriture. Un enjeu est un combat **récurrent** — il ne peut être bien documenté qu'avec une vue d'ensemble sur toutes les vidéos où il apparaît. La skill doit :
- Consolider les arguments récurrents (pas les empiler vidéo par vidéo)
- Identifier les adversaires et les alliés sur cet enjeu
- Tracer l'évolution de la position PaduTeam dans le temps
- Être explicite sur ce qui distingue un enjeu d'un thème (prescriptif vs descriptif)

### 7. `ingest-batch` (Phase 2)

**Rôle** : Ingérer plusieurs transcripts liés à un même sujet pour une cohérence maximale.

**Workflow** :
1. L'utilisateur fournit un sujet ou une liste de vidéos
2. La skill identifie tous les transcripts disponibles sur ce sujet
3. Elle lit et analyse tous les transcripts ensemble
4. Elle construit un contexte consolidé (thèses qui reviennent, évolutions, contradictions)
5. Elle appelle `ingest-video` pour chaque vidéo, en lui passant ce contexte enrichi

**Pourquoi c'est utile** : Quand on ingère la vidéo #47 sur la guerre PS/LFI isolément, on ne sait pas que les vidéos #12, #23 et #35 ont déjà couvert le sujet sous d'autres angles. Le batch permet de produire des fiches plus cohérentes et moins redondantes.

**Pourquoi c'est Phase 2** : Ça nécessite que les skills unitaires soient solides d'abord.

---

## BUILD.md — Ce qu'il doit contenir

Le fichier `BUILD.md` (référencé par `CLAUDE.md`) documente **comment** le vault est construit, pas **ce qu'il contient**. Il doit couvrir :

1. **L'architecture des skills** — Le schéma ci-dessus, avec le rôle de chaque skill
2. **Le flux de données** — Comment le contexte circule entre les skills (gather → ingest → write-*)
3. **Les invariants** — Les règles que toutes les skills doivent respecter (nommage, wikilinks, frontmatter, ton)
4. **Le cycle de vie d'une fiche** — Comment une fiche passe de ébauche → développé → mature, et quelles skills interviennent à chaque étape
5. **Les conventions git** — La stratégie de branches, le format des commits et PR (déjà documenté dans SKILL.md, à déplacer ici)

`CLAUDE.md` référencerait `BUILD.md` pour les conventions de construction, et les SKILL.md individuels se concentreraient sur leur workflow spécifique sans redire les invariants.

---

## Plan d'exécution

### Phase 1 — Fondations

1. **Écrire `BUILD.md`** avec l'architecture cible et les invariants communs
2. **Extraire les invariants** de `SKILL.md` actuel vers `BUILD.md` (conventions git, nommage, wikilinks, frontmatter, taxonomie)
3. **Créer `gather-context`** — c'est le prérequis de tout le reste
4. **Créer `write-enjeu`** — c'est la skill qui manque le plus (les enjeux sont mal servis par le monolithe)
5. **Refactorer `ingest-video`** — le transformer en orchestrateur qui délègue aux skills spécialisées

### Phase 2 — Skills spécialisées

6. **Créer `write-video`**, `write-entity`, `write-concept`** en extrayant la logique du monolithe
7. **Tester le nouveau pipeline** sur 2-3 ingestions
8. **Itérer** sur les templates et la qualité des fiches produites

### Phase 3 — Multi-vidéo

9. **Créer `ingest-batch`**
10. **Tester** sur un sujet couvert par 5+ vidéos (ex: guerre des gauches)
11. **Utiliser `ingest-batch`** pour reprendre l'ingestion des ~520 vidéos restantes par blocs thématiques

---

## Décisions prises

- **Granularité des skills write-*** : `write-entity` couvre individus ET organisations — une seule skill, les templates sont très proches.
- **Format du contexte** : Fichier temporaire structuré + lecture des fiches existantes pertinentes. Le contexte inclut : les fiches vault pertinentes, les MOC thématiques (cf. NEXT_STEPS Phase 3), et une fiche `objectif.md` décrivant les objectifs fondamentaux de la PaduTeam. `gather-context` produit un fichier temp que les skills write-* consomment.
- **Attribution** : Invariant global dans `BUILD.md`. Attribution collective ("la PaduTeam") par défaut. Attribution individuelle uniquement quand explicitement identifiable (segment solo, auto-identification, rôle spécifique).
- **Rétrocompatibilité** : Chaque fiche porte dans son frontmatter YAML la version de la skill qui l'a générée (ex: `skill_version: ingest-v2`). Les fiches existantes restent en l'état — elles seront mises à jour plus tard par `ingest-batch` qui les passera à travers les nouvelles skills. Pas de migration rétroactive manuelle.

---

## Projet fondamental de la PaduTeam (à intégrer dans CLAUDE.md)

La PaduTeam n'est pas une chaîne de commentaire politique. C'est le bras médiatique d'une **structure militante** — l'association La Brèche — dont l'objectif est la transformation de la société. La production de contenu YouTube n'est qu'une des activités de La Brèche, pas sa finalité.

### Ce que la PaduTeam cherche à faire

1. **Donner des grilles de lecture matérialistes** — Le Graphique (matrice ACM PCS INSEE), l'analyse en blocs sociaux, le matérialisme historique — pour que les viewers comprennent le monde par eux-mêmes, pas via le filtre des médias dominants. L'objectif n'est pas de commenter l'actualité mais de *former politiquement* les spectateurs.

2. **Mener la bataille culturelle** — Être présent quotidiennement face à l'extrême droite qui a pris massivement l'espace internet. Choisir un camp, assumer une position de classe, refuser le "ni-nisme" (cf. [[Campisme]]). "Radicaliser la gauche molle", porter une ligne de gauche radicale le plus largement possible.

3. **Dessiner un possible** — Contre la vision pénurique dominante du monde (qui légitime les inégalités comme "inévitables"), montrer que des alternatives existent et sont désirables. La PaduTeam veut *gagner*, pas juste *résister* : "résister c'est être sur la défensive, être là face au monde qui évolue et qu'on aime pas, et on baisse la tête — c'est pas ça qu'on doit faire."

4. **Condenser le mouvement gazeux** — La critique centrale adressée à LFI et à la gauche en général : un mouvement politique non structuré se disperse sans laisser de forme solide. La Brèche est leur réponse : construire des structures militantes denses, ancrées dans le milieu professionnel des militants (pas des commentateurs extraits du monde du travail), fédérées entre elles. La période (néolibéralisme en crise, extrême-droitisation, désocialisation des territoires) nécessite cette structuration — comme le mouvement ouvrier historique a construit des solidarités directes là où l'État Providence n'existait pas encore.

5. **Devenir majoritaire** — Sortir de la "complaisance minoritaire" : l'autosatisfaction d'être progressiste dans un océan hostile. Les idées de la PaduTeam ont vocation à devenir hégémoniques. Cela implique de "tenter des coups", de "salir les mains", de prendre des paris — pas de rester dans un cocon militant confortable.

### Principes structurants

- **Le double emploi** : Padu (pédopsychiatre), Chris (cadre industrie), Zoé (médecin généraliste) gardent leurs emplois salariés. C'est un choix militant théorisé : extraire les militants de leur milieu professionnel crée une "pseudo avant-garde" déconnectée de la pratique collective. Rester salarié, c'est garder le rapport au monde du travail.
- **Média ≠ but, média = outil** : "Notre objectif c'est d'avoir une structure militante dont la production médiatique doit être une des activités principales pour faire avancer nos idées." Devenir des professionnels des médias créerait des logiques de conservation et des choix éditoriaux dictés par la survie du média plutôt que par la ligne politique.
- **Fédération** : La Brèche porte un projet de fédération avec d'autres créateurs/associations de gauche. Charte progressiste (antiracisme, anticapitalisme, féminisme, anti-impérialisme). Objectifs : mutualisation des moyens, sécurisation juridique face à la répression, résistance à la censure des plateformes.

### Pourquoi c'est important pour le vault

Ce cadre informe le "pourquoi" derrière chaque analyse PaduTeam. Quand ils parlent du PS, ce n'est pas du commentaire politique — c'est une pièce dans le combat "Plus jamais PS". Quand ils analysent le Graphique, c'est un outil de formation politique, pas un exercice académique. Chaque fiche du vault doit porter cette intention militante — pas la nuancer, pas la neutraliser.

### Principe d'auto-amélioration du système

Chaque ingestion de vidéo est une occasion de récolter du feedback pour le système lui-même. Les transcripts peuvent révéler des insights qui devraient mettre à jour CLAUDE.md, BUILD.md, les définitions de skills ou les conventions. Rien dans la description du système n'est figé — chaque transcript est une source potentielle de raffinement.

---

## Questions ouvertes restantes

- **Structure exacte du fichier temp de contexte** : Quel format ? Quel découpage ? À prototyper avec `gather-context`.
- **Emplacement de l'objectif PaduTeam** : Directement dans `CLAUDE.md` (toujours en contexte) ou dans une fiche `objectif.md` lue par `gather-context` ? Probablement CLAUDE.md pour que ce soit toujours disponible, même hors ingestion.
- **MOC et gather-context** : Les MOC n'existent pas encore (Phase 3 de NEXT_STEPS). `gather-context` doit fonctionner sans eux dans un premier temps, puis les exploiter quand ils existeront.
