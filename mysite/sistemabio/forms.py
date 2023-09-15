from django.forms import ModelForm
from django import forms
from .models import Usuario, Sesion

class InquilinoForm(forms.ModelForm): 
    class Meta:
        model = Usuario
        fields = ['nombre','ap_paterno','ap_materno', 'curp','piso','departamento','telefono', 'correo', 'fecha_nac', 'id_perfil', 'id_status']
        # self.fields['fecha_nac'].widget.attrs[]
    def __init__(self, *args,**kwargs):
        super(InquilinoForm,self).__init__(*args,**kwargs)
        self.fields['id_perfil'].widget.attrs['class']= 'form-control'
        self.fields['id_status'].widget.attrs['class']= 'form-control'
                                              
   

class SesionForm(ModelForm):
    class Meta:
        model = Sesion
        fields = ['id_usuario']
    def __init__(self, *args,**kwargs):
         super(SesionForm,self).__init__(*args,**kwargs)
        # self.fields['id_tipo_sesion'].widget.attrs['class']='form-control'
         self.fields['id_usuario'].widget.attrs['class']= 'form-control'

class SesionForm2(ModelForm):
    class Meta:
        model = Sesion
        fields = ['dato' ]
    def __init__(self, *args,**kwargs):
        super(SesionForm2,self).__init__(*args,**kwargs)
        
        self.fields['dato'].widget.attrs['class']= 'form-control'

class SesionForm3(ModelForm):
    class Meta:
        model = Sesion
        fields = ['id_usuario', 'dato','id_tipo_sesion']
    def __init__(self, *args,**kwargs):
         super(SesionForm3,self).__init__(*args,**kwargs)
         
         self.fields['id_usuario'].widget.attrs['class']= 'form-control' 
         self.fields['dato'].widget.attrs['class']='form-control' 
         self.fields['id_tipo_sesion'].widget.value='1'


