#!/usr/bin/env python
"""
Génère PADUTEAM_CHRONOLOGIQUE.md : liste chronologique des vidéos PaduTeam
des 18 derniers mois, regroupées en batches de 2 semaines ISO (~10 vidéos/batch).

Usage:
    python generate_chronological.py            # génère le fichier
    python generate_chronological.py --dry-run  # affiche sans écrire
    python generate_chronological.py --force    # écrase même si progression existante
"""
import sys
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import subprocess

SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT      = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
OUTPUT_PATH     = os.path.join(VAULT_ROOT, "PADUTEAM_CHRONOLOGIQUE.md")
CHANNEL_URL     = "https://www.youtube.com/@PaduTeam/videos"
MONTHS_BACK     = 18
WARN_BATCH_SIZE = 12  # avertissement si batch dense
# Nombre max de vidéos à récupérer : 18 mois × ~6/semaine × ~4 semaines ≈ 450, marge incluse
PLAYLIST_LIMIT  = 600


# =====================================================================
#  DÉCOUVERTE DES VIDÉOS (avec dates réelles via métadonnées complètes)
# =====================================================================

def discover_videos_with_dates(limit=PLAYLIST_LIMIT):
    """Récupère les N dernières vidéos de la chaîne avec leurs dates de publication.

    N'utilise PAS --flat-playlist afin d'obtenir upload_date (NA en mode flat).
    Plus lent (~5-10 min pour 600 vidéos) mais fiable.
    """
    print(f"Récupération des {limit} dernières vidéos avec dates via yt-dlp...")
    print(f"(sans --flat-playlist pour avoir les dates réelles — peut prendre quelques minutes)")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--playlist-end", str(limit),
        "--skip-download",
        "--print", "%(id)s\t%(title)s\t%(upload_date>%Y-%m-%d)s",
        "--no-warnings",
        "--extractor-args", "youtube:lang=fr",
        CHANNEL_URL,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        print("ERREUR : timeout lors de la récupération des vidéos.")
        return []

    if result.returncode != 0 and not result.stdout.strip():
        print(f"ERREUR yt-dlp : {result.stderr[:300]}")
        return []
    if result.returncode != 0:
        # Des vidéos indisponibles génèrent des erreurs mais la sortie reste exploitable
        n_errors = result.stderr.count('ERROR:')
        if n_errors:
            print(f"  ⚠ {n_errors} vidéo(s) indisponible(s) ignorée(s)")

    videos = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 3:
            videos.append({
                'video_id'   : parts[0],
                'title'      : parts[1],
                'upload_date': parts[2] if parts[2] != 'NA' else '',
            })
        elif len(parts) == 2:
            videos.append({
                'video_id'   : parts[0],
                'title'      : parts[1],
                'upload_date': '',
            })

    print(f"  → {len(videos)} vidéos récupérées")
    return videos


# =====================================================================
#  UTILITAIRES DATE
# =====================================================================

def compute_cutoff_date(months=18):
    """Date plancher : now - 18 mois (approx. 548 jours)."""
    return datetime.now() - timedelta(days=int(months * 30.44))


def iso_week_to_monday(year, week):
    """Lundi de la semaine ISO (year, week)."""
    return datetime.fromisocalendar(year, week, 1)


def iso_week_to_sunday(year, week):
    """Dimanche de la semaine ISO (year, week)."""
    return datetime.fromisocalendar(year, week, 7)


def format_date_fr(dt):
    """Formate une date en français court : '21 oct 2024'."""
    MONTHS_FR = {
        1: 'jan', 2: 'fév', 3: 'mar', 4: 'avr',
        5: 'mai', 6: 'jun', 7: 'jul', 8: 'aoû',
        9: 'sep', 10: 'oct', 11: 'nov', 12: 'déc',
    }
    return f"{dt.day} {MONTHS_FR[dt.month]} {dt.year}"


# =====================================================================
#  FILTRAGE ET GROUPEMENT
# =====================================================================

def filter_and_sort_videos(videos, cutoff):
    """Garde les vidéos avec upload_date >= cutoff, trie ascendant (plus ancien en premier)."""
    filtered = []
    skipped = 0
    for v in videos:
        date_str = v.get('upload_date', '')
        if not date_str or not re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            skipped += 1
            continue
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            skipped += 1
            continue
        if date_obj >= cutoff:
            v = dict(v)
            v['date_obj'] = date_obj
            filtered.append(v)

    if skipped:
        print(f"  ⚠ {skipped} vidéos ignorées (date manquante ou invalide)")

    filtered.sort(key=lambda v: v['date_obj'])
    return filtered


