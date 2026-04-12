---
type: index
date created: Tuesday, March 31st 2026, 11:21:18 pm
date modified: Thursday, April 2nd 2026, 10:27:51 am
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
