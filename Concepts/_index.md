---
type: index
domaine: ['théorie']
thèmes: []
statut: ébauche
date created: Tuesday, March 31st 2026, 11:21:20 pm
date modified: Sunday, April 12th 2026, 5:46:48 pm
---
#domaine/théorie
# Index des concepts

## Tous les concepts

```dataview
TABLE WITHOUT ID
  file.link AS "Concept",
  domaine AS "Domaine",
  thèmes AS "Thèmes",
  statut AS "Statut",
  length(file.inlinks) AS "Mentions"
FROM "4. Jeux/Notes/Graphiked/Knowledge/concepts"
WHERE type = "concept"
SORT length(file.inlinks) DESC
```

## Concepts par domaine

```dataview
LIST
FROM "4. Jeux/Notes/Graphiked/Knowledge/concepts"
WHERE type = "concept" AND contains(domaine, "théorie")
SORT file.name ASC
```
