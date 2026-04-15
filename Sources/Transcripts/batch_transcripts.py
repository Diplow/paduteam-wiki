#!/usr/bin/env python3
"""
Batch : gestion complète des transcripts et de l'inventaire PaduTeam.

Modes d'utilisation :
    python batch_transcripts.py                # Extraction des transcripts manquants
    python batch_transcripts.py --dry-run      # Montre ce qui serait fait
    python batch_transcripts.py --discover     # Découvre les nouvelles vidéos, met à jour l'inventaire
    python batch_transcripts.py --discover --dry-run  # Montre les nouvelles vidéos sans modifier
    python batch_transcripts.py --last 5       # Extrait les transcripts des 5 dernières vidéos sans transcript
    python batch_transcripts.py --recent 3     # Récupère les 3 dernières vidéos, extrait si pas de transcript
    python batch_transcripts.py --recent 3 --dry-run  # Montre ce qui serait fait
    python batch_transcripts.py --fix          # Corrige l'inventaire (dates, URLs, transcripts existants)
    python batch_transcripts.py --full         # Fait tout : discover + fix + extraction
    python batch_transcripts.py --full --last 3  # Discover + fix + extraction des 3 dernières
    python batch_transcripts.py --enrich-fiches              # Ajoute youtube_id + corrige dates dans Videos/
    python batch_transcripts.py --enrich-fiches --dry-run    # Prévisualise sans écrire
    python batch_transcripts.py --fix-fiche-dates            # Corrige les dates manquantes via API YouTube individuelle
    python batch_transcripts.py --fix-fiche-dates --dry-run  # Prévisualise sans écrire
    python batch_transcripts.py --enrich-transcripts         # Ajoute youtube_id aux transcripts Sources/Transcripts/
    python batch_transcripts.py --enrich-transcripts --dry-run # Prévisualise sans écrire

Fonctionnalités :
- Découverte de nouvelles vidéos via yt-dlp --flat-playlist
- Ajout automatique à l'inventaire avec date de publication absolue
- Conversion des dates relatives ("il y a X jours") en dates absolues (YYYY-MM-DD)
- Résolution des URLs cassées (@PaduTeam/videos → watch?v=...)
- Liaison automatique des transcripts .md existants non référencés
- Extraction des sous-titres via yt-dlp (mode original)

Sécurités :
- Pause de 8s entre chaque vidéo (anti-ban YouTube)
- Stop après 3 échecs consécutifs
- Ne ré-extrait pas les transcripts déjà existants
"""
import subprocess
import os
import re
import sys
import json
import time
import shutil

# Force UTF-8 output on Windows to handle French characters and symbols
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime, timedelta
from difflib import SequenceMatcher

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INVENTAIRE_PATH = os.path.join(SCRIPT_DIR, "..", "Inventaire PaduTeam.md")
TRANSCRIPTS_DIR = SCRIPT_DIR
TEMP_DIR = os.path.join(SCRIPT_DIR, "_temp_ytdlp")
CHANNEL_URL = "https://www.youtube.com/@PaduTeam/videos"
VIDEOS_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "Videos"))
PAUSE_SECONDS = 8         # pause entre chaque vidéo
MAX_CONSECUTIVE_FAILS = 3  # stop après N échecs consécutifs
INTERVAL_S = 30            # regrouper le texte par blocs de ~30s


# =====================================================================
#  FONCTIONS DE PARSING DES SOUS-TITRES
# =====================================================================

def parse_json3(filepath):
    """Parse un fichier json3 YouTube en segments (timestamp_ms, texte)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    segments = []
    for event in data.get('events', []):
        if 'segs' not in event:
            continue
        start_ms = event.get('tStartMs', 0)
        text = ''.join(seg.get('utf8', '') for seg in event['segs']).strip()
        text = text.replace('\n', ' ')
        if text:
            segments.append((start_ms, text))
    return segments


def parse_vtt(filepath):
    """Parse un fichier VTT en segments (timestamp_ms, texte)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    segments = []
    blocks = re.split(r'\n\n+', content)
    for block in blocks:
        lines = block.strip().split('\n')
        for i, line in enumerate(lines):
            match = re.match(r'(\d+):(\d+):(\d+)\.(\d+)\s*-->', line)
            if match:
                h, m, s, ms = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
                start_ms = (h * 3600 + m * 60 + s) * 1000 + ms
                text = ' '.join(lines[i+1:]).strip()
                text = re.sub(r'<[^>]+>', '', text)
                if text:
                    segments.append((start_ms, text))
    return segments


def ms_to_timestamp(ms):
    """Convertit millisecondes en format m:ss ou h:mm:ss."""
    total_s = ms // 1000
    h = total_s // 3600
    m = (total_s % 3600) // 60
    s = total_s % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    else:
        return f"{m}:{s:02d}"


def build_markdown(segments):
    """Construit le contenu .md en regroupant le texte par blocs de ~INTERVAL_S secondes."""
    if not segments:
        return ''
    lines = []
    current_block_start = segments[0][0]
    current_texts = []
    for start_ms, text in segments:
        if start_ms - current_block_start >= INTERVAL_S * 1000 and current_texts:
            ts = ms_to_timestamp(current_block_start)
            lines.append(f"\n{ts}\n")
            lines.append(' '.join(current_texts) + '\n')
            current_block_start = start_ms
            current_texts = []
        current_texts.append(text)
    if current_texts:
        ts = ms_to_timestamp(current_block_start)
        lines.append(f"\n{ts}\n")
        lines.append(' '.join(current_texts) + '\n')
    return '\n'.join(lines)


# =====================================================================
#  UTILITAIRES COMMUNS
# =====================================================================

def make_filename(title):
    """Crée un nom de fichier propre à partir du titre."""
    slug = title.replace('\\', '').replace('/', '').replace(':', '').replace('*', '')
    slug = slug.replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
    slug = slug.strip()
    if len(slug) > 120:
        slug = slug[:120].strip()
    return slug + '.md'


def get_existing_transcripts():
    """Liste les fichiers .md existants dans le dossier Transcripts (sans extension)."""
    existing = set()
    for f in os.listdir(TRANSCRIPTS_DIR):
        if f.endswith('.md') and not f.startswith('_'):
            existing.add(f[:-3])
    return existing


