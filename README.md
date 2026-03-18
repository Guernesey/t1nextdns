# UT1 Toulouse → NextDNS Blocklists

Ce dépôt convertit automatiquement les catégories de blacklist UT1 (Université de Toulouse Capitole) en listes de blocage compatibles NextDNS.

## Contenu

- `update_lists.py` : télécharge l’archive UT1, nettoie les domaines, génère `dist/*.txt` et `metadata.json`.
- `dist/toulouse-<categorie>.txt` : listes prêtes à l’emploi pour NextDNS.
- `metadata.json` : métadonnées des listes générées (URL Raw, description, nombre d’entrées).

## Prérequis

- Python 3.10+
- Dépendance Python : `requests`

Installation rapide :

```bash
python -m pip install requests
```

## Utilisation locale

1. Ouvrir `update_lists.py`.
2. Remplir `CATEGORIES_TO_PROCESS` (en haut du script), par exemple :

```python
CATEGORIES_TO_PROCESS = ["adult", "agressif", "phishing"]
```

3. (Optionnel) définir les variables d’environnement pour générer les bonnes URL Raw dans `metadata.json` :

```bash
export GITHUB_OWNER="<votre-user-ou-org>"
export GITHUB_REPO="<votre-repo>"
export GITHUB_BRANCH="main"
```

4. Lancer :

```bash
python update_lists.py
```

## Ajouter une liste dans NextDNS

1. Ouvrir votre tableau de bord NextDNS.
2. Aller dans **Privacy**.
3. Dans **Add a custom filter**, coller l’URL Raw de la liste souhaitée (voir `metadata.json`).
4. Valider l’ajout.

Exemple d’URL Raw attendue :

```text
https://raw.githubusercontent.com/<owner>/<repo>/main/dist/toulouse-adult.txt
```

## Automatisation

Le workflow GitHub Actions (`.github/workflows/update.yml`) exécute la mise à jour tous les lundis à 00:00 (UTC), puis commit/push automatiquement les fichiers mis à jour.
