from django.shortcuts import render, redirect, get_object_or_404
from learningApp.models import *
from learningApp.forms import InstructorForm, CurriculumForm
from django.contrib import messages
from django.forms import formset_factory
from django.db.models import Count, Avg, Sum, Q
from django.urls import reverse
from django.db import transaction
from reportlab.pdfgen import canvas
from io import BytesIO
from learningApp.pdf import generate_certificate_pdf
from fpdf import FPDF
from django.http import HttpResponse
from tempfile import NamedTemporaryFile
from PIL import Image
import os
from django.conf import settings
from django.http import JsonResponse

def remove_from_cart(request, enroll_id):
    user = request.user
    enroll = get_object_or_404(Enrollment, id=enroll_id)
    if user == enroll.user:
        enroll.delete()
        messages.info(request, f'you removed the course "{enroll.course.title}" from your cart')
        return redirect('enrolled_courses_view')

def enrolled_courses_view(request):
    user = request.user
    enrolled_courses = Enrollment.objects.filter(user=user).order_by('-enrolled_at')

    # Update is_enroll to false
    enrollment_notification = EnrollmentNotification.objects.filter(user=user)
    add_to_cart = EnrollmentNotification.objects.filter(user=user, is_enroll=True).aggregate(counts=Count('enroll'))

    for enroll in enrollment_notification:
        enroll.is_enroll = False
        enroll.save()

    context = {
        'enrolled_courses': enrolled_courses,
        'cart':add_to_cart,

        }
    return render(request, 'learningApp/enrolled_courses.html', context)


def rate_instructor(request, instructor_id):
    user = request.user
    instructor_id = Instructor.objects.get(id = instructor_id)

    existing_review = reviewInstructor.objects.filter(user=user, instructor=instructor_id)

    with transaction.atomic():

        if request.method == 'POST':
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')

            if existing_review:
                for existing_reviews in existing_review:
                    existing_reviews.rating = rating
                    existing_reviews.comment = comment
                    existing_reviews.save()


            rate_instructor, update = reviewInstructor.objects.update_or_create(
                user = user,
                rating = rating,
                comment = comment,
                instructor = instructor_id,
                defaults={'rating': rating, 'comment': comment},
            )
            # if updated:
            #     rate_instructor.save()
            messages.info(request, 'Thank you for rating this instructor. Do you wish to enroll another course?')

            course = instructor_id.course_set.first()
            # get_course_elements = instructor_id.course_set.first()

            if course:
                return redirect(reverse('generate_certificate', args = [course.id]))
        context = {
            'instructors':instructor_id,
        }
        return render(request, 'learningApp/rate_instructor.html', context)

def search(request):
    if request.method =='GET':
        search = request.GET.get('search')
        search_query = Course.objects.filter(Q(title__icontains = search)) if search else None
    if search:
        return render(request, 'learningApp/search.html', {'searches':search_query})
    messages.success(request, f'No course with name {search} yet!')
    return redirect('all_courses')
