from deck_efficiency.analyzer import analyze_deck, clean_card_name, parse_decklist


def test_parse_common_decklist_lines():
    parsed = parse_decklist('4 Nest Ball\n2x Iono\nBoss x1\nPokémon\n# comment')
    assert [(c.count, c.name, c.section) for c in parsed] == [
        (4, 'Nest Ball', None),
        (2, 'Iono', None),
        (1, 'Boss', None),
    ]


def test_parse_section_headers_with_counts():
    parsed = parse_decklist(
        """Pokémon: 19
4 Beldum TEF 113
Trainer: 24
2 Brock's Scouting JTG 146
1 Boss's Orders MEG 114
Energy: 17
12 Metal Energy
"""
    )
    assert [(c.count, c.name, c.section) for c in parsed] == [
        (4, 'Beldum TEF 113', 'Pokémon'),
        (2, "Brock's Scouting JTG 146", 'Trainer'),
        (1, "Boss's Orders MEG 114", 'Trainer'),
        (12, 'Metal Energy', 'Energy'),
    ]


def test_clean_card_name_strips_set_codes():
    assert clean_card_name("Boss's Orders MEG 114") == "Boss's Orders"
    assert clean_card_name('Mega Excadrill ex PBL 65') == 'Mega Excadrill ex'
    assert clean_card_name('Pokégear 3.0 SVI 186') == 'Pokégear 3.0'


def test_analyze_deck_roles_and_suggestions():
    result = analyze_deck('4 Nest Ball\n4 Iono\n2 Boss\n10 Fire Energy')
    assert result['total_cards'] == 20
    assert result['role_counts']['pokemon_search'] == 4
    assert result['role_counts']['draw'] == 4
    assert any('60' in s for s in result['suggestions'])
    assert result['average_efficiency'] > 0


def test_research_is_draw_not_search():
    result = analyze_deck("3 Professor's Research")
    card = result['cards'][0]
    assert 'draw' in card['roles']
    assert 'search' not in card['roles']
    assert 'pokemon_search' not in card['roles']


def test_basic_energy_count_is_not_penalized_as_copy_rule_violation():
    result = analyze_deck('12 Fire Energy')
    card = result['cards'][0]
    assert card['efficiency'] == 55
    assert '4-copy rule' not in card['note']


def test_section_category_beats_weak_name_heuristics():
    result = analyze_deck(
        """Trainer: 24
2 Brock's Scouting JTG 146
2 Lillie's Determination MEG 119
1 Team Rocket's Petrel DRI 176
Pokémon: 19
4 Beldum TEF 113
2 Genesect ex BLK 67
Energy: 17
12 Metal Energy
"""
    )
    categories = {card['name']: card['category'] for card in result['cards']}
    assert categories["Brock's Scouting JTG 146"] == 'Trainer'
    assert categories["Lillie's Determination MEG 119"] == 'Trainer'
    assert categories["Team Rocket's Petrel DRI 176"] == 'Trainer'
    assert categories['Beldum TEF 113'] == 'Pokémon'
    assert categories['Metal Energy'] == 'Energy'
