#!/usr/bin/env python3
"""Terminal Wordle — 6 guesses, color-coded feedback, daily word + free play."""

import sys
import json
import hashlib
from datetime import date
from pathlib import Path

# ── color helpers ────────────────────────────────────────────────────────────

GREEN  = "\033[42m\033[30m"
YELLOW = "\033[43m\033[30m"
GRAY   = "\033[100m\033[97m"
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

def cell(char, color):
    return f"{color} {char.upper()} {RESET}"

# ── word list ────────────────────────────────────────────────────────────────

WORDS = """
about above abuse actor acute admit adopt adult after again agent agree ahead
alarm album alert alien align alike alibi allay alley allot allow alone along
aloof aloud altar alter angel anger angle angry anime annex antic anvil apart
apple apply aptly argue arise armor arose array aside asset atone attic audio
audit augur avail avoid awake aware awful badly baker basic basis baste batch
beach beady beard beast began begin being below bench berth beset bevel birch
bison black blade blame bland blank blaze bleak bleat bleed blend bless blimp
blind bliss block blood bloom blown bluff blunt blush board bonus booby boost
booth botch bough bound boxer brace braid brake brand brave brawn bread break
breed brick bride bring brisk broad broke brook brood broom broth brown brunt
brush budge build built bulge bulky bully bunch burst byway cabin camel candy
cargo carry cause chalk champ chaos charm chart chase cheap cheat check cheek
cheer chess chest chief china choir choke chord civic civil claim clamp clang
clash clasp clean clear cleft clerk click cliff clink cloak clock clone close
cloth cloud clown cluck clump coast cobra comet comic comma coral couch cough
could count court cover crack craft cramp crane crash creak cream creek creep
crest crisp croak cross crowd crown cruel crush crust crypt cubic curly curve
cycle daisy dance dandy darts decay decal decor delay delta depot derby deter
digit diner dinky dirge dirty disco ditch diver dizzy dodge dogma doing dolly
dough draft drain drama drape drawl drawn dread dream dress dried drift drill
drink drive droop drove drown druid dryer duped dusty dwarf dying eager early
earth eight elite elbow elder emcee ember enjoy enter envy epoxy equip erupt
essay etude evade event every exact exert exude fable facet fatal feast fetch
fever fiber filly flair flame flank flare flash flask flawy flesh flick fling
flint flock flood floor floss flout flown fluid flunk flute focal folio folly
force forge forgo forge forte forum found fount frame frank fraud freak freak
fresh friar frisk fritz front froth froze frugal fully fungi funky funny fussy
gamer gamma gaudy gecko getup ghost giant giddy girth given gland glare gleam
glide glint gloat gloop gloss glove glyph golem goody grace grade grain grant
grasp graze greed greet grief grill grimy gripe groan groin groom grope gross
group grout grove growl gruel gruff grunt guile guise gusto hairy halve handy
hasty haven hazel heady heart heave heavy hedge heist hence hertz hilly hinge
hippo hokey holly honor hoppy horde hound hover humid husky hutch hyper icing
idiom idiot idyll impel inept infer inlay inner inter intro ivory jaunt jazzy
jerky jewel jiffy joust jokey jumbo jumpy juror kayak kebab kneel knelt knife
knoll known label lance latch latte layer leapt leash ledge lefty legal lemon
level libel light lilac limit linen liver llama loamy lodge lofty login lotus
lousy lower lumpy lunar lusty lyric magic magma maize manor march marsh matte
maxim melee mercy merit messy mimic mirth misty mitre model mogul moldy mommy
money moose moray morph mossy motif muddy mummy naive natal naval navel nerdy
nerve never nicer ninja ninny nitwit noble noble nomad nonce noose north notch
novel nudge nymph occur offal olive ombre onset overt oxide oxide ozone paddy
paint panic pansy pasty patch patty pause peach peeve petal petty phase phony
piano pilot pinky pixel pixie plaid plain plait plank plant plaza plead pleat
pluck plumb plump plunge poach point poker polyp poppy porky pouch pouty power
prank prawn preen press price pride prime primo primp print prism privy prize
probe prone proof prose proud prove prowl proxy prude prune psalm psyche pudgy
pulse punch pupil purge pushy pygmy query quill quirk quota quote rabbi radar
radon raise rally ranch raven reach realm rebel rebus recap recut reedy reign
relax repay repel rerun resin retch retro retry revel rider ridge ripen rivet
risky rival rivet roast robot rogue rocky rouge rough round rowdy royal rugby
ruler rupee rusty sadly saint salsa sassy sauce savvy scald scalp scaly scalp
scant scare scarf scary scene scoff scone scoop scope scour scowl scram scrap
screw scrub seedy seize senna sense serum setup seven shack shake shall shaky
shale shame shank shape share shark sharp shawl sheen sheep sheer shelf shell
shift shine shire shirt shoal shock shore shout shove showy shrub shrug shunt
siege siren sixth sixty sixty skate skiff skimp skirt skulk skunk slack slain
slang slant slash sleek sleet slept slice slick slime slimy sling slink slope
slosh sloth slump slunk slurp smack smart smear smell smelt smile smirk smite
smoke smoky snack snaky snare snark sneak sniff snore snort snout snowy snuck
snuff solar solve sooth sorry south sowed space spare spark spawn speak speck
speed spend spice spicy spill spine spire spite splat split spoke spoon spore
sport spout spray spree sprig spunk spurn squad squat squib stack staff stage
stain stale stalk stall stand stank stash stave steak steal steam steep steer
stern stiff still sting stink stock stoic stomp stony stood stoop storm story
stout stomp strap straw stray strip strut stuck study stump stunt style suave
suede suite sulky sunny super surge swamp swank swarm swath swear sweat sweep
sweet swept swill swipe swirl swoop sword taboo taffy tangy tapir tardy taunt
tawny tease tempo tense tepid terse thank thatch thaw their there thick thief
thing think thorn those thump tiara tidal tiger tilde tinge tipsy titan today
token tonic topaz total touch tough towel toxic trail train trait tramp trash
trawl tread treat trend triad trial tribe trick tried tripe troll tromp troop
trope troth trout trove truce truck truly trump trunk truss tryst tulip tuner
tunic turbo tutor tweak tweed twice twill twirl twist tying ulcer unfit unity
until unzip upset usher utter uvula vague valid value valve vapor vault vaunt
venom verse vicar vigil vigor visor vital vivid vodka vogue voice voila voter
vouch vying wacky waltz waver weary wedge weedy weird whelp whiff whirl whisk
white whole wispy witty woozy world worse worst wrath wring wrist wrote yacht
yearn yokel young zappy zesty zippy
""".split()

