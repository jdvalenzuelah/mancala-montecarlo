#!/usr/bin/env python
# coding: utf-8

def board_str(board):
    row_str = lambda lst: ' ║ '.join([ str(x) if x > 9 else ' ' + str(x) for x in lst])
    a = row_str(board['A'][1:7])
    b = row_str(board['B'][0:6])
    p1 = board['A'][0] if board['A'][0] > 9 else ' ' + str(board['A'][0])
    p2 = board['B'][-1] if board['B'][-1] > 9 else ' ' + str(board['B'][-1])
    formatted = f"""
                 1    2    3   4    5    6
         ╔════╦════╦════╦════╦════╦════╦════╦════╗
    A -> ║    ║ {a} ║    ║ 
         ║ {p1} ╠════╬════╬════╬════╬════╬════╣ {p2} ║
    B -> ║    ║ {b} ║    ║
         ╚════╩════╩════╩════╩════╩════╩════╩════╝
         """
    return formatted

def mancala(b, turn, player):
    from copy import copy
    board = copy(b)
    def get_iteration_condition(row):
        if row == 'A':
            return (lambda rocks, cell: rocks > 0 and cell > -1)
        else:
            return (lambda rocks, cell:rocks > 0 and cell < 7)
    
    def get_reducer(row):
        if row == 'A':
            return (lambda x: x - 1)
        else:
            return (lambda x: x + 1)
    
    def to_mancala_shot(row, cell):
        if row == 'A':
            return (row, cell) if cell != 0 else None
        else:
            return (row, cell + 1) if cell != 6 else None
    
    def get_player_points_cell(player):
        if player == 1:
            return ('A', 0)
        else:
            return ('B', 6)
    
    row, cell = turn

    if not (7 > cell > 0):
        raise ValueError(f'Invalid cell number {cell} was passed!')

    if row not in ['A', 'B']:
        raise ValueError(f'Invalid row {row} was passed!')
    
    if player not in [1, 2]:
        raise ValueError(f'Invalid player {player} was passed!')

    skip_cell = get_player_points_cell(1) if player == 2 else get_player_points_cell(2)
    cell = cell if row == 'A' else (cell - 1)
    rocks = board[row][cell]
    board[row][cell] = 0

    cell = (cell - 1) if row == 'A' else (cell + 1)
    repeat = False
    last_shot = None
    while rocks > 0:
        while get_iteration_condition(row)(rocks, cell):
            if not (row, cell) == skip_cell:
                board[row][cell] += 1
                repeat = board[row][cell] > 1
                last_shot = to_mancala_shot(row, cell) if repeat else None
                rocks -= 1
            cell = get_reducer(row)(cell)
        row = 'A' if row == 'B' else 'B'
        cell = 0 if cell == -1 else 6
    return (board, repeat, last_shot)

def is_game_over(board):
    return sum(board['A'][1:7]) == 0 or sum(board['B'][0:6]) == 0

def get_game_winner(board):
    a = sum(board['A'])
    b = sum(board['B'])
    if a == b:
        return 0
    elif a > b:
        return 1
    else:
        return 2

def game_loop(board, p1, p2, display = True):
    cprint = lambda s: print(s) if display else None
    player = 1
    while not is_game_over(board):
        cprint(board_str(board))
        cprint(f"----- Turno {player} -----")
        turn = p1(board) if player == 1 else p2(board)
        board, repeat, turn = mancala(board, turn, player)
        while repeat and not is_game_over(board):
            if repeat and not turn:
                turn = p1(board) if player == 1 else p2(board)
            board, repeat, turn = mancala(board, turn, player)
            cprint(board_str(board))
        player = 1 if player == 2 else 2
    return (get_game_winner(board), board)

def mancala_montecarlo(b, iters):
    import random
    from copy import copy
    board = copy(b)
    def get_possible_moves(board):
        a = [('A', i) for i in range(1, 7) if board['A'][i] > 0]
        b = [('B', i+1) for i in range(0, 6) if board['B'][i] > 0]
        return a + b
    
    def get_optimal(res):
        items = res.items()
        max_m = None
        for item in items:
            move, stats = item
            if not max_m:
                max_m = (move, stats['wins'])
            elif stats['wins'] > max_m[1]:
                max_m = (move, stats['wins'])
        return max_m[0]
            
    
    get_random_move = lambda b: random.choice(get_possible_moves(b))
    possible_moves = get_possible_moves(board)
    results = { m : {'picks': 0, 'wins': 0} for m in  possible_moves}
    for _ in range(iters):
        board = copy(b)
        move = random.choice(possible_moves)
        results[move]['picks'] += 1
        winner, _ = game_loop(board, get_random_move, get_random_move, display = False)
        if winner == 2:
            results[move]['wins'] += 1
    return get_optimal(results)

def noob(board):
    import random
    row, cell = random.choice(['A', 'B']), random.randint(1, 6)
    while board[row][cell] == 0:
        row, cell = random.choice(['A', 'B']), random.randint(1, 6)
    return (row, cell)

def advanced(board):
    return mancala_montecarlo(board, 500)

def pro(board):
    return mancala_montecarlo(board, 10000)

def validate_turn(turn):
    if turn[0] in ['A', 'B'] and 7 > int(turn[1]) > 0:
        return (turn[0].upper(), int(turn[1]))
    return None

def get_bot():
    levels = [noob, pro, advanced]
    selected_level = input("Ingrese nivel de dificultad:\n\t1. Noob\n\t2.Pro\n\t3.Avanzado\n")
    while selected_level not in ['1', '2', '3']:
        selected_level = input("Ingrese nivel de dificultad:\n\t1. Noob\n\t2.Pro\n\t3.Avanzado\n")
    return levels[int(selected_level) - 1]

def get_player_turn(*args):
    turn = None
    while not turn:
        turn = input('Ingrese cassila a tirar: ')
        if 2 > len(turn):
            turn = None
        else:
            turn = validate_turn(tuple(turn))
    return turn

if __name__ == '__main__':
    levels = [noob, advanced, pro]
    board = {
        'A': [0,4,4,4,4,4,4],
        'B': [4,4,4,4,4,4,0]
    }

    bot = get_bot()
    winner, b = game_loop(board, get_player_turn, bot)
    print(board_str(b))
    if winner == 1:
        print('Has ganado!')
    elif winner == 2:
        print('Ha ganado el bot!')
    else:
        print('Empate')