def get_iso_week_key(date_obj):
    """Retourne (iso_year, iso_week) pour une date."""
    cal = date_obj.isocalendar()
    return (cal[0], cal[1])


def group_into_week_pairs(videos):
    """Groupe les vidéos en batches de 2 semaines ISO consécutives.

    Retourne une liste de dicts :
    {
        'batch_num'       : int,
        'week_start'      : (year, week),
        'week_end'        : (year, week),
        'date_range_start': datetime,  # lundi de week_start
        'date_range_end'  : datetime,  # dimanche de week_end
        'videos'          : list[dict],
    }
    """
    # Regrouper par semaine ISO
    by_week = defaultdict(list)
    for v in videos:
        key = get_iso_week_key(v['date_obj'])
        by_week[key].append(v)

    # Trier les semaines
    all_weeks = sorted(by_week.keys())

    # Pairer les semaines : (w1, w2), (w3, w4), ...
    batches = []
    batch_num = 1
    i = 0
    while i < len(all_weeks):
        w1 = all_weeks[i]
        w2 = all_weeks[i + 1] if i + 1 < len(all_weeks) else w1

        batch_videos = list(by_week[w1])
        if w2 != w1:
            batch_videos += list(by_week[w2])
        # Trier par date à l'intérieur du batch
        batch_videos.sort(key=lambda v: v['date_obj'])

        if batch_videos:
            batches.append({
                'batch_num'       : batch_num,
                'week_start'      : w1,
                'week_end'        : w2,
                'date_range_start': iso_week_to_monday(*w1),
                'date_range_end'  : iso_week_to_sunday(*w2),
                'videos'          : batch_videos,
            })
            batch_num += 1

        i += 2  # avancer de 2 semaines (même si w2 == w1 pour le dernier)

    return batches


# =====================================================================
#  GÉNÉRATION DU SLUG DE BRANCHE
# =====================================================================

def make_branch_slug(week_start, week_end):
    """Génère le slug de branche pour un batch.

    Exemples :
    - (2024, 43), (2024, 44) → ingest-batch/paduteam-2024-w43-w44
    - (2024, 52), (2025, 1)  → ingest-batch/paduteam-2024-w52-2025-w01
    - (2026, 16), (2026, 16) → ingest-batch/paduteam-2026-w16
    """
    y1, w1 = week_start
    y2, w2 = week_end

    if week_start == week_end:
        return f"ingest-batch/paduteam-{y1}-w{w1:02d}"
    elif y1 == y2:
        return f"ingest-batch/paduteam-{y1}-w{w1:02d}-w{w2:02d}"
    else:
        return f"ingest-batch/paduteam-{y1}-w{w1:02d}-{y2}-w{w2:02d}"


# =====================================================================
#  FORMATAGE DU FICHIER
# =====================================================================

def format_week_range_title(week_start, week_end, date_start, date_end):
    """Titre lisible du batch : 'Semaines 2024-W43 à 2024-W44 (21 oct – 03 nov 2024)'."""
    y1, w1 = week_start
    y2, w2 = week_end
    ds = format_date_fr(date_start)
    de = format_date_fr(date_end)
    if week_start == week_end:
        return f"Semaine {y1}-W{w1:02d} ({ds})"
    elif y1 == y2:
        return f"Semaines {y1}-W{w1:02d} à {y2}-W{w2:02d} ({ds} – {de})"
    else:
        return f"Semaines {y1}-W{w1:02d} à {y2}-W{w2:02d} ({ds} – {de})"


