from .exercise import special_sort


# def empty_numbers():
#     return []
#
#
# def single_number():
#     return [7]
#
#
# def one_odd_and_one_even_ordered():
#     return [2, 3]
#
#
# def one_odd_and_one_even_unordered():
#     return [3, 2]
#
#
# class TestExercise:
#
#     def test_special_sort_empty(self):
#         assert special_sort(empty_numbers) == []
#
#     def test_special_sort_single(self):
#         assert special_sort(single_number) == [7]
#
#     def test_special_sort_two_numbers_ordered(self):
#         assert special_sort(one_odd_and_one_even_ordered) == [3, 2]
#
#     def test_special_sort_two_numbers_unordered(self):
#         assert special_sort(one_odd_and_one_even_unordered) == [3, 2]
#
#     def test_special_sort_composite(self):
#         def source():
#             return [4, 3, 2, 7, 15, 11]
#
#         assert special_sort(source) == [3, 7, 11, 15, 2, 4]
#
#     def test_special_sort_all_evens(self):
#         def source():
#             return [6, 4, 2, 4, 10]
#
#         assert special_sort(source) == [2, 4, 4, 6, 10]
#
#     def test_special_sort_all_odds(self):
#         def source():
#             return [7, 3, 9, 13, 17]
#
#         assert special_sort(source) == [3, 7, 9, 13, 17]


from unittest.mock import patch
from .exercise import make_a_request


def test_it():
    with patch('requests.get') as mock_request:

        mock_request.return_value.status_code = 200
        mock_request.return_value.json = {'data':'somedata'}

        assert make_a_request() == {'data':'somedata'}
        mock_request.assert_called_once_with('https://duckduckgo.com/')