def fuzzy_match(s1, s2, threshold=0.70):
    """Vérifie si deux chaînes sont suffisamment similaires."""
    def norm(s):
        s = s.lower()
        s = re.sub(r'[^\w\s]', '', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s
    return SequenceMatcher(None, norm(s1), norm(s2)).ratio() >= threshold


def relative_date_to_absolute(date_str, ref_date=None):
    """Convertit 'il y a X jours/semaines/mois' en YYYY-MM-DD."""
    if ref_date is None:
        ref_date = datetime.now()
    date_str_lower = date_str.strip().lower()

    # Déjà au format absolu
    if re.match(r'\d{4}-\d{2}-\d{2}', date_str_lower):
        return date_str.strip()

    # Cas spéciaux
    m = re.match(r'début\s+(\d{4})', date_str_lower)
    if m:
        return f'{m.group(1)}-01-15'

    # "il y a X minutes/heures" → aujourd'hui
    if re.search(r'il y a \d+\s*(minute|heure)', date_str_lower):
        return ref_date.strftime('%Y-%m-%d')

    # "il y a X jours"
    m = re.search(r'il y a (\d+)\s*jour', date_str_lower)
    if m:
        return (ref_date - timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d')

    # "il y a X semaines"
    m = re.search(r'il y a (\d+)\s*semaine', date_str_lower)
    if m:
        return (ref_date - timedelta(weeks=int(m.group(1)))).strftime('%Y-%m-%d')

    # "il y a X mois"
    m = re.search(r'il y a (\d+)\s*mois', date_str_lower)
    if m:
        months = int(m.group(1))
        # Approximation : remonter mois par mois
        d = ref_date
        for _ in range(months):
            d = d.replace(day=1) - timedelta(days=1)
        return d.strftime('%Y-%m-%d')

    # "il y a X ans"
    m = re.search(r'il y a (\d+)\s*an', date_str_lower)
    if m:
        years = int(m.group(1))
        try:
            return ref_date.replace(year=ref_date.year - years).strftime('%Y-%m-%d')
        except ValueError:
            return (ref_date - timedelta(days=years * 365)).strftime('%Y-%m-%d')

    return date_str.strip()  # Inchangé si non reconnu


# =====================================================================
#  PARSING DE L'INVENTAIRE
# =====================================================================

INVENTORY_LINE_RE = re.compile(
    r'^\|\s*(.+?)\s*\|\s*\[YouTube\]\((.+?)\)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$'
)


def parse_inventaire(path):
    """Lit l'inventaire et retourne (header_lines, video_entries).

    Chaque video_entry est un dict avec :
        title, url, video_id, date, transcript, fiche, raw_line
    """
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    header_lines = []
    entries = []
    in_table = False

    for line in lines:
        match = INVENTORY_LINE_RE.match(line)
        if not match:
            if not in_table:
                header_lines.append(line)
            elif line.startswith('|') and '---' in line:
                header_lines.append(line)
            else:
                header_lines.append(line)
            continue

        title = match.group(1).strip()
        if title == 'Titre':
            header_lines.append(line)
            in_table = True
            continue

        url = match.group(2).strip()
        date_col = match.group(3).strip()
        transcript_col = match.group(4).strip()
        fiche_col = match.group(5).strip()

        vid_match = re.search(r'watch\?v=([a-zA-Z0-9_-]+)', url)
        video_id = vid_match.group(1) if vid_match else None

        entries.append({
            'title': title,
            'url': url,
            'video_id': video_id,
            'date': date_col,
            'transcript': transcript_col,
            'fiche': fiche_col,
        })

    return header_lines, entries


def write_inventaire(path, header_lines, entries):
    """Écrit l'inventaire complet."""
    # Supprimer les lignes vides en fin de header pour éviter de casser la table Markdown
    lines = list(header_lines)
    while lines and lines[-1].strip() == '':
        lines.pop()

    for e in entries:
        url = e['url']
        transcript = e.get('transcript', '')
        fiche = e.get('fiche', '')
        line = (
            f"| {e['title']:<100} "
            f"| [YouTube]({url}) "
            f"| {e['date']:<17} "
            f"| {transcript:<102} "
            f"| {fiche:<54} |"
        )
        lines.append(line)

    # Mettre à jour le compteur et la date
    total = len(entries)
    for i, l in enumerate(lines):
        if 'vidéos extraites' in l:
            lines[i] = f'> {total} vidéos extraites depuis la page YouTube [@PaduTeam]({CHANNEL_URL})'
        if 'Dernière mise à jour' in l:
            lines[i] = f'> Dernière mise à jour : {datetime.now().strftime("%Y-%m-%d")}'

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return total


# =====================================================================
#  DÉCOUVERTE DE NOUVELLES VIDÉOS (yt-dlp --flat-playlist)
# =====================================================================

def discover_channel_videos():
    """Utilise yt-dlp pour lister toutes les vidéos de la chaîne.

    Retourne une liste de dicts {video_id, title, upload_date}.
    """
    print("Récupération de la liste des vidéos de la chaîne via yt-dlp...")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist",
        "--print", "%(id)s\t%(title)s\t%(upload_date>%Y-%m-%d)s",
        "--no-warnings",
        "--extractor-args", "youtube:lang=fr",
        CHANNEL_URL
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        print("ERREUR: Timeout lors de la récupération de la liste des vidéos.")
        return []

    if result.returncode != 0:
        print(f"ERREUR yt-dlp: {result.stderr[:300]}")
        return []

    videos = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 3:
            videos.append({
                'video_id': parts[0],
                'title': parts[1],
                'upload_date': parts[2] if parts[2] != 'NA' else '',
            })
        elif len(parts) == 2:
            videos.append({
                'video_id': parts[0],
                'title': parts[1],
                'upload_date': '',
            })

    print(f"  → {len(videos)} vidéos trouvées sur la chaîne")
    return videos


def get_video_upload_date(video_id):
    """Récupère la date de publication exacte d'une vidéo via yt-dlp."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--print", "%(upload_date>%Y-%m-%d)s",
        "--skip-download",
        "--no-warnings",
        "--extractor-args", "youtube:lang=fr",
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            date = result.stdout.strip()
            if re.match(r'\d{4}-\d{2}-\d{2}', date):
                return date
    except (subprocess.TimeoutExpired, Exception):
        pass
    return None


# =====================================================================
#  RÉSOLUTION DES URLS ET DATES
# =====================================================================

def fix_broken_urls(entries, channel_videos=None):
    """Corrige les URLs @PaduTeam/videos en utilisant les données de la chaîne."""
    if not channel_videos:
        channel_videos = discover_channel_videos()
    if not channel_videos:
        print("Impossible de corriger les URLs sans données de la chaîne.")
        return 0

    # Index par titre normalisé
    def norm_title(t):
        t = t.lower()
        t = re.sub(r'[^\w\s]', '', t)
        t = re.sub(r'\s+', ' ', t).strip()
        return t

    channel_map = {}
    for cv in channel_videos:
        channel_map[norm_title(cv['title'])] = cv

    fixed = 0
    for e in entries:
        if '@PaduTeam/videos' not in e['url']:
            continue
        # Chercher par titre
        nt = norm_title(e['title'])
        if nt in channel_map:
            cv = channel_map[nt]
            e['url'] = f"https://www.youtube.com/watch?v={cv['video_id']}"
            e['video_id'] = cv['video_id']
            if cv.get('upload_date') and not re.match(r'\d{4}-\d{2}-\d{2}', e['date']):
                e['date'] = cv['upload_date']
            fixed += 1
        else:
            # Fuzzy match
            for ckey, cv in channel_map.items():
                if fuzzy_match(e['title'], cv['title'], 0.7):
                    e['url'] = f"https://www.youtube.com/watch?v={cv['video_id']}"
                    e['video_id'] = cv['video_id']
                    if cv.get('upload_date') and not re.match(r'\d{4}-\d{2}-\d{2}', e['date']):
                        e['date'] = cv['upload_date']
                    fixed += 1
                    break

    return fixed


def fix_relative_dates(entries):
    """Convertit toutes les dates relatives en dates absolues."""
    now = datetime.now()
    fixed = 0
    for e in entries:
        new_date = relative_date_to_absolute(e['date'], now)
        if new_date != e['date']:
            e['date'] = new_date
            fixed += 1
    return fixed


def link_existing_transcripts(entries):
    """Lie les fichiers transcript .md existants aux entrées de l'inventaire."""
    existing = get_existing_transcripts()
    linked = 0

    for e in entries:
        if e['transcript'] and '[[' in e['transcript']:
            continue  # Déjà lié

        # 1. Match exact par nom de fichier attendu
        expected = make_filename(e['title'])[:-3]  # sans .md
        if expected in existing:
            e['transcript'] = f'[[{expected}]]'
            linked += 1
            continue

        # 2. Fuzzy match sur les noms de fichier
        best_score = 0
        best_name = None
        for t in existing:
            score = SequenceMatcher(None, expected.lower(), t.lower()).ratio()
            if score > best_score:
                best_score = score
                best_name = t
        if best_score >= 0.70 and best_name:
            e['transcript'] = f'[[{best_name}]]'
            linked += 1

    return linked


# =====================================================================
#  EXTRACTION D'UN TRANSCRIPT (mode original)
# =====================================================================

def extract_one(video_id):
    """Extrait les sous-titres d'une vidéo. Retourne le contenu markdown ou None."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    url = f"https://www.youtube.com/watch?v={video_id}"

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--write-sub",
        "--write-auto-sub",
        "--sub-lang", "fr",
        "--sub-format", "json3",
        "--skip-download",
        "--no-warnings",
        "--extractor-args", "youtube:lang=fr",
        "-o", os.path.join(TEMP_DIR, "%(id)s.%(ext)s"),
        url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        return None

    # Chercher le fichier
    sub_file = None
    for f in os.listdir(TEMP_DIR):
        if video_id in f and f.endswith('.json3'):
            sub_file = os.path.join(TEMP_DIR, f)
            break

    if not sub_file:
        # Fallback vtt
        cmd[6] = "vtt"
        subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        for f in os.listdir(TEMP_DIR):
            if video_id in f and (f.endswith('.vtt') or f.endswith('.srt')):
                sub_file = os.path.join(TEMP_DIR, f)
                break

    if not sub_file:
        return None

    if sub_file.endswith('.json3'):
        segments = parse_json3(sub_file)
    else:
        segments = parse_vtt(sub_file)

    if not segments:
        return None

    return build_markdown(segments)


# =====================================================================
#  COMMANDES PRINCIPALES
# =====================================================================

def cmd_discover(dry_run=False):
    """Découvre les nouvelles vidéos et les ajoute à l'inventaire."""
    inv_path = os.path.normpath(INVENTAIRE_PATH)
    header_lines, entries = parse_inventaire(inv_path)

    # Vidéos déjà dans l'inventaire (par video_id et par titre normalisé)
    known_ids = {e['video_id'] for e in entries if e['video_id']}
    known_titles = set()
    for e in entries:
        t = e['title'].lower()
        t = re.sub(r'[^\w\s]', '', t)
        t = re.sub(r'\s+', ' ', t).strip()
        known_titles.add(t)

    # Découvrir la chaîne
    channel_videos = discover_channel_videos()
    if not channel_videos:
        print("Impossible de récupérer les vidéos de la chaîne.")
        return

    # Trouver les nouvelles
    new_videos = []
    for cv in channel_videos:
        if cv['video_id'] in known_ids:
            continue
        nt = cv['title'].lower()
        nt = re.sub(r'[^\w\s]', '', nt)
        nt = re.sub(r'\s+', ' ', nt).strip()
        if nt in known_titles:
            continue
        # Fuzzy check
        is_known = False
        for e in entries:
            if fuzzy_match(e['title'], cv['title'], 0.75):
                is_known = True
                break
        if not is_known:
            new_videos.append(cv)

    print(f"\n{'='*60}")
    print(f"DÉCOUVERTE DE NOUVELLES VIDÉOS")
    print(f"{'='*60}")
    print(f"Vidéos sur la chaîne   : {len(channel_videos)}")
    print(f"Déjà dans l'inventaire : {len(entries)}")
    print(f"Nouvelles à ajouter    : {len(new_videos)}")

    if not new_videos:
        print("Rien de nouveau à ajouter !")
        return

    if dry_run:
        print(f"\n--- DRY RUN ---")
        for i, cv in enumerate(new_videos):
            print(f"  {i+1}. {cv['title'][:70]}  ({cv['video_id']})  [{cv.get('upload_date', '?')}]")
        return

    # Ajouter les nouvelles vidéos en tête de l'inventaire
    existing_transcripts = get_existing_transcripts()
    for cv in new_videos:
        url = f"https://www.youtube.com/watch?v={cv['video_id']}"
        date = cv.get('upload_date', '')
        if not date:
            # Essayer de récupérer la date
            date = get_video_upload_date(cv['video_id']) or ''

        # Chercher un transcript existant
        transcript = ''
        expected = make_filename(cv['title'])[:-3]
        if expected in existing_transcripts:
            transcript = f'[[{expected}]]'
        else:
            for t in existing_transcripts:
                if fuzzy_match(cv['title'], t, 0.7):
                    transcript = f'[[{t}]]'
                    break

        entry = {
            'title': cv['title'],
            'url': url,
            'video_id': cv['video_id'],
            'date': date,
            'transcript': transcript,
            'fiche': '',
        }
        # Insérer au début (vidéos les plus récentes en premier)
        entries.insert(0, entry)
        print(f"  + {cv['title'][:60]}  ({cv['video_id']})")

    # Trier par date décroissante (les plus récentes en premier)
    def sort_key(e):
        d = e.get('date', '')
        if re.match(r'\d{4}-\d{2}-\d{2}', d):
            return d
        return '0000-00-00'
    entries.sort(key=sort_key, reverse=True)

    # Profiter du passage pour corriger les URLs et dates
    fixed_urls = fix_broken_urls(entries, channel_videos)
    fixed_dates = fix_relative_dates(entries)
    linked = link_existing_transcripts(entries)

    total = write_inventaire(inv_path, header_lines, entries)

    print(f"\n{'='*60}")
    print(f"RÉSUMÉ DISCOVER")
    print(f"  Nouvelles vidéos     : {len(new_videos)}")
    print(f"  URLs corrigées       : {fixed_urls}")
    print(f"  Dates converties     : {fixed_dates}")
    print(f"  Transcripts liés     : {linked}")
    print(f"  Total dans inventaire: {total}")
    print(f"{'='*60}")


def cmd_fix():
    """Corrige l'inventaire : dates, URLs, transcripts existants."""
    inv_path = os.path.normpath(INVENTAIRE_PATH)
    header_lines, entries = parse_inventaire(inv_path)

    print(f"\n{'='*60}")
    print(f"CORRECTION DE L'INVENTAIRE")
    print(f"{'='*60}")

    # Corriger les dates relatives
    fixed_dates = fix_relative_dates(entries)
    print(f"  Dates converties     : {fixed_dates}")

    # Corriger les URLs cassées (nécessite yt-dlp)
    broken = sum(1 for e in entries if '@PaduTeam/videos' in e['url'])
    if broken > 0:
        print(f"  URLs cassées trouvées: {broken}")
        fixed_urls = fix_broken_urls(entries)
        print(f"  URLs corrigées       : {fixed_urls}")
    else:
        print(f"  URLs : toutes OK")

    # Lier les transcripts existants
    linked = link_existing_transcripts(entries)
    print(f"  Transcripts liés     : {linked}")

    # Écrire
    total = write_inventaire(inv_path, header_lines, entries)
    print(f"  Total dans inventaire: {total}")
    print(f"{'='*60}")


def cmd_extract(dry_run=False, last_n=None):
    """Mode original : extrait les transcripts manquants."""
    inv_path = os.path.normpath(INVENTAIRE_PATH)
    if not os.path.exists(inv_path):
        print(f"ERREUR: Inventaire introuvable à {inv_path}")
        sys.exit(1)

    header_lines, entries = parse_inventaire(inv_path)
    existing = get_existing_transcripts()

    # Filtrer : vidéos avec un vrai video_id ET sans transcript
    to_process = []
    for e in entries:
        if not e['video_id']:
            continue
        if e['transcript'] and '[[' in e['transcript']:
            continue
        filename = make_filename(e['title'])
        if filename[:-3] in existing:
            continue
        to_process.append(e)

    total_missing = len(to_process)

    if last_n is not None:
        to_process = to_process[:last_n]

    print(f"{'='*60}")
    print(f"BATCH TRANSCRIPTS PADUTEAM")
    print(f"{'='*60}")
    print(f"Vidéos dans l'inventaire : {len(entries)}")
    print(f"Avec video ID valide     : {sum(1 for e in entries if e['video_id'])}")
    print(f"Transcripts déjà faits   : {sum(1 for e in entries if e['transcript'] and '[[' in e['transcript'])} (inventaire) + {len(existing)} (fichiers)")
    print(f"Sans transcript          : {total_missing}")
    print(f"À extraire               : {len(to_process)}{f' (limité aux {last_n} premières)' if last_n else ''}")
    print(f"Pause entre chaque       : {PAUSE_SECONDS}s")
    print(f"Stop après               : {MAX_CONSECUTIVE_FAILS} échecs consécutifs")

    if dry_run:
        print(f"\n--- DRY RUN : voici les vidéos qui seraient traitées ---")
        for i, e in enumerate(to_process):
            print(f"  {i+1}. {e['title'][:70]}  ({e['video_id']})")
        print(f"\nRelance sans --dry-run pour démarrer l'extraction.")
        return

    if not to_process:
        print("\nRien à extraire, tous les transcripts sont déjà faits !")
        return

    print(f"\nDémarrage dans 3 secondes...")
    time.sleep(3)

    success_count = 0
    fail_count = 0
    consecutive_fails = 0

    for i, e in enumerate(to_process):
        print(f"\n[{i+1}/{len(to_process)}] {e['title'][:70]}")
        print(f"           ID: {e['video_id']}")

        try:
            md_content = extract_one(e['video_id'])
        except Exception as ex:
            print(f"           ERREUR: {ex}")
            md_content = None

        if md_content:
            filename = make_filename(e['title'])
            filepath = os.path.join(TRANSCRIPTS_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)

            # Mettre à jour l'entrée
            e['transcript'] = f'[[{filename[:-3]}]]'

            print(f"           OK → {filename} ({len(md_content)} chars)")

            success_count += 1
            consecutive_fails = 0
        else:
            print(f"           ÉCHEC (pas de sous-titres FR disponibles ?)")
            fail_count += 1
            consecutive_fails += 1

            if consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                print(f"\n{'!'*60}")
                print(f"STOP : {MAX_CONSECUTIVE_FAILS} échecs consécutifs.")
                print(f"Possible rate-limit YouTube ou problème réseau.")
                print(f"{'!'*60}")
                break

        # Nettoyage temp
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR, ignore_errors=True)

        # Pause anti-ban
        if i < len(to_process) - 1:
            print(f"           Pause {PAUSE_SECONDS}s...")
            time.sleep(PAUSE_SECONDS)

    # Sauvegarder l'inventaire avec les transcripts mis à jour
    write_inventaire(inv_path, header_lines, entries)

    print(f"\n{'='*60}")
    print(f"TERMINÉ")
    print(f"  Succès   : {success_count}")
    print(f"  Échecs   : {fail_count}")
    print(f"  Restants : {len(to_process) - success_count - fail_count}")
    print(f"{'='*60}")


# =====================================================================
#  MODE RECENT : rapide, ne récupère que les N dernières vidéos
# =====================================================================

def cmd_recent(n, dry_run=False):
    """Récupère les N dernières vidéos de la chaîne et extrait les transcripts manquants."""
    print(f"Récupération des {n} dernières vidéos de la chaîne...")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist",
        "--playlist-end", str(n),
        "--print", "%(id)s\t%(title)s\t%(upload_date>%Y-%m-%d)s",
        "--no-warnings",
        "--extractor-args", "youtube:lang=fr",
        CHANNEL_URL
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        print("ERREUR: Timeout lors de la récupération.")
        return

    if result.returncode != 0:
        print(f"ERREUR yt-dlp: {result.stderr[:300]}")
        return

    videos = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            videos.append({
                'video_id': parts[0],
                'title': parts[1],
                'upload_date': parts[2] if len(parts) >= 3 and parts[2] != 'NA' else '',
            })

    print(f"  → {len(videos)} vidéos récupérées")

    # Charger l'inventaire et les transcripts existants
    inv_path = os.path.normpath(INVENTAIRE_PATH)
    header_lines, entries = parse_inventaire(inv_path)
    existing = get_existing_transcripts()
    known_ids = {e['video_id'] for e in entries if e['video_id']}

    # Déterminer ce qui manque
    to_process = []
    to_add_to_inventory = []
    for v in videos:
        has_transcript = False
        # Vérifier dans l'inventaire
        for e in entries:
            if e['video_id'] == v['video_id'] and e['transcript'] and '[[' in e['transcript']:
                has_transcript = True
                break
        # Vérifier les fichiers existants
        if not has_transcript:
            expected = make_filename(v['title'])[:-3]
            if expected in existing:
                has_transcript = True
        if not has_transcript:
            to_process.append(v)
        if v['video_id'] not in known_ids:
            to_add_to_inventory.append(v)

    print(f"\n{'='*60}")
    print(f"RECENT — {n} dernières vidéos")
    print(f"{'='*60}")
    print(f"Récupérées               : {len(videos)}")
    print(f"Nouvelles (hors inventaire): {len(to_add_to_inventory)}")
    print(f"Sans transcript          : {len(to_process)}")

    if not to_process:
        print("\nToutes ces vidéos ont déjà un transcript !")
        # Quand même ajouter les nouvelles à l'inventaire
        if to_add_to_inventory and not dry_run:
            for v in to_add_to_inventory:
                expected = make_filename(v['title'])[:-3]
                transcript = f'[[{expected}]]' if expected in existing else ''
                entries.insert(0, {
                    'title': v['title'],
                    'url': f"https://www.youtube.com/watch?v={v['video_id']}",
                    'video_id': v['video_id'],
                    'date': v.get('upload_date', ''),
                    'transcript': transcript,
                    'fiche': '',
                })
            write_inventaire(inv_path, header_lines, entries)
            print(f"  {len(to_add_to_inventory)} vidéos ajoutées à l'inventaire")
        return

    if dry_run:
        print(f"\n--- DRY RUN ---")
        for i, v in enumerate(to_process):
            print(f"  {i+1}. {v['title'][:70]}  ({v['video_id']})  [{v.get('upload_date', '?')}]")
        return

    # Extraction
    print(f"\nExtraction des transcripts...")
    success_count = 0
    fail_count = 0

    for i, v in enumerate(to_process):
        print(f"\n[{i+1}/{len(to_process)}] {v['title'][:70]}")
        print(f"           ID: {v['video_id']}")

        try:
            md_content = extract_one(v['video_id'])
        except Exception as ex:
            print(f"           ERREUR: {ex}")
            md_content = None

        if md_content:
            filename = make_filename(v['title'])
            filepath = os.path.join(TRANSCRIPTS_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"           OK → {filename} ({len(md_content)} chars)")
            success_count += 1
        else:
            print(f"           ÉCHEC (pas de sous-titres FR disponibles ?)")
            fail_count += 1

        # Nettoyage temp
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR, ignore_errors=True)

        # Pause anti-ban
        if i < len(to_process) - 1:
            print(f"           Pause {PAUSE_SECONDS}s...")
            time.sleep(PAUSE_SECONDS)

    # Mettre à jour l'inventaire : ajouter les nouvelles vidéos et lier les transcripts
    existing = get_existing_transcripts()  # Recharger après extraction
    for v in to_add_to_inventory:
        expected = make_filename(v['title'])[:-3]
        transcript = f'[[{expected}]]' if expected in existing else ''
        entries.insert(0, {
            'title': v['title'],
            'url': f"https://www.youtube.com/watch?v={v['video_id']}",
            'video_id': v['video_id'],
            'date': v.get('upload_date', ''),
            'transcript': transcript,
            'fiche': '',
        })

    # Lier les transcripts fraîchement extraits pour les entrées existantes aussi
    link_existing_transcripts(entries)
    write_inventaire(inv_path, header_lines, entries)

    print(f"\n{'='*60}")
    print(f"TERMINÉ")
    print(f"  Succès   : {success_count}")
    print(f"  Échecs   : {fail_count}")
    print(f"{'='*60}")


