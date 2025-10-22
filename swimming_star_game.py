"""Jeu narratif interactif : SwimmigStar.

Ce module propose une aventure textuelle dans laquelle SwimmigStar tente de
ranimer l'univers après avoir été projetée loin d'une cité céleste. Le joueur
peut choisir des actions, gérer l'énergie de l'héroïne et décider de suivre ou
non les conseils d'une entité mystérieuse.
"""
from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from typing import Callable, List, Sequence, Tuple


WRAP_WIDTH = 78


def print_wrapped(message: str) -> None:
    """Afficher un texte avec un retour à la ligne confortable pour le terminal."""
    if not message:
        print()
        return
    for paragraph in message.splitlines():
        if paragraph.strip():
            print(textwrap.fill(paragraph, WRAP_WIDTH))
        else:
            print()


@dataclass
class EnergyPool:
    """Représente la réserve d'énergie de SwimmigStar."""

    current: int
    maximum: int

    def can_spend(self, amount: int) -> bool:
        return self.current >= amount

    def spend(self, amount: int) -> bool:
        if amount < 0:
            raise ValueError("Le coût doit être positif.")
        if not self.can_spend(amount):
            self.current = 0
            return False
        self.current -= amount
        return True

    def restore(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("La restauration doit être positive.")
        self.current = min(self.maximum, self.current + amount)

    def is_depleted(self) -> bool:
        return self.current <= 0


@dataclass
class GameState:
    """État global du jeu."""

    energy: EnergyPool
    skills: List[str] = field(default_factory=list)
    allies: List[str] = field(default_factory=list)
    negative_influence: int = 0
    entity_presence: int = 3
    entity_trust: int = 0
    rest_count: int = 0


Choice = Tuple[str, Callable[[], None]]


def prompt_choice(question: str, choices: Sequence[Choice]) -> None:
    """Afficher une question et exécuter le gestionnaire correspondant au choix."""

    while True:
        print_wrapped(question)
        for index, (label, _) in enumerate(choices, start=1):
            print(f"  {index}. {label}")
        try:
            raw = input("> ").strip()
        except EOFError:
            farewell()
        if raw.lower() in {"quit", "exit"}:
            farewell()
        if not raw.isdigit():
            print_wrapped("Entre le numéro correspondant à ton choix.")
            continue
        value = int(raw)
        if not 1 <= value <= len(choices):
            print_wrapped("Choix invalide, essaie encore.")
            continue
        _, handler = choices[value - 1]
        handler()
        break


def farewell() -> None:
    print_wrapped("SwimmigStar replie ses rayons pour un temps. À bientôt.")
    raise SystemExit


def check_energy(state: GameState) -> None:
    """Terminer la partie si l'énergie est épuisée."""

    if state.energy.is_depleted():
        print()
        print_wrapped(
            "À force d'efforts, SwimmigStar s'éteint et dérive dans le vide. "
            "L'univers attendra un autre cycle pour se réveiller."
        )
        raise SystemExit


def rest(state: GameState, reason: str | None = None) -> None:
    state.rest_count += 1
    if reason:
        print_wrapped(reason)
    print_wrapped(
        "SwimmigStar se laisse flotter, recueillant les fragments de chaleur qui "
        "subsistent dans le vide."
    )
    before = state.energy.current
    state.energy.restore(4)
    after = state.energy.current
    gained = after - before
    if gained > 0:
        print_wrapped(
            f"Elle regagne {gained} point(s) d'énergie. Réserve actuelle : {after}/"
            f"{state.energy.maximum}."
        )
    else:
        print_wrapped("Son éclat est déjà à son zénith.")
    state.entity_presence = min(state.entity_presence + 1, 4)


def introduce_story(state: GameState) -> None:
    print_wrapped(
        "SwimmigStar dérive parmi les tours irisées d'une cité céleste lorsque "
        "l'onde d'une supernova la propulse loin de ses semblables. Les remparts "
        "de lumière disparaissent et ne restent plus que l'obscurité et le silence."
    )
    print()
    print_wrapped(
        "Pour rallumer le cosmos, elle devra tisser de nouvelles lueurs, mais "
        "chaque action consommera l'énergie qui pulse dans son cœur."
        " Heureusement, elle peut s'accorder du repos pour retrouver son souffle."
    )
    print()
    print_wrapped(
        "Une entité sage, changeante comme la marée des émotions, glisse jusqu'à "
        "elle et promet de rester à ses côtés au fil des réincarnations. "
        "SwimmigStar pourra choisir de l'écouter, de l'ignorer ou de lui demander "
        "de l'aide."
    )


def run_skill_tree(state: GameState) -> None:
    print()
    print_wrapped(
        "Les fragments de ses souvenirs forment un arbre de compétences. Chaque "
        "branche réclame une étincelle pour s'épanouir."
    )

    skills = {
        "solidarite": (
            "Éclat de Solidarité",
            "Projette un fil lumineux vers les alliées potentielles, facilitant les rencontres à venir.",
            2,
        ),
        "lullaby": (
            "Berceuse Résonante",
            "Apaise les mondes fatigués et rappelle aux planètes hostiles qu'elles peuvent changer.",
            2,
        ),
        "lantern": (
            "Lanternes de Guidage",
            "Trace des chemins sûrs à travers le néant pour retrouver son point d'ancrage.",
            3,
        ),
    }

    acquired = set()

    def learn(skill_key: str) -> None:
        if skill_key in acquired:
            print_wrapped("Cette branche brille déjà. SwimmigStar doit en choisir une autre.")
            return
        name, description, cost = skills[skill_key]
        if not state.energy.can_spend(cost):
            print_wrapped(
                "Sa lumière vacille : impossible d'alimenter cette branche pour le moment."
            )
            rest(state, "Elle prend le temps de reconstituer son énergie.")
            check_energy(state)
            return
        state.energy.spend(cost)
        acquired.add(skill_key)
        state.skills.append(name)
        print_wrapped(
            f"SwimmigStar nourrit la branche '{name}' et ressent la promesse suivante :"
        )
        print_wrapped(description)
        print_wrapped(
            f"Énergie restante : {state.energy.current}/{state.energy.maximum}."
        )
        check_energy(state)

    while True:
        finished = {"value": False}

        def continue_route() -> None:
            print_wrapped("Les branches continueront de veiller sur elle.")
            finished["value"] = True

        options: List[Choice] = []
        for key, (name, _, cost) in skills.items():
            options.append((f"Investir dans '{name}' (coût {cost})", lambda key=key: learn(key)))
        if acquired:
            options.append(("Continuer sa route", continue_route))
        options.append(("Se reposer", lambda: rest(state, None)))

        prompt_choice("Quelle branche de lumière activer ?", options)
        if finished["value"]:
            break
        check_energy(state)

    print_wrapped("Les branches vibrent doucement alors qu'elle s'éloigne de l'arbre.")


def encounter_cat_planet(state: GameState) -> None:
    print()
    print_wrapped(
        "Dans le néant, un éclat orange et blanc s'approche. Une planète striée de nuages "
        "abrite des chats qui ronronnent en chœur."
    )
    name = input("Comment SwimmigStar nomme-t-elle ce monde ? > ").strip()
    if not name:
        name = "Ronronia"
    print_wrapped(
        f"Les chats de {name} tissent un halo chaleureux autour de SwimmigStar. Leur "
        "compagnie augmente sa force."
    )
    state.allies.append(name)
    state.energy.restore(3)
    state.entity_presence = min(state.entity_presence + 1, 4)
    print_wrapped(
        f"Énergie : {state.energy.current}/{state.energy.maximum}. Alliées présentes : {', '.join(state.allies)}."
    )


@dataclass
class PlanetEncounter:
    name: str
    disposition: str
    description: str
    reward: int = 3
    penalty: int = 3

    @property
    def is_beneficial(self) -> bool:
        return self.disposition == "benefique"


def interact_with_planet(state: GameState, encounter: PlanetEncounter) -> None:
    print()
    print_wrapped(encounter.description)

    resolved = False

    def approach() -> None:
        nonlocal resolved
        if encounter.is_beneficial:
            state.allies.append(encounter.name)
            state.energy.restore(encounter.reward)
            print_wrapped(
                f"La planète {encounter.name} se rapproche et diffuse une chaleur "
                "régénératrice."
            )
            print_wrapped(
                f"Énergie : {state.energy.current}/{state.energy.maximum}."
            )
            resolved = True
        else:
            if not state.energy.can_spend(encounter.penalty):
                print_wrapped(
                    "La planète draine plus qu'elle ne le peut. SwimmigStar chancelle."
                )
                state.energy.spend(encounter.penalty)
                check_energy(state)
                return
            state.energy.spend(encounter.penalty)
            state.negative_influence += 1
            state.entity_presence = max(state.entity_presence - 1, 0)
            print_wrapped(
                f"{encounter.name} irradie une lumière épuisante. SwimmigStar perd {encounter.penalty} énergie."
            )
            print_wrapped(
                f"Réserve actuelle : {state.energy.current}/{state.energy.maximum}."
            )
            check_energy(state)
            prompt_choice(
                "Comment se libérer de cette attraction pénible ?",
                [
                    (
                        "Résister par ses propres moyens (coût 2)",
                        lambda: resist_exhausting_planet(state),
                    ),
                    (
                        "Demander l'aide d'une planète alliée",
                        lambda: call_allies_against_planet(state, encounter),
                    ),
                    ("Se reposer malgré la tension", lambda: rest(state, None)),
                ],
            )
            resolved = True

    def keep_distance() -> None:
        nonlocal resolved
        print_wrapped(
            "SwimmigStar reste à bonne distance, observant le monde tourner sans "
            "l'influencer pour l'instant."
        )
        resolved = True

    def ask_entity() -> None:
        consult_wise_entity(state, encounter)

    def take_rest() -> None:
        rest(state, None)

    prompt_choice(
        "Quelle approche adopter ?",
        [
            ("S'approcher", approach),
            ("Garder ses distances", keep_distance),
            ("Demander conseil à l'entité", ask_entity),
            ("Se reposer", take_rest),
        ],
    )

    if not resolved:
        resolved = True

    if encounter.is_beneficial and resolved:
        state.entity_trust += 1
    elif not encounter.is_beneficial and state.negative_influence > 0:
        state.entity_trust = max(state.entity_trust - 1, -3)


def resist_exhausting_planet(state: GameState) -> None:
    if not state.energy.can_spend(2):
        print_wrapped("Elle manque d'énergie pour rompre seule l'emprise. Elle doit se reposer.")
        rest(state, None)
        check_energy(state)
        return
    state.energy.spend(2)
    state.negative_influence = max(0, state.negative_influence - 1)
    print_wrapped(
        "En concentrant sa lueur intérieure, SwimmigStar fend l'étau du monde épuisant."
    )
    print_wrapped(
        f"Énergie restante : {state.energy.current}/{state.energy.maximum}."
    )
    check_energy(state)


def call_allies_against_planet(state: GameState, encounter: PlanetEncounter) -> None:
    if not state.allies:
        print_wrapped(
            "Aucune planète alliée n'est assez proche pour l'aider pour l'instant."
        )
        return
    ally = state.allies[0]
    state.allies = state.allies[1:]
    state.negative_influence = max(0, state.negative_influence - 1)
    state.entity_presence = min(state.entity_presence + 1, 4)
    print_wrapped(
        f"{ally} jaillit et détourne l'orbite de {encounter.name}, dissipant les "
        "ombres qu'elle projetait."
    )


def consult_wise_entity(state: GameState, encounter: PlanetEncounter | None = None) -> None:
    if state.entity_presence <= 0:
        print_wrapped(
            "SwimmigStar appelle, mais la voix de l'entité se perd dans le brouillard des mauvaises influences."
        )
        return

    state.entity_trust += 1
    guidance: List[str] = []
    if encounter is None:
        guidance.append(
            "Tu n'as pas besoin de brûler tout de suite. Observe, puis choisis ce qui nourrit ta lumière."
        )
    elif encounter.is_beneficial:
        guidance.append(
            "Ce monde chante sur la même fréquence que toi. Approche-toi sans crainte, mais reste attentive à ton souffle."
        )
    else:
        guidance.append(
            "Cette planète veut résoudre ses fractures avec tes forces. N'oublie pas de laisser des alliées te prêter main-forte."
        )
    if state.negative_influence > 1:
        guidance.append(
            "Les influences pesantes s'accumulent. Offre-toi du repos et rappelle une alliée si tu le peux."
        )
    print_wrapped("La voix de l'entité sage résonne :")
    for line in guidance:
        print_wrapped(f"  « {line} »")


def travel_among_planets(state: GameState) -> None:
    encounters = [
        PlanetEncounter(
            name="Chrysalis d'Aurore",
            disposition="benefique",
            description=(
                "Une sphère translucide pulse doucement. Chaque pulsation laisse "
                "échapper des spores de lumière qui cherchent une compagne."
            ),
        ),
        PlanetEncounter(
            name="Forteresse des Échos",
            disposition="epuisante",
            description=(
                "Un monde anguleux renvoie chaque rayon en un cri métallique. "
                "S'en approcher promet un dialogue difficile."
            ),
        ),
        PlanetEncounter(
            name="Compas Cristallin",
            disposition="benefique",
            description=(
                "Ses anneaux étincelants semblent capables de réaligner les étoiles "
                "elles-mêmes."),
        ),
        PlanetEncounter(
            name="Tourmente Obscure",
            disposition="epuisante",
            description=(
                "Un vortex de nuages sombres attire SwimmigStar dans une danse "
                "épuisante, alimentée par des murmures discordants."
            ),
        ),
    ]

    for encounter in encounters:
        interact_with_planet(state, encounter)
        check_energy(state)

    print_wrapped(
        "Entourée de mondes amis et attentive aux influences lourdes, SwimmigStar "
        "se sent prête à explorer d'autres formes d'existence."
    )


@dataclass
class ReincarnationStage:
    form_name: str
    narrative: str
    listening_effect: Callable[[GameState], None]
    impulse_effect: Callable[[GameState], None]
    help_effect: Callable[[GameState], None]


def reincarnation_journey(state: GameState) -> None:
    print()
    print_wrapped(
        "Pour comprendre l'origine de la vie et des émotions, SwimmigStar doit se "
        "réincarner en des formes de plus en plus petites."
    )

    stages: List[ReincarnationStage] = [
        ReincarnationStage(
            form_name="poussière d'étoile",
            narrative=(
                "Réduite à un grain scintillant, elle flotte librement, sensible au moindre souffle cosmique."
            ),
            listening_effect=lambda state: gain_clarity(state, 2),
            impulse_effect=lambda state: gamble_energy(state, gain=2, cost=1),
            help_effect=lambda state: bolster_presence(state),
        ),
        ReincarnationStage(
            form_name="goutte de lumière",
            narrative=(
                "Elle devient gouttelette suspendue au bord d'une comète, prête à "
                "ensemencer une nouvelle aurore."
            ),
            listening_effect=lambda state: gain_clarity(state, 2),
            impulse_effect=lambda state: gamble_energy(state, gain=3, cost=2),
            help_effect=lambda state: soothe_influences(state),
        ),
        ReincarnationStage(
            form_name="comète enfantine",
            narrative=(
                "Sous forme de comète, elle trace une trajectoire imprévisible, "
                "riant de ses propres étincelles."
            ),
            listening_effect=lambda state: gain_clarity(state, 3),
            impulse_effect=lambda state: gamble_energy(state, gain=4, cost=3),
            help_effect=lambda state: share_burden(state),
        ),
        ReincarnationStage(
            form_name="cellule vivante",
            narrative=(
                "Elle devient cellule, percevant la montée des premières émotions "
                "comme autant de signaux chimiques."
            ),
            listening_effect=lambda state: gain_clarity(state, 3),
            impulse_effect=lambda state: gamble_energy(state, gain=5, cost=4),
            help_effect=lambda state: weave_support(state),
        ),
        ReincarnationStage(
            form_name="humaine",
            narrative=(
                "Sous forme humaine, elle bâtit une ville inspirée par les histoires "
                "des mondes rencontrés, entourée de conseillers plus ou moins éclairés."
            ),
            listening_effect=lambda state: gain_clarity(state, 4),
            impulse_effect=lambda state: gamble_energy(state, gain=6, cost=5),
            help_effect=lambda state: orchestrate_alliance(state),
        ),
    ]

    for stage in stages:
        print()
        print_wrapped(
            f"SwimmigStar se condense en {stage.form_name}. {stage.narrative}"
        )

        def listen() -> None:
            if state.entity_presence <= 0:
                print_wrapped(
                    "L'entité est muette. SwimmigStar doit compter sur ce qu'elle a appris."
                )
                return
            print_wrapped("Elle écoute attentivement l'entité sage.")
            stage.listening_effect(state)

        def follow_impulse() -> None:
            print_wrapped("Elle suit son intuition, sans filtre.")
            stage.impulse_effect(state)

        def ask_help() -> None:
            if state.entity_presence <= 0:
                print_wrapped(
                    "Même réduite, l'entité ne parvient pas à se manifester. SwimmigStar ressent l'absence."
                )
                return
            print_wrapped("Elle demande une aide active à l'entité, qui se réincarne à ses côtés.")
            stage.help_effect(state)

        def take_rest() -> None:
            rest(state, None)

        prompt_choice(
            "Comment avancer dans cette forme ?",
            [
                ("Écouter l'entité", listen),
                ("Suivre son impulsion", follow_impulse),
                ("Demander de l'aide", ask_help),
                ("Se reposer", take_rest),
            ],
        )
        check_energy(state)

    conclude_journey(state)


def gain_clarity(state: GameState, amount: int) -> None:
    state.entity_trust += 1
    state.energy.restore(amount)
    state.entity_presence = min(state.entity_presence + 1, 4)
    print_wrapped(
        f"La clarté jaillit. Énergie : {state.energy.current}/{state.energy.maximum}."
    )


def gamble_energy(state: GameState, gain: int, cost: int) -> None:
    if state.energy.can_spend(cost):
        state.energy.spend(cost)
        print_wrapped(
            f"Le pari consomme {cost} énergie."
        )
        state.energy.restore(gain)
        print_wrapped(
            f"La chance sourit : {gain} énergie retrouvée. {state.energy.current}/{state.energy.maximum}."
        )
    else:
        print_wrapped(
            "L'effort est trop grand : SwimmigStar glisse et perd ses forces restantes."
        )
        state.energy.spend(cost)
        check_energy(state)


def bolster_presence(state: GameState) -> None:
    state.entity_presence = min(state.entity_presence + 2, 4)
    state.energy.restore(1)
    print_wrapped(
        "L'entité tisse un voile protecteur, renforçant sa présence autour de SwimmigStar."
    )
    print_wrapped(
        f"Énergie : {state.energy.current}/{state.energy.maximum}."
    )


def soothe_influences(state: GameState) -> None:
    state.negative_influence = max(0, state.negative_influence - 1)
    state.energy.restore(2)
    print_wrapped(
        "Les influences pesantes s'apaisent comme des vagues calmées par une brise lumineuse."
    )


def share_burden(state: GameState) -> None:
    if state.allies:
        ally = state.allies[-1]
        print_wrapped(
            f"{ally} accepte de partager la charge émotionnelle de cette transformation."
        )
        state.energy.restore(3)
    else:
        print_wrapped(
            "Aucune alliée n'est assez proche, mais l'entité soutient SwimmigStar de toutes ses forces."
        )
        state.energy.restore(1)


def weave_support(state: GameState) -> None:
    gained_allies = []
    if "Lanternes de Guidage" in state.skills:
        gained_allies.append("Lanterniers du Néant")
    if "Berceuse Résonante" in state.skills:
        gained_allies.append("Chorale des Calmes")
    state.allies.extend(gained_allies)
    state.energy.restore(3)
    if gained_allies:
        print_wrapped(
            "Les compétences acquises appellent de nouvelles présences bienveillantes : "
            + ", ".join(gained_allies)
        )
    else:
        print_wrapped(
            "SwimmigStar se forge seule sa résilience, gagnant tout de même en énergie."
        )


def orchestrate_alliance(state: GameState) -> None:
    gained = max(1, len(state.allies))
    state.energy.restore(gained)
    state.entity_trust += 1
    print_wrapped(
        "Dans sa forme humaine, SwimmigStar organise un conseil de mondes alliés. "
        f"Chaque voix sincère lui rend {gained} énergie au total."
    )


def conclude_journey(state: GameState) -> None:
    print()
    print_wrapped(
        "Au cœur de la ville qu'elle bâtit, SwimmigStar allume un phare rassemblant "
        "toutes les lueurs rencontrées."
    )
    print_wrapped(
        "L'entité sage, désormais plus claire, sourit : "
        "« Tes décisions ont sculpté la lumière qui nous entoure. »"
    )
    print_wrapped(
        f"Énergie finale : {state.energy.current}/{state.energy.maximum}. Alliées : {len(state.allies)}."
    )
    if state.negative_influence == 0:
        print_wrapped(
            "Les mauvaises influences se sont dissipées : l'univers renaît dans un éclat serein."
        )
    else:
        print_wrapped(
            "Quelques ombres demeurent, mais SwimmigStar sait désormais comment les éclairer."
        )
    print_wrapped("Merci d'avoir guidé SwimmigStar dans sa traversée.")


def main() -> None:
    state = GameState(energy=EnergyPool(current=10, maximum=12))
    introduce_story(state)
    run_skill_tree(state)
    encounter_cat_planet(state)
    travel_among_planets(state)
    reincarnation_journey(state)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        farewell()
