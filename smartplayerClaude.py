
import random
import time as _time

from player import Player

SIZE = 19
EMPTY = -1  # empty value in the external board representation

# --------------------------------------------------------------------------
# Padded internal board
# --------------------------------------------------------------------------
PAD = 4
W = SIZE + 2 * PAD
AREA = W * W

B_BLACK, B_WHITE, B_EMPTY, B_EDGE = 0, 1, 2, 3

AXES = (1, W, W + 1, W - 1)
DIRS8 = (1, -1, W, -W, W + 1, -W - 1, W - 1, -W + 1)

BOX1 = tuple(dr * W + dc for dr in (-1, 0, 1) for dc in (-1, 0, 1))
BOX2 = tuple(dr * W + dc for dr in range(-2, 3) for dc in range(-2, 3))

INTERIOR = tuple(
    (r + PAD) * W + (c + PAD) for r in range(SIZE) for c in range(SIZE)
)


def _build_lines():
    """Every straight line of length >= 5, as (start, step, length) slices.

    ``start`` is backed up two cells into the padding and ``length`` extended by
    four, so each slice carries two sentinel cells at both ends.  That lets the
    pattern matcher treat "blocked by the wall" and "blocked by a stone" with the
    same machinery.
    """
    lines = []
    for step, (dr, dc) in ((1, (0, 1)), (W, (1, 0)), (W + 1, (1, 1)), (W - 1, (1, -1))):
        for r in range(SIZE):
            for c in range(SIZE):
                pr, pc = r - dr, c - dc
                if 0 <= pr < SIZE and 0 <= pc < SIZE:
                    continue  # not the first cell of this line
                n = 0
                rr, cc = r, c
                while 0 <= rr < SIZE and 0 <= cc < SIZE:
                    n += 1
                    rr += dr
                    cc += dc
                if n < 5:
                    continue
                start = (r + PAD) * W + (c + PAD) - 2 * step
                lines.append((start, step, n + 4))
    return tuple(lines)


LINES = _build_lines()
NLINES = len(LINES)

_cell_lines = [[] for _ in range(AREA)]
for _li, (_start, _step, _n) in enumerate(LINES):
    for _k in range(2, _n - 2):
        _cell_lines[_start + _k * _step].append(_li)
CELL_LINES = tuple(tuple(v) for v in _cell_lines)
del _cell_lines

_T_MINE_BLACK = bytes.maketrans(bytes((B_BLACK, B_WHITE, B_EMPTY, B_EDGE)), b"xo-#")
_T_MINE_WHITE = bytes.maketrans(bytes((B_BLACK, B_WHITE, B_EMPTY, B_EDGE)), b"ox-#")

_THREAT = (
    (b"-xxxx-", 100000),                                    # open four: wins
    (b"xxxx-", 12000), (b"-xxxx", 12000),                   # four
    (b"xx-xx", 12000), (b"x-xxx", 12000), (b"xxx-x", 12000),  # split four
    (b"-xxx-", 5000),                                       # open three
    (b"-x-xx-", 3500), (b"-xx-x-", 3500),                   # broken three
    (b"xxx-", 500), (b"-xxx", 500),                         # closed three
    (b"-xx-", 300),                                         # open two
    (b"-x-x-", 180),
    (b"xxxxxx", -40000),                                    # six never wins
)

_WIN = 10 ** 9
_INF = 10 ** 12

# Branching factor per ply; deeper plies look at fewer moves.
_WIDTH = (16, 10, 8, 6, 6, 5, 5, 4, 4)

# Local shape values for move ordering: (stones in the run, open ends).
_RUN_SCORE = {
    (1, 0): 0, (1, 1): 2, (1, 2): 6,
    (2, 0): 3, (2, 1): 25, (2, 2): 80,
    (3, 0): 15, (3, 1): 200, (3, 2): 1500,
    (4, 0): 120, (4, 1): 9000, (4, 2): 45000,
}
_GAP = {1: 10, 2: 120, 3: 2500, 4: 30000}


class _Timeout(Exception):
    """Raised inside the search when the move budget is spent."""