# =====================================================================
#  ENRICHISSEMENT DES FICHES VIDEOS/ (youtube_id + dates)
# =====================================================================

def extract_youtube_id_from_frontmatter(fm):
    """Extrait le youtube_id depuis le frontmatter, y compris depuis les lignes malformées.

    Gère :
      - youtube_id: XXXXX         (normal)
      - date: youtube_id: XXXXX   (bug ingestion précédente)
    """
    # Cas normal
    m = re.search(r'^youtube_id\s*:\s*["\']?([a-zA-Z0-9_-]{8,})["\']?', fm, re.MULTILINE)
    if m:
        return m.group(1)
    # Cas malformé : "date: youtube_id: XXXXX"
    m = re.search(r'^date\s*:\s*youtube_id\s*:\s*([a-zA-Z0-9_-]{8,})', fm, re.MULTILINE)
    if m:
        return m.group(1)
    return None


def cmd_fix_fiche_dates(dry_run=False):
    """Corrige les dates incomplètes/malformées dans les fiches Videos/ via API individuelle."""
    print(f"\n{'='*60}")
    print(f"CORRECTION DES DATES DANS VIDEOS/")
    print(f"{'='*60}")

    if not os.path.isdir(VIDEOS_DIR):
        print(f"ERREUR: dossier Videos/ introuvable : {VIDEOS_DIR}")
        return

    fiche_files = [
        os.path.join(VIDEOS_DIR, f)
        for f in sorted(os.listdir(VIDEOS_DIR))
        if f.endswith('.md') and not f.startswith('_') and f != 'CLAUDE.md'
    ]

    # Identifier les fiches à corriger
    to_fix = []
    for fiche_path in fiche_files:
        try:
            with open(fiche_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue
        if not content.startswith('---'):
            continue
        end = content.find('\n---', 3)
        if end == -1:
            continue
        fm = content[3:end]

        youtube_id = extract_youtube_id_from_frontmatter(fm)
        if not youtube_id:
            continue  # Pas de youtube_id → ne peut pas récupérer la date

        date_m = re.search(r'^date\s*:\s*(\S+)', fm, re.MULTILINE)
        date_val = date_m.group(1) if date_m else None

        # Malformé ou incomplet ?
        if date_val and date_val.startswith('youtube_id'):
            need_fix = True  # "date: youtube_id: XXXXX"
        elif not date_val:
            need_fix = True
        elif re.match(r'\d{4}-\d{2}-\d{2}$', date_val):
            need_fix = False  # Déjà complet
        else:
            need_fix = True   # Partiel : YYYY-MM, YYYY, YYYY-MM-XX, etc.

        if need_fix:
            to_fix.append((fiche_path, youtube_id, date_val))

    print(f"  Fiches à corriger : {len(to_fix)}")
    if dry_run:
        for path, yt_id, old_date in to_fix:
            print(f"  [dry-run] {os.path.basename(path)[:70]} | date={old_date} | yt={yt_id}")
        return

    updated = 0
    failed = 0

    for i, (fiche_path, youtube_id, old_date) in enumerate(to_fix):
        name = os.path.basename(fiche_path)
        print(f"\n[{i+1}/{len(to_fix)}] {name[:70]}")
        print(f"    date actuelle : {old_date}  |  youtube_id : {youtube_id}")

        new_date = get_video_upload_date(youtube_id)
        if not new_date:
            print(f"    ÉCHEC : impossible de récupérer la date")
            failed += 1
        else:
            print(f"    → {new_date}")
            _fix_fiche_date_and_id(fiche_path, youtube_id, new_date)
            updated += 1

        if i < len(to_fix) - 1:
            time.sleep(5)

    print(f"\n{'='*60}")
    print(f"RÉSUMÉ")
    print(f"  Dates corrigées : {updated}")
    print(f"  Échecs          : {failed}")
    print(f"{'='*60}")


def _fix_fiche_date_and_id(fiche_path, youtube_id, new_date):
    """Réécrit proprement date et youtube_id dans le frontmatter."""
    with open(fiche_path, 'r', encoding='utf-8') as f:
        content = f.read()

    end = content.find('\n---', 3)
    fm = content[3:end]
    body = content[end:]

    # 1. Supprimer toutes les lignes date: et youtube_id: existantes (y compris malformées)
    fm = re.sub(r'^date\s*:.*$\n?', '', fm, flags=re.MULTILINE)
    fm = re.sub(r'^youtube_id\s*:.*$\n?', '', fm, flags=re.MULTILINE)

    # 2. Insérer date: et youtube_id: après la ligne type:
    type_m = re.search(r'^(type\s*:.*)$', fm, re.MULTILINE)
    if type_m:
        insert_pos = type_m.end()
        fm = fm[:insert_pos] + f"\ndate: {new_date}\nyoutube_id: {youtube_id}" + fm[insert_pos:]
    else:
        fm = fm.rstrip() + f"\ndate: {new_date}\nyoutube_id: {youtube_id}\n"

    with open(fiche_path, 'w', encoding='utf-8') as f:
        f.write('---' + fm + body)

def get_transcript_title_from_fiche(fiche_path):
    """Extrait le nom de fichier du wikilink dans la section ## Transcript."""
    try:
        with open(fiche_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return None
    m = re.search(r'##\s+Transcript\s*\n\[\[([^\]]+)\]\]', content)
    if not m:
        return None
    link = m.group(1).strip()
    return link.split('/')[-1]  # basename si chemin complet type [[Vault/dossier/nom]]


def read_fiche_frontmatter_fields(fiche_path):
    """Lit youtube_id et date depuis le frontmatter d'une fiche."""
    result = {'youtube_id': None, 'date': None}
    try:
        with open(fiche_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return result
    if not content.startswith('---'):
        return result
    end = content.find('\n---', 3)
    if end == -1:
        return result
    fm = content[3:end]
    for line in fm.splitlines():
        m = re.match(r'^youtube_id\s*:\s*["\']?([a-zA-Z0-9_-]+)["\']?\s*$', line)
        if m:
            result['youtube_id'] = m.group(1)
        m = re.match(r'^date\s*:\s*(\S+)\s*$', line)
        if m:
            result['date'] = m.group(1)
    return result


def update_fiche_frontmatter(fiche_path, youtube_id=None, date=None, dry_run=False):
    """Met à jour chirurgicalement youtube_id et/ou date dans le frontmatter.

    - youtube_id : ajouté après la ligne 'date:' si absent
    - date       : remplacé si partiel (YYYY-MM), inséré si absent
    Retourne True si une modification a été effectuée.
    """
    try:
        with open(fiche_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False

    if not content.startswith('---'):
        return False
    end = content.find('\n---', 3)
    if end == -1:
        return False

    fm = content[3:end]
    body = content[end:]  # inclut le '\n---' de fermeture

    original_fm = fm
    changes = []

    # --- Corriger / insérer la date ---
    if date:
        date_m = re.search(r'^(date\s*:)\s*(\S+)\s*$', fm, re.MULTILINE)
        if date_m:
            existing = date_m.group(2)
            if not re.match(r'\d{4}-\d{2}-\d{2}', existing):
                fm = fm[:date_m.start(2)] + date + fm[date_m.end(2):]
                changes.append(f"date: {existing} → {date}")
        else:
            # Insérer après 'type:' ou en fin de frontmatter
            type_m = re.search(r'^(type\s*:.*)$', fm, re.MULTILINE)
            if type_m:
                insert_pos = type_m.end()
                fm = fm[:insert_pos] + f"\ndate: {date}" + fm[insert_pos:]
            else:
                fm = fm.rstrip() + f"\ndate: {date}"
            changes.append(f"date: (absent) → {date}")

    # --- Insérer youtube_id ---
    if youtube_id and not re.search(r'^youtube_id\s*:', fm, re.MULTILINE):
        date_line = re.search(r'^(date\s*:.*)$', fm, re.MULTILINE)
        if date_line:
            insert_pos = date_line.end()
            fm = fm[:insert_pos] + f"\nyoutube_id: {youtube_id}" + fm[insert_pos:]
        else:
            type_m = re.search(r'^(type\s*:.*)$', fm, re.MULTILINE)
            if type_m:
                insert_pos = type_m.end()
                fm = fm[:insert_pos] + f"\nyoutube_id: {youtube_id}" + fm[insert_pos:]
            else:
                fm = fm.rstrip() + f"\nyoutube_id: {youtube_id}"
        changes.append(f"youtube_id: {youtube_id}")

    if not changes or fm == original_fm:
        return False

    if dry_run:
        print(f"    [dry-run] {os.path.basename(fiche_path)} : {', '.join(changes)}")
        return True

    new_content = '---' + fm + body
    with open(fiche_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True


def cmd_enrich_fiches(dry_run=False):
    """Ajoute youtube_id et corrige les dates dans les fiches Videos/."""
    print(f"\n{'='*60}")
    print(f"ENRICHISSEMENT DES FICHES VIDEOS/")
    print(f"{'='*60}")

    if not os.path.isdir(VIDEOS_DIR):
        print(f"ERREUR: dossier Videos/ introuvable : {VIDEOS_DIR}")
        return

    # Récupérer toutes les vidéos de la chaîne (1 seule requête)
    channel_videos = discover_channel_videos()
    if not channel_videos:
        print("Impossible de récupérer les vidéos de la chaîne.")
        return

    # Construire l'index norm(title) → {video_id, date}
    def norm_title(t):
        t = t.lower()
        t = re.sub(r'[^\w\s]', '', t)
        t = re.sub(r'\s+', ' ', t).strip()
        return t

    channel_map = {}
    for cv in channel_videos:
        key = norm_title(cv['title'])
        channel_map[key] = cv

    # Lister les fiches
    fiche_files = [
        os.path.join(VIDEOS_DIR, f)
        for f in os.listdir(VIDEOS_DIR)
        if f.endswith('.md') and not f.startswith('_') and f != 'CLAUDE.md'
    ]
    print(f"  Fiches trouvées   : {len(fiche_files)}")
    print(f"  Vidéos chaîne     : {len(channel_videos)}")
    if dry_run:
        print(f"  Mode              : DRY-RUN (aucune écriture)")

    updated = 0
    skipped = 0
    no_match = 0
    no_match_list = []

    for fiche_path in sorted(fiche_files):
        fields = read_fiche_frontmatter_fields(fiche_path)
        has_id = bool(fields['youtube_id'])
        date_complete = bool(fields['date'] and re.match(r'\d{4}-\d{2}-\d{2}', fields['date']))

        if has_id and date_complete:
            skipped += 1
            continue

        # Chercher la vidéo correspondante
        fiche_name = os.path.splitext(os.path.basename(fiche_path))[0]
        transcript_title = get_transcript_title_from_fiche(fiche_path)

        cv_match = None

        # 1. Match exact sur le titre transcript
        if transcript_title:
            key = norm_title(transcript_title)
            if key in channel_map:
                cv_match = channel_map[key]
            else:
                # Fuzzy sur titre transcript
                best_score, best_cv = 0, None
                for ckey, cv in channel_map.items():
                    score = SequenceMatcher(None, key, ckey).ratio()
                    if score > best_score:
                        best_score, best_cv = score, cv
                if best_score >= 0.75:
                    cv_match = best_cv

        # 2. Fallback : match sur le nom de la fiche
        if not cv_match:
            key = norm_title(fiche_name)
            if key in channel_map:
                cv_match = channel_map[key]
            else:
                best_score, best_cv = 0, None
                for ckey, cv in channel_map.items():
                    score = SequenceMatcher(None, key, ckey).ratio()
                    if score > best_score:
                        best_score, best_cv = score, cv
                if best_score >= 0.75:
                    cv_match = best_cv

        if not cv_match:
            no_match += 1
            no_match_list.append(fiche_name)
            continue

        new_id = cv_match['video_id'] if not has_id else None
        new_date = cv_match.get('upload_date') if not date_complete else None
        # Ne pas écraser une date complète déjà présente
        if new_date and not re.match(r'\d{4}-\d{2}-\d{2}', new_date):
            new_date = None

        if not new_id and not new_date:
            skipped += 1
            continue

        did_update = update_fiche_frontmatter(
            fiche_path,
            youtube_id=new_id,
            date=new_date,
            dry_run=dry_run
        )
        if did_update:
            updated += 1
            if not dry_run:
                print(f"  ✓ {fiche_name[:70]}")

    print(f"\n{'='*60}")
    print(f"RÉSUMÉ")
    print(f"  Mises à jour : {updated}")
    print(f"  Déjà OK      : {skipped}")
    print(f"  Non matchées : {no_match}")
    if no_match_list:
        print(f"\nFiches sans match YouTube :")
        for name in no_match_list:
            print(f"  - {name}")
    print(f"{'='*60}")


# =====================================================================
#  ENRICHISSEMENT DES TRANSCRIPTS (youtube_id)
# =====================================================================

def add_youtube_id_to_transcript(transcript_path, youtube_id, dry_run=False):
    """Ajoute youtube_id au frontmatter d'un transcript s'il n'y est pas déjà."""
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False

    if not content.startswith('---'):
        # Pas de frontmatter → en créer un minimal
        if dry_run:
            return True
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(f'---\nyoutube_id: {youtube_id}\n---\n' + content)
        return True

    end = content.find('\n---', 3)
    if end == -1:
        return False

    fm = content[3:end]
    if re.search(r'^youtube_id\s*:', fm, re.MULTILINE):
        return False  # Déjà présent

    fm = fm.rstrip() + f'\nyoutube_id: {youtube_id}\n'

    if dry_run:
        return True

    with open(transcript_path, 'w', encoding='utf-8') as f:
        f.write('---' + fm + content[end:])
    return True


def cmd_enrich_transcripts(dry_run=False):
    """Ajoute youtube_id aux fichiers Sources/Transcripts/ via les fiches Videos/ + yt-dlp."""
    print(f"\n{'='*60}")
    print(f"ENRICHISSEMENT DES TRANSCRIPTS")
    print(f"{'='*60}")

    if not os.path.isdir(VIDEOS_DIR):
        print(f"ERREUR: dossier Videos/ introuvable : {VIDEOS_DIR}")
        return

    # --- Étape 1 : propager depuis les fiches Videos/ ---
    # Chaque fiche qui a youtube_id + wikilink ## Transcript → on sait quel transcript correspond
    transcript_to_id = {}  # nom de fichier (sans .md) → youtube_id

    for f in sorted(os.listdir(VIDEOS_DIR)):
        if not f.endswith('.md') or f.startswith('_') or f == 'CLAUDE.md':
            continue
        fiche_path = os.path.join(VIDEOS_DIR, f)
        fields = read_fiche_frontmatter_fields(fiche_path)
        yt_id = fields['youtube_id']
        if not yt_id:
            continue
        transcript_name = get_transcript_title_from_fiche(fiche_path)
        if transcript_name:
            transcript_to_id[transcript_name] = yt_id

    print(f"  Fiches avec youtube_id + lien transcript : {len(transcript_to_id)}")

    # --- Étape 2 : fuzzy match via yt-dlp pour les transcripts restants ---
    transcript_files = sorted([
        f for f in os.listdir(TRANSCRIPTS_DIR)
        if f.endswith('.md') and not f.startswith('_')
    ])
    names_without_ext = [f[:-3] for f in transcript_files]
    uncovered = [n for n in names_without_ext if n not in transcript_to_id]

    print(f"  Transcripts total   : {len(transcript_files)}")
    print(f"  Couverts par fiches : {len(transcript_to_id)}")
    print(f"  À matcher via yt-dlp: {len(uncovered)}")

    if uncovered:
        channel_videos = discover_channel_videos()
        if channel_videos:
            def norm_title(t):
                t = t.lower()
                t = re.sub(r'[^\w\s]', '', t)
                t = re.sub(r'\s+', ' ', t).strip()
                return t

            channel_map = {norm_title(cv['title']): cv for cv in channel_videos}

            fuzzy_matched = 0
            for name in uncovered:
                key = norm_title(name)
                cv = channel_map.get(key)
                if not cv:
                    best_score, best_cv = 0, None
                    for ckey, cv_item in channel_map.items():
                        score = SequenceMatcher(None, key, ckey).ratio()
                        if score > best_score:
                            best_score, best_cv = score, cv_item
                    if best_score >= 0.75:
                        cv = best_cv
                if cv:
                    transcript_to_id[name] = cv['video_id']
                    fuzzy_matched += 1
            print(f"  Matchés via yt-dlp  : {fuzzy_matched}")

    # --- Étape 3 : écrire dans les fichiers transcript ---
    updated = 0
    skipped = 0
    no_match = 0

    for transcript_file in transcript_files:
        name = transcript_file[:-3]
        transcript_path = os.path.join(TRANSCRIPTS_DIR, transcript_file)
        youtube_id = transcript_to_id.get(name)

        if not youtube_id:
            no_match += 1
            continue

        if dry_run:
            # Vérifier quand même si déjà présent
            try:
                with open(transcript_path, 'r', encoding='utf-8') as fh:
                    head = fh.read(300)
                if 'youtube_id' in head:
                    skipped += 1
                    continue
            except Exception:
                pass
            print(f"  [dry-run] {transcript_file[:70]} → {youtube_id}")
            updated += 1
        else:
            result = add_youtube_id_to_transcript(transcript_path, youtube_id, dry_run=False)
            if result:
                updated += 1
            else:
                skipped += 1

    print(f"\n{'='*60}")
    print(f"RÉSUMÉ")
    print(f"  Mis à jour  : {updated}")
    print(f"  Déjà OK     : {skipped}")
    print(f"  Sans match  : {no_match}")
    print(f"{'='*60}")


# =====================================================================
#  MAIN
# =====================================================================

def main():
    args = sys.argv[1:]
    dry_run = '--dry-run' in args

    # Parse --last N / --recent N
    def parse_int_arg(flag):
        if flag not in args:
            return None
        idx = args.index(flag)
        if idx + 1 < len(args):
            try:
                return int(args[idx + 1])
            except ValueError:
                print(f"ERREUR: {flag} attend un nombre, reçu '{args[idx + 1]}'")
                sys.exit(1)
        else:
            print(f"ERREUR: {flag} attend un nombre (ex: {flag} 5)")
            sys.exit(1)

    last_n = parse_int_arg('--last')
    recent_n = parse_int_arg('--recent')

    if recent_n is not None:
        cmd_recent(recent_n, dry_run=dry_run)
        return

    if '--full' in args:
        # Tout faire : discover + fix + extract
        cmd_discover(dry_run=dry_run)
        if not dry_run:
            cmd_extract(dry_run=False, last_n=last_n)
    elif '--discover' in args:
        cmd_discover(dry_run=dry_run)
    elif '--fix' in args:
        cmd_fix()
    elif '--enrich-fiches' in args:
        cmd_enrich_fiches(dry_run=dry_run)
    elif '--fix-fiche-dates' in args:
        cmd_fix_fiche_dates(dry_run=dry_run)
    elif '--enrich-transcripts' in args:
        cmd_enrich_transcripts(dry_run=dry_run)
    else:
        # Mode par défaut : extraction seule (compatibilité)
        cmd_extract(dry_run=dry_run, last_n=last_n)


if __name__ == '__main__':
    main()
