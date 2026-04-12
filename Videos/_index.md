---
type: index
date created: Tuesday, March 31st 2026, 11:21:13 pm
date modified: Sunday, April 12th 2026, 5:46:47 pm
---
# Index des vidéos

## Toutes les vidéos ingérées

```dataview
TABLE WITHOUT ID
  file.link AS "Vidéo",
  date AS "Date",
  intervenants AS "Intervenants",
  domaine AS "Domaine",
  format AS "Format",
  statut AS "Statut"
FROM "4. Jeux/Notes/Graphiked/Knowledge/videos"
WHERE type = "vidéo"
SORT date DESC
```

## Par domaine

```dataview
TABLE WITHOUT ID
  file.link AS "Vidéo",
  domaine AS "Domaine",
  thèmes AS "Thèmes"
FROM "4. Jeux/Notes/Graphiked/Knowledge/videos"
WHERE type = "vidéo"
SORT domaine ASC
```

## Par enjeu

```dataview
TABLE WITHOUT ID
  file.link AS "Vidéo",
  enjeux AS "Enjeux",
  date AS "Date"
FROM "4. Jeux/Notes/Graphiked/Knowledge/videos"
WHERE type = "vidéo" AND enjeux
SORT date DESC
```
