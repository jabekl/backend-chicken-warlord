# Backend-chicken-warlord

LINK ZUM SPIEL: [CHICKEN WARLORD](https://chicken-warlord.herokuapp.com/)

Die volle Projekterklärung findet man bei dem [Repo für das Frontend](https://github.com/jabekl/chicken-warload/). 

## Wie funktioniert es?

Es gibt folgende Methoden, um die Api zu verwenden:

- Get Request für die Top 3 (url/):

```json
[
    {
        "name" : "Name1",
        "points" : 1
    },
    {
        "name" : "Name2",
        "points" : 2
    },
    {
        "name" : "Name3",
        "points" : 3
    }
]
```

- Post Request für einen neuen Eintag (url/top-3-post):

```json
{
    "name": "xy",
    "points": 0
}  
```

Für die Api benötigt man eine Basic Http Authorisation im Header und eine Angabe über die Formatierung für die Datenübergabe:

```json
{
    "Authorization" : "Api key",
    "Content-Type" : "application/json"
}
```
