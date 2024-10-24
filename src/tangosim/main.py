from models import Tile

def init_game_pieces() -> List[Tile]:
    for num_ticks in range(1, 6):
        print(num_ticks)

def main() -> None:
    player1_pieces = init_game_pieces()
    print("hello world")
    pass

if __name__ == "__main__":
    main()