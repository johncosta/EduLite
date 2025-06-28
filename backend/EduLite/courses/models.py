# backend/Edulite/courses/models.py
# Contains course models, course modules, course membership models, course chatrooms

from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from chat.models import ChatRoom
from .model_choices import (
    COUNTRY_CHOICES,
    LANGUAGE_CHOICES,
    SUBJECT_CHOICES,
    COURSE_VISIBILITY_CHOICES,
    COURSE_ROLE_CHOICES,
    COURSE_MEMBERSHIP_STATUS,
)

User = get_user_model()


class Course(models.Model):
    """
    A course is a collection of modules that are taught by a teacher to a group of students.
    which can be public, private, or restricted.
    """

    title = models.CharField(blank=False, null=False, max_length=128)
    outline = models.TextField(blank=True, null=True, max_length=1000)

    language = models.CharField(
        max_length=64, choices=LANGUAGE_CHOICES, blank=True, null=True
    )
    country = models.CharField(
        max_length=64, choices=COUNTRY_CHOICES, blank=True, null=True
    )
    subject = models.CharField(
        max_length=64, choices=SUBJECT_CHOICES, blank=True, null=True
    )

    # the visibiliiity choices include: public, private, restricted
    visiblity = models.CharField(
        max_length=64, choices=COURSE_VISIBILITY_CHOICES, null=False, default="private"
    )

    # the start and end date are the dates when the course is available to students
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(
        default=datetime(2099, 12, 31, 23, 59, 59),  # default to a far future date
        blank=True,
        null=True,
    )

    # the is_active flag is used to indicate if the course is currently active
    is_active = models.BooleanField(default=False)

    # the allow_join_requests flag is used to indicate if the course allows join requests
    allow_join_requests = models.BooleanField(default=False)

    def clean(self) -> None:
        return super().clean()

    def __str__(self) -> str:
        return self.title


class CourseModule(models.Model):
    """
    Represents a modular unit within a Course. Each module can be dynamically linked
    to different types of content such as lectures, quizzes, assignments, etc.

    This flexible structure is implemented using Django's GenericForeignKey, which
    allows associating the module with any content type (model) instance dynamically.

    Reference:
    Django Documentation – Content types framework
    https://docs.djangoproject.com/en/stable/ref/contrib/contenttypes/
    """

    course = models.ForeignKey(
        Course, related_name="course_modules", on_delete=models.CASCADE
    )
    # the title of the module
    title = models.CharField(max_length=128, blank=True, null=True)
    
    # Display order of the module within the course
    order = models.PositiveIntegerField(default=0)

    # the content_type and object_id are used to link the module to a specific content object
    # example: Lecture, Quiz, Assignment, etc.
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="course_contents",
        help_text="The type of the content object",
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    
    # the index is used to speed up the lookup of the content_object
    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        
    def __str__(self):
        if self.title:
            return f"{self.course.title} - {self.title}"
        else:
            return f"{self.course.title} module {self.order}"


class CourseMembership(models.Model):
    """
    Represents a user's membership in a course.
    A user can have multiple memberships in a course, each with a different role.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="course_memberships"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(
        max_length=32, choices=COURSE_ROLE_CHOICES, default="student"
    )
    status = models.CharField(
        max_length=64, choices=COURSE_MEMBERSHIP_STATUS, default="pending"
    )

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.role}"


class CourseChatRoom(models.Model):
    """
    Represents a chatroom associated with a course.
    This allows for a multiple chatrooms to be shared across single course.
    """

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_chatrooms"
    )
    chatroom = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="course_links"
    )
    created_by = models.ForeignKey(
        User, related_name="chatroom_user", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.course.title} - {self.chatroom.title}"