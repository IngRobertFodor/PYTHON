# Chess Square Color

def get_chess_square_color(row, column):
    chess_board = []

    for row_square in range(0,8):
        square = ""
        for column_square  in range(0,8):
            if column_square == 0:
                square = "white"
            elif column_square == 1:
                square = "black"
            elif column_square >= 2 and column_square % 2 == 0:
                square = "white"
            else:
                square = "black"
            chess_board.append(square)
            print(square, " ", end="")
        print("")
    print()

    print(chess_board)
    print()

    # How many elements each list (in our case row) of chess board should have.
    n = 8
    new_chess_board = []
    for i in range(0, len(chess_board), n):
        new_chess_board.append(chess_board[i:i+n])
    print(new_chess_board)
    print()

    ### Using list comprehension.
    new_chess_board_two = [chess_board[i:i+n] for i in range(0, len(chess_board), n)]
    print(new_chess_board_two)
    print()

    return new_chess_board[row][column]


result = get_chess_square_color(4,6)
print(result)