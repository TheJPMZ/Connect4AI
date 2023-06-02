import numpy as np
from flask import Flask, render_template, request, redirect, url_for
import json
import random

app = Flask(__name__)







def get_valid_locations(board):
    valid_locations = []
    for col in range(7):
        if board[5][col] == 0:
            valid_locations.append(col)
    return valid_locations

def winning_move(board, piece):
    for c in range(4):
        for r in range(6):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    for c in range(7):
        for r in range(3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    for c in range(4):
        for r in range(3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    for c in range(4):
        for r in range(3, 6):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0

def get_heuristic(window, piece):
    opponent_piece = 1 if piece == 2 else 2
    score = 0
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opponent_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score

def heuristic_score(board, piece):
    score = 0
    for r in range(6):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(4):
            window = row_array[c:c+4]
            score += get_heuristic(window, piece)

    for c in range(7):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(3):
            window = col_array[r:r+4]
            score += get_heuristic(window, piece)

    for r in range(3):
        for c in range(4):
            window = [board[r+i][c+i] for i in range(4)]
            score += get_heuristic(window, piece)

    for r in range(3):
        for c in range(4):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += get_heuristic(window, piece)

    return score

def get_next_open_row(board, column):
    for r in range(6):
        if board[r][column] == 0:
            return r

def drop_piece(board, row, column, piece):
    board[row][column] = piece

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):
                return (None, 10000000000000)
            elif winning_move(board, 1):
                return (None, -10000000000000)
            else: 
                return (None, 0)
        else: 
            return (None, heuristic_score(board, 2))
    if maximizingPlayer:
        value = -np.Inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 2)
            new_score = minimax(temp_board, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player
        value = np.Inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 1)
            new_score = minimax(temp_board, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

@app.route('/move', methods=['POST'])
def get_move():
    data = request.get_json()
    board = data['board']
    turn = data['player']

    if turn == 2:
        columnas = minimax(board, 5, -np.Inf, np.Inf, False)[0]
    else:
        columnas = minimax(board, 5, -np.Inf, np.Inf, True)[0]
    
    return json.dumps({'column': columnas})

if __name__ == '__main__':
    from socketIO_client import SocketIO
    import random

    server_url = "http://192.168.1.104"
    server_port = 4000

    socketIO = SocketIO(server_url, server_port)

    def on_connect():
        print("Connected to server")
        socketIO.emit('signin', {
            'user_name': "Mememaster",
            'tournament_id': 142857,
            'user_role': 'player'
        })

    def on_ok_signin():
        print("Login")

    def on_finish(data):
        game_id = data['game_id']
        player_turn_id = data['player_turn_id']
        winner_turn_id = data['winner_turn_id']
        board = data['board']
        # Your logic for handling 'finish' event here

    def on_ready(data):
        game_id = data['game_id']
        player_turn_id = data['player_turn_id']
        board = data['board']
        print("I'm player:", player_turn_id)
        print(board)
        
        if player_turn_id == 2:
            columnas = minimax(board, 5, -np.Inf, np.Inf, False)[0]
        else:
            columnas = minimax(board, 5, -np.Inf, np.Inf, True)[0]
            
        move = columnas
        
        
        print("Move in:", move)
        socketIO.emit('play', {
            'tournament_id': 142857,
            'player_turn_id': player_turn_id,
            'game_id': game_id,
            'movement': move
        })

    def on_finish(data):
        game_id = data['game_id']
        player_turn_id = data['player_turn_id']
        winner_turn_id = data['winner_turn_id']
        board = data['board']
        
        # Your cleaning board logic here
        
        print("Winner:", winner_turn_id)
        print(board)
        socketIO.emit('player_ready', {
            'tournament_id': 142857,
            'player_turn_id': player_turn_id,
            'game_id': game_id
        })

    socketIO.on('connect', on_connect)
    socketIO.on('ok_signin', on_ok_signin)
    socketIO.on('finish', on_finish)
    socketIO.on('ready', on_ready)
    socketIO.on('finish', on_finish)

    socketIO.wait()