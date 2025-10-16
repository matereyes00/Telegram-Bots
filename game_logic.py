# In game_logic.py

import re
from collections import defaultdict

# Points for collector cards based on count (index 0 is for 0 cards)
SHELL_POINTS = [0, 0, 2, 4, 6, 8, 10]
OCTOPUS_POINTS = [0, 0, 3, 6, 9, 12]
PENGUIN_POINTS = [0, 1, 3, 5]
SAILOR_POINTS = [0, 0, 5]

# Canonical names to handle user input variations (plural, typos, etc.)
CARD_MAP = {
    "crab": "crab", "crabs": "crab",
    "boat": "boat", "boats": "boat",
    "fish": "fish",
    "swimmer": "swimmer",
    "shark": "shark",
    "shell": "shell", "shells": "shell",
    "octopus": "octopus", "octopuses": "octopus",
    "penguin": "penguin", "penguins": "penguin",
    "sailor": "sailor", "sailors": "sailor",
    "lighthouse": "lighthouse",
    "shoal": "shoal", "shoal of fish": "shoal",
    "colony": "colony", "penguin colony": "colony",
    "captain": "captain",
}

def calculate_score(card_text: str):
    """Parses a string of cards and calculates the total score."""
    card_counts = defaultdict(int)
    
    # Simple regex to find "number card_name" patterns
    pattern = re.compile(r"(\d+)\s+([a-zA-Z\s]+)")
    matches = pattern.findall(card_text.lower())

    if not matches:
        return "Please list your cards in the format: `/score 2 crabs, 3 shells, 1 lighthouse`", {}

    for count, name in matches:
        name = name.strip()
        canonical_name = CARD_MAP.get(name)
        if canonical_name:
            card_counts[canonical_name] += int(count)

    total_score = 0
    score_breakdown = []

    # --- Calculate Score ---

    # 1. Collector Cards
    if "shell" in card_counts:
        count = min(card_counts["shell"], len(SHELL_POINTS) - 1)
        points = SHELL_POINTS[count]
        total_score += points
        score_breakdown.append(f"{count} Shells: {points} pts")

    if "octopus" in card_counts:
        count = min(card_counts["octopus"], len(OCTOPUS_POINTS) - 1)
        points = OCTOPUS_POINTS[count]
        total_score += points
        score_breakdown.append(f"{count} Octopuses: {points} pts")
        
    if "penguin" in card_counts:
        count = min(card_counts["penguin"], len(PENGUIN_POINTS) - 1)
        points = PENGUIN_POINTS[count]
        total_score += points
        score_breakdown.append(f"{count} Penguins: {points} pts")

    if "sailor" in card_counts:
        count = min(card_counts["sailor"], len(SAILOR_POINTS) - 1)
        points = SAILOR_POINTS[count]
        total_score += points
        score_breakdown.append(f"{count} Sailors: {points} pts")

    # 2. Duo Cards (1 point per pair)
    for card in ["crab", "boat", "fish"]:
        if card in card_counts:
            pairs = card_counts[card] // 2
            if pairs > 0:
                total_score += pairs
                score_breakdown.append(f"{pairs} pair(s) of {card.capitalize()}s: {pairs} pts")

    # 3. Multiplier Cards
    if "lighthouse" in card_counts and "boat" in card_counts:
        points = card_counts["lighthouse"] * card_counts["boat"]
        total_score += points
        score_breakdown.append(f"Lighthouse + Boats: {points} pts")

    if "shoal" in card_counts and "fish" in card_counts:
        points = card_counts["shoal"] * card_counts["fish"]
        total_score += points
        score_breakdown.append(f"Shoal + Fish: {points} pts")

    if "colony" in card_counts and "penguin" in card_counts:
        points = card_counts["colony"] * card_counts["penguin"] * 2
        total_score += points
        score_breakdown.append(f"Colony + Penguins: {points} pts")
        
    if "captain" in card_counts and "sailor" in card_counts:
        points = card_counts["captain"] * card_counts["sailor"] * 3
        total_score += points
        score_breakdown.append(f"Captain + Sailors: {points} pts")

    # --- Format final response ---
    if not score_breakdown:
        return "I couldn't find any scorable cards in your message. Try again! If you were trying to score a mermaid card, do it under /color_bonus. A Mermaid card's only role in scoring is to act as a key that unlocks your ability to claim a color bonus. The points from the bonus come from your colored cards, not from the Mermaid itself.", {}
        
    response_text = "Here's your score breakdown:\n"
    response_text += "\n".join(f"• {item}" for item in score_breakdown)
    response_text += f"\n\n**Total Score: {total_score}**"
    
    return response_text, card_counts

def calculate_color_bonus(card_text: str):
    """Parses a string of colors and mermaids to calculate the color bonus."""
    
    pattern = re.compile(r"(\d+)\s+([a-zA-Z]+)")
    matches = pattern.findall(card_text.lower())

    if not matches:
        # Return plain text with no backslashes
        return "Please list your cards by color count. \nExample: `/color-bonus 4 blue, 3 pink, 1 mermaid`"

    mermaid_count = 0
    color_counts = []

    for count_str, name in matches:
        count = int(count_str)
        if "mermaid" in name:
            mermaid_count = count
        else:
            color_counts.append(count)
    
    if mermaid_count == 0:
        return "You need at least **1 Mermaid** to score a color bonus."

    color_counts.sort(reverse=True)
    groups_to_score = min(mermaid_count, len(color_counts))
    
    if groups_to_score == 0:
        return f"You have **{mermaid_count} Mermaid(s)** but no colors listed. Your bonus is 0."

    final_scores = color_counts[:groups_to_score]
    total_bonus = sum(final_scores)

    breakdown = " + ".join(map(str, final_scores))
    # This string now returns plain text with parentheses
    response = (
        f"With **{mermaid_count} Mermaid(s)**, you score your top **{groups_to_score}** color group(s).\n"
        f"Calculation: {breakdown}\n\n"
        f"**Total Color Bonus: {total_bonus}**"
    )
    
    return response