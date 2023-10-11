from django.http import HttpResponseRedirect,HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.template import loader
import datetime
import base64
import os
import errno
import cv2
#creatiionform
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Usuario, Sesion
from .forms import InquilinoForm, SesionForm, SesionForm2, SesionForm3


#Administrador e Index
def index(request):
     title='Index'
    # return HttpResponse("Hello, world. You're at the polls index.")
     return render (request,"sistemabio/index.html",{
          'mytitle':title
     })  
def signup(request):
        if request.method == 'GET':
            print('enviando formulario')
            title='Registrar'
            return render(request, "sistemabio/signup.html",{
                'mytitle':title,
                'form':UserCreationForm
            } ) 
        else:
             if request.POST["password1"] == request.POST["password2"]:
                  #register user
                  try:
                    user = User.objects.create_user(username=request.POST["username"],
                                                   password=request.POST["password1"])
                    user.save()
                    login(request, user)
                    return redirect('/sistemabio/principal/')
                   # return HttpResponse('User creado satisfactoriamente')        
                  except IntegrityError:
                       return render(request, "sistemabio/signup.html",{
                            'error': 'El user ya existe',
                            'form':UserCreationForm
                        } ) 
             return render(request, "sistemabio/signup.html",{
                            'error': 'Passwords no coinciden',
                            'form':UserCreationForm
                        } )   
 

   #return render(request, "sistemabio/signin.html",
def signin(request):
         if request.method == "GET":
            title='Iniciar sesion'
            return render(request, "sistemabio/signin.html",{
                'mytitle':title,
                'form':AuthenticationForm
            } )        
         else:
              user = authenticate( request, username=request.POST['username'], password=request.POST['password'])
              if user is None:
                return render(request, 'sistemabio/signin.html',{
                    'error': "usuario o password es incorrecto.",
                    'form': AuthenticationForm
                    })

              login(request, user)
              return redirect('/sistemabio/principal/')
            
   #return render(request, "sistemabio/signin.html",
@login_required
def principal(request):
     title='Principal Administrador'
     return render (request,"sistemabio/principal_2.html",{
          'mytitle':title
     })
@login_required
def signout(request):
     logout(request)
     messages.warning(request,"Estás desconectado ahora. Inicia sesión")
     return redirect('/sistemabio/signin/')
def about(request):
     title='About'
     return render (request,"sistemabio/about.html",{
          'mytitle':title
     })
def perfil_administrador(request):
     title='Perfil administrador'
     return render (request,"sistemabio/administradores/perfil.html",{
          'mytitle':title
     })
def administradores(request):
     title='Administradores'
     return render (request,"sistemabio/administradores/administradores.html",{
          'mytitle':title
     })
# Inquiinos
def inquilinos(request):
     inquilinos = Usuario.objects.all().order_by('id_usuario')
     paginacion = Paginator(inquilinos,20)
     page_num = request.GET.get('page')
     page = paginacion.get_page(page_num)
     title='Inquilinos'
     sesiones = Sesion.objects.all()
     return render (request,"sistemabio/inquilinos/all-inquilinos.html",{
          'mytitle':title,
          'count': paginacion.count,
          'inquilinos':inquilinos,
          'sesiones': sesiones
     })
@login_required
def new_inquilino(request):
     if request.method == "GET":
        form=  InquilinoForm
        return render(request, 'sistemabio/inquilinos/new-inquilino.html', 
                      {"form":  InquilinoForm })   
     else:
        # print(request.POST)
        # return render(request, 'sistemabio/inquilinos/new-inquilino.html', {"form":  InquilinoForm})
        # commit=False es para procesar los datos antes de guardar, se usa cuando no tienes todos tus 
        # campos llenos de ese form   new_inquilino = form.save()  new_inquilino.save()
        try:
            form = InquilinoForm(request.POST)
            if form.is_valid():
               form.save()
               # print('form ', form['nombre'].value())
               # print('form usuario : ', form['nombre'].value(),  form['ap_paterno'].value(),  form['ap_materno'].value() ) 
            print("Formulario es ", form.is_valid())
            messages.success(request," El registro ha sido un éxito.")
            inquilino = get_object_or_404(Usuario, nombre=form['nombre'].value())
            print('inquilino: ', inquilino.id_usuario)
          #   print('usuario id facial ', inquilino.id_usuario)
            personName = str(inquilino.id_usuario) + inquilino.nombre + inquilino.ap_paterno + inquilino.ap_materno
            print("Nombre de personName es: ", personName)
            dataPath = 'C:/Users/yobis/Desktop/sistemabiors/SistemaBiometricoJessi/mysite/sistemabio/static/inquilinos'
            personPath = dataPath + '/' + personName
            print("Nombre de carpeta es: ", personPath)
            try:
                 os.mkdir(personPath, mode=0o755)
                 print('Carpeta creada: ',personPath)
            except OSError as e:
                 if e.errno!=errno.EEXIST:
                      raise
            return redirect('/sistemabio/new_biometricos/')
        except ValueError:
            messages.error(request, "Error no se creo el inquilino.")
            return render(request, 'sistemabio/inquilinos/new-inquilino.html', 
                          {"form":  InquilinoForm , 
                           "error": "Error creando el inquilino."})
     
