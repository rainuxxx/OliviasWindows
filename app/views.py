import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir='instantclient_21_6')
import hashlib
import base64
from imp import IMP_HOOK
from django.shortcuts import render, redirect
from xhtml2pdf import pisa
import datetime
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives,EmailMessage
from django.template.loader import get_template, render_to_string
from django.db import connection
import random
from .models import *
from django.http.response import JsonResponse

#PAGINAS DE CLIENTES
def index(request):

    return render(request, 'cliente/index.html')

def cerrar_sesion(request):
    try:
        del request.session['usuario']
    except KeyError:
        pass
    return redirect('index')

def iniciar_sesion(request):
    if not request.session._session:
        if request.method == 'POST':
            correo = request.POST.get('correo')
            contrasena = request.POST.get('contrasena')
            contrasena_cifrada = encriptar_contrasena(contrasena)
            try:
                usuario = filtrar_usuario_x_correo(correo)
                activo = usuario[0]['data'][10]
                if activo == 1:
                    contrasena_bdd = usuario[0]['data'][11]
                    if contrasena_bdd == contrasena_cifrada:
                        request.session['usuario'] = {
                        'tipo': usuario[0]['data'][8],
                        'id': usuario[0]['data'][0],
                        'primer_nombre': usuario[0]['data'][1],
                        'apellido_paterno': usuario[0]['data'][3],
                        'correo': usuario[0]['data'][7]}
                        return redirect('index')
                    else:
                        return redirect('iniciar_sesion')
                else:
                    pass
            except IndexError:
                return redirect('iniciar_sesion')
    else:
        return redirect('index')
    return render(request, 'cliente/iniciar_sesion.html')

def registro(request):
    if not request.session._session:
        data = {
            'comuna':listar_comuna(),
        }

        if request.method == 'POST':
            primer_nombre = request.POST.get('primer_nombre')
            segundo_nombre = request.POST.get('segundo_nombre')
            apellido_paterno = request.POST.get('apellido_paterno')
            apellido_materno = request.POST.get('apellido_materno')
            direccion = request.POST.get('direccion')
            telefono = request.POST.get('telefono')
            correo = request.POST.get('correo')
            comuna = request.POST.get('comuna')
            contrasena = request.POST.get('contrasena')
            contrasena2 = request.POST.get('contrasena2')
            if contrasena == contrasena2:
                contrasena_cifrada = encriptar_contrasena(contrasena)
                salida = agregar_usuario(primer_nombre,segundo_nombre,apellido_paterno,apellido_materno,
                direccion,telefono,correo,comuna,contrasena_cifrada)
                if salida == 1:
                    data['mensaje'] = 'Funciono correctamente'
                else:
                    data['mensaje'] = 'no funciono'
            else:
                data['mensaje'] = 'las contrasenas no coinciden'

        return render(request,'cliente/registro.html',data)
    else:
        return redirect('index')


def modificar_usuario_pagina(request):
    if not request.session._session:
        return redirect('index')
    
    if  request.session['usuario']['tipo'] == 3:
        correo = request.session['usuario']['correo']

        data = {
            'usuario':filtrar_usuario_x_correo(correo),
            'comuna':listar_comuna(),
        }

        if request.method == 'POST':
            primer_nombre = request.POST.get('primer_nombre')
            segundo_nombre = request.POST.get('segundo_nombre')
            apellido_paterno = request.POST.get('apellido_paterno')
            apellido_materno = request.POST.get('apellido_materno')
            direccion = request.POST.get('direccion')
            telefono = request.POST.get('telefono')
            comuna = request.POST.get('comuna')
            salida = modificar_usuario(primer_nombre,segundo_nombre,apellido_paterno,apellido_materno,
            direccion,telefono,correo,comuna)
            if salida == 1:
                data['mensaje'] = 'Funciono correctamente'
                return redirect('modificar_usuario')
            else:
                data['mensaje'] = 'no funciono'

        return render(request,'cliente/modificar_usuario.html',data)
    else:
        return redirect('index')


