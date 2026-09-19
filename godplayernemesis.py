import time
import random
from player import Player

SIZE = 19
EMPTY = -1

class SearchTimeout(Exception):
    pass

class RealGosu(Player):
    def __init__(self, color):
        super().__init__(color)
    
    def take_turn(self, board, time_limit=3.0):
        start_time = time.time()
        self.end_time = start_time + (time_limit * 0.9) # 10% 여유 마진

        # 1. 첫 수 또는 두 번째 수 대응
        stones = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] != EMPTY]
        if not stones: 
            return (SIZE // 2, SIZE // 2)
        if len(stones) == 1:
            r, c = stones[0]
            dr, dc = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)])
            if 0 <= r + dr < SIZE and 0 <= c + dc < SIZE: 
                return (r + dr, c + dc)

        # 2. 휴리스틱(규칙) 기반으로 모든 빈 칸의 점수를 매겨 정렬
        candidates = self.get_sorted_candidates(board)
        if not candidates:
            return (SIZE // 2, SIZE // 2)
            
        # 가장 높은 점수를 받은 좌표가 기본 선택 (Minimax가 시간초과나도 이걸 반환)
        best_move = candidates[0][1]

        # 3. Minimax 탐색 (깊이 1~3 정도만 얕고 빠르게)
        # 휴리스틱이 너무 정확해서 깊게 안 파고들어도 4목/3목 다 막아냅니다.
        for depth in range(1, 4):
            try:
                # 상위 12개의 유력한 수만 탐색
                top_moves = [c[1] for c in candidates[:12]]
                move, score = self.minimax(board, depth, -float('inf'), float('inf'), True, self.color, top_moves)
                best_move = move
                if score > 5000000:  # 확정 승리 루트를 찾으면 즉시 종료
                    break
            except SearchTimeout:
                break
                
        return best_move

    def get_sorted_candidates(self, board):
        """빈 칸들을 평가하여 가장 시급하고 좋은 수부터 정렬"""
        candidates = []
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] == EMPTY:
                    # 근처 2칸 이내에 돌이 있는 곳만 탐색 (연산 최적화)
                    if self.has_neighbor(board, r, c):
                        score = self.evaluate_single_move(board, r, c)
                        candidates.append((score, (r, c)))
                        
        # 점수(내림차순) 정렬
        candidates.sort(reverse=True, key=lambda x: x[0])
        return candidates

    def has_neighbor(self, board, r, c):
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                nr, nc = r + dr, c + dc
                if 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] != EMPTY:
                    return True
        return False

    def evaluate_single_move(self, board, r, c):
        """
        문자열이 아닌 직접 탐색 방식.
        이 위치에 두었을 때 나와 상대방의 5목, 4목, 3목 완성 여부를 정확히 카운트합니다.
        """
        score = 0
        opp = 1 - self.color
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        # 1. 내가 뒀을 때의 이득 (공격)
        board[r][c] = self.color
        for dr, dc in directions:
            count, open_ends = self.count_line_stats(board, r, c, dr, dc, self.color)
            if count >= 5: score += 10000000       # 5목 완성 (무조건 둠)
            elif count == 4 and open_ends == 2: score += 1000000  # 열린 4목 (필승)
            elif count == 4 and open_ends == 1: score += 100000   # 닫힌 4목
            elif count == 3 and open_ends == 2: score += 50000    # 열린 3목
            elif count == 3 and open_ends == 1: score += 1000
            elif count == 2 and open_ends == 2: score += 500

        # 2. 상대가 뒀을 때의 이득 (방어 - 가장 중요)
        # 상대의 4목/3목을 막는 것에 공격보다 더 높은 가중치를 부여합니다.
        board[r][c] = opp
        for dr, dc in directions:
            count, open_ends = self.count_line_stats(board, r, c, dr, dc, opp)
            if count >= 5: score += 8000000        # 상대 5목 방어 (무조건 막음)
            elif count == 4 and open_ends == 2: score += 800000   # 상대 열린 4목 방어
            elif count == 4 and open_ends == 1: score += 90000    # 상대 닫힌 4목 방어
            elif count == 3 and open_ends == 2: score += 60000    # 상대 열린 3목 방어 (내 열린3보다 중요하게 세팅)
            elif count == 3 and open_ends == 1: score += 800

        board[r][c] = EMPTY # 원래대로 복구
        
        # 3. 따내기(Capture) 룰 보너스
        score += self.check_capture(board, r, c, self.color) * 150000
        score += self.check_capture(board, r, c, opp) * 120000

        return score

    def count_line_stats(self, board, r, c, dr, dc, color):
        """특정 방향으로 연속된 돌의 개수와 뚫린 끝(빈칸)의 개수를 정확히 셉니다."""
        count = 1
        open_ends = 0
        
        # 정방향 탐색
        nr, nc = r + dr, c + dc
        while 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == color:
            count += 1
            nr += dr
            nc += dc
        if 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == EMPTY:
            open_ends += 1
            
        # 역방향 탐색
        nr, nc = r - dr, c - dc
        while 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == color:
            count += 1
            nr -= dr
            nc -= dc
        if 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == EMPTY:
            open_ends += 1
            
        return count, open_ends

    def check_capture(self, board, r, c, color):
        opp = 1 - color
        captures = 0
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            if 0 <= r + 3 * dr < SIZE and 0 <= c + 3 * dc < SIZE:
                if board[r + dr][c + dc] == opp and board[r + 2 * dr][c + 2 * dc] == opp and board[r + 3 * dr][c + 3 * dc] == color:
                    captures += 1
        return captures

    def apply_move(self, board, r, c, color):
        new_board = [row[:] for row in board]
        new_board[r][c] = color
        opp = 1 - color
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            if 0 <= r + 3 * dr < SIZE and 0 <= c + 3 * dc < SIZE:
                if new_board[r + dr][c + dc] == opp and new_board[r + 2 * dr][c + 2 * dc] == opp and new_board[r + 3 * dr][c + 3 * dc] == color:
                    new_board[r + dr][c + dc] = EMPTY
                    new_board[r + 2 * dr][c + 2 * dc] = EMPTY
        return new_board

    def minimax(self, board, depth, alpha, beta, is_maximizing, current_color, moves):
        if time.time() > self.end_time:
            raise SearchTimeout()
            
        if depth == 0:
            return None, 0 # 바닥 노드에서는 점수 계산 생략 (휴리스틱 정렬 신뢰)

        best_move = moves[0]
        
        if is_maximizing:
            max_eval = -float('inf')
            for r, c in moves:
                new_board = self.apply_move(board, r, c, current_color)
                
                # 방금 둔 수로 인해 이겼는지 체크
                score = self.evaluate_single_move(board, r, c)
                if score > 5000000: return (r, c), score
                
                # 다음 턴의 유력한 수 추출
                next_moves = [item[1] for item in self.get_sorted_candidates(new_board)[:6]]
                if not next_moves: continue
                
                _, eval_score = self.minimax(new_board, depth - 1, alpha, beta, False, 1 - current_color, next_moves)
                eval_score += score * 0.1 # 현재 수의 가치를 살짝 더해줌
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (r, c)
                alpha = max(alpha, eval_score)
                if beta <= alpha: break
            return best_move, max_eval
        else:
            min_eval = float('inf')
            for r, c in moves:
                new_board = self.apply_move(board, r, c, current_color)
                
                score = self.evaluate_single_move(board, r, c)
                if score > 5000000: return (r, c), -score
                
                next_moves = [item[1] for item in self.get_sorted_candidates(new_board)[:6]]
                if not next_moves: continue
                
                _, eval_score = self.minimax(new_board, depth - 1, alpha, beta, True, 1 - current_color, next_moves)
                eval_score -= score * 0.1
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (r, c)
                beta = min(beta, eval_score)
                if beta <= alpha: break
            return best_move, min_eval