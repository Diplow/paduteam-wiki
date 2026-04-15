---
name: gather-context
description: >
  Rassemble tout ce que le vault sait sur un sujet donné et produit un document de contexte structuré.
  Utilisé en amont des skills write-* pour leur fournir une vision d'ensemble plutôt qu'un contexte partiel.
  Déclencher quand une autre skill a besoin de contexte vault, ou quand l'utilisateur demande
  "quel contexte on a sur X", "qu'est-ce qu'on sait de X", "rassemble les infos sur X".
date created: Sunday, April 12th 2026, 6:45:00 pm
date modified: Wednesday, April 15th 2026, 1:40:01 pm
---

# Skill : Gather Context

## Vue d'ensemble

Cette skill prend un **sujet** (nom d'enjeu, concept, individu, organisation, thème de vidéo, ou question libre) et produit un **document de contexte structuré** contenant tout ce que le vault sait déjà sur ce sujet.

Le contexte produit est destiné à être consommé par les skills `write-*` (write-enjeu, write-concept, write-entity, write-video). Il peut aussi être utilisé directement pour répondre à une question de l'utilisateur.

## Principe

Les skills d'écriture ne doivent pas faire de recherche extensive — elles reçoivent le contexte et se concentrent sur la rédaction. C'est cette skill qui fait le travail de recherche.

---

## Entrée

Un sujet, fourni sous l'une de ces formes :
- Nom d'une fiche existante (ex: "Plus jamais PS", "Jean-Luc Melenchon", "Saint Graphique")
- Thème transversal (ex: "guerre des gauches", "Palestine")
- Titre ou sujet d'une vidéo à ingérer (ex: "les municipales 2026")
- Question libre (ex: "qu'est-ce que la PaduTeam pense du PS ?")

## Sortie

Un fichier temporaire `Sources/.context-tmp.md` (ignoré par git via `.gitignore`) contenant le contexte structuré. Ce fichier est écrasé à chaque appel.

---

## Workflow

### Étape 1 — Identifier les fiches directement liées

Chercher dans le vault les fiches dont le sujet est le thème principal :

1. **Fiche exacte** : si le sujet correspond à un fichier existant dans `Enjeux/`, `Concepts/`, `Individus/`, `Organisations/`, le lire en entier
2. **Fiches vidéo** : chercher dans `Videos/` les fiches qui mentionnent le sujet (grep dans le contenu ou dans les tags thèmes/enjeux du frontmatter)
3. **MOC et Enjeux liés** : ces deux types de fiches sont les meilleurs relais de contexte — elles agrègent des liens thématiques par nature. Chercher dans `MOC/` et `Enjeux/` les fiches qui touchent au sujet (par wikilinks ou par thème). Les lire en priorité.
4. **Fiches entités liées (profondeur 1)** : à partir des wikilinks trouvés dans les fiches ci-dessus (y compris MOC et enjeux), identifier les individus, organisations et concepts les plus pertinents (ceux qui reviennent dans 2+ fiches liées au sujet). Les lire.
5. **Fiches connexes (profondeur 2)** : dans les fiches lues à l'étape 4, relever les wikilinks vers des MOC, enjeux ou concepts qui semblent pertinents pour le sujet. Les lire à leur tour. Privilégier les fiches structurantes (MOC, enjeux, concepts) plutôt que les fiches terminales (individus, organisations) pour la profondeur 2 — elles produisent des connexions plus riches.

**Critère d'arrêt** : ne pas aller au-delà de la profondeur 2. Si une fiche de profondeur 2 ouvre un sujet très différent du sujet initial, ne pas la suivre.

### Étape 1b — Exploration par grep (pistes élargies)

La recherche par fiches et wikilinks ne trouve que ce qui est déjà explicitement lié. Pour découvrir des connexions que le vault n'a pas encore formalisées :

1. **Mots-clés du sujet** : générer 5-10 mots-clés et synonymes liés au sujet (ex: pour "Plus jamais PS" → PS, socialiste, Faure, Hollande, trahison, noisette, social-démocratie, gauche molle...)
2. **Grep dans toutes les fiches** (`Individus/`, `Organisations/`, `Concepts/`, `Enjeux/`, `Videos/`) pour ces mots-clés
3. **Grep dans les transcripts** pour les mêmes mots-clés — ne pas lire les transcripts, juste noter lesquels matchent et le nombre de hits (un transcript avec 20 occurrences de "PS" est probablement plus pertinent qu'un avec 1)
4. **Évaluer les pistes** : parmi les résultats grep, identifier les fiches et transcripts qui n'étaient pas déjà trouvés à l'étape 1. Les lire si ils semblent apporter du contexte nouveau.

Cette étape est particulièrement utile pour :
- Les sujets transversaux qui touchent beaucoup de fiches sans y être centraux
- Les connexions non formalisées (un concept utilisé dans une vidéo mais pas encore lié à l'enjeu)
- Les transcripts non ingérés qui traitent du sujet sans qu'on le sache

### Étape 2 — Scanner les transcripts disponibles

Chercher dans `Sources/Transcripts/` les transcripts qui traitent du sujet :

1. Croiser avec `Sources/Inventaire PaduTeam.md` pour identifier les vidéos pertinentes (par titre)
2. Si le sujet est un enjeu ou un thème large, grep les transcripts pour des mots-clés associés
3. **Ne pas lire les transcripts en entier** à cette étape — noter seulement lesquels sont pertinents et si ils ont déjà été ingérés (colonne Fiche de l'inventaire)

Distinguer :
- **Transcripts déjà ingérés** → la fiche vidéo contient déjà l'essentiel, pas besoin de relire le transcript
- **Transcripts non encore ingérés** → signaler leur existence comme source potentielle non exploitée

### Étape 3 — Construire le document de contexte

Écrire `Sources/.context-tmp.md` avec la structure suivante :

```markdown
# Contexte : {SUJET}

Généré le {DATE} par gather-context.

## Fiche principale
{Contenu complet de la fiche principale si elle existe, sinon "Pas de fiche existante"}

## Fiches vidéo pertinentes
{Pour chaque vidéo liée, résumé + thèses clés — copier les sections pertinentes}

## Entités liées (profondeur 1-2)
{Liste des individus, organisations, concepts connexes avec un résumé 1 ligne de leur rapport au sujet}
{Indiquer la profondeur : (direct) pour les liens de la fiche principale, (indirect) pour les liens découverts via une fiche liée}

## Pistes grep (connexions non formalisées)
{Fiches et transcripts découverts par grep qui ne sont pas déjà liés par wikilinks}
{Pour chaque piste : fichier, nombre de hits, extrait pertinent si utile}

## Transcripts non ingérés disponibles
{Liste des transcripts qui traitent du sujet mais n'ont pas encore de fiche vidéo — source de contexte supplémentaire}
{Indiquer le nombre de hits grep par transcript pour prioriser}

## Lacunes identifiées
{Ce qui manque : fiches orphelines, sujets mentionnés mais pas documentés, contradictions entre fiches, connexions qui devraient exister (wikilinks manquants)}
```

### Étape 4 — Rapporter à l'appelant

Résumer en quelques lignes :
- Volume de contexte trouvé (nombre de fiches, de vidéos, de transcripts)
- Les lacunes principales
- Recommandation : le contexte est-il suffisant pour écrire/enrichir, ou faut-il d'abord ingérer des transcripts supplémentaires ?

---

## Règles

- **Ne pas modifier le vault.** Cette skill est en lecture seule — elle ne crée ni ne modifie aucune fiche.
- **Ne pas lire tous les transcripts.** Les transcripts sont longs. Ne les lire que si spécifiquement demandé ou si le contexte des fiches existantes est insuffisant.
- **Budget de 30K tokens maximum.** Le fichier de contexte ne doit pas dépasser ~30K tokens. Au-delà, les skills write-* se noient dans le bruit. Copier en entier la fiche principale et les MOC/enjeux liés ; résumer les fiches secondaires (vidéos, entités) à leurs passages pertinents. Si le sujet est très transversal et que le budget est atteint, prioriser la profondeur (fiches les plus riches) plutôt que la couverture (toutes les fiches qui matchent).
- **Signaler les transcripts non ingérés.** C'est une information cruciale : elle permet à l'orchestrateur de décider s'il faut d'abord ingérer ces vidéos avant d'écrire/enrichir une fiche.
