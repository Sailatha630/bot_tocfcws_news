from mock import mock
import unittest
import datetime
from helper import compare_time


class TestHelper(unittest.TestCase):
    def test_compare_time(self):
        # WHEN
        mock_utcnow = datetime.datetime(2000, 1, 1, 18, 10, 0)
        with mock.patch.object(datetime, 'datetime', mock.Mock(wraps=datetime.datetime)) as patched:
            patched.utcnow.return_value = mock_utcnow
            timestamp = "2000-1-1 18:00:00"
            # DO
            r = compare_time(timestamp)
            # THEN
        self.assertGreaterEqual(mock_utcnow, datetime.datetime(2000,1,1,18,0,0))
        self.assertEqual(5, r)
    


if __name__ == '__main__':
    unittest.main()