class SmartPlayerClaude(Player):

    VULN_PENALTY = 1200
    CAP_VALUE = 1500       # per captured stone, in the static evaluation
    QUICK_CAP = 3000       # per captured stone, when ordering moves
    QUICK_VULN = 2400      # per pair left capturable, when ordering moves
    TIME_DIVISOR = 18.0    # share of the remaining clock to spend on one move
    TIME_CAP = 2.5

    def __init__(self, color, think_time=1.5, max_depth=8):
        super().__init__(color)
        self.think_time = think_time   # seconds used when no time limit is given
        self.max_depth = max_depth
        self._line_cache = {}
        self._rng = random.Random(0xC1A0DE)
        self._vulnerable = ((b"oxx-", -self.VULN_PENALTY),
                            (b"-xxo", -self.VULN_PENALTY))

    def _score_line(self, raw):
        """Score one line, from the point of view of whoever 'x' is."""
        blocked = raw.replace(b"#", b"o")
        total = 0
        for pat, val in _THREAT:
            n = blocked.count(pat)
            if n:
                total += n * val
        for pat, val in self._vulnerable:
            n = raw.count(pat)
            if n:
                total += n * val
        return total

    # ------------------------------------------------------------------
    # Player interface
    # ------------------------------------------------------------------
    def take_turn(self, board, time=-1):
        started = _time.monotonic()
        self._load(board)
        self.deadline = started + self._budget(time)
        self._nodes = 0

        pool = self._root_pool()
        if not pool:                                  # empty board
            centre = (SIZE // 2 + PAD) * W + (SIZE // 2 + PAD)
            if self.cells[centre] == B_EMPTY:
                return self._rc(centre)
            pool = [p for p in INTERIOR if self.cells[p] == B_EMPTY]
            if not pool:
                raise ValueError("take_turn called on a full board")

        me = self.color

        # Order the root once, then reuse that order to seed each deepening.
        scored = sorted(((self._quick(p, me), p) for p in pool), reverse=True)
        self._root_quick = {p: s for s, p in scored}
        ordered = [p for _, p in scored[: _WIDTH[0]]]
        for _, p in scored[_WIDTH[0]:]:
            if self._captures_at(p, me):
                ordered.append(p)

        # An outright win now needs no search at all.
        for p in ordered:
            status = self._make(p, me)
            self._unmake()
            if status == 1:
                return self._rc(p)

        best = ordered[0]
        for depth in range(2, self.max_depth + 1):
            try:
                move, best_value, values = self._root(depth, ordered)
            except _Timeout:
                break                                  # keep the last full depth
            best = move
            ordered = [p for _, p in sorted(values, reverse=True)]
            if abs(best_value) >= _WIN - 1000:
                break            # win found, or every move loses: nothing to add
            if _time.monotonic() > self.deadline:
                break
        return self._rc(best)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def _root(self, depth, ordered):
        me = self.color
        alpha = -_INF
        best = ordered[0]
        best_key = (-_INF, -1)
        best_value = -_INF
        values = []
        for p in ordered:
            status = self._make(p, me)
            if status == 1:
                value = _WIN
            elif status == 2:
                value = -_WIN
            elif status == 3:
                value = 0
            elif depth <= 1:
                value = self._static(me)
            else:
                value = -self._nega(depth - 1, -_INF, -alpha, 1 - me, 1)
            self._unmake()
            values.append((value, p))
            key = (value, self._root_quick.get(p, 0), self._rng.randint(0, 7))
            if key > best_key:
                best_key = key
                best = p
                best_value = value
            if value > alpha:
                alpha = value
        return best, best_value, values

    def _nega(self, depth, alpha, beta, color, ply):
        self._nodes += 1
        if not self._nodes & 127 and _time.monotonic() > self.deadline:
            raise _Timeout
        moves = self._gen(color, ply)
        if not moves:
            return self._static(color)
        best = -_INF
        for p in moves:
            status = self._make(p, color)
            if status == 1:
                value = _WIN - ply
            elif status == 2:
                value = -(_WIN - ply)
            elif status == 3:
                value = 0
            elif depth <= 1:
                value = self._static(color)
            else:
                value = -self._nega(depth - 1, -beta, -alpha, 1 - color, ply + 1)
            self._unmake()
            if value > best:
                best = value
                if value > alpha:
                    alpha = value
                    if alpha >= beta:
                        break
        return best

    def _static(self, color):
        if color == B_BLACK:
            score = self.sum_b - self.sum_w
        else:
            score = self.sum_w - self.sum_b
        return score + (self.caps[color] - self.caps[1 - color]) * self.CAP_VALUE

    # ------------------------------------------------------------------
    # Move generation
    # ------------------------------------------------------------------
    def _gen(self, color, ply):
        cells = self.cells
        nb1 = self.nb1
        pool = [p for p in INTERIOR if cells[p] == B_EMPTY and nb1[p]]
        if not pool:
            return []
        width = _WIDTH[ply] if ply < len(_WIDTH) else _WIDTH[-1]
        scored = sorted(((self._quick(p, color), p) for p in pool), reverse=True)
        moves = [p for _, p in scored[:width]]
        if ply <= 2:
            # A capture can end the game outright (it can hand the opponent a
            # five), so never let one fall off the end of the ordered list.
            extra = 0
            for _, p in scored[width:]:
                if self._captures_at(p, color):
                    moves.append(p)
                    extra += 1
                    if extra >= 4:
                        break
        return moves

    def _root_pool(self):
        cells = self.cells
        near = bytearray(AREA)
        found = False
        for p in INTERIOR:
            if cells[p] < B_EMPTY:
                found = True
                for off in BOX2:
                    near[p + off] = 1
        if not found:
            return []
        return [p for p in INTERIOR if cells[p] == B_EMPTY and near[p]]

    def _quick(self, p, color):
        """Rough value of playing ``color`` at ``p`` -- used for ordering only."""
        mine = B_BLACK if color == 0 else B_WHITE
        theirs = B_WHITE if color == 0 else B_BLACK
        score = self._shape(p, mine) + (self._shape(p, theirs) * 94) // 100
        score += self._captures_at(p, color) * self.QUICK_CAP
        score -= self._vulnerable_at(p, color) * self.QUICK_VULN
        return score

    def _shape(self, p, stone):
        """Value of the four lines through ``p`` if ``p`` held ``stone``."""
        cells = self.cells
        total = 0
        for d in AXES:
            run = 1
            ends = 0
            x = p + d
            while cells[x] == stone:
                run += 1
                x += d
            if cells[x] == B_EMPTY:
                ends += 1
                y = x + d
                gap = 0
                while cells[y] == stone:
                    gap += 1
                    y += d
                if gap:
                    total += _GAP.get(gap, 400)
            x = p - d
            while cells[x] == stone:
                run += 1
                x -= d
            if cells[x] == B_EMPTY:
                ends += 1
                y = x - d
                gap = 0
                while cells[y] == stone:
                    gap += 1
                    y -= d
                if gap:
                    total += _GAP.get(gap, 400)
            if run == 5:
                total += 500000
            elif run > 5:
                total += 30
            else:
                total += _RUN_SCORE[(run, ends)]
        return total

    def _captures_at(self, p, color):
        """Number of enemy stones ``color`` would take by playing at ``p``."""
        cells = self.cells
        mine = B_BLACK if color == 0 else B_WHITE
        theirs = B_WHITE if color == 0 else B_BLACK
        taken = 0
        for d in DIRS8:
            if (cells[p + d] == theirs and cells[p + d + d] == theirs
                    and cells[p + d + d + d] == mine):
                taken += 2
        return taken

    def _vulnerable_at(self, p, color):
        """Pairs including ``p`` that the opponent could take next move."""
        cells = self.cells
        mine = B_BLACK if color == 0 else B_WHITE
        theirs = B_WHITE if color == 0 else B_BLACK
        count = 0
        for d in DIRS8:
            if cells[p + d] != mine:
                continue
            behind = cells[p - d]
            ahead = cells[p + d + d]
            if (behind == theirs and ahead == B_EMPTY) or (
                    behind == B_EMPTY and ahead == theirs):
                count += 1
        return count

    # ------------------------------------------------------------------
    # Make / unmake
    # ------------------------------------------------------------------
    def _make(self, p, color):
        """Play at ``p``; return 0 normal, 1 mover wins, 2 opponent wins, 3 tie."""
        cells = self.cells
        nb1 = self.nb1
        mine = B_BLACK if color == 0 else B_WHITE
        theirs = B_WHITE if color == 0 else B_BLACK

        taken = []
        for d in DIRS8:
            if (cells[p + d] == theirs and cells[p + d + d] == theirs
                    and cells[p + d + d + d] == mine):
                taken.append(p + d)
                taken.append(p + d + d)

        cells[p] = mine
        for off in BOX1:
            nb1[p + off] += 1
        for q in taken:
            cells[q] = B_EMPTY
            for off in BOX1:
                nb1[q + off] -= 1

        dirty = set(CELL_LINES[p])
        for q in taken:
            dirty.update(CELL_LINES[q])
        saved = []
        ls_b, ls_w = self.ls_b, self.ls_w
        for li in dirty:
            saved.append((li, ls_b[li], ls_w[li]))
            self._recompute(li)

        self.caps[color] += len(taken)
        self.stack.append((p, taken, saved, color))

        # Exactly five through the new stone wins for the mover.
        mover_five = False
        for d in AXES:
            if self._run(p, d, mine) == 5:
                mover_five = True
                break
        # Taking stones can shorten an enemy six into an enemy five -- which
        # wins for them, on our own move.
        other_five = False
        for q in taken:
            for d in AXES:
                for n in (q + d, q - d):
                    if cells[n] == theirs and self._run(n, d, theirs) == 5:
                        other_five = True
                        break
                if other_five:
                    break
            if other_five:
                break

        if mover_five and other_five:
            return 3
        if mover_five:
            return 1
        if other_five:
            return 2
        return 0

    def _unmake(self):
        p, taken, saved, color = self.stack.pop()
        cells = self.cells
        nb1 = self.nb1
        theirs = B_WHITE if color == 0 else B_BLACK

        cells[p] = B_EMPTY
        for off in BOX1:
            nb1[p + off] -= 1
        for q in taken:
            cells[q] = theirs
            for off in BOX1:
                nb1[q + off] += 1

        ls_b, ls_w = self.ls_b, self.ls_w
        for li, old_b, old_w in saved:
            self.sum_b += old_b - ls_b[li]
            ls_b[li] = old_b
            self.sum_w += old_w - ls_w[li]
            ls_w[li] = old_w
        self.caps[color] -= len(taken)

    def _run(self, p, d, stone):
        """Length of the maximal run of ``stone`` through ``p`` along ``d``."""
        cells = self.cells
        n = 1
        x = p + d
        while cells[x] == stone:
            n += 1
            x += d
        x = p - d
        while cells[x] == stone:
            n += 1
            x -= d
        return n

    # ------------------------------------------------------------------
    # Board bookkeeping
    # ------------------------------------------------------------------
    def _load(self, board):
        cells = bytearray(b"\x03" * AREA)
        nb1 = [0] * AREA
        for r in range(SIZE):
            base = (r + PAD) * W + PAD
            row = board[r]
            for c in range(SIZE):
                v = row[c]
                p = base + c
                if v == EMPTY:
                    cells[p] = B_EMPTY
                else:
                    cells[p] = B_BLACK if v == 0 else B_WHITE
                    for off in BOX1:
                        nb1[p + off] += 1
        self.cells = cells
        self.nb1 = nb1
        self.ls_b = [0] * NLINES
        self.ls_w = [0] * NLINES
        self.sum_b = 0
        self.sum_w = 0
        for li in range(NLINES):
            self._recompute(li)
        self.caps = [0, 0]
        self.stack = []

    def _recompute(self, li):
        start, step, n = LINES[li]
        key = bytes(self.cells[start:start + step * n:step])
        cached = self._line_cache.get(key)
        if cached is None:
            cached = (self._score_line(key.translate(_T_MINE_BLACK)),
                      self._score_line(key.translate(_T_MINE_WHITE)))
            if len(self._line_cache) < 400000:
                self._line_cache[key] = cached
        new_b, new_w = cached
        self.sum_b += new_b - self.ls_b[li]
        self.ls_b[li] = new_b
        self.sum_w += new_w - self.ls_w[li]
        self.ls_w[li] = new_w

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _rc(p):
        return (p // W - PAD, p % W - PAD)

    def _budget(self, remaining_ms):
        """Seconds to spend on this move, from the milliseconds left in the game."""
        try:
            remaining_ms = float(remaining_ms)
        except (TypeError, ValueError):
            return self.think_time
        if remaining_ms < 0:
            return self.think_time
        seconds = remaining_ms / 1000.0
        if seconds <= 0.3:
            return max(0.01, seconds * 0.4)
        return max(0.05, min(seconds / self.TIME_DIVISOR, self.TIME_CAP))
