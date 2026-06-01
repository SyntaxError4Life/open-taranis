### Mise à jour paquet Python (open-taranis)

#### 1. **Prépa code/version**
- Bump version dans `pyproject.toml` : `version = "X.Y.Z"`.
- Harmonise `__version__` dans `src/open_taranis/__init__.py`.
- Ajoute deps si besoin : `dependencies = ["openai", "..."]`.
- Commit : `git add . && git commit -m "Update to vX.Y.Z: [détails]"`.

#### 2. **Build & Test local**
- `hatch build` (génère `dist/` avec .whl et .tar.gz).
- `pip uninstall open-taranis` (si installé).
- `pip install dist/open_taranis-X.Y.Z-py3-none-any.whl`.
- Test : `python -c "import open_taranis; print(open_taranis.__version__)"`.
- `rm -rf dist/` après.

#### 3. **Release GitHub/PyPI**
- `git tag vX.Y.Z`.
- `git push origin main` (si changes).
- `git push origin vX.Y.Z` (trigger workflow).
- Vérifie Actions : log pour erreurs (auth, build, twine).
- Si conflit tag : `git push origin :refs/tags/vX.Y.Z` puis repush.

#### Choses à penser            
- **Secrets GitHub** : PYPI_USERNAME=`__token__`, PYPI_PASSWORD=token PyPI (scope upload).
- **Versionning** : SemVer (major.minor.patch) ; pas de re-upload même version.
- **TestPyPI** : Pour debug : `twine upload --repository testpypi dist/*`.
- **Post-release** : Update README exemples ; `pip install open-taranis==X.Y.Z --upgrade` pour valider.
- **Erreurs courantes** : Tirets vs underscores (import fail) ; token auth 403 (check `__token__`).

# En cours :
1. git add . && git commit -m "Update to vX.Y.Z"
2. git tag vX.Y.Z
3. git push origin main && git push origin vX.Y.Z