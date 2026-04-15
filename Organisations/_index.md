---
type: index
date created: Tuesday, March 31st 2026, 11:21:18 pm
date modified: Wednesday, April 15th 2026, 1:40:01 pm
---
# Index des organisations

## Toutes les organisations

```dataview
TABLE WITHOUT ID
  file.link AS "Organisation",
  domaine AS "Domaine",
  thèmes AS "Thèmes",
  quadrant_graphique AS "Position Graphique",
  statut AS "Statut",
  length(file.inlinks) AS "Mentions"
FROM "4. Jeux/Notes/Graphiked/Knowledge/organisations"
WHERE type = "organisation"
SORT length(file.inlinks) DESC
```
