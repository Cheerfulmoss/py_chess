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

import pdb


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
    value = 10
    pawn = 1
    bishop, knight = 3.33, 3.05
    rook = 5.63
    queen = 9.5
    king = 0
    white = 0
    black = 0

    for square in board.piece_map():
        piece = board.piece_at(square)
        if piece is None:
            pass
        else:
            piece = piece.symbol()
        if piece == "K":
            if "q" in board.board_fen() or "Q" in board.board_fen():
                square_piece = square_sets_w("king_s")
                mod = square_piece[square] / value
                add = king + mod
                white += add
            else:
                square_piece = square_sets_w("king_e")
                mod = square_piece[square] / value
                add = king + mod
                white += add
        if piece == "P":
            square_piece = square_sets_w("pawn")
            mod = square_piece[square] / value
            add = pawn + mod
            white += add
        if piece == "B":
            square_piece = square_sets_w("bishop")
            mod = square_piece[square] / value
            add = bishop + mod
            white += add
        if piece == "N":
            square_piece = square_sets_w("knight")
            mod = square_piece[square] / value
            add = knight + mod
            white += add
        if piece == "R":
            square_piece = square_sets_w("rook")
            mod = square_piece[square] / value
            add = rook + mod
            white += add
        if piece == "Q":
            square_piece = square_sets_w("queen")
            mod = square_piece[square] / value
            add = queen + mod
            white += add

        if piece == "k":
            if "q" in board.board_fen() or "Q" in board.board_fen():
                square_piece = square_sets_b("king_s")
                mod = square_piece[square] / value
                add = king + mod
                black += add
            else:
                square_piece = square_sets_b("king_e")
                mod = square_piece[square] / value
                add = king + mod
                black += add
        if piece == "p":
            square_piece = square_sets_b("pawn")
            mod = square_piece[square] / value
            add = pawn + mod
            black += add
        if piece == "b":
            square_piece = square_sets_b("bishop")
            mod = square_piece[square] / value
            add = bishop + mod
            black += add
        if piece == "n":
            square_piece = square_sets_b("knight")
            mod = square_piece[square] / value
            add = knight + mod
            black += add
        if piece == "r":
            square_piece = square_sets_b("rook")
            mod = square_piece[square] / value
            add = rook + mod
            black += add
        if piece == "q":
            square_piece = square_sets_b("queen")
            mod = square_piece[square] / value
            add = queen + mod
            black += add
        square += 1
    return black, white


