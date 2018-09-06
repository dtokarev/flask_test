import unittest


class TestUtils(unittest.TestCase):
    def test_search_generate_keyword_set(self):
        from project.utils.search import generate_keywords

        keys = generate_keywords('some movie name')
        self.assertListEqual(['some movie name'], keys)

        keys = generate_keywords('some movie name (TV)')
        self.assertListEqual(['some movie name (TV)', 'some movie name'], keys)

        keys = generate_keywords('some movie name (TV)', year=2010)
        self.assertListEqual(['some movie name (TV) 2010', 'some movie name 2010'], keys)

        keys = generate_keywords('some movie name (TV)', 'OR THIS MOVIE NAME (TELEVISION)', year=2010)
        print(keys)
        self.assertListEqual([
            'some movie name (TV) OR THIS MOVIE NAME (TELEVISION) 2010',
            'some movie name OR THIS MOVIE NAME 2010',
            'some movie name 2010',
        ], keys)

    def test_unit_converter_size_human_to_float(self):
        from project.utils.unit_converter import size_human_to_float

        self.assertEquals(1, size_human_to_float('1 KB', 'KB'))
        self.assertEquals(1000000, size_human_to_float('1 GB', 'KB'))
        self.assertEquals(0.5, size_human_to_float('500 MB', 'GB'))

        self.assertEquals(0.77, size_human_to_float('807086080 \n 769.7 MB ↓', 'GB'))
        self.assertAlmostEquals(1460, size_human_to_float('807086080 \n 1.46 GB ↓', 'MB'), delta=1)

        self.assertRaises(ValueError, size_human_to_float, '1 KB', 'XB')
        self.assertRaises(ValueError, size_human_to_float, '1 XB', 'KB')

    def test_unit_converter_duration_human_to_sec(self):
        from project.utils.unit_converter import duration_human_to_sec

        self.assertEquals(60, duration_human_to_sec('00:01:00'))
        self.assertEquals(60, duration_human_to_sec('0:01:00'))
        self.assertEquals(3700, duration_human_to_sec('01:01:40'))

    def test_system_guess_type(self):
        from project.domain.enum import FileTypes
        from project.utils.system import guess_type

        self.assertIs(guess_type('webm', 'video/webm'), FileTypes.VIDEO)
        self.assertIs(guess_type('mp3', 'audio/mp3'), FileTypes.AUDIO)
        self.assertIs(guess_type('txt', 'text/plain'), FileTypes.JUNK)

    def test_get_disk_usage_perc_is_float(self):
        from project.utils.system import get_disk_usage_perc
        self.assertIs(type(get_disk_usage_perc()), float)