def recuperar_contrasena(request):
    if not request.session._session:
        data = {}

        if request.method == "POST":
            email = request.POST.get('email')
            usuario = filtrar_usuario_x_correo(email)
            id = usuario[0]['data'][0]
            username = usuario[0]['data'][4]
            resp = email_recuperar_contrasena(email,id,username)
            resp.send()
            data['mensaje'] = 'correo enviado'

        return render(request, 'cliente/recuperar_contrasena.html',data)
    else:
        return redirect('index')

def email_recuperar_contrasena(email,id,username):

    context = {'mail': email, 'id': id, 'username':username}
    template = get_template('cliente/correo_cambiar_contrasena.html')
    content = template.render(context)

    correo = EmailMultiAlternatives(
        'Recuperar su contrasena',
        'Pasteleria',
        settings.EMAIL_HOST_USER,
        to=[email]
    )
    
    correo.attach_alternative(content, 'text/html')
    return correo

def cambiar_contrasena(request):
    if not request.session._session:
        data = {}

        id = request.GET.get('id')
        if request.method == 'POST':
            contrasena = request.POST.get('contrasena_nueva')
            contrasena_encriptada= encriptar_contrasena(contrasena)
            salida = funcion_cambiar_contrasena(id,contrasena_encriptada)
            if salida == 1:
                return redirect('index')
            else:
                data['mensaje'] = 'no funciono'
        return render(request, 'cliente/cambiar_contrasena.html',data)
    else:
        return redirect('index')


def producto(request):
    lista=listar_producto()
    page_number=request.GET.get('page',1)
    try:
        paginator = Paginator(lista,6)
        lista = paginator.get_page(page_number)
        data = {
            'entity':lista,
            'paginator':paginator,
        }
        return render(request, 'cliente/producto.html', data)
    except:
        return redirect('producto')

def nuevo_blog(request):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 3 or request.session['usuario']['tipo'] == 1:

        data = {}

        if request.method == 'POST':
            titulo = request.POST.get('titulo')
            cuerpo = request.POST.get('cuerpo')
            usuario_id = request.POST.get('usuario')

            salida = agregar_blog(titulo,usuario_id,cuerpo)
            if salida == 1:
                data['mensaje'] = 'Funciono correctamente'
            else:
                data['mensaje'] = 'no funciono'

        return render(request, 'cliente/blog.html', data)
    else:
        return redirect('index')

def mostrar_blog(request):
    lista = listar_blog()
    page_number = request.GET.get('page',1)
    try:
        paginator = Paginator(lista,5)
        lista = paginator.get_page(page_number)
        data = {
        'entity':lista,
        'paginator':paginator,
        'usuario':listar_usuario(),
        }

        if request.method == 'POST':
            id = request.POST.get('id_blog')
            salida = eliminar_blog(id)
            if salida == 1:
                return redirect('mostrar_blog')
            else:
                data['mensaje'] = 'no funciono'

        return render(request,'cliente/mostrar_blog.html',data)
    except:
        return redirect('mostrar_blog')

def contacto(request):

    return render(request, 'cliente/contacto.html')

def correo_contacto(request):

    if request.method == 'POST':
        nombres = request.POST['nombres']
        apellidos = request.POST['apellidos']
        email = request.POST['correo']
        asunto = request.POST['asunto']
        descripcion = request.POST['descripcion']

        template = render_to_string('cliente/correo_contacto.html', {
            'nombres':nombres,
            'apellidos':apellidos,
            'descripcion':descripcion,
            'correo': email,
        })

        correo = EmailMessage(
            asunto,
            template,
            email,

            ['pasteleria.masterc137@gmail.com']
        )

        correo.fail_silently = False

        correo.send()
        messages.success(request, 'se ha enviado tu correo')
        return redirect('/contacto')

    pass

def cotizacion(request,id):
    if not request.session._session:
        return redirect('index')
    if request.session['usuario']['tipo']==3:
        data = {
            'producto':filtrar_producto(id),
        }
        return render(request, 'cliente/cotizacion.html', data)
    else:
        return redirect('index')

