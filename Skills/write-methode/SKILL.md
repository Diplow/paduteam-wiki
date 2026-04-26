---
name: write-methode
description: >
  Rédige ou enrichit une fiche de couche "méthode" — c'est-à-dire une grille d'analyse
  PaduTeam (matérialisme historique, Le Graphique, analyse en blocs sociaux, analyse
  concrète de la situation concrète…). Une méthode est un *outil* qui organise le regard,
  pas un sujet ni un combat. Déclencher quand l'utilisateur demande une promotion d'un
  concept en méthode, ou la création/enrichissement d'une fiche méthode.
date created: 2026-04-25
date modified: 2026-04-25
---

# Skill : Write Méthode

## Vue d'ensemble

Une **méthode** capture une grille d'analyse mobilisée par la PaduTeam pour lire le réel. Elle se reconnaît à trois signes : (1) elle énonce un principe d'analyse, pas une thèse ; (2) elle est transversale (s'applique à plusieurs objets) ; (3) elle produit des distinctions opérantes. Si le sujet décrit *un* phénomène plutôt que *comment regarder*, c'est un concept ordinaire — utiliser `write-concept`.

## Prérequis

- `Sources/.context-tmp.md` produit récemment par `gather-context` sur la méthode
- Conventions partagées : voir `BUILD.md`
- Si une fiche existe déjà (souvent dans `Concepts/`), la lire en entier — décider création vs enrichissement

## Entrée / Sortie

- **Entrée** : nom de la méthode, contexte gather-context
- **Sortie** : fiche dans `Concepts/{Nom}.md` (la fiche reste dans Concepts/ — la méthode est une *vue* via le frontmatter, pas une migration physique). Frontmatter mis à jour : `couche: methode` (ou ajout à la liste si déjà présent), `couche_skill_version: write-methode-2026-04-25`

## Sections attendues

```markdown
---
type: concept
couche: methode
domaine: [...]
thèmes: [...]
aliases: [...]
skill_version: write-concept-YYYY-MM-DD
couche_skill_version: write-methode-YYYY-MM-DD
---
#domaine/... #thème/...

# {Nom de la méthode}

## Définition
1-3 phrases : qu'est-ce que cette méthode énonce comme principe d'analyse ?

## Mécanisme
Comment elle opère : quelles distinctions elle produit, quels rapports elle met en lumière, ce qu'elle rend visible que d'autres méthodes ratent.

## Exemples d'application
2-4 cas concrets où la PaduTeam mobilise cette méthode (avec wikilinks vers les vidéos, les individus analysés, les enjeux éclairés).

## Concepts dérivés
[[Concept1]], [[Concept2]] — outils analytiques qui découlent de cette méthode ou la spécifient.

## Vidéos où elle est mobilisée
- [[Titre vidéo]] — comment elle y est appliquée
```

## Anti-patterns

- **Confondre méthode et concept** : si la fiche décrit *un état du monde* (ex. moïsation), c'est une conjoncture, pas une méthode. Si elle décrit *un horizon désirable*, c'est un possible.
- **Énumérer sans articuler** : la section *Mécanisme* doit dire *comment* la méthode produit ses distinctions, pas juste *quoi* elle observe.
- **Oublier la transversalité** : une méthode s'applique à plusieurs objets. Donner au moins 2 exemples d'objets différents éclairés par elle.