@login_required
def new_biometricos(request):
      if request.method == "GET":
         form= SesionForm
         inquilinos = Usuario.objects.all()
         return render(request, 'sistemabio/inquilinos/new-biometricos.html', 
                       {"form": SesionForm,
                        'inquilinos': inquilinos
                        })   
      else:
         form= SesionForm
         inquilinos = Usuario.objects.all()
         return render(request, 'sistemabio/inquilinos/new-biometricos.html', 
                       {"form": SesionForm,
                        'inquilinos': inquilinos
                        })  

@login_required
def new_biometrico(request, usuario_id):
     if request.method == "GET":
        inquilino = get_object_or_404(Usuario,pk=usuario_id)
        form= SesionForm(instance=inquilino)
        return render(request, 'sistemabio/inquilinos/new-biometrico.html', 
                      {"form": SesionForm, 'inquilino':inquilino,
                       })   
     else:
        # print(request.POST)
        # return render(request, 'sistemabio/inquilinos/new-inquilino.html', {"form":  InquilinoForm})
        try:
            form = SesionForm(request.POST)
            new_biometricos = form.save(commit=False)
            new_biometricos.save()
            messages.success(request," El registro biométrico ha sido un éxito.")
            return redirect('/sistemabio/new_biometrico/')
        except ValueError:
            messages.error(request, "Error no se registro el biométrico.")
            return render(request, 'sistemabio/inquilinos/new-biometrico.html', 
                          {"form":  SesionForm,
                           "error": "Error registrando el biométrico."})
        
def search_inquilino(request):
     #buscar por tipo de usuario
     busqueda = request.POST.get("buscar")
     print('nusqueda es ',busqueda)
     nombre = request.POST.get("nombre")
     print('nombre es ',nombre)
     piso = request.POST.get("piso")
     print('npiso es ',piso)
     departamento = request.POST.get("departamento")
     print('ndepartamento es ',departamento)
     inquilinos = Usuario.objects.all()
     if busqueda:
        inquilinos = Usuario.objects.filter(
            Q(piso__icontains = busqueda) | 
            Q(nombre__icontains = busqueda) |
            Q(curp__icontains = busqueda) |
            Q(departamento__icontains = busqueda)
        ).distinct()  
     if nombre:
        inquilinos = Usuario.objects.filter(
            Q(nombre__icontains = nombre) 
        ).distinct()  
        print('nombre des ',nombre)
     if piso:
        inquilinos = Usuario.objects.filter(
            Q(piso__icontains = piso) 
        ).distinct() 
        print('npiso des ',piso) 
     if departamento:
        inquilinos = Usuario.objects.filter(
            Q(departamento__icontains = departamento)
        ).distinct() 
        print('ndepartamento des ',departamento)
        print('inquilino es ',inquilinos)
    # inquilino = get_object_or_404(Usuario,pk=inquilino_para)
    #  inquilinos = Usuario.objects.filter(nombre='jessica sanchez pruebaF5')
     title='search'
     return render (request,"sistemabio/inquilinos/s-inquilinos.html",{
          'mytitle':title,
          'inquilinos':inquilinos
     })
#     
def detail_inquilino(request, usuario_id):
    inquilino = get_object_or_404(Usuario,id_usuario=usuario_id)
    sesiones =  Sesion.objects.all().filter(id_usuario_id=usuario_id).values() 
#    sesiones =  Sesion.objects.filter(id_usuario=1).values('id_sesion', 'id_usuario_id', 'id_tipo_sesion', 'completado', 'dato', 'fecha_creacion', 'fecha_actualizacion')
    print('usuario id ', usuario_id)
    print(sesiones)
    print('................')
    for sesion in sesiones:
     #    print('dato: ',sesion)
     #    print('dato: ',sesion['id_sesion']) para acceder a los campos es con '' dentro de corchetes
        print('=======================')   
        print('dato: ',sesion['dato'])
        #tenemos los numeros en byte que es la variable sesion['dato']
        #por lo que solo falta codificarla en base64 cpn la siguiente linea
        pytho = base64.b64encode(sesion['dato'])
        #ahora la  decodificamos de bytes a caracteres
        python642 = pytho.decode('utf-8')
        print(pytho)
        print('-------------------------------')
        print(python642)
        print('+++++++++++++++++++++++++++++++++')
        python6423 = str(python642).replace('dataimage/jpegbase64','data:image/jpeg;base64,')
     #     python6423 = 'data:image/jpg;base64,' + str(python642)
        print('uuuuuuuuuu',python6423)
        print('***********************')

    title='detail'
    return render(request,"sistemabio/inquilinos/detail-inquilino.html",{
        'mytitle':title,
        'inquilino':inquilino,
        'sesiones':sesiones,
        'python6423' : python6423,
    })
