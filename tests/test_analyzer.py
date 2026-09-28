from deck_efficiency.analyzer import analyze_deck, parse_decklist


def test_parse_common_decklist_lines():
    parsed = parse_decklist('4 Nest Ball\n2x Iono\nBoss x1\nPokémon\n# comment')
    assert parsed == [(4, 'Nest Ball'), (2, 'Iono'), (1, 'Boss')]


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
