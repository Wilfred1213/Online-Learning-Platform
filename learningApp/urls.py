from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name = 'index'),
    path('all_courses/', views.all_courses, name = 'all_courses'),
    path('curriculum_form/', views.curriculum_form, name = 'curriculum_form'),
    path('create_course/', views.create_course, name = 'create_course'),
    path('category_detail/<int:category_id>/', views.category_detail, name = 'category_detail'),
    path('course_detail/<int:course_id>/', views.course_detail, name = 'course_detail'),
    path('review_course/<int:course_id>/', views.review_course, name = 'review_course'),
    path('reply_comment/<int:course_id>/<int:review_id>/', views.reply_comment, name = 'reply_comment'),
    path('reply_review/<int:review_id>/', views.reply_review, name = 'reply_review'),
    path('likereview/<int:review_id>/', views.likereview, name = 'likereview'),
    path('likereply/<int:replyreview_id>/', views.likereply, name = 'likereply'),
    path('lessonpage/<int:course_id>/', views.lessonpage, name = 'lessonpage'),
    path('quiz_page/<int:course_id>/', views.quiz_page, name = 'quiz_page'),
    path('view_score/<int:course_id>/', views.view_score, name='view_score'),
    path('generate_certificate/<int:course_id>/', views.generate_certificate, name='generate_certificate'),
    path('generate_certificate_pdf/<int:certificate_id>/', views.generate_certificate_pdf, name='generate_certificate_pdf'),
    path('subscription', views.news_sub, name='subscription'),
    path('search', views.search, name='search'),
    path('rate_instructor/<int:instructor_id>/', views.rate_instructor, name='rate_instructor'),
    # path('get_enrollment_count/', views.get_enrollment_count, name = 'get_enrollment_count'),
    path('enrolled_courses_view/', views.enrolled_courses_view, name = 'enrolled_courses_view'),
    path('remove_from_cart/<int:enroll_id>/', views.remove_from_cart, name = 'remove_from_cart'),

]