# def detail_inquilino2(request, usuario_id, sesion_idu):
#     inquilino = get_object_or_404(Usuario,id_usuario=usuario_id)
#     sesion = get_object_or_404(Sesion, id_usuario_id=sesion_idu)
#     print('usuario id ', usuario_id)
#     print('sesion id ', sesion_idu)
#     title='detail'
#     return render(request,"sistemabio/inquilinos/detail-inquilino.html",{
#         'mytitle':title,
#         'inquilino':inquilino,
#         'sesion':sesion,
#     })

def delete_inquilino(request, inquilino_id):
    inquilino = Usuario.objects.get( id_usuario=inquilino_id)
    if request.method == 'POST':
        inquilino.delete()
        return redirect('/sistemabio/inquilinos/')
    return render(request,"sistemabio/inquilinos/delete-inquilino.html",{
        'inquilino':inquilino
    })
@login_required
def edit_inquilino(request, usuario_id):
     if request.method == "GET":
          inquilino = get_object_or_404(Usuario,pk=usuario_id)
          form = InquilinoForm(instance=inquilino)
          return render(request,"sistemabio/inquilinos/edit-inquilino.html",{
               'inquilino':inquilino,
               'form':form})
     else:
          try:
               inquilino = Usuario.objects.get(pk=usuario_id)
               form = InquilinoForm(request.POST,instance=inquilino)
               # commit=False es para procesar los datos antes de guardar, se usa cuando no tienes todos tus 
               # campos llenos de ese form   
                    # update_inquilino = form.save(commit=False) 
                    # update_inquilino.save()
               # if form.is_valid():
               form.save()
               print('Edición de usuario: ', usuario_id)
               messages.success(request,"Inquilino actualizado exitosamente")
               print("Formulario es ", form.is_valid())
               return redirect('/sistemabio/inquilinos/')
          except ValueError:
            messages.error(request, "Error al actualizar el inquilino.")
            return render(request, 'sistemabio/inquilinos/edit-inquilino.html', 
                          {'inquilino': inquilino, "form":  InquilinoForm, "error": "Error actualizando el inquilino."})

