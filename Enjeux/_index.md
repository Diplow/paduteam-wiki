---
type: index
date created: Tuesday, March 31st 2026, 11:21:22 pm
date modified: Sunday, April 12th 2026, 5:46:48 pm
---
# Index des enjeux stratégiques

## Tous les enjeux

```dataview
TABLE WITHOUT ID
  file.link AS "Enjeu",
  domaine AS "Domaine",
  thèmes AS "Thèmes",
  statut AS "Statut",
  length(file.inlinks) AS "Vidéos liées"
FROM "4. Jeux/Notes/Graphiked/Knowledge/enjeux"
WHERE type = "enjeu"
SORT length(file.inlinks) DESC
```

## Vidéos par enjeu

```dataview
TABLE WITHOUT ID
  file.link AS "Vidéo",
  enjeux AS "Enjeux",
  date AS "Date"
FROM "4. Jeux/Notes/Graphiked/Knowledge/videos"
WHERE type = "vidéo" AND enjeux
SORT date DESC
```
