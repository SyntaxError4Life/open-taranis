# Le streaming

```python
import open_taranis as T

client = T.Clients.openrouter 

request = T.Request(
    tools=None, tool_choice="auto",
    temperature=0.4
)

### Nous sommes tout là ###
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
### ### ### ### ### ### ###
```

---

Enfin le **steaming** dans **`open-taranis`** est la partie la plus importante et ce qui a pris le plus de **temps à coder**, tout dans une seule fonction `T.handle_streaming()` qui prend comme arguments :
- `request:Request` : Le **profil** de la conversation/agent pour le **steam**
- `client:Client` : Le **client** avec notre **endpoint**
- `model:str` : Le **nom du modèle** via le client
- `messages:list[dict]` : L'**historique de la conversation**, qu'on voit juste après
- `API_KEY:str=None` : La **clé API** qu'on peut donner en **dur ou via notre propre moyen**, plutôt que via les **variables d'environnement**

À chaque chunk valide on retourne ces éléments :
- `token` : Le **token reçu** en texte
- `is_thinking` : Le **booléen** indiquant si le token reçu vient d'un **raisonnement ou non**
- `tools` : La **liste des outils reçus**, qu'on verra plus tard
- `tool_bool` ou `run` : Un **booléen** inquant si on a reçu au moins un outil, utile pour **relancer** une **boucle agentique**
- `meta` : Un **dicitonnaire** de méta-données utiles pour de l'analyse et autres (certains clients ne donnent rien !)

Sur la page suivante on verra donc comment on gère l'**historique** ainsi que les **prompts et autres** !!