# Datos biométricos
def facial(request, usuario_id):
     if request.method == "GET":
         inquilino = get_object_or_404(Usuario,pk=usuario_id)
         form= SesionForm3(instance=inquilino)
         return render(request, 'sistemabio/facial.html', 
                       {  'inquilino':inquilino,
                          "form": form
                        })
     else:
          try:
               form = SesionForm3(request.POST)
               print("formulario", form.is_valid())
               print('form ', form['dato'].value())
               new_facial = form.save(commit=False)
               inquilino = get_object_or_404(Usuario,pk=usuario_id)
               print('id usuario: ', usuario_id)
               print('usuario: ',inquilino.nombre, inquilino.ap_paterno, inquilino.ap_materno ) 
               # sesion = get_object_or_404(Sesion,id_usuario_id=usuario_id)
               # print('id tipo sesion : ',sesion.id_tipo_sesion)
               # print('=======================')   
               # print('sesion dato', sesion.dato)
               personName =  str(usuario_id) + inquilino.nombre + inquilino.ap_paterno + inquilino.ap_materno 
               print("Nombre de personName es: ", personName)
               dataPath = 'C:/Users/yobis/Desktop/sistemabiors/SistemaBiometricoJessi/mysite/sistemabio/static/inquilinos' + '/' + personName 
               personPath = dataPath + '/' + 'FACIAL' + personName
               print("Nombre de carpeta es: ", personPath)
               if not os.path.exists(personPath):
                    try:
                         os.mkdir(personPath, mode=0o755)
                         print('Carpeta creada: ',personPath)
                    except OSError as e:
                         if e.errno!=errno.EEXIST:
                              raise
               else :
                    print('el directorio ya existe')
               print('form dato: ', form['dato'].value())
               dato = form['dato'].value()
               dato_rep = str(dato).replace('data:image/jpeg;base64,', '')
               print('dato_rep: ', dato_rep)
               #primero codificamos de string/cadena/caracteres a bytes por que la función b64encode no recibe str como parámetro, sino bytes
               dato_utf= dato_rep.encode('utf-8')
               print('imagen decode: ',dato_utf )
               #decodificamos los bytes en base64
               img_decode = base64.b64decode(dato_utf)
               img_name= 'prueba11235_{}.jpg'.format(2)
               img_file = open(personPath+'/'+img_name, 'wb')
               img_file.write(img_decode)
               # inicia la deteccion y recorte 
               faceClassif = cv2.CascadeClassifier('C:/Users/yobis/Desktop/sistemabiors/SistemaBiometricoJessi/mysite/sistemabio/static/haarcascades/haarcascade_frontalface_default.xml')
               captureList = os.listdir(personPath)
               print('lista de imagenes', captureList)
               count = 0
               for filename in captureList:
                    imagepath = personPath+"/"+filename
                    print(imagepath)
                    # image_file = open(personPath +'/'+filename, 'rb')
                    # print(image_file)
                    # image = image_file.read()
                    image = cv2.imread(imagepath)
                    if image is None: continue
                    imageAux = cv2.imread(imagepath)
                    # imageAux = image_file.read()
                    gray = cv2.cvtColor(image,  cv2.COLOR_BGR2GRAY)
                    faces = faceClassif.detectMultiScale(gray, 1.1, 5)
                    for (x, y, w, h) in faces:
                         cv2.rectangle(image, (x, y), (x + w, y + h), (128, 0, 255), 2)
                         cv2.rectangle(image, (10, 5), (450, 25), (255, 255, 255), 2)
                         rostro = imageAux[y:y + h, x:x + w]
                         rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
                         cv2.imwrite(personPath +'/'+ filename, rostro)
                         print('leyendo imagenerecorte')
                    # image.close()
                    # os.remove(imagepath)
               #volver  asubir imagenes a la bd
               # print('lista de imagenes 2 ', captureList)
               # for filename in captureList:
                    imagepath = personPath+"/"+filename
                    print(imagepath)
                    image = cv2.imread(imagepath)
                    # image_file = open(personPath +'/'+filename, 'rb')
                    # # print("image: ",image)
                    # image = image_file.read()
                    # imag_utf =image.encode('utf-8')
                    # print('dddd ',imag_utf)
                    #tenemos los numeros en byte que es la variable sesion['dato']
                    #por lo que solo falta codificarla en base64 cpn la siguiente linea
                    # pytho = base64.b64decode(image)
                    # print(pytho)
                    print('-------------------------------')
                    # #ahora la  decodificamos de bytes a caracteres
                    python642 = base64.b64encode(image)
                    print(python642)
                    decode_img = python642.decode('utf-8')
                    print('ppppppppp ', decode_img)
                    # python6424 = python642.encode('utf-8')
                    # print(python6424)
                    # print('+++++++++++++++++++++++++++++++++')
                    # python6423 = 'data:image/jpg;base64,' + str(python642)
                    # print('===============',python6423)
                    # python6425 = python6423.encode('utf-8')
                    # print(python6425)
                    # python = base64.b64encode(python6425)
                    # print('**************',python)
                    # # usando join(), format() y bytearray() para convertir a binario  
                    # # bin_result =  '' .join(format(x, '08b' )  for  x in bytearray(python6423, 'utf-8' ))  
                    # # print('*-*-*-*-*-*-*-*-*-*-*-*', bin_result)

               count += 1
               print(new_facial)
               # print('form dato: ', form['dato'].value())
               # dato = form['dato'].value()
               new_facial.dato = decode_img
               # print(new_facial.dato)
               new_facial.save()

              
                    
               messages.success(request," El registro facial ha sido un éxito.")
               return redirect('/sistemabio/inquilinos/')
          except ValueError:
               messages.error(request, "Error no se creo el registro facial.")
               return render(request, 'sistemabio/facial.html', 
                              { 'inquilino': inquilino,"form":  form , 
                              "error": "Error creando el registro facial."})
          
                    
def voz(request,usuario_id):
     if request.method == "GET":
         inquilino = get_object_or_404(Usuario,pk=usuario_id)
         form= SesionForm3(instance=inquilino)
         return render(request, 'sistemabio/voz.html', 
                       {  'inquilino':inquilino,
                          "form": form
                        })
     else:
          try:
               # inquilino = get_object_or_404(Usuario,pk=usuario_id)
               # form = SesionForm3(request.POST,instance=inquilino)
               form = SesionForm3(request.POST)
               print("formulario", form.is_valid())
               new_voz = form.save(commit=False)
               new_voz.save()
               # form.save()
               print('usuario id voz ', usuario_id)
               messages.success(request," El registro de voz ha sido un éxito.")
               return redirect('/sistemabio/inquilinos/')
          except ValueError:
               messages.error(request, "Error no se creo el registro de voz.")
               return render(request, 'sistemabio/voz.html', 
                              { 
                              #     'inquilino': inquilino,
                                  "form":  form , 
                              "error": "Error creando el registro de voz."})
     # title='Voz'
     # return render (request,'sistemabio/voz.html',{
     #      'mytitle':title
     # })



    