def addtocart(request):
    if not request.session._session:
        return redirect('index')

    if request.session['usuario']['tipo']==3:
        if request.method =='POST':
            prod_id = int(request.POST.get('product_id'))
            product_check = Producto.objects.get(id=prod_id)
            if(product_check):
                if(Carrito.objects.filter(usuario=request.session['usuario']['id'], producto_id=prod_id)):
                    return JsonResponse({'status': "El producto ya existe en el carro"})
                else:
                    prod_qty = int(request.POST.get('product_qty'))

                    if product_check.cantidad >= prod_qty:
                        usuario_instancia = Usuario.objects.get(id = request.session['usuario']['id'])
                        Carrito.objects.create(usuario=usuario_instancia, producto_id=prod_id, cantidad=prod_qty)
                        return JsonResponse({'status': "El producto se agregó correctamente"})
                    else:
                        return JsonResponse({'status': "Solamente "+str(product_check.cantidad) + " cantidades disponibles"})
            else:
                return JsonResponse({'status': "No se encontró el producto"})
    return redirect('index')

def updatecart(request):
    if not request.session._session:
        return redirect('index')

    if request.method =='POST':
        prod_id = int(request.POST.get('product_id'))
        if(Carrito.objects.filter(usuario=request.session['usuario']['id'], producto_id=prod_id)):
            prod_qty = int(request.POST.get('product_qty'))
            cart = Carrito.objects.get(producto_id=prod_id, usuario_id=request.session['usuario']['id'])
            cart.cantidad =prod_qty
            cart.save()
            return JsonResponse({'status': "Se actualizó correctamente el carro"})
    return redirect('index')

def deletecartitem(request):
    if not request.session._session:
        return redirect('index')

    if request.method =='POST':
        prod_id = int(request.POST.get('product_id'))
        if(Carrito.objects.filter(usuario=request.session['usuario']['id'], producto_id=prod_id)):
            cartitem = Carrito.objects.get(producto_id=prod_id, usuario_id=request.session['usuario']['id'])
            cartitem.delete()
            return JsonResponse({'status': "Se eliminó el articulo correctamente"})
        
    return redirect('/')

def carrito(request):
    if not request.session._session:
        return redirect('index')
    if request.session['usuario']['tipo'] == 3:
        carrito = Carrito.objects.filter(usuario=request.session['usuario']['id'])
        data = {'carrito':carrito}
        return render(request, "cliente/carrito.html", data)
    else:
        return redirect('index')

def compra(request):
    if not request.session._session:
        return redirect('index')

    try:

        if request.session['usuario']['tipo'] == 3:

            rawcart = Carrito.objects.filter(usuario=request.session['usuario']['id'])
            for item in rawcart:
                if item.cantidad > item.producto.cantidad:
                    Carrito.objects.delete(id=item.id)
            cartitem = Carrito.objects.filter(usuario=request.session['usuario']['id'])
            total_price = 0
            for item in cartitem:
                total_price = total_price + item.producto.precio * item.cantidad


            data = {'cartitem':cartitem, 'total_price':total_price}
            return render(request, "cliente/compra.html", data)
        else:
            return redirect('index')
    except AttributeError:
        return redirect('carrito')

def placeorder(request):
    if not request.session._session:
        return redirect('index')

    if request.method == 'POST':

        currentuser = Usuario.objects.filter(id=request.session['usuario']['id'])
        neworder = Orden()
        neworder.usuario = Usuario.objects.get(id = request.session['usuario']['id'])

        neworder.tipo_pago = request.POST.get('payment_mode')
        neworder.id_pago = request.POST.get('payment_id')
        neworder.estado = "pendiente"
        

        cart = Carrito.objects.filter(usuario=request.session['usuario']['id'])
        car_total_price = 0
        for item in cart:
            cart_total_price = car_total_price + item.producto.precio * item.cantidad
            cart_subtotal = car_total_price + item.producto.precio * item.cantidad
            cart_subtotal = cart_subtotal - (cart_subtotal * 0.19)

        neworder.total_precio = cart_total_price
        neworder.subtotal = cart_subtotal
        neworder.creado = datetime.datetime.now()
        
        nroseguimiento = 'orden'+str(random.randint(1111111,9999999))
        while Orden.objects.filter(seguimiento=nroseguimiento) is None:
            nroseguimiento = 'orden'+str(random.randint(1111111,9999999))


        neworder.seguimiento= nroseguimiento
        neworder.save()

        neworderitems = Carrito.objects.filter(usuario=request.session['usuario']['id'])
        for item in neworderitems:
            OrdenProducto.objects.create(
                orden=neworder,
                producto=item.producto,
                precio= item.producto.precio,
                cantidad=item.cantidad    
            )

            orderproduct = Producto.objects.filter(id=item.producto_id).first()
            orderproduct.cantidad = orderproduct.cantidad - item.cantidad
            orderproduct.save()

        Carrito.objects.filter(usuario=request.session['usuario']['id']).delete()

        payMode = request.POST.get('payment_mode')
        if(payMode == "Pago por PayPal"):
            return JsonResponse({'status': "Tu compra fue comprada con exito"})
        else:
            messages.success(request, "Tu compra fue comprada con exito")
        
       
    return redirect('ordenes')


