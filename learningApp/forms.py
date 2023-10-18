from learningApp.models import Instructor, Curriculum
from django.forms import ModelForm

class InstructorForm(ModelForm):
    
    class Meta:
        model = Instructor
        fields = ['name', 'photo', 'comment']
        
class CurriculumForm(ModelForm):
    
    class Meta:
        model = Curriculum
        fields = ['course', 'heading', 'heading_intro', 'sub_heading', 'sub_heading_intro']
        
    