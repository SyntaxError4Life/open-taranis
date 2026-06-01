# Les requêtes

```python
import open_taranis as T

client = T.Clients.openrouter 

request = T.Request(                  # 
    tools=None, tool_choice="auto",   # Nous sommes ici
    temperature=0.4                   #
)                                     #

print("assistant : ",end="")
for token, is_thinking, tools, tool_bool, meta in T.handle_streaming(
    request=request,
    client=client,
    model="nvidia/nemotron-3-nano-30b-a3b:free",
    messages=[T.create.user_prompt("Tell me about yourself")],
    API_KEY=None
) : 
    print(token, end="", flush=True)

print(f"\n\n{meta}")
```

---

Dans **`open-taranis`** on a implémenté des fonctions pour les requêtes pour les mêmes raisons que les `Client`, ces fonctions de requêtes sont des sortes de **profils réutilisables** entre **clients**.

Les seuls faits pour le moment :
1. `Request` : L'objet de base qui est héritable
2. `VeniceRequest` : Hérite de `Request` pour ajouter des champs spécifiques à **Venice.ai**

Les objets **spécifiques** à un client peuvent tout de même être utilisés avec d'**autres clients** mais des **erreurs** de endpoint **sont à prévoir**.

---

Dans le `Request` par défaut on a tous ces arguments :
- `tools` : La liste des outils qui seront partagés au endpoint
- `tool_choice` : Comment est le choix, de base à `auto`
- `temperature` : La température du modèle, de base à `0.4` (pour du code par ex)
- `max_tokens` : Le nombre max de tokens que le contexte peut faire, de base à `4096` comme ollama
- Et d'autres paramètres...

`Request` gère les erreurs **HTTP**, **expiration**, problème avec l'URL du **client** et d'autres erreurs gérées par le module `requests` de **python**.

---

On a aussi une fonction `Request.make()` permettant de générer ce qui est nécessaire au flux de stream, mais nous verrons ça à la prochaine page !!