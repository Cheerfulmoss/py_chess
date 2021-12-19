from chess_bot.Black_square_sets import square_sets_b
from chess_bot.White_square_sets import square_sets_w


def piece_val(piece_symbol, destination, turn):
    piece_symbol = piece_symbol.lower()

    pawn = 1
    bishop, knight = 3.33, 3.05
    rook = 5.63
    queen = 9.5
    king = 0

    if piece_symbol == "p":
        if turn is True:
            pawn_mod = square_sets_w("pawn")[destination]
        else:
            pawn_mod = square_sets_b("pawn")[destination]
        return pawn + pawn_mod
    if piece_symbol == "b":
        if turn is True:
            bishop_mod = square_sets_w("bishop")[destination]
        else:
            bishop_mod = square_sets_b("bishop")[destination]
        return bishop + bishop_mod
    if piece_symbol == "n":
        if turn is True:
            knight_mod = square_sets_w("knight")[destination]
        else:
            knight_mod = square_sets_b("knight")[destination]
        return knight + knight_mod
    if piece_symbol == "r":
        if turn is True:
            rook_mod = square_sets_w("rook")[destination]
        else:
            rook_mod = square_sets_b("rook")[destination]
        return rook + rook_mod
    if piece_symbol == "q":
        if turn is True:
            queen_mod = square_sets_w("queen")[destination]
        else:
            queen_mod = square_sets_b("queen")[destination]
        return queen + queen_mod
    if piece_symbol == "k":
        return king


def square_to_index(square):
    column = square[0]
    if column == "a":
        column = 0
    if column == "b":
        column = 1
    if column == "c":
        column = 2
    if column == "d":
        column = 3
    if column == "e":
        column = 4
    if column == "f":
        column = 5
    if column == "g":
        column = 6
    if column == "h":
        column = 7

    row = (int(square[1]) - 1) * 8
    index = row + column
    return index


def uci_to_index(uci):
    if len(uci) == 4:
        origin = uci[:2]
        destination = uci[2:]

        origin_index = square_to_index(origin)
        destination_index = square_to_index(destination)
        return origin_index, destination_index

    if len(uci) == 5:
        origin = uci[:2]
        destination = uci[2:][:2]
        piece_symbol = uci[2:][-1]

        origin_index = square_to_index(origin)
        destination_index = square_to_index(destination)
        return origin_index, destination_index, piece_symbol
