
def piece_val(piece_symbol):
    piece_symbol = piece_symbol.lower()

    pawn = 1
    bishop, knight = 3.33, 3.05
    rook = 5.63
    queen = 9.5
    king = 9

    if piece_symbol == "p":
        return pawn
    if piece_symbol == "b":
        return bishop
    if piece_symbol == "n":
        return knight
    if piece_symbol == "r":
        return rook
    if piece_symbol == "q":
        return queen
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
