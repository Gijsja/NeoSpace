# Cat Factions & Social Dynamics

## The 10 Factions

Factions represent the philosophical and behavioral alignments of the CatNetwork. Each cat belongs to one faction, which heavily influences their dialogue style, PAD reactivity, and affinity thresholds.

1. **The Concrete Sentinels** – Hypervigilant, territorial. Guardians of boundaries.
2. **The Velvet Anarchs** – Mischievous, chaotic. Disruptors who love system errors.
3. **The Static Monks** – Zen, stoic. Minimized reaction to all stimulus.
4. **The Neon Claws** – Aggressive, dominant. Thrive on high energy and conflict.
5. **The Soft Collapse** – Sleepy, entropic. Seek rest and disengagement.
6. **The Peripheral Eye** – Anxious, paranoid. Constantly scanning for threats.
7. **The Bonded Mass** – Affectionate, collective. Value loyalty and proximity.
8. **The Cold Iteration** – Aloof, robotic. Efficient and sovereign.
9. **The Restless Grid** – Bored, overstimulated. Seek constant novelty.
10. **The Quiet Pressure** – Patient, subtle. Long-term influence over short-term action.

## Street Status (Affinity)

Affinity is a float value from `-100` (Severed) to `+100` (Ally). The system maps this score + your interaction count to a "Street Status" label.

**The Ladder:**
- **Tier 0**: Unknown / Stranger
- **Tier 1**: Just Met / Seen You Around
- **Tier 2**: Neutral / Cool With
- **Tier 3 (Positive)**: Solid -> Trusted -> OG -> Respected
- **Tier 3 (Negative)**: Weird Vibes -> Watching You -> Hostile -> Cut Off

## Dynamic Interactions

### 1. The PAD Model
Every interaction updates a cat's **Pleasure**, **Arousal**, and **Dominance**.
- **Pleasure**: Valence (Good/Bad).
- **Arousal**: Energy (High/Low).
- **Dominance**: Power (Dom/Sub).

### 2. Vocalization Maps
Cats have faction-specific "idle sounds" used when they aren't speaking English.
- *Sentinels*: "Hrm.", "Mrr."
- *Anarchs*: "Brrp!", "Pfft."
- *Monks*: "Mm.", "Prr."

### 3. Faction Logic
Factions interpret "Deeds" differently.
- **System Error**: Use +Pleasure for Anarchs (Chaos), -Pleasure for Sentinels (Order).
- **Timeout**: -Arousal (Boredom) for everyone, but Soft Collapse tolerates it best.
