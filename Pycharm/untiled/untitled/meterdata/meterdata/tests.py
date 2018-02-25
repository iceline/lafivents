from django.test import TestCase

from .models import MeterInput

class MeterInputTest(TestCase):
    def test_valid_directory(self):
        input = MeterInput(directory = 'C:\\Users\\', title = 'testcase')
        input.save() 
        output = MeterInput.objects.get(title = 'testcase')
        self.assertEqual(input.directory, 'C:\\Users\\')
        self.assertEqual(str(input), 'testcase')
    def test_invalid_directory(self):
        input = MeterInput(directory = 'C:\\Nonexistant\\', title = 'testcase')
        self.assertRaises(ValueError, input.save())
    