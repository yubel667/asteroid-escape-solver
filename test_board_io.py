import unittest
import board_io

class TestBoardIO(unittest.TestCase):
    def test_parse_and_visualize_board(self):
        board = board_io.parse_board("01")
        serialized_board = board_io.serialize_board(board)
        with open("questions/01.txt", "r") as f:
            expected_board = f.read()
        self.assertEqual(serialized_board, expected_board)
        
        # test for debug occupancy
        debug_occupancy_map = board_io.debug_occupancy_map(board)
        with open("test/test_occupancy.txt", "r") as f:
            expected_occupancy_map = f.read()
        self.assertEqual(debug_occupancy_map, expected_occupancy_map)

if __name__ == "__main__":
    unittest.main()