def order_moves(input_board, moves):
    move_dict = {}

    turn_board = input_board.copy()
    test_board = input_board.copy()
    turn_board.pop()

    opposite_turn = turn_board.turn
    current_turn = input_board.turn

    for move in moves:
        score_guess = 0
        move_str = move.uci()
        if len(move_str) == 4:
            origin, destination = uci_to_index(move_str)
            move_piece = turn_board.piece_at(origin)
            capture_piece = input_board.piece_at(destination)

            test_board.push(move)
            if test_board.is_stalemate() or test_board.is_insufficient_material() or \
                    test_board.is_seventyfive_moves() or test_board.is_fifty_moves() or \
                    test_board.is_fivefold_repetition() or test_board.is_repetition():
                score_guess = -999
                if score_guess in move_dict:
                    move_dict[score_guess].append(move)
                else:
                    move_dict[score_guess] = [move]
            if test_board.is_checkmate():
                score_guess = 99999
                if score_guess in move_dict:
                    move_dict[score_guess].append(move)
                else:
                    move_dict[score_guess] = [move]
            test_board.pop()

            if input_board.gives_check(move):
                defender_count = -1
                attacker_count = 0
                if input_board.is_attacked_by(opposite_turn, destination):
                    attackers = input_board.attackers(opposite_turn, destination).tolist()
                    defenders = input_board.attackers(current_turn, destination).tolist()
                    for piece in defenders:
                        defender_count += 1
                    for piece in attackers:
                        attacker_count += 1

                    for index, result in enumerate(attackers):
                        if result:
                            piece = input_board.piece_at(index).symbol().lower()
                            if (piece == "k" or piece != "k") and defender_count > attacker_count:
                                score_guess = round(10 * piece_val(move_piece.symbol(), destination, current_turn), 3)
                            if (piece == "k" or piece != "k") and defender_count < attacker_count:
                                score_guess = round(piece_val(move_piece.symbol(), destination, current_turn), 3)
                            if score_guess in move_dict:
                                move_dict[score_guess].append(move)
                            else:
                                move_dict[score_guess] = [move]
            elif capture_piece is not None:
                defender_count = -1
                attacker_count = 0
                attackers = input_board.attackers(opposite_turn, destination).tolist()
                defenders = input_board.attackers(current_turn, destination).tolist()
                for piece in defenders:
                    defender_count += 1
                for piece in attackers:
                    attacker_count += 1

                if piece_val(move_piece.symbol(), destination, current_turn) < piece_val(capture_piece.symbol(),
                                                                                         destination, opposite_turn):
                    score_guess = piece_val(capture_piece.symbol(), destination, opposite_turn)
                if defender_count > attacker_count:
                    score_guess += round(10 * piece_val(capture_piece.symbol(), destination, opposite_turn) - \
                                         piece_val(move_piece.symbol(), destination, current_turn), 3)
                if attacker_count > defender_count:
                    score_guess -= round(10 * piece_val(capture_piece.symbol(), destination, opposite_turn) + \
                                         piece_val(move_piece.symbol(), destination, current_turn), 3)
                if score_guess in move_dict:
                    move_dict[score_guess].append(move)
                else:
                    move_dict[score_guess] = [move]

            elif input_board.is_attacked_by(opposite_turn, destination):
                attackers = input_board.attackers(opposite_turn, destination).tolist()
                for index, result in enumerate(attackers):
                    if result:
                        piece = input_board.piece_at(index).symbol().lower()
                        if piece == "p":
                            score_guess -= round(piece_val(move_piece.symbol(), destination, current_turn) + piece_val(
                                input_board.piece_at(index).symbol(), index, opposite_turn), 3)

            else:
                score_guess += round(piece_val(move_piece.symbol(), destination, current_turn), 3)
            if score_guess in move_dict:
                move_dict[score_guess].append(move)
            else:
                move_dict[score_guess] = [move]
        else:
            origin, destination, promotion = uci_to_index(move_str)
            move_piece = turn_board.piece_at(origin)
            capture_piece = input_board.piece_at(destination)

            if input_board.is_attacked_by(opposite_turn, destination):
                attackers = input_board.attackers(opposite_turn, destination).tolist()
                for index, result in enumerate(attackers):
                    if result:
                        piece = input_board.piece_at(index).symbol().lower()
                        score_guess -= round(piece_val(move_piece.symbol(), destination, current_turn) +
                                             piece_val(promotion, destination, current_turn) +
                                             piece_val(piece, destination, opposite_turn), 3)
            elif input_board.attackers(origin):
                for square in input_board.attackers(origin):
                    piece = input_board.piece_at(square).symbol().lower()
                    score_guess = round(piece_val(move_piece.symbol(), destination, current_turn) +
                                        piece_val(promotion, destination, current_turn) +
                                        piece_val(piece, destination, opposite_turn), 3)
                    if score_guess in move_dict:
                        move_dict[score_guess].append(move)
                    else:
                        move_dict[score_guess] = [move]
            else:
                score_guess = round(10 * piece_val(promotion, destination, current_turn), 3)
            if score_guess in move_dict:
                move_dict[score_guess].append(move)
            else:
                move_dict[score_guess] = [move]

    return move_dict


def search(search_board, depth, alpha, beta):
    if depth == 0:
        eval = evaluate(search_board)
        return eval

    moves = order_moves(search_board, generate_moves(search_board))
    if len(moves) == 0:
        if search_board.is_checkmate():
            return -99999
        return 0

    evals = moves.keys()
    move_eval = max(evals)
    moves_search = moves[move_eval]
    random.shuffle(moves_search)

    for move in moves_search:
        search_board.push(move)
        evaluation = -1 * search(search_board, depth - 1, -beta, -alpha)
        search_board.pop()

        if evaluation >= beta:
            return beta

        alpha = max(alpha, evaluation)
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
            ran = book_moves(board)
            move = ran[1]
            eval = ran[0]
            board.push(move)

            if turn:
                print(f"White: {eval, move}")
            else:
                print(f"Black: {eval, move}")
            return eval, move

        moves = generate_moves(board)
        move_order = order_moves(think_board, moves)

        evals = move_order.keys()
        move_eval = max(evals)
        moves_search = move_order[move_eval]
        random.shuffle(moves_search)
        best_moves = {}
        for move2 in moves_search:
            think_board_two.push(move2)
            move_eval = search(think_board_two, depth, -99999, 99999)
            if move_eval in best_moves:
                best_moves[move_eval].append(move2)
            else:
                best_moves[move_eval] = [move2]
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
    force_game_over = False
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
                node = node.add_variation(move[1])
                node.comment = f"Move: {move[0]}"
            else:
                move = input(f": ")
                player_push = chess.Move.from_uci(move)
                board.push(player_push)
                node = node.add_variation(chess.Move.from_uci(move))
    if play == "both":
        while not board.is_game_over() and force_game_over == False:
            move = make_move(board)
            node = node.add_variation(move[1])
            node.comment = f"Move: {move[0]}"
            if board.fullmove_number == 200:
                force_game_over = True

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
