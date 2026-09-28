# Card Categorisation and Role Tagging Strategy

The analyzer should treat **card identity** and **deck role** as separate problems.

## 1. Card category: use reliable sources first

A card should be categorised as `Pokémon`, `Trainer`, or `Energy` using this priority order:

1. **Decklist section headers** from pasted exports.
   - `Pokémon: 19` means every following card is Pokémon until the next section.
   - `Trainer: 24` means every following card is Trainer.
   - `Energy: 17` means every following card is Energy.
2. **Card database metadata** from a Pokémon TCG API or local snapshot.
   - This should become the long-term source of truth.
   - Store card name, set code, collector number, supertype, subtypes, rules text, attacks, abilities, and regulation mark.
3. **Name/text heuristics** only as a fallback.
   - Heuristics are useful for early MVP behavior, but should not be treated as competitive-grade accuracy.

## 2. Clean exported names before matching

Deck exports often include set codes and collector numbers:

- `Boss's Orders MEG 114`
- `Mega Excadrill ex PBL 65`
- `Pokégear 3.0 SVI 186`

Before role lookup, strip the trailing set/number suffix and match against the printed card name:

- `Boss's Orders`
- `Mega Excadrill ex`
- `Pokégear 3.0`

Keep the original name visible in the UI so users can still see the exact print.

## 3. Role tags: infer from card text, not just names

Role tags should describe what the card does for the deck:

- `pokemon_search`
- `draw`
- `gust`
- `switch`
- `energy_acceleration`
- `energy_recovery`
- `recovery`
- `evolution_support`
- `disruption`
- `stadium`
- `tool`
- `attacker`
- `support_pokemon`
- `damage_modifier`
- `bench_setup`
- `discard_synergy`
- `utility`

Use deterministic rules over card text, for example:

| Text pattern | Role |
| --- | --- |
| `search your deck for a Pokémon` | `pokemon_search`, `search` |
| `draw cards until` / `draw X cards` | `draw` |
| `switch your Active Pokémon` | `switch` |
| `switch 1 of your opponent's Benched Pokémon` | `gust` |
| `attach ... Energy from your discard pile/deck/hand` | `energy_acceleration` |
| `put ... Energy from your discard pile into your hand/deck` | `energy_recovery` |
| `evolve` / `Stage 2` / `Rare Candy` | `evolution_support` |
| `discard cards from your opponent's hand` | `disruption` |
| `Stadium` supertype/subtype | `stadium` |
| `Pokémon Tool` subtype | `tool` |

## 4. Manual overrides should be small

Manual tagging every card is not realistic. Use overrides only for:

- meta staples
- cards with weird wording
- cards whose role depends heavily on archetype
- corrections submitted after the automated tagger gets something wrong

Suggested override format later:

```json
{
  "Boss's Orders": ["gust"],
  "Buddy-Buddy Poffin": ["pokemon_search", "search", "consistency"],
  "Team Rocket's Petrel": ["draw", "disruption"]
}
```

## 5. Long-term scoring should be deck-contextual

A card's role score should depend on the deck, not just the card.

Examples:

- `Rare Candy` is excellent in a Stage 2 deck and poor in a deck with no Stage 2 line.
- `Buddy-Buddy Poffin` is stronger when the deck has many 70 HP-or-less Basic Pokémon.
- Energy acceleration matters only if it matches the deck's energy types and attack costs.
- A second gust card may be valuable; a seventh gust card is probably redundancy.

## 6. Recommended roadmap

1. Section-aware deck parsing. ✅
2. Strip set/collector suffixes before matching. ✅
3. Add a small known-card override dictionary for staples. ✅
4. Add Pokémon TCG API lookup and local lightweight cache.
5. Build text-based role inference from API card text.
6. Add manual correction UI/admin JSON for exceptions.
7. Add archetype detection and probability math.
8. Use Limitless/meta decklists later to tune role weights and common counts.