def ordenes(request):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 3:
        id=request.session['usuario']['id']
        lista = filtrar_orden(id)
        page_number = request.GET.get('page',1)
        try:
            paginator = Paginator(lista,5)
            lista = paginator.get_page(page_number)
            data={
                'entity':lista,
                'paginator':paginator,
            }
            return render(request,'cliente/ordenes.html',data)
        except:
            pass
    else:
        return redirect('index')

def orden_detalle(request,id_orden):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 3:
        id_usuario = request.session['usuario']['id']
        data = {
            'orden_producto':filtrar_orden_producto(id_orden,id_usuario),
        }

        return render(request, 'cliente/orden_detalle.html',data)
    else:
        return redirect('index')

#PAGINAS DE FUNCIONARIOS
def funcionario(request):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 2 or request.session['usuario']['tipo'] == 1:
        return render(request, 'funcionario/funcionario.html')
    else:
        return redirect('index')

def nueva_categoria(request):
    if not request.session._session:
        return redirect('index')
    if  request.session['usuario']['tipo'] == 2 or request.session['usuario']['tipo'] == 1:

        data = {}

        if request.method == 'POST':
            nombre = request.POST.get('nombre_categoria')
            salida = agregar_categoria(nombre)
            if salida == 1:
                messages.success(request, "Se ingresó correctamente", extra_tags='')
            else:
                messages.error(request, 'Error: La categoria ya existe')

        return render(request, 'funcionario/nueva_categoria.html', data)
    else:
        return redirect('index')

def nuevo_producto(request):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 2 or request.session['usuario']['tipo'] == 1:
        try:

            data = {
                'categoria':listar_categoria(),
            }

            if request.method == 'POST':
                nombre = request.POST.get('nombre_producto')
                precio = request.POST.get('precio')
                cantidad = request.POST.get('stock')
                categoria_id = request.POST.get('categoria')
                imagen = request.FILES['imagen'].read()
                sku = request.POST.get('sku')
                estado = request.POST.get('estado')
                salida = agregar_producto(nombre, precio, cantidad, categoria_id, imagen, sku, estado)
                if salida == 1:
                    messages.success(request, "Se ingresó correctamente", extra_tags='')                    
                else:
                    messages.error(request, 'Error: El producto ya existe')   

            return render(request, 'funcionario/nuevo_producto.html', data)
        except:
            return redirect('nuevo_producto')
    else:
        return redirect('index')

def mostrar_categoria(request):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 2 or request.session['usuario']['tipo'] == 1:

        lista=listar_categoria()
        page_number=request.GET.get('page',1)
        try:
            paginator = Paginator(lista,3)
            lista = paginator.get_page(page_number)
            data = {
                'entity':lista,
                'paginator':paginator,
            }
            if request.method == 'POST':
                id = request.POST.get('id_categoria')
                salida = eliminar_categoria(id)
                if salida == 1:
                    data['mensaje'] = 'funciono'
                    return redirect('mostrar_categoria')
                else:
                    data['mensaje'] = 'no funciono'

            return render(request, 'funcionario/mostrar_categoria.html', data)
        except:
            return redirect('mostrar_categoria')
    else:
        return redirect('index')