def news_sub(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if subscriptionNewsletter.objects.filter(email = email).exists():
            messages.info(request, f'Some has already subscribe with this email {email}')
            return redirect('index')
        elif email is None:
            messages.info(request, f'You did not enter email')
            return redirect('index')
        subscriptionNewsletter.objects.create(email = email)
        messages.success(request, 'You subscribed to our newsletter')
        return redirect('index')
    return redirect('index')



def curriculum_form(request):
    course = Course.objects.all()
    formset= formset_factory(CurriculumForm)
    if request.method =='POST':
        form = formset(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.info(request, 'Curriculum created add more')
            return redirect('curriculum_form')
        messages.info(request, 'Erro saving curriculum')
        return redirect('curriculum_form')
    form = CurriculumForm()
    context = {
        'forms':formset,
        'courses':course,
    }
    return render(request, 'learningApp/create_curriculum.html', context)

def review_course(request, course_id):
    the_course_id = Course.objects.get(id=course_id)
    user = request.user

    if not user.is_authenticated:
        messages.error(request, 'You are not permitted here!')
        return redirect('index')

    if request.method == 'POST':
        name = request.POST.get('name')
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')
        photo = request.FILES.get('photo')

        if the_course_id and the_course_id.title:
            course_review =Review(user=user, name = name, course =the_course_id, comment=comment,
                            rating = rating, photo=photo)
            course_review.save()

            messages.info(request, 'Thank you for review this course')
            return redirect('index')

    return render(request, 'learningApp/review.html')


def create_course(request):
    user = request.user
    all_category_list= Category.objects.all()
    if not user.is_instructor:
        messages.error(request, 'You are not permitted here!')
        return redirect('index')
    # if user.is_instructor:
    if request.method == 'POST':
        title = request.POST.get('title')
        price = request.POST.get('price')
        description = request.POST.get('description')
        requirement = request.POST.get('requirement')
        duration = request.POST.get('duration')
        category_id = request.POST.get('category')
        target_audience = request.POST.get('target_audience')
        thumbnail = request.POST.get('thumbnail')

        course =Course(user=user, title = title, price =price, description=description,
                        requirement = requirement, duration=duration,
                        target_audience=target_audience, thumbnail=thumbnail)
        course.save()


        course.categories.add(category_id)
        messages.info(request, 'Saved!')
        return redirect('index')

    context={
        'categories':all_category_list,
    }
    return render(request, 'learningApp/create_course.html', context)

def index(request):
    user =request.user
    intro = Intro.objects.first()
    menu = Menu.objects.all()
    events = upcomingEvent.objects.all()[:3]
    instructors = Instructor.objects.all().order_by('-post_date')[:4]

    add_to_cart = EnrollmentNotification.objects.filter(user=user, is_enroll = True).aggregate(counts = Count('enroll'))
    categories_with_enrollment = Category.objects.annotate(enrollment_count=Count('course__enrollment'))
    # get_url = reverse('category_detail', args =[categories_with_enrollment.first, course.first])
    if request.method == 'POST':
        name = request.POST.get('name')
        # course_id = request.POST['course']  # Get the selected course ID
        comment = request.POST.get('comment')
        photo = request.POST.get('photo')  # Use request.FILES to handle file uploads

        if user.is_instructor and Instructor.objects.filter(name=name).exists:
            messages.info(request, 'You already filled the Instructor detail. Add you courses!')
            return redirect('create_course')
        instructor = Instructor(name=name, comment=comment, photo=photo)
        instructor.save()

        if instructor:
            messages.info(request, 'Instructor data saved!')
            return redirect('create_course')
        messages.info(request, 'Error!')
        return redirect('index')


    context = {
        # 'get_url':get_url,
        'events':events,
        'intros': intro,
        'menus': menu,
        'categories': categories_with_enrollment,
        'instructors':instructors,
        'cart':add_to_cart,
    }

    return render(request, 'learningApp/index.html', context)

def all_courses(request):
    user = request.user
    course_cat = Category.objects.all()

    course = Course.objects.all().order_by('created_at')[:3]

    galary = Course.objects.all().order_by('created_at')[:9]

    add_to_cart = EnrollmentNotification.objects.filter(user=user, is_enroll=True).aggregate(counts=Count('enroll'))

    if request.method =='GET':
        search = request.GET.get('search')
        search_course = Course.objects.filter(Q(title__icontains = search)) if search else None
        if not search:
            messages.info(request, 'Not available')
    context = {
        'searches':search_course,
        'galary':galary,
        'courses':course,

        'categories':course_cat,
        'cart':add_to_cart,
    }
    return render(request, 'learningApp/courses.html', context)

def category_detail(request, category_id):
    category_id = Category.objects.get(id = category_id)
    get_all_course_with_the_same_category = category_id.course_set.all()
    courses_with_user_count = category_id.course_set.annotate(user_count=Count('enrollment', distinct=True),
            average_rating=Avg('review__rating'))
    get_latest_course = Category.objects.all().order_by('-update_date')[0:2]
    events = upcomingEvent.objects.all()[:3]

    add_to_cart = EnrollmentNotification.objects.filter(user=request.user, is_enroll=True).aggregate(counts=Count('enroll'))

    instructors =Instructor.objects.all()[:4]
    context ={
        'events':events,
        'instructors':instructors,
        'courses_with_user_count': courses_with_user_count,

        'categories':category_id,
        'latest_course':get_latest_course,
        'cart':add_to_cart,
    }
    return render(request, 'learningApp/same_cat_courses.html', context)

def course_detail(request, course_id):
    user=request.user
    try:
        course = Course.objects.get(id=course_id)
        enroll = course.enrollment_set.filter(user = user)

    except Course.DoesNotExist:
        return render(request, 'learningApp/error_template.html', {'message': 'Course not found'})

    lesson = course.lesson_set.all().count
    instructor = Instructor.objects.filter(course = course)
    get_instructor = instructor.first()
    # rating_instructor = reviewInstructor.objects.filter(instructor=get_instructor).annotate(rating = Avg('rating'))
    add_to_cart = EnrollmentNotification.objects.filter(user=user, is_enroll=True).aggregate(counts=Count('enroll'))

    # first_instructor = instructor.first()

    faq = Questions.objects.all()
    latest_course = Course.objects.exclude(title=course.title)[:3]
    curriculum = Curriculum.objects.all()


    reviews = Review.objects.filter(course=course).annotate(course_rating=Avg('rating'))
    num_reviews = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    first_instructor = Instructor.objects.filter(course=course).first()
    reviews_instructor= reviewInstructor.objects.filter(instructor__id=first_instructor.id).aggregate(
        course_rating=Avg('rating'),
        review_count = Count('comment'),
        quiz_count = Count('instructor__course__quiz')
    )

    # Calculate the number of reviews in each rating category (1 to 5 stars)
    rating_counts = reviews.values('rating').annotate(count=Count('rating')).order_by('rating')

    rating_coun = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    # Calculate the number of reviews in each rating category (1 to 5 stars)
    for rating_count in reviews.values('rating').annotate(count=Count('rating')).order_by('rating'):
        rating = rating_count['rating']
        count = rating_count['count']
        rating_coun[rating] = count

    # Calculate the percentage widths for each rating category
    total_reviews = reviews.count()
    rating_percentages = [0] * 5

    for rating in range(1, 6):
        index = 5 - rating
        count = rating_coun[rating]
        rating_percentages[index] = (count / total_reviews) * 100


    enrollment = None
    if enroll :
        return redirect(reverse('lessonpage', args=[course.id]))
    elif request.method == 'POST' and 'enrolled' in request.POST:
        if enrollment is None:
            enrollment = Enrollment(user=request.user, course=course)
            enrollment.save()
            messages.info(request, f'You successfully enrolled in this course: {course.title}')

            return redirect(reverse('enrolled_courses_view'))
            # return redirect(reverse('lessonpage', args=[course.id]))
    context = {
        'average_rating': average_rating,
        'rating_percentages': rating_percentages,
        'reviews': reviews,
        'num_reviews': num_reviews,
        'latest_course': latest_course,
        'courses': course,
        'faqs': faq,
        'curs': curriculum,
        'instructors':instructor,
        'lessons':lesson,
        'enroll':enroll,
        'cart':add_to_cart,
        'reviewinstructor':reviews_instructor,
    }
    return render(request, 'learningApp/course.html', context)


def reply_comment(request, course_id, review_id):
    user = request.user
    the_course_id = Course.objects.get(id=course_id)
    get_review = Review.objects.filter(course=review_id)
    reply_url = reverse('reply_comment', args=[course_id, review.id])


    for review in get_review:
        review.replies = Review.objects.filter(parent_comment=review)

    if not user.is_authenticated:
        messages.error(request, 'You are not permitted here!')
        return redirect('index')

    if request.method == 'POST':
        # name = request.POST.get('name')
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')
        # photo = request.FILES.get('photo')

        if the_course_id and the_course_id.title:
            course_review =Review(user=user, name = list(user.first_name and user.last_name),
                                  course =the_course_id, comment=comment,
                                photo=the_course_id.user.photo,parent_comment = get_review
                                )
            course_review.save()
            # if course_review:
            #     course_review.parent_comment.add(get_review)

            messages.info(request, 'Thank you for review this course')
            return redirect('index')
    context = {
        'get_review':get_review,
        'reply_url':reply_url,
    }
    return render(request, 'learningApp/reply.html', context)

def reply_review(request, review_id):
    user = request.user
    get_review_id = Review.objects.get(id = review_id)

    if request.method == 'POST':
        comment = request.POST.get('comment')

        ReplyReview.objects.create(
            user =user,
            parent_review =get_review_id,
            comment_text = comment,


        )
        messages.info(request, f'You reply to {get_review_id.user}')
        # return redirect(reverse('course_detail', args=[str(get_review_id.course.id)]))
        return redirect('course_detail', course_id=get_review_id.course.title)
    return render(request, 'learningApp/reply.html', {})


def likereview(request, review_id):
    user = request.user
    review = Review.objects.get(id=review_id)

    if not user.is_authenticated:
        messages.info(request, 'You have to login first')
        return redirect('course_detail', course_id=review.course.title)

    if request.method == "POST" and "like" in request.POST:
        if user in review.likes.all():
            # User has already liked the review, so we will remove the like.
            review.likes.remove(user)
            return redirect('course_detail', course_id=review.course.title)
        else:
            # User hasn't liked the review, so we will add the like.
            review.likes.add(user)
            return redirect('course_detail', course_id=review.course.title)

    return redirect('course_detail', course_id=review.course.title)

def likereply(request, replyreview_id):
    user = request.user
    review = ReplyReview.objects.get(id=replyreview_id)

    if not user.is_authenticated:
        messages.info(request, 'You have to login first')
        return redirect('course_detail', course_id=review.parent_review.course.title)

    if request.method == "POST" and "like" in request.POST:
        if user in review.likes.all():
            # User has already liked the review, so we will remove the like.
            review.likes.remove(user)
            return redirect('course_detail', course_id=review.parent_review.course.title)

        else:
            # User hasn't liked the review, so we will add the like.
            review.likes.add(user)
            return redirect('course_detail', course_id=review.parent_review.course.title)


    return redirect('course_detail', course_id=review.parent_review.course.title)


def lessonpage(request, course_id):
    user = request.user
    add_to_cart = EnrollmentNotification.objects.filter(user=user, is_enroll=True).aggregate(counts=Count('enroll'))

    certificate=None
    if certificate:
        messages.info(request, f'You have already gotton your certificate on this course. Enroll another course ')
        return redirect('all_courses')
    try:
        course = Course.objects.get(id = course_id)
        lesson =Lesson.objects.filter(course = course)
        tutors = Instructor.objects.filter(course__lesson=lesson.first()) if lesson else []

        certificate = Certificate.objects.filter(user=user, course=course)
    except Course.DoesNotExist:
        messages.info(request, 'No lesson uploaded yet!')

    context = {
        'lessons':lesson,
        'tutors':tutors,
        'course':course,
        'certificate':certificate,
        'cart':add_to_cart,
    }
    # Generate the URL for the quiz detail page (if lessons exist)
    # quiz_url = None
    # if lesson:
    #     first_lesson = lesson.first()
    quiz_url = reverse('quiz_page', args=[course.id])

    context['quiz_url'] = quiz_url
    return render(request, 'learningApp/lesson.html', context)

def quiz_page(request, course_id):
    add_to_cart = EnrollmentNotification.objects.filter(user=request.user, is_enroll=True).aggregate(counts=Count('enroll'))

    try:
        courses = get_object_or_404(Course, pk=course_id)
        quiz = Quiz.objects.filter(course=courses)
        score = QuizScore.objects.filter(user=request.user, quiz__course=courses).annotate(score_count=Sum('score'))

        # Get user answers related to the current user and the quiz questions
        user_answers = UserAnswer.objects.filter(
            user=request.user,
            question__in=quiz
        )
        if not quiz:
            messages.info(request, 'No quiz uploaded to this course yet!')
            return redirect(reverse('lessonpage', args = [courses.id]))

    except Course.DoesNotExist:
        messages.info(request, 'No quiz loaded yet!')


    if request.method == 'POST':
        user = request.user

        # Use a transaction to ensure consistency in the database
        with transaction.atomic():
            QuizScore.objects.filter(user=user, quiz__course=courses).delete()
            for question in quiz:
                question_id = request.POST.get(f'question_{question.id}')
                selected_option = request.POST.get(f'question_{question.id}')
                is_correct = question.answers == selected_option  # Check if the selected option is correct

                # Add an "answered_correctly" attribute to the question
                question.answered_correctly = is_correct

                # Delete the previous user answer for the same question
                UserAnswer.objects.filter(
                    user=user,
                    question=question
                ).delete()

                # Create the new user answer
                UserAnswer.objects.create(
                    user=user,
                    question=question,
                    selected_option=selected_option,
                    is_correct=is_correct
                )


                # Calculate the total score for the user within the current course
                total_score = QuizScore.objects.filter(user=user, quiz__course=courses).aggregate(total_score=Sum('score'))['total_score'] or 0

                quiz_score = QuizScore.objects.get(user=user, quiz=quiz.first())

        return redirect(reverse('quiz_page', args=[courses.id]))

    context = {
        'quiz': quiz,
        'scores': score,
        # 'cumulative': cumulative,
        'user_answers': user_answers,
        'cart':add_to_cart,

    }
    return render(request, 'learningApp/quiz.html', context)

#
def view_score(request, course_id):
    user = request.user
    courses = get_object_or_404(Course, pk=course_id)
    course_url = reverse('view_score', args = [courses.id])
    add_to_cart = EnrollmentNotification.objects.filter(user=user, is_enroll=True).aggregate(counts=Count('enroll'))

    try:
        # Calculate the cumulative score by summing up scores from all related QuizScore instances
        cumulative_score = CumulativeScore.objects.get(user=user, course=courses).total_score
        quiz_count = Quiz.objects.filter(course=courses).count()

        get_half = quiz_count / 2

        if cumulative_score is not None and cumulative_score >= get_half:
            messages.info(request, f'Congratulations {user}, you have passed this course!')
        else:
            messages.info(request, f'Oop! Sorry {user}, you have failed this course. Please try again.')

    except CumulativeScore.DoesNotExist:
        cumulative_score = None
        quiz_count = 0  # Set to 0 when the user doesn't have a cumulative score.

    context = {
        'score': cumulative_score,
        'outof': quiz_count,
        'course_url':course_url,
        'get_half':get_half,
        'courses':courses,
        'cart':add_to_cart
    }

    return render(request, 'learningApp/quiz_result.html', context)

def generate_certificate(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    passing_score_threshold = 0.5
    instructor = Instructor.objects.filter(course = course)

    try:
        cumulative_score = CumulativeScore.objects.get(user=user, course=course).total_score
        total_possible_score = Quiz.objects.filter(course=course).aggregate(total_score=Sum('points'))['total_score'] or 0
        if cumulative_score >= passing_score_threshold * total_possible_score:
            # User has passed the course, generate a certificate
            certificate = Certificate(user=user, course=course)
            certificate.save()

            context = {
                'certificate': certificate,
                'course':course,
                'instructor':instructor,
            }

            return render(request, 'learningApp/certificate.html', context)

    except CumulativeScore.DoesNotExist:
        pass

    # Redirect the user to the course view if they haven't passed or don't have a score
    return redirect('index')

def generate_certificate_pdf(request, certificate_id):
    try:
        # Retrieve the certificate object from the database
        certificate = get_object_or_404(Certificate, id=certificate_id)

        # Create a PDF object with custom dimensions (adjust as needed)
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()

        # Set font and text color
        pdf.add_font('custom_font', '', os.path.join(settings.BASE_DIR, 'learningApp/static/learningApp/fonts/Skranji/Skranji-Regular.ttf'), uni=True)
        pdf.set_font('custom_font', '', 18)  # Change to your custom font style and size
        pdf.set_text_color(0, 0, 0)

        # Convert the JPEG logo to a PNG image (replace with your actual logo path)
        logo_path = os.path.join(settings.BASE_DIR, 'learningApp/static/learningApp/images/certificate.jpg')
        png_logo_path = os.path.join(settings.BASE_DIR, 'learningApp/static/learningApp/images/certificate_logo.png')

        img = Image.open(logo_path)
        img.save(png_logo_path, "PNG")

        # Add the PNG logo to the PDF (centered)
        pdf.image(png_logo_path, x=70, w=70)

        # Certificate title
        pdf.cell(0, 20, "Certificate of Completion", 0, 1, "C")

        # Add some spacing after the title
        pdf.cell(0, 10, "", 0, 1)

        # "Issued to" section with italic style
        pdf.set_font(family="Arial", style="I", size=12)
        pdf.cell(0, 15, "Issued to:", 0, 1, "C")

        # User's name with custom font style and underline
        user_name = f"{certificate.user.first_name} {certificate.user.last_name}"
        pdf.set_font('custom_font', 'U', 20)  # Change to your custom font style and size
        pdf.cell(0, 15, user_name, 0, 1, "C")

        # Course title
        pdf.set_font(family="Arial", style="B", size=14)
        course_title = certificate.course.title
        pdf.cell(0, 15, f"For successfully completing the course:", 0, 1, "C")
        pdf.cell(0, 15, course_title, 0, 1, "C")

        # Add some spacing before the issued date
        pdf.cell(0, 10, "", 0, 1)

        # Issued date
        pdf.set_font(family="Arial", style="", size=12)
        issued_date = certificate.issued_date.strftime("%d/%m/%Y")
        pdf.cell(0, 15, f"Issued on: {issued_date}", 0, 1, "C")

        # Add some spacing before the signature section
        pdf.cell(0, 20, "", 0, 1)

        # Signature section
        pdf.set_font(family="Arial", style="B", size=14)
        pdf.cell(0, 10, "", 0, 1)  # Adjust vertical spacing
        pdf.cell(0, 10, "Signature:", 0, 1, "L")

        # Printed name
        pdf.set_font(family="Arial", style="", size=12)
        pdf.cell(0, 10, "Printed Name:", 0, 1, "L")

        # Add some spacing for the actual signature
        pdf.cell(0, 10, "", 0, 1)

        # Serial number and certificate ID (make these unique for each certificate)
        serial_number = "SN: 12345"  # Replace with a unique serial number
        certificate_id = f"Certificate ID: {certificate.id}"  # Use the actual certificate ID
        pdf.cell(0, 10, serial_number, 0, 1, "L")
        pdf.cell(0, 10, certificate_id, 0, 1, "L")

        # Set background color and border
        pdf.set_fill_color(255, 255, 205)  # Background color (white)
        pdf.set_draw_color(0, 0, 0)  # Border color (black)
        pdf.set_line_width(1)  # Border width
        pdf.rect(10, 10, 190, 270, 'D')  # Rectangle (border)

        # Create a temporary file to save the PDF
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)

        # Read the contents of the temporary file
        with open(tmp_file.name, 'rb') as pdf_file:
            pdf_content = pdf_file.read()

        # Set the content type and response headers
        response = HttpResponse(pdf_content, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="certificate_{certificate_id}.pdf"'

        return response
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponse("An error occurred while generating the PDF certificate.")