WORDS = sorted(set(w for w in WORDS if len(w) == 5))

# ── scoring ──────────────────────────────────────────────────────────────────

def score_guess(guess, answer):
    """Return list of (char, color) for each position."""
    result = [None] * 5
    answer_remaining = list(answer)

    # green pass
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            result[i] = (g, GREEN)
            answer_remaining[i] = None

    # yellow / gray pass
    for i, g in enumerate(guess):
        if result[i] is not None:
            continue
        if g in answer_remaining:
            result[i] = (g, YELLOW)
            answer_remaining[answer_remaining.index(g)] = None
        else:
            result[i] = (g, GRAY)

    return result

# ── keyboard tracker ─────────────────────────────────────────────────────────

KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]

def render_keyboard(used):
    lines = []
    for row in KEYBOARD_ROWS:
        parts = []
        for ch in row:
            color, _ = used.get(ch, (None, 0))
            if color:
                parts.append(cell(ch, color))
            else:
                parts.append(f" {ch.upper()} ")
        lines.append("  " + " ".join(parts))
    return "\n".join(lines)

COLOR_PRIORITY = {GREEN: 3, YELLOW: 2, GRAY: 1, None: 0}

def update_keyboard(used, scored):
    for ch, color in scored:
        _, prev_priority = used.get(ch, (None, 0))
        if COLOR_PRIORITY[color] > prev_priority:
            used[ch] = (color, COLOR_PRIORITY[color])

# ── stats ────────────────────────────────────────────────────────────────────

STATS_FILE = Path(__file__).parent / "stats.json"

def load_stats():
    if STATS_FILE.exists():
        return json.loads(STATS_FILE.read_text())
    return {"played": 0, "won": 0, "streak": 0, "best_streak": 0,
            "distribution": {str(i): 0 for i in range(1, 7)},
            "last_win_date": ""}

def save_stats(stats):
    STATS_FILE.write_text(json.dumps(stats, indent=2))