def mostrar_producto(request):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 2 or request.session['usuario']['tipo'] == 1:

        lista = listar_producto_funcionario()
        page_number = request.GET.get('page',1)
        try:
            paginator = Paginator(lista,6)
            lista = paginator.get_page(page_number)
            data = {
            'entity':lista,
            'paginator':paginator,
            }
            if request.method == 'POST':
                id = request.POST.get('id_producto')
                salida = eliminar_producto(id)
                if salida == 1:
                    data['mensaje'] = 'Funciono'
                    return redirect('mostrar_producto')
                else:
                    data['mensaje'] = 'no funciono'

            return render(request, 'funcionario/mostrar_producto.html', data)
        except:
            return redirect('mostrar_producto')
    else:
        return redirect('index')


def modificar_categoria(request,id):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 2 or request.session['usuario']['tipo'] == 1:
        data = {
            'categoria':filtrar_categoria(id)
        }

        if request.method == 'POST':
            nombre = request.POST.get('nombre_categoria')
            salida = editar_categoria(id,nombre)
            if salida == 1:
                data['mensaje'] = 'si funciono'
                return redirect('mostrar_categoria')
            else:
                data['mensaje'] = 'no funciono'

        return render(request, 'funcionario/modificar_categoria.html', data)
    else:
        return redirect('index')

def modificar_producto(request,id):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 2 or request.session['usuario']['tipo'] == 1:
        data = {
            'producto':filtrar_producto(id),
            'categoria':listar_categoria(),
        }

        if request.method == 'POST':
            nombre_producto = request.POST.get('nombre_producto')
            precio = request.POST.get('precio')
            cantidad = request.POST.get('stock')
            categoria_id = request.POST.get('categoria')
            imagen = request.FILES['imagen'].read()
            sku = request.POST.get('sku')
            estado = request.POST.get('estado')
            salida = editar_producto(id,nombre_producto,precio,cantidad,categoria_id,imagen,sku,estado)
            if salida == 1:
                return redirect('mostrar_producto')
            else:
                data['mensaje'] = 'no funciono'

        return render(request, 'funcionario/modificar_producto.html',data)
    else:
        return redirect('index')


def ventas(request):
    if not request.session._session:
        return redirect('index')
    if  request.session['usuario']['tipo'] == 2 or request.session['usuario']['tipo'] == 1:
        lista = listar_orden()
        page_number = request.GET.get('page',1)
        try:
            paginator = Paginator(lista,10)
            lista = paginator.get_page(page_number)
            data={
                'entity':lista,
                'paginator':paginator,
            }
            return render(request,'funcionario/ventas.html',data)
        except:
            pass
    else:
        return redirect('index')

def ventas_detalle(request,id):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 2 or request.session['usuario']['tipo'] == 1:
        data = {
            'venta':filtrar_venta_detalle(id)
        }

        return render(request, 'funcionario/ventas_detalles.html',data)
    else:
        return redirect('index')

#PAGINAS DE ADMINISTRADOR

def registro_admin(request):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 1:
        data = {
            'comuna':listar_comuna(),
            'tipo':listar_tipo_usuario(),
        }

        if request.method == 'POST':
            primer_nombre = request.POST.get('primer_nombre')
            segundo_nombre = request.POST.get('segundo_nombre')
            apellido_paterno = request.POST.get('apellido_paterno')
            apellido_materno = request.POST.get('apellido_materno')
            direccion = request.POST.get('direccion')
            telefono = request.POST.get('telefono')
            correo = request.POST.get('correo')
            tipo_usuario = request.POST.get('tipo_usuario')
            comuna = request.POST.get('comuna')
            contrasena = request.POST.get('contrasena')
            contrasena2 = request.POST.get('contrasena2')
            if contrasena == contrasena2:
                contrasena_cifrada = encriptar_contrasena(contrasena)
                salida = agregar_usuario_admin(primer_nombre,segundo_nombre,apellido_paterno,apellido_materno,
                direccion,telefono,correo,tipo_usuario,comuna,contrasena_cifrada)
                if salida == 1:
                    data['mensaje'] = 'Funciono correctamente'
                else:
                    data['mensaje'] = 'no funciono'
            else:
                data['mensaje'] = 'las contrasenas no coinciden'

        return render(request,'administrador/registro_admin.html',data)
    else:
        return redirect('index')

