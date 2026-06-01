# Les clients

```python
import open_taranis as T

client = T.Clients.openrouter # Nous sommes ici

request = T.Request(
    tools=None, tool_choice="auto",
    temperature=0.4
)

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

Dans **`open-taranis`** on a implémenté les clients séparément pour deux raisons :
1. Rendre les endpoint plus **faciles à utiliser** sans avoir à les écrire.
2. Permettre dans le futur d'ajouter des **méta-paramètres** comme pour un **client spécifique**

Voilà la liste ce qu'on a déjà configuré :
- `openrouter` pour [openrouter.ai](https://openrouter.ai/) soit des milliers de modèles
- `huggingface` pour [huggingface.co](https://huggingface.co/)
- `venice.ai` pour [venice.ai](https://venice.ai/home), très pratique pour un endpoint anonyme
- `deepseek.ai` pour [deepseek.com](https://platform.deepseek.com/), le leader chinois.
- `x.ai` pour [x.ai](https://console.x.ai/)
- `mistral.ai` pour [mistral.ai](https://console.mistral.ai/home)
- `groq` pour [groq.come](https://console.groq.com/home), le plus rapide en **streaming+outils**
- `Kimi Code` pour [kimi.com](https://www.kimi.com/code), pas officiel mais le spoofing fonctionne pour le moment

Après en annexe vous avez `ollama` qui pointe en local et sans clé API, que du **localhost** est conseillé !!

---

Dans le code ça ressemble à cela :
```python
T.Clients.openrouter
T.Clients.huggingface
T.Clients.veniceai
T.Clients.deepseek
T.Clients.xai
T.Clients.groq
T.Clients.kimi_code

T.Clients.ollama
```

D'ailleurs **pour coder votre propre client**, ici pour un serveur **llama.cpp** par **exemple**, vous pouvez faire :
```python
custom_client = T.Client(
    API_KEY_name="llama_server_API_KEY",
    BASE_URL="https://api.https://example.com/"
)
```
Après vous pourrez l'**utiliser librement**

---

Dans la prochaine page on verra les requêtes, comment les faire !!