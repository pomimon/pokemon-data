from pathlib import Path
from typing import Optional
import os
import json
import pprint

from pokemontcgsdk import Card
from pokemontcgsdk import Type
from pokemontcgsdk import Supertype
from pokemontcgsdk import Subtype
from pokemontcgsdk import Rarity

def get_data_dir() -> Path:
    root = Path("/Users/mango/projects/data-analytics/pokemon-data")
    path = root / "data"

    return path


# Creates a new directory at 'path',
# returns a boolean indicating if the path was created
def mkdirp(path: Path) -> bool:
    if path.exists():
        return False

    os.mkdir(path)

    return True


def write_json(data: any, path: Path):
    with open(path, "w") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def fetch_resource(name: str, root: Path, fetcher) -> bool:
    path = root / f"{name}.json"

    if path.exists():
        return False

    print(f"> Fetching {name}")

    data = fetcher()

    print(f"> Storing {name} at {path}")

    write_json(data, path)

    return True

# ------------ #
# Transformers #
# ------------ #

def transform_ability(value: any) -> dict:
    return {
        "name": value.name,
        "text": value.text,
        "type": value.type,
    }

def transform_ancient_trait(value: any) -> dict:
    return {
        "name": value.name,
        "text": value.text,
    }

def transform_attack(value: any) -> dict:
    return {
        "name": value.name,
        "cost": value.cost,
        "convertedEnergyCost": value.convertedEnergyCost,
        "damage": value.damage,
        "text": value.text,
    }

def transform_card_market(value: any) -> dict:
    return {
        "url": value.url,
        "updatedAt": value.updatedAt,
        "prices": transform_optional(value.prices, transform_card_market_prices),
    }

def transform_card_market_prices(value: any) -> dict:
    return {
        "averageSellPrice": value.averageSellPrice,
        "lowPrice": value.lowPrice,
        "trendPrice": value.trendPrice,
        "germanProLow": value.germanProLow,
        "suggestedPrice": value.suggestedPrice,
        "reverseHoloSell": value.reverseHoloSell,
        "reverseHoloLow": value.reverseHoloLow,
        "reverseHoloTrend": value.reverseHoloTrend,
        "lowPriceExPlus": value.lowPriceExPlus,
        "avg1": value.avg1,
        "avg7": value.avg7,
        "avg30": value.avg30,
        "reverseHoloAvg1": value.reverseHoloAvg1,
        "reverseHoloAvg7": value.reverseHoloAvg7,
        "reverseHoloAvg30": value.reverseHoloAvg30,
    }

def transform_card_image(value: any) -> dict:
    return {
        "small": value.small,
        "large": value.large,
    }

def transform_legality(value: any) -> dict:
    return {
        "unlimited": value.unlimited,
        "expanded": value.expanded,
        "standard": value.standard,
    }

def transform_resistance(value: any) -> dict:
    return {
        "type": value.type,
        "value": value.value,
    }

def transform_set(value: any) -> dict:
    return {
        "id": value.id,
        "images": transform_set_image(value.images),
        "legalities": transform_legality(value.legalities),
        "name": value.name,
        "printedTotal": value.printedTotal,
        "ptcgoCode": value.ptcgoCode,
        "releaseDate": value.releaseDate,
        "series": value.series,
        "total": value.total,
        "updatedAt": value.updatedAt,
    }


def transform_set_image(value: any) -> dict:
    return {
        "symbol": value.symbol,
        "logo": value.logo,
    }

def transform_tcg_player(value: any) -> dict:
    return {
        "url": value.url,
        "updatedAt": value.updatedAt,
        "prices": transform_optional(value.prices, transform_tcg_player_prices),
    }

def transform_tcg_player_prices(value: any) -> dict:
    return {
        "normal": transform_optional(value.normal, transform_tcg_player_price),
        "holofoil": transform_optional(value.holofoil, transform_tcg_player_price),
        "reverseHolofoil": transform_optional(value.reverseHolofoil, transform_tcg_player_price),
        "firstEditionHolofoil": transform_optional(value.firstEditionHolofoil, transform_tcg_player_price),
        "firstEditionNormal": transform_optional(value.firstEditionNormal, transform_tcg_player_price),
    }

def transform_tcg_player_price(value: any) -> dict:
    return {
        "low": value.low,
        "mid": value.mid,
        "high": value.high,
        "market": value.market,
        "directLow": value.directLow,
    }

def transform_weakness(value: any) -> dict:
    return {
        "type": value.type,
        "value": value.value,
    }

def transform_optional(value: any, transformer) -> Optional[dict]:
    if value is None:
        return None
    return transformer(value)

def transform_optional_list(value: any, transformer) -> Optional[list[dict]]:
    if value is None:
        return None
    return [transformer(item) for item in value]

def transform_card(value: Card) -> dict:
    return {
        "abilities": transform_optional_list(value.abilities, transform_ability),
        "artist": value.artist,
        "ancientTrait": transform_optional(value.ancientTrait, transform_ancient_trait),
        "attacks": transform_optional_list(value.attacks, transform_attack),
        "cardmarket": transform_optional(value.cardmarket, transform_card_market),
        "convertedRetreatCost": value.convertedRetreatCost,
        "evolvesFrom": value.evolvesFrom,
        "flavorText": value.flavorText,
        "hp": value.hp,
        "id": value.id,
        "images": transform_card_image(value.images),
        "legalities": transform_legality(value.legalities),
        "regulationMark": value.regulationMark,
        "name": value.name,
        "nationalPokedexNumbers": value.nationalPokedexNumbers,
        "number": value.number,
        "rarity": value.rarity,
        "resistances": transform_optional_list(value.resistances, transform_resistance),
        "retreatCost": value.retreatCost,
        "rules": value.rules,
        "set": transform_set(value.set),
        "subtypes": value.subtypes,
        "supertype": value.supertype,
        "tcgplayer": transform_optional(value.tcgplayer, transform_tcg_player),
        "types": value.types,
        "weaknesses": transform_optional_list(value.weaknesses, transform_weakness),
    }


def main():
    root = get_data_dir()
    created = mkdirp(root)

    print(f"> Root Directory Created: {created}")

    fetch_resource("types", root, Type.all)
    fetch_resource("supertypes", root, Supertype.all)
    fetch_resource("subtypes", root, Subtype.all)
    fetch_resource("rarities", root, Rarity.all)

    print("> Fetching All Cards")

    page = 1
    path = root / "cards.json"

    cards = []

    with open(path) as file:
        current = json.load(file)
        cards = current["data"]
        page = current["page"] + 1

    while True:
        print(f"> Fetching Page #{page}")

        data = Card.where(page=page, pageSize=250)

        if len(data) == 0:
            break

        page += 1
        cards.extend([transform_card(card) for card in data])

        data = {
            "page": page,
            "data": cards,
        }

        write_json(data, path)

    print(f"> Total Cards Found: {len(cards)}")

if __name__ == "__main__":
    main()

