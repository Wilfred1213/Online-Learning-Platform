from django.db import models
from django.conf import settings
from django.utils import timezone
from embed_video.fields import EmbedVideoField
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Sum
from django.utils import timezone

# Category model to categorize courses
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=10000, default = 'description')
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True)
    update_date = models.DateTimeField(default=timezone.now)
    
    
    def __str__(self):
        return self.name

    def display_image(self):
        if self.thumbnail.url:
            return self.thumbnail.url
        return None
  
class Instructor(models.Model):
    name =models.CharField(max_length=200)
    photo = models.ImageField(upload_to='instructors/')
    comment =models.TextField(max_length=10000, null = False)
    post_date = models.DateTimeField(auto_now_add=True)
    position = models.CharField(max_length = 100, default='Position')
    
    def __str__(self):
        return self.name

    def display_image(self):
        if self.photo.url:
            return self.photo.url
        return None
class reviewInstructor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, null=True)
    comment = models.TextField(max_length =500, null=True)

# Course model
class Course(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    categories = models.ManyToManyField(Category)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    instructor = models.ManyToManyField(Instructor)
    price = models.IntegerField(default=0)
    requirement= models.TextField(max_length=10000, default = 'requirement')
    target_audience= models.TextField(max_length=10000)
    update_date = models.DateTimeField(default=timezone.now)
    duration =models.CharField(max_length=20, blank = True)
    
    def __str__(self):
        return f'id: {self.id} Title: {self.title} - Created by: {self.user} - Categories: {", ".join(str(cat) for cat in self.categories.all())} - Instructors: {", ".join(str(instruc) for instruc in self.instructor.all())}'

    def display_image(self):
        if self.thumbnail.url:
            return self.thumbnail.url
        return None
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name =models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.IntegerField(default =0)
    comment =models.TextField(max_length=10000, null = False)
    photo = models.ImageField(upload_to='review_image/', blank=False, null=True)
    post_date = models.DateTimeField(auto_now_add=True)
    
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)
    
    
    def __str__(self):
        return f"Comment by {self.user.username} - comment: {self.comment}"

    def display_image(self):
        if self.photo.url:
            return self.photo.url
        return None

class ReplyReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent_review = models.ForeignKey(Review, on_delete=models.CASCADE)
    comment_text =models.TextField(max_length=10000, null = False)
    post_date = models.DateTimeField(auto_now_add=True)
    
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked', blank=True)
    

    def __str__(self):
        return self.comment_text

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    # order = models.PositiveIntegerField()
    video = EmbedVideoField(default = 'www')

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course.title

class EnrollmentNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    enroll = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    is_enroll = models.BooleanField(default = False)

    def __str__(self):
        return 'User: %s Course: %s' % (self.user, self.enroll.course.title)

@receiver(post_save, sender = Enrollment)
def enrollment_count(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        enroll = instance
        enroll, updated = EnrollmentNotification.objects.update_or_create(
            user = user, enroll = enroll, is_enroll = True
        )

# Progress model to track user progress within a course
class Progress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

class Intro(models.Model):
    welcoming_note = models.CharField(max_length=100, null = True)
    description =models.TextField(max_length=100, null = True)
    
class Menu(models.Model):
    title = models.CharField(max_length=1000, null = True)
    description =models.TextField(max_length=100, null = True)
    icon =models.ImageField(upload_to='menu_images/')
    
class Curriculum(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=False)
    heading =models.TextField(max_length=10000, null = True)
    heading_intro =models.TextField(max_length=10000, null = True)
    sub_heading=models.TextField(max_length=10000, null = True)
    sub_heading_intro =models.TextField(max_length=10000, null = True, blank=True)
    
class Questions(models.Model):
    title = models.CharField(max_length=1000, null = True)
    asks =models.TextField(max_length=1000, null = True)
    answers =models.TextField(max_length=1000, null = True)
    
    def __str__(self):
        return f'Title: {self.title}'
    
class Quiz(models.Model):
    # lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    option1 = models.CharField(max_length=1000, null=True)
    option2 = models.CharField(max_length=1000, null=True)
    option3 = models.CharField(max_length=1000, null=True)
    option4 = models.CharField(max_length=1000, null=True)
    asks = models.TextField(max_length=1000, null=True)
    answers = models.TextField(max_length=1000, null=True)
    points = models.IntegerField(default=1)

    def __str__(self):
        return f'Question: {self.asks}'

class UserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1000, null=True) 
    is_correct = models.BooleanField(default = False)

    def __str__(self):
        return f'User: {self.user}, Question: {self.question.asks}, Selected Option: {self.selected_option}, Correct: {self.is_correct}'

@receiver(post_save, sender=UserAnswer)
def save_user_score(sender, created, instance, **kwargs):
    if created:
        user = instance.user
        quiz = instance.question
        score_to_add = 1 if instance.is_correct else 0  # Adjust the scoring system as needed

        # Update or create a QuizScore instance for the user and quiz
        QuizScore.objects.update_or_create(
            user=user,
            quiz=quiz,
            defaults={'score': score_to_add}
        )


class QuizScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null = True)
    score = models.IntegerField()  # Store the user's score for the quiz

    def __str__(self):
        return f'User: {self.user}, Lesson: {self.quiz}, Score: {self.score}'

@receiver(post_save, sender=QuizScore)
def update_cumulative_score(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        quiz = instance.quiz
        course = quiz.course

        # Calculate the total score for the user within the current course
        total_score = (
            QuizScore.objects
            .filter(user=user, quiz__course=course)
            .aggregate(total_score=models.Sum('score'))['total_score'] or 0
        )

        # Create or update the cumulative score for the user within the current course
        cumulative_score, _ = CumulativeScore.objects.get_or_create(
            user=user,
            course=course
        )
        cumulative_score.total_score = total_score
        cumulative_score.save()

class CumulativeScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    # quiz_score = models.ForeignKey('QuizScore', on_delete=models.CASCADE, null=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, null=True)
    # quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, null=True)


    def __str__(self):
        return f'User: {self.user}, Total Score: {self.total_score}'

    class Meta:
        unique_together = ('user', 'course')

class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issued_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Certificate for {self.user.username} - {self.course.title}'

class upcomingEvent(models.Model):
    title = models.CharField(max_length=1000)
    thumbnail = models.ImageField(upload_to ='events')
    event_date = models.DateTimeField(auto_now_add=True)
    event_date_future = models.DateField(default = timezone.now)
    description = models.TextField(max_length = 10000)
    address = models.CharField(max_length = 500)
    time = models.CharField(max_length = 20, null = True)

    def display_image(self):
        if self.thumbnail.url:
            return self.thumbnail.url
        return None

class subscriptionNewsletter(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email
