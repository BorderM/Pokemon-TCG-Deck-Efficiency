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
