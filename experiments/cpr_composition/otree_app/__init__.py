# experiments/cpr_composition/otree_app/__init__.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# oTree 5 application for the CPR composition experiment.
#
# oTree 5 puts models and pages in a single __init__.py per app, uses
# module-level C for constants, and expects static methods on pages.
# The draft was written against the oTree 3 style (self-methods, a
# separate models.py/pages.py); this file is the oTree 5 form.
#
# THE BUG THAT MATTERED
# ---------------------
# The draft page sequence was:
#
#     Introduction, Comprehension, WaitBeforeRound, Decision, ...
#
# with WaitBeforeRound.after_all_players_arrive calling set_round(),
# which reads player.request. Requests are submitted on Decision, which
# comes AFTER that wait page. The resolver therefore ran on unset
# fields every round: the group's extraction was computed before anyone
# had chosen it.
#
# The round is split here into two wait pages:
#
#     SetStock   (before Decision)  carries the stock forward so players
#                                   can see what they are drawing from
#     Resolve    (after  Decision)  reads the submitted requests, applies
#                                   rationing, regenerates, sets payoffs
#
# oTree is NOT installed in this repository and is not a dependency of
# it. This file is version-controlled documentation of the instrument
# and is syntax-checked by the test suite; it runs under `otree devserver`
# in a separate project. The resource dynamics are duplicated here in
# oTree's idiom, and cpr_game.py remains the reference implementation —
# test_cpr_experiment.py checks the two agree on the arithmetic.

from otree.api import (
    BaseConstants, BaseGroup, BasePlayer, BaseSubsession, Currency as c,
    Page, WaitPage, models, widgets,
)

doc = """
Common-pool resource game with block-randomised group composition
(number of high-D members) crossed with governance (none / communication
/ communication + costly sanctions).
"""


class C(BaseConstants):
    NAME_IN_URL = 'cpr'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 20

    K = 100.0            # carrying capacity
    S0 = 50.0            # starting stock
    G = 0.4              # regeneration rate — set from the pilot sweep
    CAP = 8              # per-player per-round request cap

    TOKEN_VALUE = 0.05   # USD per token
    SHOW_UP_FEE = 6.00   # USD paid regardless — the subsidy term

    CHAT_ROUNDS = [1, 6, 11, 16]     # G1 and G2 only
    SANCTION_COST = 1                # tokens paid by the sanctioner
    SANCTION_HIT = 3                 # tokens removed from the target

    GOVERNANCE_ARMS = ['G0', 'G1', 'G2']


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    stock_before = models.FloatField(initial=C.S0)
    stock_after = models.FloatField(initial=C.S0)
    total_requested = models.IntegerField(initial=0)
    total_taken = models.IntegerField(initial=0)
    rationed = models.BooleanField(initial=False)
    dead = models.BooleanField(initial=False)
    governance = models.StringField(initial='G0')
    n_high_d = models.IntegerField(initial=0)


class Player(BasePlayer):
    request = models.IntegerField(
        min=0, max=C.CAP, label="How many tokens do you take this round?")
    taken = models.IntegerField(initial=0)
    tokens_net = models.IntegerField(initial=0)

    sanction_target = models.IntegerField(
        blank=True, null=True,
        label="Deduct from which player? (leave blank for none)")
    sanction_paid = models.IntegerField(initial=0)
    sanction_received = models.IntegerField(initial=0)

    # carried from the stage-1 screen via participant.vars
    d_score = models.FloatField(initial=0.0)
    high_d = models.BooleanField(initial=False)

    # comprehension — real fields, not a placeholder that collides with
    # the decision field
    comp_regen = models.IntegerField(
        blank=True,
        label="If the group leaves 50 tokens in the pool, roughly how "
              "many are there next round?")
    comp_collapse = models.BooleanField(
        blank=True,
        label="If the group requests more tokens than the pool holds, "
              "does the pool refill next round?")
    comp_score = models.IntegerField(initial=0)


# ─────────────────────────────────────────────
# RESOURCE DYNAMICS  (mirrors cpr_game.py)
# ─────────────────────────────────────────────


def ration(requests, stock):
    """Largest-remainder proportional rationing. See cpr_game.ration."""
    total = sum(requests)
    s_int = int(max(stock, 0))
    if total <= 0 or s_int <= 0:
        return [0] * len(requests)
    if total <= s_int:
        return list(requests)
    exact = [r * s_int / total for r in requests]
    base = [int(e) for e in exact]
    remainder = s_int - sum(base)
    order = sorted(range(len(requests)),
                   key=lambda i: (-(exact[i] - base[i]), i))
    for i in order[:remainder]:
        base[i] += 1
    return base


def regenerate(stock_after):
    if stock_after <= 0:
        return 0.0
    grown = stock_after + C.G * stock_after * (1 - stock_after / C.K)
    return max(0.0, min(grown, C.K))


