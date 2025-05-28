-- Get all Mcdonald's Pokemon (name, artist name, hp, and image)
SELECT 
  c.name,
  c.artist,
  c.hp,
  i.'primary' AS image
FROM
  Card c
Join 
  Card_Image ci
ON 
  c.id = ci.card
JOIN
  Image i
ON 
  i.id = ci.image
WHERE 
  c.cardId LIKE 'mcd%'

-- BEGINNER --
-- What are the names and IDs of all cards in a specific card set?
SELECT
  c.name,
  c.id,
  c.cardId
FROM
  Card c
JOIN
  CardSet cs
ON
  c.cardSet = cs.id
WHERE
  cs.setId LIKE 'dp%'


-- What are the names and IDs of all cards in a specific card set?
SELECT 
  COUNT(c.rarity),
  r.name
FROM
  Card c
JOIN
  Rarity r
ON
  c.rarity = r.id
GROUP BY r.name


-- What types exist in the dataset?
SELECT name
FROM Type

-- INTERMEDIATE --
-- Which cards have both a weakness and a resistance?
SELECT
  Card.id,
  Card.name,
  Card.cardId,
  Type.name AS type,
  Resistance_Type.name AS resistance,
  Weakness_Type.name AS weakness
FROM
  Card
JOIN Card_Type            ON Card.id = Card_Type.card
JOIN Type                 ON Type.id = Card_Type.type

JOIN Card_Weakness        ON Card.id = Card_Weakness.card
JOIN Weakness             ON Weakness.id = Card_Weakness.weakness
JOIN Type Weakness_type   ON Weakness_type.id = Weakness.type_

JOIN Card_Resistance      ON Card.id = Card_Resistance.card
JOIN Resistance           ON Resistance.id = Card_Resistance.resistance
JOIN Type Resistance_Type ON Resistance_Type.id = Resistance.type_


-- What are the different attack types, and how many times is each used?
SELECT 
  Type.name,
  COUNT(*) AS usage
FROM
  Attack_card
JOIN Type ON Attack_Type.type_ = Type.id
JOIN Attack_Type ON Attack_Card.attack = Attack_Type.attack
GROUP BY Type.name
ORDER BY usage DESC


-- Which cards have more than one subtype?
SELECT 
  Card.name,
  Card.id,
  COUNT(*) AS card_count
FROM
  Card_SubType
JOIN Card ON Card.id = Card_SubType.card
GROUP BY
  Card.name, Card.id
HAVING COUNT(*) > 1

-- What abilities are associated with each ability type?
SELECT 
  Ability.name AS ability,
  AbilityType.name AS ability_type
FROM
  Ability
JOIN AbilityType ON Ability.type_ = AbilityType.id

  
-- ADVANCED --
-- For each card, what are its attacks and their respective attack types?
SELECT 
  Card.name,
  Attack.name AS attack,
  Type.name AS type
FROM
  Card
JOIN
  Attack_Card ON Attack_Card.card = Card.id
JOIN 
  Attack ON Attack.id = Attack_Card.attack 
JOIN
  Attack_Type ON Attack_Type.attack = Attack.id
JOIN
  Type ON Type.id = Attack_Type.type_


-- Which types are most commonly associated with cards?
SELECT 
  Type.name,
  Count(Type.id) AS type_count
FROM
  Card
JOIN
  Card_Type ON Card.id = Card_Type.card
JOIN
  Type ON Type.id = Card_Type.type
GROUP BY
  Type.id
ORDER BY type_count DESC


-- What are the most common weaknesses across all cards?
SELECT 
  Type.name,
  Count(Type.id) AS type_count
FROM
  Card
JOIN
  Card_Weakness ON Card.id = Card_Weakness.card
JOIN 
  Weakness ON Weakness.id = Card_Weakness.weakness
JOIN
  Type ON Type.id = Weakness.type_
GROUP BY
  Type.id
ORDER BY type_count DESC


-- Which cards have abilities of a certain ability type (e.g., “Special” if applicable)?
SELECT 
  Card.name,
  Ability.name,
  Ability.text
FROM
  Card
JOIN
  Ability_Card ON Ability_Card.card = Card.id
JOIN
  Ability ON Ability.id = Ability_Card.ability
JOIN
  AbilityType ON AbilityType.id = Ability.type_
WHERE 
  AbilityType.name = 'Poké-Power'



  -- Find all cards that share the same type and subtype.
SELECT
  Card.name AS Card,
  SubType.name AS SubType,
  Type.name AS Type
FROM
  Card
JOIN Card_SubType ON Card.id = Card_SubType.card
JOIN SubType ON Card_SubType.subtype = SubType.id
JOIN Card_Type ON Card.id = Card_Type.card
JOIN Type ON Card_Type.type = Type.id
GROUP BY SubType, Type 

