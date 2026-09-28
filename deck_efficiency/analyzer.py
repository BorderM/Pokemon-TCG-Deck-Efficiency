from __future__ import annotations

from dataclasses import dataclass, asdict
import re

DECK_SIZE = 60

ROLE_WEIGHTS = {
    'attacker': 82,
    'draw': 86,
    'search': 90,
    'pokemon_search': 92,
    'evolution_support': 84,
    'energy': 58,
    'energy_acceleration': 86,
    'energy_recovery': 74,
    'recovery': 70,
    'gust': 82,
    'switch': 76,
    'disruption': 78,
    'stadium': 64,
    'tool': 62,
    'consistency': 88,
    'utility': 60,
}

# Small starter dictionary. Unknown cards are still handled through name heuristics.
KNOWN_CARD_ROLES = {
    'nest ball': {'pokemon_search', 'search', 'consistency'},
    'buddy-buddy poffin': {'pokemon_search', 'search', 'consistency'},
    'ultra ball': {'pokemon_search', 'search', 'consistency'},
    'capturing aroma': {'pokemon_search', 'search'},
    'great ball': {'pokemon_search', 'search'},
    'arven': {'search', 'tool', 'consistency'},
    'rare candy': {'evolution_support', 'consistency'},
    'iono': {'draw', 'disruption', 'consistency'},
    "professor's research": {'draw', 'consistency'},
    'professor research': {'draw', 'consistency'},
    'boss’s orders': {'gust'},
    "boss's orders": {'gust'},
    'counter catcher': {'gust', 'disruption'},
    'switch': {'switch'},
    'switch cart': {'switch'},
    'escape rope': {'switch', 'disruption'},
    'super rod': {'recovery', 'energy_recovery'},
    'energy retrieval': {'energy_recovery'},
    'superior energy retrieval': {'energy_recovery'},
    'earthen vessel': {'energy_recovery', 'search'},
}

TRAINER_KEYWORDS = {
    'ball', 'candy', 'research', 'iono', 'orders', 'switch', 'rod', 'vessel', 'catcher',
    'poffin', 'arven', 'vacuum', 'stadium', 'town', 'cape', 'belt', 'tool', 'boss'
}
ENERGY_KEYWORDS = {'energy', 'energies'}
POKEMON_MARKERS = {' ex', ' v', ' vmax', ' vstar', ' gx'}


@dataclass
class DeckCard:
    count: int
    name: str
    category: str
    roles: set[str]
    efficiency: int
    note: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d['roles'] = sorted(self.roles)
        return d


def normalise_name(name: str) -> str:
    return re.sub(r'\s+', ' ', name.strip().lower().replace('’', "'"))


def has_word(text: str, word: str) -> bool:
    """Match a standalone word/phrase without treating 'research' as 'search'."""
    return re.search(rf'(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])', text) is not None


def parse_decklist(deck_text: str) -> list[tuple[int, str]]:
    cards: list[tuple[int, str]] = []
    for raw_line in deck_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        # Ignore common section headers from exports.
        if line.lower().rstrip(':') in {'pokemon', 'trainer', 'trainers', 'energy', 'energies'}:
            continue
        match = re.match(r'^(\d+)\s*x?\s+(.+)$', line, flags=re.I)
        if not match:
            match = re.match(r'^(.+?)\s+x(\d+)$', line, flags=re.I)
            if match:
                name, count = match.group(1), int(match.group(2))
                cards.append((count, name.strip()))
            continue
        cards.append((int(match.group(1)), match.group(2).strip()))
    return cards


def categorize(name: str, roles: set[str]) -> str:
    n = normalise_name(name)
    if 'energy' in roles or any(k in n for k in ENERGY_KEYWORDS):
        return 'Energy'
    if roles & {'draw', 'search', 'pokemon_search', 'gust', 'switch', 'evolution_support', 'stadium', 'tool'}:
        return 'Trainer'
    if any(k in n for k in TRAINER_KEYWORDS):
        return 'Trainer'
    return 'Pokémon'


