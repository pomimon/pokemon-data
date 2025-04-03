import pathlib
import json

# from pony.orm import *
from pony.orm import set_sql_debug
from pony.orm import Database
from pony.orm import Optional
from pony.orm import Required
from pony.orm import db_session
from pony.orm import commit
from pony.orm import Set

db = Database()

set_sql_debug(True)

class Mixin(object):
  @classmethod
  def find_or_create(klass, **kwargs):
    # TODO: Fix Hack Later
    query = dict(kwargs)

    if "cost" in query:
      del query["cost"]

    if "images" in query:
      del query["images"]

    instance = klass.get(**query)

    if instance is None:
      instance = klass(**kwargs)

    return instance

class Rarity(db.Entity, Mixin):
  name = Required(str, unique=True)
  cards = Set("Card")

class SuperType(db.Entity, Mixin):
  name = Required(str, unique=True)
  cards = Set("Card")

class SubType(db.Entity, Mixin):
  name = Required(str, unique=True)
  cards = Set("Card")

class Type(db.Entity, Mixin):
  name = Required(str, unique=True)
  cards = Set("Card")
  weaknesses = Set("Weakness")
  resistances = Set("Resistance")
  attacks = Set("AttackType")

class Weakness(db.Entity, Mixin):
  type_ = Required(Type)
  value = Required(str)
  cards = Set("Card")

class Resistance(db.Entity, Mixin):
  type_ = Required(Type)
  value = Required(str)
  cards = Set("Card")

class AbilityType(db.Entity, Mixin):
  name = Required(str, unique=True)
  abilities = Set("Ability")

class Ability(db.Entity, Mixin):
  name = Required(str)
  text = Required(str)
  type_ = Required(AbilityType)
  cards = Set("Card")

class Attack(db.Entity, Mixin):
  name = Required(str)
  cost = Set("AttackType")
  convertedEnergyCost = Required(int)
  damage = Optional(str, nullable=True)
  text = Optional(str, nullable=True)
  cards = Set("Card")

class AttackType(db.Entity, Mixin):
  _table_ = "Attack_Type"
  attack = Required(Attack)
  type_ = Required(Type)

class Image(db.Entity, Mixin):
  primary = Required(str, nullable=True)
  secondary = Required(str, nullable=True)
  cards = Set("Card")
  cardSets = Set("CardSet")

class Card(db.Entity, Mixin):
  abilities = Set(Ability)
  artist = Optional(str, nullable=True)
  # ancientTrait: Optional[AncientTrait]
  attacks = Set(Attack)
  # cardmarket: Optional[Cardmarket]
  convertedRetreatCost = Optional(int)
  evolvesFrom = Optional(str, nullable=True)
  flavorText = Optional(str, nullable=True)
  hp = Optional(str, nullable=True)
  cardId = Required(str)
  images = Set(Image)
  # legalities: Legality
  name = Required(str)
  # nationalPokedexNumbers: Optional[List[int]]
  number = Required(str)
  rarity = Optional(Rarity)
  regulationMark = Optional(str, nullable=True)
  resistances = Set(Resistance)
  # retreatCost: Optional[List[str]]
  # rules: Optional[List[str]]
  cardSet = Required("CardSet")
  subtypes = Set(SubType)
  supertype = Required(SuperType)
  # tcgplayer: Optional[TCGPlayer]
  types = Set(Type)
  weaknesses = Set(Weakness)

class CardSet(db.Entity, Mixin):
  setId = Required(str)
  images = Set(Image)
  # legalities: Legality
  name = Required(str)
  printedTotal = Required(int)
  ptcgoCode = Optional(str, nullable=True)
  releaseDate = Required(str)
  series = Required(str)
  total = Required(int)
  updatedAt = Required(str)
  card = Set(Card)


def get_data_dir():
    root = pathlib.Path("/Users/mango/projects/data-analytics/pokemon-data")
    path = root / "data"
    return path


def load_json(path):
    with open(path, "r") as file:
        return json.load(file)
    return None


# setting up connection to database
db.bind(provider='sqlite', filename='cards.sqlite', create_db=True)
db.generate_mapping(check_tables=False, create_tables=True)
db.drop_all_tables(with_all_data=True)
db.create_tables()


