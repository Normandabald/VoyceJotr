import unittest
from voycejotr.utils import count_tokens

class TestCountTokens(unittest.TestCase):
    def test_count_tokens(self):
        # Test with a known input
        text = "This is a test."
        expected_output = 5
        self.assertEqual(count_tokens(text), expected_output)

    def test_count_tokens_exception(self):
        # Test exception handling
        bad_input = None  # None should raise an exception
        with self.assertRaises(Exception):
            count_tokens(bad_input)

if __name__ == '__main__':
    unittest.main()