def mostrar_usuario(request):
    if not request.session._session:
        return redirect('index')

    if  request.session['usuario']['tipo'] == 1:
        lista = listar_usuario()
        page_number = request.GET.get('page',1)
        try:
            paginator = Paginator(lista,40)
            lista = paginator.get_page(page_number)
            data = {
            'entity':lista,
            'paginator':paginator,
            }

            if request.method == 'POST':
                id = request.POST.get('id_usuario')
                salida = eliminar_usuario(id)
                if salida == 1:
                    data['mensaje'] = 'funciono'
                else:
                    data['mensaje'] = 'no funciono'

            return render(request, 'administrador/mostrar_usuario.html', data)
        except:
            return redirect('administrador/mostrar_usuario.html')
    else:
        return redirect('index')

def modificar_usuario_admin_pagina(request,correo):
    if not request.session._session:
        return redirect('index')
    
    if  request.session['usuario']['tipo'] == 1:

        data = {
            'tipo':listar_tipo_usuario(),
        }

        if request.method == 'POST':
            tipo = request.POST.get('tipo')
            salida = modificar_usuario_admin(correo,tipo)
            if salida == 1:
                data['mensaje'] = 'Funciono correctamente'
                return redirect('funcionario')
            else:
                data['mensaje'] = 'no funciono'

        return render(request,'administrador/modificar_usuario.html',data)
    else:
        return redirect('index')

#PROCEDIMIENTOS ALMACENADOS

def agregar_usuario(primer_nombre,segundo_nombre,apellido_paterno,apellido_materno,direccion,
telefono,correo,comuna,contrasena_cifrada):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor() 
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_AGREGAR_USUARIO',[primer_nombre ,segundo_nombre,apellido_paterno,
    apellido_materno,direccion,telefono,correo,comuna,contrasena_cifrada,salida])
    return salida.getvalue()

def modificar_usuario(primer_nombre,segundo_nombre,apellido_paterno,apellido_materno,direccion,
telefono,correo,comuna):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor() 
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_EDITAR_USUARIO',[primer_nombre ,segundo_nombre,apellido_paterno,
    apellido_materno,direccion,telefono,correo,comuna,salida])
    return salida.getvalue()

def modificar_usuario_admin(correo,tipo_usuario):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor() 
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_EDITAR_USUARIO_ADMIN',[correo,tipo_usuario,salida])
    return salida.getvalue()

def agregar_usuario_admin(primer_nombre,segundo_nombre,apellido_paterno,apellido_materno,direccion,
telefono,correo,tipo_usuario,comuna,contrasena_cifrada):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor() 
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_AGREGAR_USUARIO_ADMIN',[primer_nombre ,segundo_nombre,apellido_paterno,
    apellido_materno,direccion,telefono,correo,tipo_usuario,comuna,contrasena_cifrada,salida])
    return salida.getvalue()

def agregar_categoria(nombre):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor() 
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_AGREGAR_CATEGORIA',[nombre,salida])
    return salida.getvalue()

def agregar_producto(nombre, precio, cantidad, categoria_id, imagen, sku, estado):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor() 
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_AGREGAR_PRODUCTO',[nombre, precio, cantidad, categoria_id, imagen, sku, estado, salida])
    return salida.getvalue()

def eliminar_categoria(id):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor()
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_ELIMINAR_CATEGORIA',[id,salida])
    return salida.getvalue()

def funcion_cambiar_contrasena(id,contrasena):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor() 
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_CAMBIAR_CONTRASENA',[id,contrasena,salida])
    return salida.getvalue()

def eliminar_producto(id):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor()
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_ELIMINAR_PRODUCTO',[id,salida])
    return salida.getvalue()

def editar_categoria(id,nombre):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor() 
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_EDITAR_CATEGORIA',[id, nombre,salida])
    return salida.getvalue()

def agregar_blog(titulo,usuario_id,cuerpo):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor() 
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_AGREGAR_BLOG',[titulo,usuario_id,cuerpo, salida])
    return salida.getvalue()