@db_session
def main():
  # 1. Initialize common variables/state
  root_path = get_data_dir()

  # 2.a. Load rarity JSON and create database records
  for name in load_json(root_path / "rarities.json"):
    _rarity = Rarity.find_or_create(name=name)

  # 2.b. Load supertype JSON and create database records
  for name in load_json(root_path / "supertypes.json"):
    _supertype = SuperType.find_or_create(name=name)

  # 2.c. Load subtype JSON and create database records
  for name in load_json(root_path / "subtypes.json"):
    _subtype = SubType.find_or_create(name=name)

  # 2.d. Load type JSON and create database records
  for name in load_json(root_path / "types.json"):
    _type = Type.find_or_create(name=name)

  # 2.e. Load card JSON and create database records
  cards = load_json(root_path / "cards.json")

  for card in cards["data"][:5]:
  # for card in cards["data"][:250]:
  #   if card["name"] != "Celebi & Venusaur-GX":
  #     continue

    fks = {}

    fks["supertype"] = SuperType.find_or_create(name=card["supertype"])

    fks["images"] = Image.find_or_create(
      primary=card["images"]["small"],
      secondary=card["images"]["large"],
    )

    fks["set"] = CardSet.find_or_create(
      setId=card["set"]["id"],
      images=Image.find_or_create(
        primary=card["set"]["images"]["symbol"],
        secondary=card["set"]["images"]["logo"],
      ),
      # legalities: Legality
      name=card["set"]["name"],
      printedTotal=card["set"]["printedTotal"],
      ptcgoCode=card["set"]["ptcgoCode"],
      releaseDate=card["set"]["releaseDate"],
      series=card["set"]["series"],
      total=card["set"]["total"],
      updatedAt=card["set"]["updatedAt"],
    )

    if card["rarity"] is not None:
      fks["rarity"] = Rarity.find_or_create(name=card["rarity"])

    if card["types"] is not None:
      fks["types"] = [Type.find_or_create(name=name) for name in card["types"]]

    if card["subtypes"] is not None:
      fks["subtypes"] = [SubType.find_or_create(name=name) for name in card["subtypes"]]

    if card["weaknesses"] is not None:
      fks["weaknesses"] = []

      for weakness in card["weaknesses"]:
        type_ = Type.find_or_create(name=weakness["type"])
        entry = Weakness.find_or_create(type_=type_, value=weakness["value"])
        fks["weaknesses"].append(entry)

    if card["resistances"] is not None:
      fks["resistances"] = []

      for resistance in card["resistances"]:
        type_ = Type.find_or_create(name=resistance["type"])
        entry = Resistance.find_or_create(type_=type_, value=resistance["value"])
        fks["resistances"].append(entry)

    if card["abilities"] is not None:
      fks["abilities"] = []

      for ability in card["abilities"]:
        type_ = AbilityType.find_or_create(name=ability["type"])
        entry = Ability.find_or_create(type_=type_, name=ability["name"], text=ability["text"])
        fks["abilities"].append(entry)

    if card["attacks"] is not None:
      fks["attacks"] = []

      for attack in card["attacks"]:
        entity = Attack.find_or_create(
          name=attack["name"],
          cost=[],
          convertedEnergyCost=attack["convertedEnergyCost"],
          damage=attack["damage"],
          text=attack["text"]
        )

        for name in attack["cost"]:
          AttackType(
            attack=entity,
            type_=Type.find_or_create(name=name)
          )

        fks["attacks"].append(entity)

    # print(f"Foreign Keys: {fks}")

    Card(
      abilities=fks.get("abilities", []),
      artist=card["artist"],
      # ancientTrait: Optional[AncientTrait]
      attacks=fks.get("attacks", []),
      # cardmarket: Optional[Cardmarket]
      convertedRetreatCost=card["convertedRetreatCost"],
      evolvesFrom=card["evolvesFrom"],
      flavorText=card["flavorText"],
      hp=card["hp"],
      cardId=card["id"],
      images=fks["images"],
      # legalities: Legality
      name=card["name"],
      # nationalPokedexNumbers: Optional[List[int]]
      number=card["number"],
      rarity=fks.get("rarity"),
      regulationMark=card["regulationMark"],
      resistances=fks.get("resistances", []),
      # retreatCost: Optional[List[str]]
      # rules: Optional[List[str]]
      cardSet=fks["set"],
      subtypes=fks.get("subtypes", []),
      supertype=fks["supertype"],
      # tcgplayer: Optional[TCGPlayer]
      types=fks.get("types", []),
      weaknesses=fks.get("weaknesses", []),
    )


  # 3. Write all records to the database
  commit()

  print(db)

if __name__ == "__main__":
  main()