-- Find all cards that share the same type and subtype.
-- SELECT
--   Card.name AS Card,
--   SubType.name AS SubType,
--   Type.name AS Type
-- FROM
--   Card
-- JOIN Card_Type ON Card.id = Card_Type.card
-- JOIN Type ON Card_Type.type = Type.id
-- JOIN Card_SubType ON Card.id = Card_SubType.card
-- JOIN SubType ON Card_SubType.subtype = SubType.id

-- -- Self-join to find another card with the same type and subtype
-- JOIN Card Cards ON Card.id != Cards.id
-- JOIN Card_Type Cards_Type 
-- ON Cards.id = Cards_Type.card AND Card_Type.type = Cards_Type.type
-- JOIN Card_SubType Cards_SubType 
-- ON Cards.id = Cards_SubType.card AND Card_SubType.subtype = Cards_SubType.subtype

-- -- Step 1: Find shared (type, subtype) pairs
WITH shared_type_subtype AS (
    SELECT
        ct.type AS type_id,
        cst.subtype AS subtype_id
    FROM Card_Type ct
    JOIN Card_SubType cst ON ct.card = cst.card
    GROUP BY ct.type, cst.subtype
    HAVING COUNT(DISTINCT ct.card) > 1
)

-- -- Step 2: Find all cards that match those pairs
SELECT
    c.name AS card_name,
    t.name AS type_name,
    st.name AS subtype_name
FROM shared_type_subtype sts
JOIN Card_Type ct ON sts.type_id = ct.type
JOIN Card_SubType cst ON sts.subtype_id = cst.subtype AND ct.card = cst.card
JOIN Card c ON ct.card = c.id
JOIN Type t ON ct.type = t.id
JOIN SubType st ON cst.subtype = st.id;


-- CTES --
-- Find the total number of cards each type appears on.
-- Use a CTE to first count card appearances per type, then sort the final result by count.

WITH TypeCounts AS (
    SELECT 
        Card_Type.type AS type_id,
        COUNT(DISTINCT Card_Type.card) AS card_count
    FROM Card_Type
    GROUP BY Card_Type.type
)

SELECT 
    Type.name AS type_name,
    TypeCounts.card_count
FROM Type
JOIN TypeCounts ON Type.id = TypeCounts.type_id
ORDER BY TypeCounts.card_count DESC;


-- Find all subtypes that are used by more than 5 cards.
-- Use a CTE to group by subtype and count, and filter in the main query.

WITH subtypes_count AS (
  SELECT 
      Card_SubType.subtype AS subtype_id,
      COUNT(Card_SubType.card) AS card_count
  FROM Card_SubType
  GROUP BY Card_SubType.subtype
  )
SELECT
  SubType.name,
  subtypes_count.card_count
FROM SubType
JOIN subtypes_count ON SubType.id = subtypes_count.subtype_id
WHERE subtypes_count.card_count > 5


-- List cards that have at least 2 attacks. 
-- Use a CTE to count attacks per card, and return cards with count ≥ 2.

WITH Attack_Count AS (
  SELECT 
      Attack_Card.card AS Card_Id,
      Count(*) AS Card_Count
  FROM Attack_Card
  GROUP BY Attack_Card.card
)

SELECT 
  Card.name,
  Attack_Count.Card_Count
 FROM Card
 JOIN Attack_Count ON Card.id = Attack_Count.card_Id
 WHERE Attack_Count.Card_Count > 2


 -- Return all cards where the cards ability name contains the word heal
-- Use a CTE to isolate card-ability joins with that filter, then join to get the card names.

WITH Ability_Names AS (
  SELECT 
    Ability_Card.card AS card_id,
    Ability.name AS name 
  FROM Ability_Card
  JOIN Ability ON Ability.id = Ability_Card.ability
  )
  
SELECT 
  Card.name,
  Ability_Names.name
FROM 
  Card
JOIN Ability_Names ON Card.id = Ability_Names.card_id
WHERE Ability_Names.name LIKE '%heal%'


-- Find the average number of attacks per card subtype.
-- Use a CTE to join Card, Card_SubType, and Attack_Card, then group and average in the outer query.

WITH AVG_Number AS (
  SELECT 
    Attack_Card.attack AS attack_id,
    Card_SubType.subtype AS subtype_id,
    COUNT(Attack_Card.attack) AS attack_count
  FROM Card
  JOIN Card_SubType ON Card_SubType.card = Card.id
  JOIN Attack_Card ON Attack_Card.card = Card.id
  GROUP BY Card.id, Card_SubType.subtype
)

SELECT 
  SubType.name AS subtype,
  ROUND(AVG(attack_count), 2) AS avg_attacks
FROM AVG_Number
JOIN SubType ON AVG_Number.subtype_id = SubType.id
GROUP BY SubType.name
ORDER BY avg_attacks DESC;
