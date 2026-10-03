"""Divisor Harmonics v0 -- FROZEN concepts, items and prompt templates (CC Brief 'Divisor Harmonics v0', Will 2026-10-03).
Frozen at the sealing commit; any change is a dated amendment. `{}` is the item slot; the item is always preceded by a
space inside the template (so the tokenizer sees ' January', ' 14:00', ' 7', ...). The position read is the LAST token of
the item (templates end with the item, so this is the last token of the prompt). 16 templates per concept.

Boundary conditions: months / hours / weekdays periodic; numbers open (lattice 0..99). Weekdays = PRIME CONTROL (N = 7).
Shuffled control: 12 common nouns in a fixed random order (seed 20261003), with neutral templates.
"""
import random

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
HOURS = [f"{h}:00" for h in range(24)]                      # 24 h format, no am/pm; '14:00' -> ' 14', ':', '00'
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
NUMBERS = [str(i) for i in range(100)]
_rng = random.Random(20261003)
_NOUNS = ["table", "river", "window", "garden", "pencil", "mountain", "bottle", "candle", "jacket", "mirror",
          "ladder", "basket"]
NOUNS = _NOUNS[:]; _rng.shuffle(NOUNS)                      # fixed order; it is NOT a cycle

# Templates. Months: every template names the calendar frame before the item (disambiguates 'May'; the paper's
# "The month of the year is [MONTH]" is template 0).
T_MONTHS = [
    "The month of the year is {}", "This happened in the month of {}", "The calendar month is {}",
    "Our meeting is scheduled for the month of {}", "The invoice is dated in the month of {}",
    "Her birthday falls in the month of {}", "The report covers the month of {}", "The next month on the calendar is {}",
    "Rent is due in the month of {}", "The festival is held every year in the month of {}",
    "Sales figures are listed for the month of {}", "The weather is typical for the month of {}",
    "The school term begins in the month of {}", "The photograph was taken in the month of {}",
    "The lease runs through the month of {}", "On the calendar, the month shown is {}",
]
T_HOURS = [
    "The time of day is {}", "The clock on the wall reads {}", "The train departs at {}", "The meeting starts at {}",
    "The alarm is set for {}", "The store opens at {}", "The current time is {}", "The shift begins at {}",
    "The flight lands at {}", "The broadcast airs at {}", "The time shown on the schedule is {}",
    "The appointment is booked for {}", "The ferry leaves the harbour at {}", "The lecture is timetabled for {}",
    "The gate closes at {}", "On the 24-hour clock the time is {}",
]
T_WEEKDAYS = [
    "The day of the week is {}", "Today is {}", "The meeting is on {}", "The delivery is expected on {}",
    "The shop is closed on {}", "The match is played on {}", "The class meets every {}", "Garbage is collected on {}",
    "The report is due on {}", "The next day of the week is {}", "The appointment is on {}",
    "The market is held every {}", "The deadline falls on {}", "The flight is booked for {}",
    "The weekly call takes place on {}", "On the calendar, the day shown is {}",
]
T_NUMBERS = [
    "The number is {}", "The value is {}", "The answer is {}", "The count came to {}", "The total is {}",
    "The score was {}", "The reading on the meter is {}", "The temperature is {}", "The page number is {}",
    "The room number is {}", "The quantity ordered is {}", "The result of the calculation is {}",
    "The jersey number is {}", "The bus route is number {}", "The next number in the list is {}",
    "The figure written on the card is {}",
]
T_NOUNS = [
    "The word is {}", "The object is a {}", "She pointed at the {}", "The item on the list is {}",
    "The next word is {}", "He wrote down the word {}", "The picture shows a {}", "The label says {}",
    "The thing in the box is a {}", "The clue was the word {}", "The card reads {}", "The missing item is the {}",
    "The teacher said the word {}", "The answer to the riddle is {}", "The last word spoken was {}",
    "On the card, the word shown is {}",
]

CONCEPTS = {
    #  name:      (items,    templates,  N,   boundary,   role)
    "months":    (MONTHS,   T_MONTHS,   12,  "periodic", "composite"),
    "hours":     (HOURS,    T_HOURS,    24,  "periodic", "composite"),
    "weekdays":  (WEEKDAYS, T_WEEKDAYS, 7,   "periodic", "prime_control"),
    "numbers":   (NUMBERS,  T_NUMBERS,  100, "open",     "composite"),
    "nouns":     (NOUNS,    T_NOUNS,    12,  "none",     "shuffled_control"),
}
for _k, (_it, _tp, _n, _b, _r) in CONCEPTS.items():
    assert len(_it) == _n and len(_tp) == 16 and all(t.endswith("{}") for t in _tp), _k

def prompts(name):
    items, tps, *_ = CONCEPTS[name]
    return [[t.format(it) for it in items] for t in tps]      # [template][item]
