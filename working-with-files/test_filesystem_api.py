from unittest.mock import patch, mock_open, MagicMock
import pytest

from filesystem_api import get_file_line_by_line

@patch("builtins.open", new_callable=mock_open)
def test_read_file_lines_non_existing_file(mock_file):
    filename = "test"
    mock_file.side_effect = FileNotFoundError()

    with pytest.raises(FileNotFoundError):
        # need to consume the file contents so that it actually tries to read to trigger the error
        list(get_file_line_by_line(filename))

    mock_file.assert_called_with(filename, 'r', encoding='utf-8')


@patch("builtins.open", new_callable=mock_open, read_data="ipsum")
def test_read_file_manages_file_descriptor_properly_after_reading(mock_open):
    filename = "test"

    list(get_file_line_by_line(filename))

    mock_open.assert_called_once_with(filename, 'r', encoding='utf-8')

    handle = mock_open()
    handle.__exit__.assert_called()


@patch("builtins.open", new_callable=mock_open, read_data="ipsum\nlorem")
def test_read_file_lines_with_an_iterator(mock_open):
    filename = "test"

    list(get_file_line_by_line(filename)) == [
        "ipsum",
        "lorem"
    ]
