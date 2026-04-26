---
name: write-possible
description: >
  Rédige ou enrichit une fiche de couche "possible" — c'est-à-dire un horizon désirable
  défendu par la PaduTeam (choc d'abondance, universalisme matériel, socialisme
  autogestionnaire, désagrégation de l'empire américain comme progrès…). Un possible se
  distingue d'un enjeu (combat) : le combat se mène *contre*, le possible se déploie
  *vers*. Déclencher quand l'utilisateur demande une promotion d'un concept en possible,
  ou la création/enrichissement d'une fiche possible.
date created: 2026-04-25
date modified: 2026-04-25
---

# Skill : Write Possible

## Vue d'ensemble

Un **possible** capture une vision du monde positive que la PaduTeam articule comme horizon défendable. Il se reconnaît à trois signes : (1) il énonce un horizon désirable, pas seulement une critique ; (2) il articule un mécanisme matériel (comment on y va) ; (3) il a une *vision adverse* (le possible adverse à combattre). Sans vision adverse, c'est une utopie ; sans mécanisme, c'est un slogan.

## Prérequis

- `Sources/.context-tmp.md` produit récemment par `gather-context` sur le possible
- Conventions partagées : voir `BUILD.md`
- Si une fiche existe déjà (souvent dans `Concepts/`), la lire en entier — décider création vs enrichissement

## Entrée / Sortie

- **Entrée** : nom du possible, contexte gather-context
- **Sortie** : fiche dans `Concepts/{Nom}.md`. Frontmatter : `couche: possible`, `couche_skill_version: write-possible-2026-04-25`

## Sections attendues

```markdown
---
type: concept
couche: possible
domaine: [...]
thèmes: [...]
aliases: [...]
skill_version: write-concept-YYYY-MM-DD
couche_skill_version: write-possible-YYYY-MM-DD
---
#domaine/... #thème/...

# {Nom du possible}

## Horizon
1-3 phrases : quel monde, quelle organisation matérielle, quelle relation aux autres défend ce possible ?

## Mécanisme matériel
Comment on y va concrètement : quelles institutions, quelles luttes, quels rapports de forces produisent cet horizon. Pas une description du résultat — la voie matérielle.

## Vision adverse
Quel possible concurrent est défendu par les adversaires ? (Ex. : pénurie contre abondance, hiérarchie raciale contre universalisme matériel, empire unifié contre désagrégation.) Sans vision adverse explicite, le possible n'a pas de tranchant politique.

## Concepts associés
[[Concept1]], [[Concept2]] — méthodes qui le pensent, conjonctures qui l'ouvrent ou le ferment, enjeux qui le portent.

## Vidéos clés
- [[Titre vidéo]] — comment le possible y est articulé
```

## Anti-patterns

- **Possible sans vision adverse** : si on ne peut pas nommer ce *contre quoi* le possible se déploie, c'est qu'il n'a pas de contenu politique. La section est obligatoire.
- **Mécanisme idéaliste** : la section *Mécanisme matériel* doit décrire des rapports de forces, pas des bonnes intentions. « On éduquera les gens » n'est pas un mécanisme matériel.
- **Confondre possible et enjeu** : « Plus jamais PS » est un combat (enjeu), « universalisme matériel » est un possible. Si la fiche est centrée sur un *adversaire à abattre* plutôt que sur un horizon, utiliser `write-enjeu`.
