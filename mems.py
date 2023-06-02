import numpy as np
from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

ROWS = 6
COLUMNS = 7

def create_board():
    return np.zeros((ROWS,COLUMNS))

def valid_move(board, column):
    return board[ROWS-1][column] == 0

def drop_piece(board, row, column, piece):
    board[row][column] = piece

def get_next_open_row(board, column):
    for r in range(ROWS):
        if board[r][column] == 0:
            return r

def winning_move(board, piece):
    # Horizontal check
    for c in range(COLUMNS-3):
        for r in range(ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Vertical check
    for c in range(COLUMNS):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Positive diagonal check
    for c in range(COLUMNS-3):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Negative diagonal check
    for c in range(COLUMNS-3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def evaluate_window(window, piece):
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

def score_position(board, piece):
    score = 0
    # Score horizontal
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMNS-3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLUMNS):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROWS-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    # Score positive sloped diagonal
    for r in range(ROWS-3):
        for c in range(COLUMNS-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Score negative sloped diagonal
    for r in range(ROWS-3):
        for c in range(COLUMNS-3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0






def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):
                return (None, 10000000000000)
            elif winning_move(board, 1):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, 2))
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

import random

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMNS):
        if valid_move(board, col):
            valid_locations.append(col)
    return valid_locations

def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col

def draw_board(board):
    for x in reversed(board):
        for y in x:
            print(str(int(y)).replace("1","💛").replace("0","⬛").replace("2","🔵"), end=" ")
        print()

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


def main():
    board = create_board()
    print(board)
    game_over = False
    turn = 0

    while not game_over:
        # Player 1 Input
        if turn == 0:
            col, minimax_score = minimax(board, 4, -np.inf, np.inf, False)
            if valid_move(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 1)

                if winning_move(board, 1):
                    print("Player 1 Wins!!")
                    game_over = True

        # AI Input
        else: 
            col, minimax_score = minimax(board, 4, -np.inf, np.inf, True)

            print(col)

            if valid_move(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)

                if winning_move(board, 2):
                    print("AI Wins!!")
                    game_over = True

        print("Board after " + str(turn+1) + " move")
        draw_board(board)

        turn += 1
        turn = turn % 2 # alternate players

if __name__ == '__main__':
    main()

exit()

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
        print(board, player_turn_id)
        
        board = np.array([np.array(x) for x in board])
        
        try:
            if int(player_turn_id) == 2:
                columnas = minimax(board, 5, -np.Inf, np.Inf, False)[0]
            else:
                columnas = minimax(board, 5, -np.Inf, np.Inf, True)[0]
        except:
            move = random.randint(0,5)
            
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
