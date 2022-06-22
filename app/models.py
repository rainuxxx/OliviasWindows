from django.db import models


class Blog(models.Model):
    usuario = models.ForeignKey('Usuario', models.DO_NOTHING)
    titulo = models.CharField(max_length=50)
    cuerpo = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'blog'


class Carrito(models.Model):
    usuario = models.ForeignKey('Usuario', models.DO_NOTHING)
    producto = models.ForeignKey('Producto', models.DO_NOTHING)
    cantidad = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'carrito'


class Categoria(models.Model):
    id = models.SmallAutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=40)

    class Meta:
        managed = False
        db_table = 'categoria'


class Comuna(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=35)
    provincia = models.ForeignKey('Provincia', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'comuna'


class Orden(models.Model):
    usuario = models.ForeignKey('Usuario', models.DO_NOTHING)
    total_precio = models.IntegerField()
    subtotal = models.IntegerField()
    tipo_pago = models.CharField(max_length=100, blank=True, null=True)
    id_pago = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=40)
    seguimiento = models.CharField(unique=True, max_length=150)
    creado = models.DateTimeField(blank=True, null=True)
    actualizado = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orden'


class OrdenProducto(models.Model):
    id = models.BigAutoField(primary_key=True)
    producto = models.ForeignKey('Producto', models.DO_NOTHING)
    orden = models.ForeignKey(Orden, models.DO_NOTHING)
    precio = models.IntegerField()
    cantidad = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'orden_producto'


class Producto(models.Model):
    nombre = models.CharField(max_length=40)
    precio = models.IntegerField()
    cantidad = models.IntegerField()
    categoria = models.ForeignKey(Categoria, models.DO_NOTHING)
    imagen = models.BinaryField(blank=True, null=True)
    sku = models.IntegerField(unique=True)
    estado = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'producto'


class Provincia(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=35)

    class Meta:
        managed = False
        db_table = 'provincia'


class TipoUsuario(models.Model):
    id = models.BooleanField(primary_key=True)
    tipo = models.CharField(max_length=35)

    class Meta:
        managed = False
        db_table = 'tipo_usuario'


class Usuario(models.Model):
    primer_nombre = models.CharField(max_length=35)
    segundo_nombre = models.CharField(max_length=35, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=35)
    apellido_materno = models.CharField(max_length=35)
    direccion = models.CharField(max_length=100)
    telefono = models.IntegerField()
    correo = models.CharField(unique=True, max_length=100)
    tipo_usuario = models.ForeignKey(TipoUsuario, models.DO_NOTHING)
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING)
    activo = models.BooleanField()
    contrasena = models.CharField(max_length=40)
    fecha_activacion = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'