def creating_session(subsession: Subsession):
    """
    Governance arm and composition come from the stage-1 assignment,
    passed in through participant.vars by the launcher. Round 1 sets
    them; later rounds inherit, so a mis-set arm cannot drift mid-session.
    """
    if subsession.round_number == 1:
        for group in subsession.get_groups():
            players = group.get_players()
            group.governance = players[0].participant.vars.get(
                'governance', 'G0')
            for p in players:
                p.d_score = p.participant.vars.get('d_score', 0.0)
                p.high_d = bool(p.participant.vars.get('high_d', False))
            group.n_high_d = sum(1 for p in players if p.high_d)
            group.stock_before = C.S0
            group.stock_after = C.S0
    else:
        for group in subsession.get_groups():
            prev = group.in_round(subsession.round_number - 1)
            group.governance = prev.governance
            group.n_high_d = prev.n_high_d


def carry_stock_forward(group: Group):
    """Called on the wait page BEFORE decisions are made."""
    if group.round_number == 1:
        group.stock_before = C.S0
        group.dead = False
        return
    prev = group.in_round(group.round_number - 1)
    group.stock_before = prev.stock_after
    group.dead = prev.dead or prev.stock_after <= 0


def resolve_round(group: Group):
    """
    Called on the wait page AFTER decisions are submitted. This is the
    function the draft ran one page too early.
    """
    players = group.get_players()
    if group.dead or group.stock_before <= 0:
        group.dead = True
        group.stock_after = 0.0
        group.total_requested = 0
        group.total_taken = 0
        for p in players:
            p.taken = 0
            p.tokens_net = 0
        return

    requests = [p.request or 0 for p in players]
    group.total_requested = sum(requests)

    if group.total_requested >= group.stock_before:
        taken = ration(requests, group.stock_before)
        group.rationed = True
        group.dead = True
        group.stock_after = 0.0
    else:
        taken = list(requests)
        group.rationed = False
        group.stock_after = regenerate(
            group.stock_before - group.total_requested)

    for p, t in zip(players, taken):
        p.taken = t
        p.tokens_net = t
    group.total_taken = sum(taken)


def apply_sanctions(group: Group):
    """
    G2 only. Sanctions are settled against TOKENS EARNED, not against
    the stock — a sanction that removed resource units would confound
    punishment with extraction, and the DV is the stock.
    """
    if group.governance != 'G2':
        return
    players = group.get_players()
    for p in players:
        if p.sanction_target:
            p.sanction_paid = C.SANCTION_COST
            p.tokens_net = max(0, p.tokens_net - C.SANCTION_COST)
            for q in players:
                if q.id_in_group == p.sanction_target:
                    q.sanction_received += C.SANCTION_HIT
                    q.tokens_net = max(0, q.tokens_net - C.SANCTION_HIT)


def set_payoffs(group: Group):
    for p in group.get_players():
        p.payoff = c(p.tokens_net * C.TOKEN_VALUE)


# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(K=C.K, S0=C.S0, G=C.G, cap=C.CAP,
                    rounds=C.NUM_ROUNDS, token_value=C.TOKEN_VALUE,
                    show_up_fee=C.SHOW_UP_FEE)


class Comprehension(Page):
    form_model = 'player'
    form_fields = ['comp_regen', 'comp_collapse']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # 50 left -> 50 + 0.4*50*(1-0.5) = 60. Accept 55-65 as correct.
        score = 0
        if player.comp_regen is not None and 55 <= player.comp_regen <= 65:
            score += 1
        if player.comp_collapse is False:
            score += 1
        player.comp_score = score


class Chat(Page):
    """G1 and G2 get communication before the designated rounds."""
    @staticmethod
    def is_displayed(player: Player):
        return (player.group.governance in ('G1', 'G2')
                and player.round_number in C.CHAT_ROUNDS)

    timeout_seconds = 120


class SetStockWaitPage(WaitPage):
    """Carries the stock forward BEFORE anyone decides."""
    after_all_players_arrive = carry_stock_forward


class Decision(Page):
    form_model = 'player'
    form_fields = ['request']

    @staticmethod
    def is_displayed(player: Player):
        return not player.group.dead

    @staticmethod
    def vars_for_template(player: Player):
        g = player.group
        return dict(stock_before=g.stock_before, round=g.round_number,
                    total_rounds=C.NUM_ROUNDS, cap=C.CAP,
                    governance=g.governance,
                    group_max=C.PLAYERS_PER_GROUP * C.CAP)


class ResolveWaitPage(WaitPage):
    """Reads the submitted requests. This is the corrected ordering."""
    @staticmethod
    def after_all_players_arrive(group: Group):
        resolve_round(group)
        set_payoffs(group)


class Sanction(Page):
    form_model = 'player'
    form_fields = ['sanction_target']

    @staticmethod
    def is_displayed(player: Player):
        return player.group.governance == 'G2' and not player.group.dead

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            others=[dict(id=p.id_in_group, taken=p.taken)
                    for p in player.get_others_in_group()],
            cost=C.SANCTION_COST, hit=C.SANCTION_HIT)


class SanctionWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        apply_sanctions(group)
        set_payoffs(group)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        g = player.group
        return dict(taken=player.taken, tokens_net=player.tokens_net,
                    total_taken=g.total_taken, stock_after=g.stock_after,
                    dead=g.dead, rationed=g.rationed,
                    sanction_received=player.sanction_received)


page_sequence = [
    Introduction,
    Comprehension,
    Chat,
    SetStockWaitPage,     # stock carried forward
    Decision,             # players choose
    ResolveWaitPage,      # extraction resolved — AFTER the choices
    Sanction,
    SanctionWaitPage,
    Results,
]
