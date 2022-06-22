from rest_framework import serializers
from .models import Categoria, Producto,Usuario

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['nombre','sku', 'precio','categoria','cantidad','estado']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id','nombre']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['correo','contrasena','tipo_usuario_id']