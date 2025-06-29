from django.test import TestCase
from ..models import Course
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

class CourseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.course1 = Course.objects.create(
            title = 'test_course1',
            outline = "This is test_course1 outline",
            language = "en",
            country = "US",
            subject = "physics",
            visiblity = "public",
            start_date = datetime(2025, 12, 31, 23, 59, 59),
            end_date = datetime(2025, 12, 31, 23, 59, 59) + timedelta(days=30),
            is_active = False,
            allow_join_requests = False,
        )
        
        cls.course2 = Course.objects.create(
            title = 'test_course2',
            outline = "This is test_course2 outline",
            language = "en",
            country = "US",
            subject = "math",
        )
        cls.course3 = Course.objects.create(
            title = 'test_course3',
            language = "en",
            country = "US",
            subject = "math",
        )
        cls.course4 = Course.objects.create(
            title = 'test_course4'
        )
       
    def test_course_creation(self) -> None:
        self.assertEqual(self.course1.title, 'test_course1')
        self.assertEqual(self.course1.outline, "This is test_course1 outline")
        self.assertEqual(self.course1.language, "en")
        self.assertEqual(self.course1.country, "US")
        self.assertEqual(self.course1.subject, "physics")
        self.assertEqual(self.course1.visiblity, "public")
        self.assertEqual(self.course1.start_date, datetime(2025, 12, 31, 23, 59, 59))
        self.assertEqual(self.course1.end_date, datetime(2025, 12, 31, 23, 59, 59) + timedelta(days=30))
        self.assertEqual(self.course1.is_active, False)
        self.assertEqual(self.course1.allow_join_requests, False)
        
    def test_course_default_values(self):
        self.assertEqual(self.course1.visiblity, "public")
        self.assertFalse(self.course1.is_active)
        self.assertFalse(self.course1.allow_join_requests)
        
    def test_course_delete(self):
        self.course1.delete()
        self.assertEqual(Course.objects.count(), 3)
        
    def test_course_update(self):
        self.course3.title = "updated_course3"
        self.course3.save()
        self.assertEqual(self.course3.title, "updated_course3")
        
    def test_course_title_max_length(self):
        self.course3.title = "x" * 129
        self.course3.save()
        with self.assertRaises(ValidationError):
            self.course3.full_clean()
    
    def test_course_title_with_blank_values(self):
        self.course3.title = "    "
        self.course3.save()
        with self.assertRaises(ValidationError):
            self.course3.full_clean()
            
    def test_course_startdate_after_enddate(self):
        self.course1.start_date = datetime(2025, 12, 31, 23, 59, 59)
        self.course1.end_date = datetime(2025, 12, 11, 23, 59, 59)
        self.course1.save()
        with self.assertRaises(ValidationError):
            self.course1.full_clean()
        
    def test_course_value_null(self):
        self.course4.full_clean()
        self.assertIsNone(self.course4.outline)
        self.assertIsNone(self.course4.language)
        self.assertIsNone(self.course4.country)
        self.assertIsNone(self.course4.subject)
        self.assertIsNotNone(self.course4.start_date)
        self.assertIsNotNone(self.course4.end_date)
        self.assertEqual(self.course4.visiblity, "private") 
        self.assertFalse(self.course4.is_active)
        self.assertFalse(self.course4.allow_join_requests)
                

            