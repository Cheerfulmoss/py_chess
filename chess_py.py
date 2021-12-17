import chess
import chess.pgn
import chess.engine
import chess.polyglot
import chess.svg
import random
import os
import time
import math
from chess_bot.White_square_sets import square_sets_w
from chess_bot.Black_square_sets import square_sets_b
from chess_bot.order_moves_back import piece_val, uci_to_index


def generate_moves(legal_board):
    legal_moves_list = []
    legal_moves = legal_board.legal_moves
    for move in legal_moves:
        legal_moves_list.append(move)
    return legal_moves_list


def get_piece_count(board):
    pieces = 0
    for square in board.piece_map():
        piece = board.piece_at(square)
        if piece is not None:
            pieces += 1
    return pieces


def select_book():
    global book

    cwd = os.getcwd() + "\\polyglot"
    book_list = os.listdir(cwd)
    book_index = random.randint(0, len(book_list) - 1)
    book = book_list[book_index]
    print(
        f"Book List: {book_list}\n"
        f"Selected Book: {book}"
    )
    return book


def evaluate(board):
    turn = board.turn

    black, white = material_count(board)
    eval = white - black

    if not turn and eval != 0:
        eval *= -1

    return eval


def material_count(board):
    pawn = 1
    bishop, knight = 3.33, 3.05
    rook = 5.63
    queen = 9.5
    white = 0
    black = 0

    for square in board.piece_map():
        piece = board.piece_at(square)
        if piece is None:
            pass
        else:
            piece = piece.symbol()
        if piece == "P":
            square_piece = square_sets_w("pawn")
            mod = square_piece[square]
            add = pawn + mod
            white += add
        if piece == "B":
            square_piece = square_sets_w("bishop")
            mod = square_piece[square]
            add = bishop + mod
            white += add
        if piece == "N":
            square_piece = square_sets_w("knight")
            mod = square_piece[square]
            add = knight + mod
            white += add
        if piece == "R":
            square_piece = square_sets_w("rook")
            mod = square_piece[square]
            add = rook + mod
            white += add
        if piece == "Q":
            square_piece = square_sets_w("queen")
            mod = square_piece[square]
            add = queen + mod
            white += add
        if piece == "p":
            square_piece = square_sets_b("pawn")
            mod = square_piece[square]
            add = pawn + mod
            black += add
        if piece == "b":
            square_piece = square_sets_b("bishop")
            mod = square_piece[square]
            add = bishop + mod
            black += add
        if piece == "n":
            square_piece = square_sets_b("knight")
            mod = square_piece[square]
            add = knight + mod
            black += add
        if piece == "r":
            square_piece = square_sets_b("rook")
            mod = square_piece[square]
            add = rook + mod
            black += add
        if piece == "q":
            square_piece = square_sets_b("queen")
            mod = square_piece[square]
            add = queen + mod
            black += add
        square += 1
    return black, white


def order_moves(input_board):
    multiplier = 10

    mini = input_board.copy()
    move_o = input_board.peek()
    mini.pop()

    if move_o is None:
        return -1

    else:
        score_guess = 0

        move = move_o.uci()
        if len(move) == 4:
            origin, destination = uci_to_index(move)

            move_type = mini.piece_at(origin)
            capture_type = mini.piece_at(destination)

            if capture_type is not None:
                capture_type = capture_type.symbol()
                capture_val = piece_val(capture_type)
                move_val = piece_val(move_type.symbol())
                score_guess = 10 * capture_val - move_val
                return score_guess

            if mini.turn:
                turn = chess.BLACK
            else:
                turn = chess.WHITE

            if mini.is_attacked_by(turn, destination):
                if input_board.is_checkmate():
                    return 99999
                attackers = mini.attackers(turn, destination).tolist()

                for index, result in enumerate(attackers):
                    if result:
                        if mini.piece_at(index).symbol().lower() == "p":
                            score_guess -= piece_val(mini.piece_at(origin).symbol()) * multiplier
                            return score_guess
                        elif mini.piece_at(origin).symbol() == "q":
                            if mini.piece_at(index).symbol().lower() != "q":
                                score_guess -= piece_val(mini.piece_at(index).symbol()) * multiplier
                        else:
                            return 0
                    else:
                        return 1
            if mini.gives_check(move_o):
                if input_board.is_checkmate():
                    return 99999
                elif mini.is_attacked_by(turn, destination):
                    attackers = mini.attackers(turn, destination).tolist()
                    for index, result in enumerate(attackers):
                        if result:
                            if mini.piece_at(index).symbol().lower() != "k":
                                score_guess -= piece_val(mini.piece_at(origin).symbol()) * math.ceil(multiplier / 2)
                                return score_guess
                            else:
                                if not input_board.is_fivefold_repetition() or not input_board.is_stalemate() or not input_board.is_fifty_moves() or not input_board.is_insufficient_material():
                                    return 10 * piece_val("k") - math.ceil(
                                        piece_val(mini.piece_at(origin).symbol()) / 2)
                                else:
                                    return -999
                        else:
                            return 0
                else:
                    if not input_board.is_fivefold_repetition() or not input_board.is_stalemate() or not input_board.is_fifty_moves() or not input_board.is_insufficient_material():
                        return 10 * piece_val("k") - math.ceil(piece_val(mini.piece_at(origin).symbol()) / 2)
                    else:
                        return -999
            else:
                return 0

        else:
            if mini.turn:
                turn = chess.BLACK
            else:
                turn = chess.WHITE

            origin, destination, piece_symbol = uci_to_index(move)
            if mini.is_attacked_by(turn, destination):
                if input_board.is_checkmate():
                    return 99999
                attackers = mini.attackers(turn, destination).tolist()
                for index, result in enumerate(attackers):
                    if result:
                        score_guess -= piece_val(mini.piece_at(origin).symbol()) * math.ceil(multiplier / 2)
                        return score_guess
                    else:
                        score_guess += piece_val(piece_symbol) * math.ceil(multiplier / 2)
                        return
            else:
                score_guess += piece_val(piece_symbol)
                return score_guess