def editar_producto(id,nombre, precio, cantidad, categoria_id, imagen, sku, estado):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor() 
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_EDITAR_PRODUCTO',[id,nombre, precio, cantidad, categoria_id, imagen, sku, estado,salida])
    return salida.getvalue()

def eliminar_usuario(id):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor()
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_ELIMINAR_USUARIO',[id,salida])
    return salida.getvalue()

def eliminar_blog(id):
    cursor_dj = connection.cursor()
    cursor_ex = cursor_dj.connection.cursor()
    salida = cursor_ex.var(cx_Oracle.NUMBER)
    cursor_ex.callproc('SP_ELIMINAR_BLOG',[id,salida])
    return salida.getvalue()

def filtrar_usuario_x_correo(correo):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_FILTRAR_USUARIO_X_CORREO',[correo,out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista

def listar_blog():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_LISTAR_BLOG', [out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista

def listar_tipo_usuario():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_LISTAR_TIPO_USUARIO', [out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista

def listar_usuario():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_LISTAR_USUARIO', [out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista

def listar_comuna():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_LISTAR_COMUNA', [out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista

def listar_categoria():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_LISTAR_CATEGORIA', [out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista

def listar_producto():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_LISTAR_PRODUCTO', [out_cur])

    lista = []
    for fila in out_cur:
        data = {
            'data':fila,
            'imagen': str(base64.b64encode(fila[5].read()), 'utf-8')
        }
        lista.append(data)

    return lista

def listar_producto_funcionario():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_LISTAR_PRODUCTO_FUNCIONARIO', [out_cur])

    lista = []
    for fila in out_cur:
        data = {
            'data':fila,
            'imagen': str(base64.b64encode(fila[5].read()), 'utf-8')
        }
        lista.append(data)

    return lista

def filtrar_categoria(id):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_FILTRAR_CATEGORIA', [id,out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista

def filtrar_producto(id):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_FILTRAR_PRODUCTO', [id,out_cur])

    lista = []
    for fila in out_cur:
        data = {
            'data':fila,
            'imagen': str(base64.b64encode(fila[5].read()), 'utf-8')
        }
        lista.append(data)

    return lista



def filtrar_orden(id):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_FILTRAR_ORDEN',[id,out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista

def filtrar_orden_producto(id_orden,id_usuario):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_FILTRAR_ORDEN_PRODUCTO',[id_orden,id_usuario,out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista


def listar_orden():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_LISTAR_ORDEN', [out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista

def filtrar_venta_detalle(id):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_FILTRAR_VENTA_PRODUCTO',[id,out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista

def listar_orden_producto():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()

    cursor.callproc('SP_LISTAR_ORDEN_PRODUCTO', [out_cur])

    lista = []
    for i in out_cur:
        lista.append({
            'data':i
        })
    
    return lista


def encriptar_contrasena(contrasena):
	contrasena = contrasena.encode('ascii')
	contrasena_cifrada = hashlib.md5(contrasena).hexdigest()
	return contrasena_cifrada



#serializers


from rest_framework.serializers import Serializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from .serializers import CategoriaSerializer, ProductoSerializer, UserSerializer
from app.models import Categoria,  Producto, Usuario

@csrf_exempt
@api_view(['GET', 'POST'])

def lista_productos(request):
    if request.method =='GET':
        producto = Producto.objects.all()
        serializer = ProductoSerializer(producto, many=True)
        return Response(serializer.data)
    elif request.method=='POST':
        data =  JSONParser().parse(request)
        serializer = ProductoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET', 'POST'])
def lista_categorias(request):
    if request.method =='GET':
        categoria =  Categoria.objects.all()
        serializer = CategoriaSerializer(categoria, many=True)
        return Response(serializer.data)
    elif request.method=='POST':
        data =  JSONParser().parse(request)
        serializer = CategoriaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET', 'POST'])
def lista_usuario_mobile(request):
    if request.method =='GET':
        usuario =  Usuario.objects.all()
        serializer = UserSerializer(usuario, many=True)
        return Response(serializer.data)
    elif request.method=='POST':
        data =  JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