def format_batch_section(batch):
    """Formate une section ## Batch XX complète."""
    num       = batch['batch_num']
    slug      = make_branch_slug(batch['week_start'], batch['week_end'])
    title     = format_week_range_title(
        batch['week_start'], batch['week_end'],
        batch['date_range_start'], batch['date_range_end']
    )
    videos    = batch['videos']
    dense_warning = f"<!-- ⚠ batch dense : {len(videos)} vidéos -->\n" if len(videos) > WARN_BATCH_SIZE else ""

    lines = []
    lines.append(f"## Batch {num:02d} — {title}")
    lines.append("")
    if dense_warning:
        lines.append(dense_warning.strip())
    lines.append(f"Statut : ⏳ en attente")
    lines.append(f"Slug branche : {slug}")
    lines.append("")
    for v in videos:
        lines.append(f"- [ ] {v['title']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    return '\n'.join(lines)


def generate_header(total_videos, total_batches, cutoff, today):
    """En-tête YAML + intro du fichier."""
    cutoff_str = cutoff.strftime('%Y-%m-%d')
    today_str  = today.strftime('%Y-%m-%d')
    return f"""---
generated: {today_str}
period: {cutoff_str} → {today_str}
total_videos: {total_videos}
total_batches: {total_batches}
---

# PADUTEAM — Ingestion chronologique (18 mois)

Fichier de suivi pour l'ingestion chronologique des vidéos PaduTeam
de {format_date_fr(cutoff)} à {format_date_fr(today)}.
Batches de 2 semaines ISO (~10 vidéos/batch), du plus ancien au plus récent.

Généré par `Sources/Transcripts/generate_chronological.py`.
Pour lancer l'ingestion : `python Sources/Transcripts/run_ingest.py`

---

"""


def write_chronologique(batches, output_path, cutoff, today):
    """Écrit le fichier PADUTEAM_CHRONOLOGIQUE.md complet."""
    total_videos = sum(len(b['videos']) for b in batches)
    content = generate_header(total_videos, len(batches), cutoff, today)
    for batch in batches:
        content += format_batch_section(batch)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


# =====================================================================
#  GUARD : ne pas écraser une progression existante
# =====================================================================

def check_existing_file(output_path, force):
    """Retourne True si on peut continuer, False si on doit s'arrêter."""
    if not os.path.exists(output_path):
        return True
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if '✅ fait' in content or '✅' in content:
        if not force:
            print(f"ERREUR : {output_path} existe et contient des batches ✅ déjà traités.")
            print("La progression serait perdue. Options :")
            print("  --force    : écrase et perd la progression")
            print("  --dry-run  : voir les nouvelles vidéos sans écraser")
            return False
        else:
            print(f"⚠ --force : écrasement d'un fichier avec progression existante.")
    return True


# =====================================================================
#  MAIN
# =====================================================================

def main():
    args      = sys.argv[1:]
    dry_run   = '--dry-run' in args
    force     = '--force' in args

    if not dry_run:
        if not check_existing_file(OUTPUT_PATH, force):
            sys.exit(1)

    today  = datetime.now()
    cutoff = compute_cutoff_date(MONTHS_BACK)
    print(f"Période : {format_date_fr(cutoff)} → {format_date_fr(today)}")
    print(f"Récupération des vidéos de la chaîne via yt-dlp...")

    videos   = discover_videos_with_dates()
    filtered = filter_and_sort_videos(videos, cutoff)
    batches  = group_into_week_pairs(filtered)

    total_videos = sum(len(b['videos']) for b in batches)

    print(f"\n{'='*60}")
    print(f"RÉSUMÉ")
    print(f"{'='*60}")
    print(f"Vidéos sur la chaîne      : {len(videos)}")
    print(f"Dans la période (18 mois) : {len(filtered)}")
    print(f"Batches de 2 semaines     : {len(batches)}")

    if dry_run:
        print(f"\n--- DRY RUN ---")
        for b in batches:
            n = len(b['videos'])
            warn = f"  ⚠ batch dense" if n > WARN_BATCH_SIZE else ""
            slug = make_branch_slug(b['week_start'], b['week_end'])
            print(f"  Batch {b['batch_num']:02d} : {b['date_range_start'].strftime('%Y-%m-%d')} → "
                  f"{b['date_range_end'].strftime('%Y-%m-%d')}  ({n} vidéos){warn}")
        print(f"\nTotal : {total_videos} vidéos en {len(batches)} batches")
        print(f"Relancer sans --dry-run pour générer {OUTPUT_PATH}")
        return

    write_chronologique(batches, OUTPUT_PATH, cutoff, today)
    print(f"\n✓ Généré : {OUTPUT_PATH}")
    print(f"  {total_videos} vidéos en {len(batches)} batches")
    print(f"\nProchaines étapes :")
    print(f"  python Sources/Transcripts/run_ingest.py --dry-run")
    print(f"  python Sources/Transcripts/run_ingest.py --batch 1  # test sur 1 batch")
    print(f"  python Sources/Transcripts/run_ingest.py             # lancement complet")


if __name__ == '__main__':
    main()