def search(search_board, depth, alpha, beta):
    if depth == 0:
        eval = evaluate(search_board)
        return eval

    moves = generate_moves(search_board)
    random.shuffle(moves)
    if search_board.is_game_over():
        if search_board.is_checkmate():
            return 99999
        return 0
    if len(moves) == 0:
        if search_board.is_game_over():
            if search_board.is_checkmate():
                return 99999
        return 0

    move_order = {}
    for move in moves:
        search_board.push(move)
        move_eval = order_moves(search_board)
        if move_eval in move_order:
            move_order[move_eval].append(move)
        else:
            move_order[move_eval] = [move]
        search_board.pop()

    evals = move_order.keys()
    move_eval = max(evals)
    moves_search = move_order[move_eval]

    for move in moves_search:
        search_board.push(move)
        eval = -1 * round(search(search_board, depth - 1, -beta, -alpha), 3)
        search_board.pop()
        if type(eval) == tuple and len(eval) == 0:
            eval = -100
        if eval >= beta:
            return beta
        alpha = max(alpha, eval)

    return alpha


global book


def book_moves(opening_board):
    global book
    best_val = 0
    with chess.polyglot.open_reader(f"polyglot//{book}") as reader:
        for entry in reader.find_all(opening_board):
            if type(best_val) != chess.polyglot.Entry:
                if entry.weight > best_val:
                    best_val = entry
            elif entry.weight > best_val.weight:
                best_val = entry
    if best_val != 0:
        return best_val.weight, best_val.move
    else:
        return None


def make_move(board):
    if not board.is_game_over():
        depth = 4
        if get_piece_count(board) <= 8:
            depth = 6
        if get_piece_count(board) <= 4:
            depth = 8

        turn = board.turn
        think_board = board.copy()
        think_board_two = board.copy()

        while book_moves(board) is not None:
            ran = book_moves(board)[1]
            board.push(ran)
            mini = board.copy()
            move = order_moves(mini)

            if turn:
                print(f"White: {move, ran}")
            else:
                print(f"Black: {move, ran}")
            return move, ran

        moves = generate_moves(board)
        random.shuffle(moves)
        move_order = {}
        for move in moves:
            think_board.push(move)
            move_eval = order_moves(think_board)
            if move_eval in move_order:
                move_order[move_eval].append(move)
            else:
                move_order[move_eval] = [move]
            think_board.pop()

        evals = move_order.keys()
        move_eval = max(evals)
        moves_search = move_order[move_eval]
        best_moves = {}
        for move in moves_search:
            think_board_two.push(move)
            move_eval = search(think_board_two, depth, -99999, 99999)
            if move_eval in best_moves:
                best_moves[move_eval].append(move)
            else:
                best_moves[move_eval] = [move]
            think_board_two.pop()

        evals = best_moves.keys()
        move_eval = max(evals)
        best_moves_f = best_moves[move_eval]
        best_move = random.choice(best_moves_f)

        board.push(best_move)

        if turn:
            print(f"White: {move_eval, best_move}")
        else:
            print(f"Black: {move_eval, best_move}")
        print(board)

        return move_eval, best_move


def play_game(board):
    opening_book = select_book()

    start = time.time()
    game = chess.pgn.Game()

    game.headers["White"] = "Random Player 1"
    game.headers["Black"] = "Random Player 2"
    game.setup(board)
    node = game

    play = input("How to play: ").lower()
    if play == "white":
        while not board.is_game_over():
            if board.turn:
                move = make_move(board)
                print(board)
                node = node.add_variation(move[1])
                node.comment = f"Move: {move[0]}"
            else:
                move = input(f": ")
                player_push = chess.Move.from_uci(move)
                board.push(player_push)
                node = node.add_variation(chess.Move.from_uci(move))
    if play == "black":
        while not board.is_game_over():
            if not board.turn:
                move = make_move(board)
                print(board)
                node = node.add_variation(move[1])
                node.comment = f"Move: {move[0]}"
            else:
                move = input(f": ")
                player_push = chess.Move.from_uci(move)
                board.push(player_push)
                node = node.add_variation(chess.Move.from_uci(move))
    if play == "both":
        while not board.is_game_over():
            move = make_move(board)
            node = node.add_variation(move[1])
            node.comment = f"Move: {move[0]}"

    outcome = board.outcome()
    if outcome is None:
        outcome = "skip"
    move_count = board.fullmove_number
    game.headers["Event"] = f"Random Moves + {opening_book[:-4]}: {move_count}"
    game.headers["Result"] = board.result()
    end = time.time() - start
    return game, outcome, move_count, end


def main():
    board = chess.Board()
    game_play = play_game(board)
    print(f"Time: {game_play[3]}")
    print(game_play[0])
    print(game_play[1])
    print("\n")

    with open("game_save.txt", "w") as save_file:
        save_file.write(str(game_play[0]))
    board.reset()


main()