def record_result(stats, won, attempts):
    today = str(date.today())
    stats["played"] += 1
    if won:
        stats["won"] += 1
        stats["distribution"][str(attempts)] += 1
        if stats["last_win_date"] == str(date.today().replace(day=date.today().day - 1)):
            stats["streak"] += 1
        else:
            stats["streak"] = 1
        stats["best_streak"] = max(stats["streak"], stats["best_streak"])
        stats["last_win_date"] = today
    else:
        stats["streak"] = 0
    save_stats(stats)

def print_stats(stats):
    print(f"\n{BOLD}── Your stats ──{RESET}")
    print(f"  Played: {stats['played']}  Won: {stats['won']}  "
          f"Streak: {stats['streak']}  Best: {stats['best_streak']}")
    print(f"\n{BOLD}Guess distribution:{RESET}")
    total = max(sum(stats["distribution"].values()), 1)
    for n in range(1, 7):
        count = stats["distribution"][str(n)]
        bar = "█" * max(1, round(20 * count / total)) if count else ""
        print(f"  {n}: {bar} {count}")

# ── daily word ───────────────────────────────────────────────────────────────

def daily_word():
    seed = hashlib.md5(str(date.today()).encode()).digest()
    idx = int.from_bytes(seed[:4], "big") % len(WORDS)
    return WORDS[idx]

# ── main game loop ───────────────────────────────────────────────────────────

def play(answer):
    guesses = []
    used = {}  # char -> (color, priority)

    print(f"\n{BOLD}  ╔══════════════╗{RESET}")
    print(f"{BOLD}  ║  W O R D L E  ║{RESET}")
    print(f"{BOLD}  ╚══════════════╝{RESET}")
    print(f"{DIM}  Guess the 5-letter word in 6 tries.{RESET}")
    print(f"{DIM}  {cell('G',GREEN)} = right spot  "
          f"{cell('Y',YELLOW)} = wrong spot  "
          f"{cell('X',GRAY)} = not in word{RESET}\n")

    for attempt in range(1, 7):
        # render board
        for g in guesses:
            scored = score_guess(g, answer)
            print("  " + " ".join(cell(ch, color) for ch, color in scored))
        for _ in range(6 - len(guesses)):
            print("  " + " ".join(f"[ ]" for _ in range(5)))
        print()
        print(render_keyboard(used))
        print()

        # input
        while True:
            try:
                raw = input(f"  Guess {attempt}/6: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n  Quitting. Bye!")
                sys.exit(0)

            if len(raw) != 5:
                print(f"  {DIM}Enter a 5-letter word.{RESET}")
                continue
            if not raw.isalpha():
                print(f"  {DIM}Letters only.{RESET}")
                continue
            break

        scored = score_guess(raw, answer)
        guesses.append(raw)
        update_keyboard(used, scored)

        # clear screen for next render
        print("\033[2J\033[H", end="")

        if raw == answer:
            # final board
            for g in guesses:
                sc = score_guess(g, answer)
                print("  " + " ".join(cell(ch, color) for ch, color in sc))
            print()
            msgs = ["Genius!", "Magnificent!", "Impressive!", "Splendid!", "Great!", "Phew!"]
            print(f"\n  {BOLD}{msgs[attempt - 1]}{RESET}  Solved in {attempt} guess{'es' if attempt > 1 else ''}.\n")
            return True, attempt

    # loss
    for g in guesses:
        sc = score_guess(g, answer)
        print("  " + " ".join(cell(ch, color) for ch, color in sc))
    print(f"\n  The word was {BOLD}{answer.upper()}{RESET}.\n")
    return False, 6

# ── entry point ──────────────────────────────────────────────────────────────

def main():
    free_play = "--free" in sys.argv or "-f" in sys.argv
    answer = WORDS[int(sys.argv[sys.argv.index("--word") + 1])] \
        if "--word" in sys.argv else \
        (WORDS[hash(sys.argv[sys.argv.index("-r") + 1]) % len(WORDS)] \
        if "-r" in sys.argv else daily_word())

    if free_play:
        import random
        answer = random.choice(WORDS)

    print("\033[2J\033[H", end="")  # clear screen
    stats = load_stats()
    won, attempts = play(answer)
    record_result(stats, won, attempts)
    print_stats(stats)
    print()

if __name__ == "__main__":
    main()
