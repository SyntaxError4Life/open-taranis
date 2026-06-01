# Les prompts

Pour simplifier le développement, des fonctions de pour **écrire l'historique de la conversation** ont été fait dans la classe `create` comme :
- `T.create.system_prompt`
- `T.create.user_prompt`
- `T.create.assistant_response`
- `T.create.function_response`

Et donc voilà comment fonctionne chacune :

1. `system_prompt` prend :
    - `content:str` : Le contenu des instructions
2. `user_prompt` prend :
    - `content` : Le contenu du message de l'utilisateur
    - `images` : La liste d'images en URL ou base64
3. `assistant_response` prend :
    - `content` : Le contenu de la réponse de l'assistant
    - `tool_calls` : La liste des outils
    - `reasoning_content` : Le contenu du raisonnement (pour **certains** endpoints)
4. `function_response` prend :
    - `id` : L'identifiant de l'outil en chaîne de texte
    - `result` : Le résultat aussi en texte
    - `name` : Le nom de l'outil

Pour les images on a la fonction `image_to_base64` qui prend le **chemin local** de l'image dans **votre machine** et le retourne en **base 64**.

---

Voilà un exemple complet :
```python
messages = [
    T.create.system_prompt("Tu es un agent nommé **Taranis**"),
    T.create.user_prompt("Qu'est-ce qu'il y a dans cette image ?", ["https://upload.wikimedia.org/wikipedia/commons/d/d9/Collage_of_Nine_Dogs.jpg"]),
    T.create.assistant_response("Je vois un collage de 9 chiens..."),
    T.create.user_prompt("D'accord et combien de temps vit le chien en haut au milieu ?"),
    T.create.assistant_response(
        reasoning_content="À cet endroit je vois un labrador, je regarde sur le web",
        tool_calls=[
            {
            "id": "0010",
            "type": "function",
            "function": {
                "name": "web_search",
                "arguments": "{\"search\": \"Durée de vie labrador\"}"
            }
            }
        ]
    ),
    T.create.function_response("0010", "10-12 ans", "web_search"),
    T.create.assistant_response("Entre 10 et 12 ans...")
]
```

Ensuite on verra comment on fait les outils avec **`open-taranis`** !!