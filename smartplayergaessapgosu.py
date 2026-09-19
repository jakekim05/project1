import time
import random
from player import Player

SIZE = 19
EMPTY = -1

class SearchTimeout(Exception):
    """제한 시간 초과 시 탐색을 중단하기 위한 커스텀 예외"""
    pass

class SmartPlayerGaeSsapGosu(Player):
    def __init__(self, color):
        super().__init__(color)
        
        # 내가 유리한 패턴과 점수 (공격)
        self.my_patterns = {
            'XXXXX': 100000000,   # 승리 (5목)
            '.XXXX.': 10000000,   # 열린 4 (필승)
            '.XXXXO': 100000, 'OXXXX.': 100000, 'X.XXX': 100000, 'XXX.X': 100000, 'XX.XX': 100000, # 닫힌 4
            '.XXX.': 80000,       # 열린 3
            '.XX.X.': 50000, '.X.XX.': 50000, # 끊긴 열린 3
            '.XX.': 1000,         # 열린 2
        }
        
        # 상대방이 유리한 패턴과 점수 (방어/감점)
        self.opp_patterns = {
            'OOOOO': -100000000,
            '.OOOO.': -10000000,
            '.OOOOX': -100000, 'XOOOO.': -100000, 'O.OOO': -100000, 'OOO.O': -100000, 'OO.OO': -100000,
            '.OOO.': -80000,
            '.OO.O.': -50000, '.O.OO.': -50000,
            '.OO.': -1000,
        }

    def take_turn(self, board, time_limit=3.0):
        """
        주어진 시간(time_limit) 내에 최선의 수를 찾아 반환합니다.
        Iterative Deepening(반복 심화) 기법을 사용하여 시간이 허락하는 한 깊게 탐색합니다.
        """
        # 시간 제한이 이상하게 넘어올 경우를 대비한 안전장치
        if not isinstance(time_limit, (int, float)) or time_limit <= 0:
            time_limit = 5.0
            
        start_time = time.time()
        # 탐색 종료 한계 시간 설정 (여유 버퍼 5% 확보)
        self.end_time = start_time + (time_limit * 0.95)

        # 1. 첫 수 또는 두 번째 수 등 극초반 오프닝 하드코딩 (연산 낭비 방지)
        stones = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] != EMPTY]
        if len(stones) == 0:
            return (SIZE // 2, SIZE // 2)  # 첫 수는 무조건 정중앙
        if len(stones) == 1:
            r, c = stones[0]
            # 상대가 첫 수를 두었다면 대각선으로 붙여서 둠
            dr, dc = random.choice([(1, 1), (1, -1), (-1, 1), (-1, -1)])
            if 0 <= r + dr < SIZE and 0 <= c + dc < SIZE:
                return (r + dr, c + dc)

        # 2. 미니맥스 탐색 시작
        best_move = None
        # 탐색할 후보군을 휴리스틱으로 추려냄 (연산 속도 극대화)
        candidates = self.get_candidates(board, self.color, max_count=12)
        
        if not candidates:
            # 보드가 가득 차거나 에러 방지용 Fallback
            for r in range(SIZE):
                for c in range(SIZE):
                    if board[r][c] == EMPTY: return (r, c)

        # 깊이를 1부터 점진적으로 늘려가며 탐색 (Iterative Deepening)
        for depth in range(1, 10):
            try:
                move, score = self.minimax_root(board, depth, candidates)
                best_move = move
                
                # 강제 승리/패배 노드를 찾으면 탐색 조기 종료
                if abs(score) > 50000000:
                    break
            except SearchTimeout:
                # 시간이 다 되면 직전 깊이까지 찾아둔 best_move를 신뢰하고 리턴
                break
                
        return best_move if best_move else candidates[0]

    def minimax_root(self, board, depth, candidates):
        """탐색 트리의 최상단 루트 노드 (가장 좋은 첫 수를 고름)"""
        best_move = candidates[0]
        max_eval = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        for r, c in candidates:
            if time.time() > self.end_time:
                raise SearchTimeout()
                
            # 직접 둬보고 캡처된 돌 개수를 파악
            new_board, captures = self.apply_move(board, r, c, self.color)
            
            # 다음 턴(상대방)으로 넘김
            eval_score = self.minimax(new_board, depth - 1, alpha, beta, False, 1 - self.color, captures)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (r, c)
                
            alpha = max(alpha, eval_score)
            
        return best_move, max_eval

    def minimax(self, board, depth, alpha, beta, is_maximizing, current_color, capture_diff):
        """알파베타 푸르닝이 적용된 미니맥스 재귀 함수"""
        if time.time() > self.end_time:
            raise SearchTimeout()
            
        # 1. 현재 보드 상태 평가 (캡처 우위 반영)
        score = self.evaluate_board_state(board) + (capture_diff * 150000)
        
        # 누군가 5목을 만들었거나 승리했다면 깊이에 따른 보상/패널티 부여 
        # (빠르게 이기는 길, 늦게 지는 길을 선호하도록)
        if abs(score) >= 50000000:
            return score * (depth + 1)
            
        # 2. 바닥 노드 도달
        if depth == 0:
            return score
            
        candidates = self.get_candidates(board, current_color, max_count=8 if depth > 1 else 5)
        if not candidates:
            return score
            
        if is_maximizing:
            max_eval = -float('inf')
            for r, c in candidates:
                new_board, captures = self.apply_move(board, r, c, current_color)
                eval_score = self.minimax(new_board, depth - 1, alpha, beta, False, 1 - current_color, capture_diff + captures)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta Pruning
            return max_eval
        else:
            min_eval = float('inf')
            for r, c in candidates:
                new_board, captures = self.apply_move(board, r, c, current_color)
                eval_score = self.minimax(new_board, depth - 1, alpha, beta, True, 1 - current_color, capture_diff - captures)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha Pruning
            return min_eval

    def get_candidates(self, board, current_color, max_count):
        """
        무의미한 빈 칸 탐색을 막기 위해 기존 돌 주변 반경 2칸 이내의 빈 칸만 후보로 등록하고,
        quick_eval을 통해 가장 가능성 높은 수부터 정렬하여 반환 (알파베타 효율 극대화)
        """
        candidates = set()
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] != EMPTY:
                    # 돌 주변 5x5 영역 탐색
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == EMPTY:
                                candidates.add((nr, nc))
                                
        scored_candidates = []
        for r, c in candidates:
            score = self.quick_eval(board, r, c, current_color)
            scored_candidates.append((score, (r, c)))
            
        # 점수가 높은 순으로 정렬하여 상위 max_count 개수만 리턴
        scored_candidates.sort(reverse=True, key=lambda x: x[0])
        return [item[1] for item in scored_candidates[:max_count]]

    def quick_eval(self, board, r, c, color):
        """특정 위치에 두었을 때의 잠재적 가치를 아주 빠르게 계산하는 휴리스틱"""
        score = 0
        opp = 1 - color
        char_map = {color: 'X', opp: 'O', EMPTY: '.'}
        opp_char_map = {opp: 'X', color: 'O', EMPTY: '.'}

        # 해당 자리에 내 돌을 두었다고 가정한 공격 점수
        board[r][c] = color
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            line = []
            for k in range(-4, 5):
                nr, nc = r + k * dr, c + k * dc
                if 0 <= nr < SIZE and 0 <= nc < SIZE:
                    line.append(char_map[board[nr][nc]])
            s_line = "".join(line)
            for pat, val in self.my_patterns.items():
                if pat in s_line: score += val
        
        # 해당 자리에 상대가 두었다고 가정한 방어 점수 (상대의 패턴을 깸)
        board[r][c] = opp
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            line = []
            for k in range(-4, 5):
                nr, nc = r + k * dr, c + k * dc
                if 0 <= nr < SIZE and 0 <= nc < SIZE:
                    line.append(opp_char_map[board[nr][nc]])
            s_line = "".join(line)
            for pat, val in self.my_patterns.items():
                if pat in s_line: score += val * 0.9  # 방어는 공격보다 살짝 낮게 가중치

        # 보드 원상복구
        board[r][c] = EMPTY
        
        # 따내기(Capture) 규칙 확인 (내가 따는 것, 상대가 따는 것을 막는 것 모두 보너스)
        score += self.check_capture_count(board, r, c, color) * 150000
        score += self.check_capture_count(board, r, c, opp) * 100000

        return score

    def evaluate_board_state(self, board):
        """보드 전체의 현재 형세를 평가 (문자열 패턴 매칭 기반)"""
        char_map = {self.color: 'X', 1 - self.color: 'O', EMPTY: '.'}
        lines = []
        
        # 가로, 세로, 대각선 라인을 모두 추출
        for r in range(SIZE):
            lines.append("".join(char_map[board[r][c]] for c in range(SIZE)))
        for c in range(SIZE):
            lines.append("".join(char_map[board[r][c]] for r in range(SIZE)))
        for d in range(-SIZE + 1, SIZE):
            lines.append("".join(char_map[board[i][i - d]] for i in range(max(0, d), min(SIZE, SIZE + d))))
        for d in range(0, 2 * SIZE - 1):
            lines.append("".join(char_map[board[i][d - i]] for i in range(max(0, d - SIZE + 1), min(SIZE, d + 1))))
            
        score = 0
        for line in lines:
            if len(line) < 5: continue
            for pat, val in self.my_patterns.items():
                score += line.count(pat) * val
            for pat, val in self.opp_patterns.items():
                score += line.count(pat) * val
                
        return score

    def check_capture_count(self, board, r, c, color):
        """특정 위치에 두었을 때 캡처할 수 있는 상대 돌의 개수(쌍) 반환"""
        opp = 1 - color
        captures = 0
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            if 0 <= r + 3 * dr < SIZE and 0 <= c + 3 * dc < SIZE:
                if board[r + dr][c + dc] == opp and board[r + 2 * dr][c + 2 * dc] == opp and board[r + 3 * dr][c + 3 * dc] == color:
                    captures += 2
        return captures

    def apply_move(self, board, r, c, color):
        """돌을 두고 캡처 룰을 적용한 새로운 보드 상태와 따낸 돌 개수를 반환"""
        new_board = [row[:] for row in board]
        new_board[r][c] = color
        opp = 1 - color
        captured_total = 0
        
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            if 0 <= r + 3 * dr < SIZE and 0 <= c + 3 * dc < SIZE:
                if new_board[r + dr][c + dc] == opp and new_board[r + 2 * dr][c + 2 * dc] == opp and new_board[r + 3 * dr][c + 3 * dc] == color:
                    new_board[r + dr][c + dc] = EMPTY
                    new_board[r + 2 * dr][c + 2 * dc] = EMPTY
                    captured_total += 2
                    
        return new_board, captured_total