"""
Course Goals Application Configuration

Signal handlers are connected here.
"""


from django.apps import AppConfig


class CourseGoalsConfig(AppConfig):
    """
    Application Configuration for Course Goals.
    """
    name = 'lms.djangoapps.course_goals'

    def ready(self):
        """
        Connect signal handlers.
        """
