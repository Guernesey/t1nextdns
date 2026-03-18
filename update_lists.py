#!/usr/bin/env python3
from __future__ import annotations

import ipaddress
import json
import os
import re
import tarfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable

import requests

CATEGORIES_TO_PROCESS = []

SOURCE_URL = "https://dsi.ut-capitole.fr/blacklists/download/blacklists.tar.gz"
DIST_DIR = Path("dist")
TMP_DIR = Path("tmp")
ARCHIVE_PATH = TMP_DIR / "blacklists.tar.gz"
METADATA_PATH = Path("metadata.json")

GITHUB_OWNER = os.getenv("GITHUB_OWNER", "your-github-username")
GITHUB_REPO = os.getenv("GITHUB_REPO", "your-repo-name")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

DOMAIN_REGEX = re.compile(
    r"^(?=.{1,253}$)(?!-)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\\.)+[a-z]{2,63}$",
    re.IGNORECASE,
)


def ensure_directories() -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)


def download_archive(url: str, output_path: Path) -> None:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    output_path.write_bytes(response.content)


def is_valid_domain(value: str) -> bool:
    candidate = value.strip().lower().rstrip(".")

    if not candidate:
        return False

    if "://" in candidate or "/" in candidate:
        return False

    if candidate.startswith("http"):
        return False

    try:
        ipaddress.ip_address(candidate)
        return False
    except ValueError:
        pass

    return DOMAIN_REGEX.match(candidate) is not None


def normalize_line(line: str) -> str | None:
    stripped = line.strip()

    if not stripped or stripped.startswith("#"):
        return None

    if "#" in stripped:
        stripped = stripped.split("#", 1)[0].strip()

    if not stripped:
        return None

    cleaned = stripped.lower().rstrip(".")
    if not is_valid_domain(cleaned):
        return None

    return cleaned


def extract_domains_from_member(archive: tarfile.TarFile, member: tarfile.TarInfo) -> set[str]:
    extracted = archive.extractfile(member)
    if extracted is None:
        return set()

    valid_domains: set[str] = set()
    for raw_line in extracted:
        line = raw_line.decode("utf-8", errors="ignore")
        normalized = normalize_line(line)
        if normalized:
            valid_domains.add(normalized)

    return valid_domains


def find_domains_member(
    archive: tarfile.TarFile,
    category: str,
) -> tarfile.TarInfo | None:
    for member in archive.getmembers():
        if not member.isfile():
            continue

        parts = PurePosixPath(member.name).parts
        if len(parts) >= 2 and parts[-1] == "domains" and parts[-2] == category:
            return member

    return None


def list_available_categories(archive: tarfile.TarFile) -> list[str]:
    categories = set()
    for member in archive.getmembers():
        if not member.isfile():
            continue

        parts = PurePosixPath(member.name).parts
        if len(parts) >= 2 and parts[-1] == "domains":
            categories.add(parts[-2])

    return sorted(categories)


def build_header(category: str, source_url: str, generated_at: str) -> list[str]:
    return [
        f"# Name: Toulouse UT1 - {category}",
        f"# Source: {source_url}",
        f"# Generated: {generated_at}",
        "",
    ]


def write_category_file(category: str, domains: Iterable[str], generated_at: str) -> Path:
    output_path = DIST_DIR / f"toulouse-{category}.txt"
    sorted_domains = sorted(set(domains))

    lines = build_header(category, SOURCE_URL, generated_at)
    lines.extend(sorted_domains)

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def build_raw_url(category: str) -> str:
    return (
        f"https://raw.githubusercontent.com/{GITHUB_OWNER}/"
        f"{GITHUB_REPO}/{GITHUB_BRANCH}/dist/toulouse-{category}.txt"
    )


def category_description(category: str) -> str:
    readable = category.replace("_", " ").replace("-", " ").strip()
    return f"UT1 category: {readable.title()}"


def generate_metadata(metadata: dict[str, dict[str, str | int]], generated_at: str) -> None:
    payload = {
        "source": SOURCE_URL,
        "generated_at": generated_at,
        "categories": metadata,
    }
    METADATA_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def process_categories(categories: list[str]) -> dict[str, dict[str, str | int]]:
    if not categories:
        print("CATEGORIES_TO_PROCESS est vide. Aucune catégorie traitée.")
        return {}

    metadata: dict[str, dict[str, str | int]] = {}

    with tarfile.open(ARCHIVE_PATH, mode="r:gz") as archive:
        available = set(list_available_categories(archive))
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        for category in categories:
            if category not in available:
                print(f"Catégorie introuvable dans l'archive: {category}")
                continue

            member = find_domains_member(archive, category)
            if member is None:
                print(f"Fichier domains introuvable pour: {category}")
                continue

            domains = extract_domains_from_member(archive, member)
            write_category_file(category, domains, generated_at)

            metadata[category] = {
                "url": build_raw_url(category),
                "description": category_description(category),
                "entries_count": len(domains),
            }

    return metadata


def main() -> None:
    ensure_directories()
    download_archive(SOURCE_URL, ARCHIVE_PATH)

    categories = [category.strip() for category in CATEGORIES_TO_PROCESS if category.strip()]
    metadata = process_categories(categories)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    generate_metadata(metadata, generated_at)
    print(f"Terminé. {len(metadata)} catégorie(s) générée(s).")


if __name__ == "__main__":
    main()
