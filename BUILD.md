---
date created: Sunday, April 12th 2026, 6:30:00 pm
date modified: 2026-04-26
---
# BUILD.md — Conventions PaduTeam

Ce fichier documente les **conventions propres à PaduTeam**. Les invariants génériques (architecture des skills, nommage, wikilinks, frontmatter universel, hashtags, sourcing YouTube, workflow git) vivent dans le `BUILD.md` de WikiPol à la racine du repo parent — voir `../../BUILD.md`.

---

## Architecture en couches d'accès

Au-delà des fiches « entité » de base (Vidéos / Individus / Organisations / Concepts / Enjeux / Évènements), trois **couches d'accès** rendent navigable la pensée PaduTeam comme projet structuré :

- **Méthodes** (`Methodes/`) — outils d'analyse (matérialisme historique, Le Graphique, analyse en blocs sociaux). Une méthode organise le regard.
- **Conjonctures** (`Conjonctures/`) — diagnostics du moment historique (crise de l'hégémonie US, triple crise du capitalisme, moïsation, extrême-droitisation). Une conjoncture décrit un état structurant.
- **Possibles** (`Possibles/`) — horizons défendus (universalisme matériel, choc d'abondance, désagrégation progressiste de l'empire). Un possible se déploie *vers* un horizon ; un enjeu se mène *contre* un adversaire.

**Spécificité PaduTeam** : ces 3 couches **n'ont pas de fichiers propres** au-delà du MOC + `.base`. Les concepts qui en relèvent restent dans `Concepts/` avec un champ `couche` en frontmatter (`couche: methode | conjoncture | possible`, ou liste si transverse). Méthodes/Conjonctures/Possibles sont donc des **vues** sur Concepts, matérialisées par les `.base` Obsidian.

Les **Évènements** (`Evenements/{periode}/`), en revanche, sont des entités à part entière (type `evenement`), organisés en sous-dossiers de période (`2026/`, `1950-1979/`…).

Les skills `write-methode`, `write-conjoncture`, `write-possible`, `write-enjeu`, `write-evenement` sont des **skills source-spécifiques** (`Skills/`) qui surchargent les versions génériques de WikiPol. Voir la section « Skills spécifiques à PaduTeam » dans `CLAUDE.md`.

---

## Attribution

**Attribution collective par défaut** — les analyses sont attribuées à « la PaduTeam », pas à un membre individuel. N'attribuer individuellement que quand c'est explicitement identifiable dans le transcript :

- Segment solo (un seul intervenant)
- Auto-identification (« moi en tant que médecin… »)
- Rôle spécifique reconnu (« Chris qui a conçu le Graphique »)

Le tag `paduteam` n'est **pas utilisé** dans les fiches — tout le vault est PaduTeam par définition.

---

## Taxonomie

### Domaines (5, fixes)

`politique-intérieure`, `géopolitique`, `économie`, `théorie`, `société`.

### Thèmes (vocabulaire contrôlé, extensible)

`élections`, `anti-impérialisme`, `Palestine`, `Venezuela`, `féminisme`, `racisme-antiracisme`, `ruralité`, `médias-propagande`, `guerre-des-gauches`, `le-Graphique`, `travail`, `écologie`, `répression-justice`, `psychiatrie-psychologie`, `Iran`, `États-Unis`, `Amérique-latine`, `antivalidisme`, `santé`.

Ajouter un nouveau thème si un sujet revient dans **2+ vidéos**.

### Enjeux (combats stratégiques récurrents)

`plus-jamais-PS`, `Palestine-libre`, `anti-impérialisme`, `le-Graphique`, `union-populaire`, `campisme-assumé`.

Ajouter un nouvel enjeu si un combat revient dans **3+ vidéos** avec une position constante.

---

## Back-références vers les couches d'accès

Les fiches bas-niveau (Vidéos, Individus, Organisations, Concepts) qui mobilisent un objet de couche supérieure le déclarent en frontmatter — c'est ce qui alimente les `.base` des couches.

```yaml
methodes: [Materialisme historique, Graphique]
conjonctures: [Crise de l hegemonie americaine, Triple crise du capitalisme]
possibles: [Desagregation de l empire americain]
evenements: [Guerre USA-Iran 2026, Enlevement Maduro 2026]
# enjeux: [...] existe déjà sur les vidéos
```

**Ne pas remplir ces champs gratuitement** — uniquement si la fiche bas-niveau *traite significativement* de l'objet de couche. Ce sont les `.base` qui alimentent la navigation par couche : la qualité du back-référencement = la qualité de la navigation.

---

## Style

- Phrases courtes, pas de remplissage
- Fidélité totale à l'analyse PaduTeam
- Ton analytique, pas encyclopédique — restituer la vision PaduTeam, pas Wikipedia
- Les jugements de valeur de la PaduTeam font partie de la restitution : ne pas les censurer, ne pas les atténuer
- Si la PaduTeam dit « Hollande est un traître », écrire « Hollande est un traître »

---

## Volume

Être ambitieux dans la création de fiches. Chaque personne mentionnée significativement, chaque parti cité, chaque mécanisme analytique décrit mérite sa fiche. Il vaut mieux créer une fiche minimale (ébauche) que de laisser un lien orphelin.
