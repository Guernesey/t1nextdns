# UT1 Toulouse → NextDNS Blocklists

This repository automatically converts UT1 (Université Toulouse 1 Capitole) blacklist categories into NextDNS-compatible blocklists.

## Contents

- `update_lists.py`: downloads the UT1 archive, cleans domain entries, and generates `dist/*.txt` plus `ut1<id>`.
- `dist/UT1-<group>.txt`: grouped blocklists generated from multiple categories (large ones are automatically split into `...-1.txt`, `...-2.txt`, etc.).
- `ut1<id>.json` (example: `ut1adult.json`): NextDNS-compatible metadata file generated per published list.

## Requirements

- Python 3.10+
- Python dependency: `requests`

Quick installation:

```bash
python -m pip install requests
```

## Local Usage

1. (Optional) Define environment variables to generate correct GitHub raw URLs in `metadata.json`:

```bash
export GITHUB_OWNER="<your-user-or-org>"
export GITHUB_REPO="<your-repo>"
export GITHUB_BRANCH="main"
```

2. Create a `.env` file with grouped lists to publish in `metadata.json` (required):

```dotenv
Adult:adult,agressif,drogue,lingerie,sexual_education,dating,celebrity
Actuality:press,radio,fakenews,sports
Financial:financial,bitcoin,shopping,cryptojacking
```

- Group format: `<ListName>:<category1>,<category2>,...` (one line per list).
- All bundles come from these group definitions. At least one line must be present.
- Per-category files are always generated for every available UT1 category.
- When a bundle exceeds ~70 MB, it is automatically split into multiple `UT1-<group>-N.txt` files. The corresponding `ut1<id>.json` entries follow the "UT1 bundle <group>" naming convention and list every part so you can add them all in NextDNS.

3. Run:

```bash
python update_lists.py
```

4. (Optional) Enable automatic Git commit and push directly from the script:

## Automation

The GitHub Actions workflow (`.github/workflows/update.yml`) runs every day, then automatically commits and pushes updated files.

## License and Credits

- **Source data**: The original blacklist data is provided by Université Toulouse 1 Capitole (UT1) and distributed under the **Licence Ouverte Etalab 2.0**.
- **Repository code**: The code in this repository is released under the **MIT License**.
