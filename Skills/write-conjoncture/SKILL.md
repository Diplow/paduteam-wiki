---
name: write-conjoncture
description: >
  Rédige ou enrichit une fiche de couche "conjoncture" — c'est-à-dire un diagnostic d'état
  structurant du moment historique selon la PaduTeam (crise de l'hégémonie américaine,
  triple crise du capitalisme, moïsation, extrême-droitisation, néolibéralisme en crise…).
  Une conjoncture n'est pas un évènement (fait daté) ni une méthode (outil). Déclencher
  quand l'utilisateur demande une promotion d'un concept en conjoncture, ou la création/
  enrichissement d'une fiche conjoncture.
date created: 2026-04-25
date modified: 2026-04-25
---

# Skill : Write Conjoncture

## Vue d'ensemble

Une **conjoncture** capture un état structurant du moment historique tel que la PaduTeam le diagnostique. Elle se reconnaît à trois signes : (1) elle décrit un état, pas un fait ponctuel ; (2) elle recouvre plusieurs années ; (3) elle articule un mécanisme causal (pourquoi le monde est dans cet état). C'est ce qui rend lisibles les évènements qui s'y inscrivent.

## Prérequis

- `Sources/.context-tmp.md` produit récemment par `gather-context` sur la conjoncture
- Conventions partagées : voir `BUILD.md`
- Si une fiche existe déjà (souvent dans `Concepts/`), la lire en entier — décider création vs enrichissement

## Entrée / Sortie

- **Entrée** : nom de la conjoncture, contexte gather-context
- **Sortie** : fiche dans `Concepts/{Nom}.md` (reste dans Concepts/ — conjoncture = vue via frontmatter). Frontmatter : `couche: conjoncture`, `periode: YYYY-YYYY`, `couche_skill_version: write-conjoncture-2026-04-25`

## Sections attendues

```markdown
---
type: concept
couche: conjoncture
periode: "2008-2026"
domaine: [...]
thèmes: [...]
aliases: [...]
skill_version: write-concept-YYYY-MM-DD
couche_skill_version: write-conjoncture-YYYY-MM-DD
---
#domaine/... #thème/...

# {Nom de la conjoncture}

## Diagnostic
1-3 phrases : qu'est-ce que la PaduTeam constate, et pourquoi c'est structurant ?

## Mécanisme
Le rapport causal qui produit cet état (contradictions du capital, basculement géopolitique, recomposition des classes…). Pas une description, une explication.

## Symptômes / manifestations
Comment cette conjoncture se manifeste concrètement — listes des phénomènes visibles qu'elle rend lisibles. Avec wikilinks vers les évènements, individus, organisations.

## Période
Bornes temporelles approximatives. Évènements qui ouvrent / cristallisent / accentuent la conjoncture.

## Concepts associés
[[Concept1]], [[Concept2]] — autres conjonctures qui s'articulent, méthodes mobilisées pour la lire, possibles qu'elle ouvre ou ferme.

## Vidéos clés
- [[Titre vidéo]] — comment la conjoncture y est diagnostiquée
```

## Anti-patterns

- **Confondre conjoncture et évènement** : « Élection Trump 2 » est un évènement ; « extrême-droitisation » est une conjoncture qu'il accélère.
- **Diagnostic descriptif sans mécanisme** : la section *Mécanisme* est obligatoire — sans elle, la fiche est juste une description, pas un diagnostic.
- **Bornes temporelles floues** : `periode` doit être renseignée même approximative ; sans repère temporel, on perd l'ancrage matérialiste.