def infer_roles(name: str) -> set[str]:
    n = normalise_name(name)
    roles = set(KNOWN_CARD_ROLES.get(n, set()))
    if 'energy' in n:
        roles.add('energy')
    if has_word(n, 'ball') or 'poffin' in n or has_word(n, 'search'):
        roles.update({'search', 'pokemon_search'})
    if 'research' in n or 'draw' in n or n == 'iono':
        roles.add('draw')
    if 'boss' in n or 'catcher' in n:
        roles.add('gust')
    if 'switch' in n or 'rope' in n:
        roles.add('switch')
    if 'candy' in n or 'evolution' in n:
        roles.add('evolution_support')
    if 'stadium' in n or 'town' in n:
        roles.add('stadium')
    if 'tool' in n or 'cape' in n or 'belt' in n:
        roles.add('tool')
    if 'rod' in n or 'retrieval' in n or 'recycler' in n:
        roles.add('recovery')
    if any(marker in n for marker in POKEMON_MARKERS):
        roles.add('attacker')
    return roles or {'utility'}


def score_card(count: int, category: str, roles: set[str], total_cards: int) -> tuple[int, str]:
    base = max(ROLE_WEIGHTS.get(role, 55) for role in roles)
    note_bits = []

    if 'pokemon_search' in roles or 'draw' in roles:
        if count >= 4:
            base += 5
            note_bits.append('high-count consistency card')
        elif count <= 1:
            base -= 10
            note_bits.append('low count for a consistency role')

    if 'energy' in roles:
        base = 55
        note_bits.append('necessary resource; efficiency depends on attack costs')

    if 'evolution_support' in roles and count >= 3:
        note_bits.append('strong if the deck relies on Stage 2 setup')

    if count > 4 and 'energy' not in roles:
        base -= 25
        note_bits.append('count exceeds normal 4-copy rule')

    if category == 'Pokémon' and 'attacker' not in roles:
        base = max(base, 58)
        note_bits.append('needs manual role tagging to judge accurately')

    score = max(20, min(100, int(base)))
    if not note_bits:
        note_bits.append('reasonable role fit; refine with matchup/archetype data later')
    return score, '; '.join(note_bits)


def analyze_deck(deck_text: str) -> dict:
    parsed = parse_decklist(deck_text)
    cards: list[DeckCard] = []
    for count, name in parsed:
        roles = infer_roles(name)
        category = categorize(name, roles)
        efficiency, note = score_card(count, category, roles, sum(c for c, _ in parsed))
        cards.append(DeckCard(count, name, category, roles, efficiency, note))

    total = sum(c.count for c in cards)
    by_category = {'Pokémon': 0, 'Trainer': 0, 'Energy': 0}
    role_counts: dict[str, int] = {}
    for card in cards:
        by_category[card.category] = by_category.get(card.category, 0) + card.count
        for role in card.roles:
            role_counts[role] = role_counts.get(role, 0) + card.count

    suggestions = build_suggestions(total, by_category, role_counts)
    avg_efficiency = round(sum(c.efficiency * c.count for c in cards) / total, 1) if total else 0
    return {
        'total_cards': total,
        'deck_size_ok': total == DECK_SIZE,
        'by_category': by_category,
        'role_counts': dict(sorted(role_counts.items())),
        'average_efficiency': avg_efficiency,
        'cards': [c.to_dict() for c in sorted(cards, key=lambda c: (-c.efficiency, c.category, c.name))],
        'suggestions': suggestions,
    }


def build_suggestions(total: int, categories: dict[str, int], roles: dict[str, int]) -> list[str]:
    out = []
    if total != DECK_SIZE:
        out.append(f'Deck has {total} cards; official decks should be exactly 60.')
    if categories.get('Pokémon', 0) < 10:
        out.append('Pokémon count looks low; ensure you have enough Basics and attacker/support lines.')
    if categories.get('Energy', 0) < 7:
        out.append('Energy count looks low unless the deck has strong acceleration or very cheap attacks.')
    if roles.get('pokemon_search', 0) < 6:
        out.append('Consider more Pokémon search/setup cards; many decks want roughly 6–10 search outs.')
    if roles.get('draw', 0) < 6:
        out.append('Draw support looks light; consider more draw Supporters/items for consistency.')
    if roles.get('switch', 0) < 2:
        out.append('Switching options are limited; add mobility if retreat costs or status effects matter.')
    if roles.get('gust', 0) < 2:
        out.append('Gust effects are limited; most decks want ways to target benched threats.')
    if not out:
        out.append('Core counts look reasonable for a first pass. Next step: archetype-specific scoring.')
    return out
