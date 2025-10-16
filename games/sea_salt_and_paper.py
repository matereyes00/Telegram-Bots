# This file contains the rules for the game "Sea, Salt & Paper".
# The text has been cleaned, corrected, and reformatted for clarity and optimal AI processing.

RULES_TEXT = """

## GAME TITLE
Sea Salt & Paper

## GAME OBJECTIVE
Be the first player to reach the required number of points to win the game. The game is played over several rounds.
- **2 players:** 40 points
- **3 players:** 35 points
- **4 players:** 30 points

---

## HOW TO PLAY A TURN
On your turn, you must perform these steps in order:

**Step 1: Add a Card to Your Hand**
You must choose **one** of two options:
- **Option A: Draw from the Deck.** Take the top two cards from the deck. Secretly add one to your hand and place the other face-up on either discard pile.
- **Option B: Take from a Discard Pile.** Choose one of the two discard piles and take the top card.

**Step 2: (Optional) Play Duo Cards**
If you have a pair of Duo cards, you may play them face-up on the table in front of you to immediately trigger their effect. You can play multiple pairs on the same turn. (See 'Card Types & Effects' below).

**Step 3: (Optional) End the Round**
If you have **7 or more points** in your hand and on the table, you may choose to end the round by announcing either "STOP" or "LAST CHANCE". If you don't, your turn ends.

---

## ENDING A ROUND
When a player with at least 7 points ends the round, they reveal their hand.

### If you announce "STOP"
- The round ends immediately.
- All players reveal their hands and score the points from their cards.

### If you announce "LAST CHANCE"
You are betting that you will have the highest score.
- All other players get one final turn.
- After their turns, all scores are calculated.
- **If your score is HIGHEST (or tied for highest):** You win the bet!
    - You score points for your cards **PLUS** a Color Bonus.
    - Other players score **ONLY** their Color Bonus (they do not score points from their cards).
- **If any opponent's score is HIGHER than yours:** You lose the bet!
    - You score **ONLY** your Color Bonus.
    - Other players score the full points from their cards.

### Special Case: Empty Deck
If the deck runs out of cards, the round ends immediately. No players score any points for that round.

---

## CARD TYPES & EFFECTS

### Duo Cards (Play a pair to get the effect)
- **Crabs (Pair):** Secretly look through a discard pile and take any card you want.
- **Boats (Pair):** Immediately take another full turn.
- **Fish (Pair):** Draw the top card from the deck.
- **Shark + Swimmer (Pair):** Steal a random card from an opponent's hand.

### Collector Cards
These cards score points based on how many you collect.
- Shells
- Octopus
- Penguins
- Sailors

### Bonus Cards
These cards help you earn the Color Bonus at the end of a round.
- **Mermaids (4 total):** If you play all 4 Mermaids, you **instantly win the game**.
- **Lighthouses** (Yellow)
- **Shoals of Fish** (Light Blue)
- **Penguin Colonies** (Dark Blue)
- **Captains** (Orange)

---

## SCORING SUMMARY
Points are calculated at the end of a round.

### Duo Card Scoring
- **Any pair of Duo cards** (Crabs, Boats, Fish, Shark+Swimmer) is worth **1 point**.

### Collector Card Scoring
- **Shells:** 1=0 pts, 2=2 pts, 3=4 pts, 4=6 pts, 5=8 pts, 6=10 pts.
- **Octopus:** 1=0 pts, 2=3 pts, 3=6 pts, 4=9 pts, 5=12 pts.
- **Penguins:** 1=1 pt, 2=3 pts, 3=5 pts.
- **Sailors:** 1=0 pts, 2=5 pts.

### Color Bonus Scoring
The Color Bonus is mainly scored when "LAST CHANCE" is called.
- To score a color, you must have the **most cards of that color** compared to all other players. Ties count, meaning all tied players get the bonus for that color.
- If you qualify, you score **1 point for each card** of that color.
- The colors are: **Lighthouses** (Yellow), **Shoals of Fish** (Light Blue), **Penguin Colonies** (Dark Blue), and **Captains** (Orange).
- **Mermaids and the Color Bonus:** Mermaids themselves are a color (Pink) but also enhance your bonus. For each Mermaid card you have, you get to score one of your qualifying color groups.
    - **1 Mermaid:** Score the bonus for your most numerous qualifying color.
    - **2 Mermaids:** Score the bonus for your two most numerous qualifying colors.
    - (And so on for 3 or 4 Mermaids).

"""