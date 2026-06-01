# Le commencement

Un petit exemple de **code** :
```python
import open_taranis as T

client = T.Clients.openrouter # API_KEY in env_var

request = T.Request(
    tools=None, tool_choice="auto",
    temperature=0.4,
    # and others....
)

print("assistant : ",end="")
for token, is_thinking, tools, tool_bool, meta in T.handle_streaming(
    request=request,
    client=client,
    model="nvidia/nemotron-3-nano-30b-a3b:free",
    messages=[T.create.user_prompt("Tell me about yourself")],
    API_KEY=None
) : 
    # You can add `if not is_thinking :` to see only the reals tokens
    print(token, end="", flush=True)

print(f"\n\n{meta}")
```

Ici on a :
1. `import open_taranis as T` : L'importation du module
2. `client = T.Clients` Pour récupérer l'objet `Clients` dont on a besoin (ici `openrouter`)
3. `request = T.Request` Pour générer l'objet servant à faire nos **requêtes** avec les paramètres classiques
4. `for token, is_thinking, tools, tool_bool, meta in T.handle_streaming` est notre méga-boucle avec tout ce dont on a besoin
5. `T.create.user_prompt` : Fonction pour passer le texte au bon format
6. `print(token, end="", flush=True)` : Ici c'est pas important mais c'est conseillé pour voir chaque token dans le terminal
7. Enfin et élément important ici qui est le **`meta`**, il retourne (quand possible) un dictionnaire comme.

---

Détails :
- On retourne les **tokens classiques** et de **raisonnement** en **même temps** puis on retourne un **booléen si raisonnement**.
- `tool_bool` est similaire, il indique si on a un outil, dans une **boucle agentique** on peut le nommer `run`, indique si on **continue la boucle ou non**.
- Les clés API sont **récupérées automatiquements** depuis l'env python, faites `taranis clients` dans votre terminal pour voir **lesquelles sont détectées**.
- La variable `meta` a pour valeur de base `{'prompt_tokens': 0, 'completion_tokens': 0, 'cached_tokens': 0}` *(utile pour calculer les coûts en temps réel)*

Dans la prochaine page on va voir les **client** justement !!