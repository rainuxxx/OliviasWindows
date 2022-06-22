$(document).ready(function () {
    
    $('.increment-btn').click(function(e){
        e.preventDefault();

        var inc_value = $(this).closest('.product_data').find('.qty-input').val();
        var value = parseInt(inc_value,10);
        value = isNaN(value) ? 0: value;
        if(value < 10)
        {
            value++;
            $(this).closest('.product_data').find('.qty-input').val(value);
        }
    });

    $('.decrement-btn').click(function(e){
        e.preventDefault();

        var dec_value = $(this).closest('.product_data').find('.qty-input').val();
        var value = parseInt(dec_value,10);
        value = isNaN(value) ? 0: value;
        if(value > 1)
        {
            value--;
            $(this).closest('.product_data').find('.qty-input').val(value);
        }
    });

    $('.addToCartBtn').click(function(e){
        e.preventDefault();

        var product_id = $(this).closest('.product_data').find('.prod_id').val();
        var product_qty = $(this).closest('.product_data').find('.qty-input').val();
        var token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            method: "POST",
            url: "/add-to-cart",
            data: {
                'product_id':product_id,
                'product_qty':product_qty,
                csrfmiddlewaretoken: token
            },
            success: function(response){
                console.log(response)
                alertify.success(response.status)
            }
        });
    });



    $('.changeQuantity').click(function(e){
        e.preventDefault();

        var product_id = $(this).closest('.product_data').find('.prod_id').val();
        var product_qty = $(this).closest('.product_data').find('.qty-input').val();
        var token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            method: "POST",
            url: "/update-cart",
            data: {
                'product_id':product_id,
                'product_qty':product_qty,
                csrfmiddlewaretoken: token
            },
            success: function(response){
                console.log(response)
                alertify.success(response.status)
            }
        });
    });



    $(document).on('click', '.delete-cart-item', function(e){
        e.preventDefault();

        var product_id = $(this).closest('.product_data').find('.prod_id').val();
        var token = $('input[name=csrfmiddlewaretoken]').val();

        $.ajax({
            method: "POST",
            url: "/carrito/delete-cart-item",
            data: {
                'product_id':product_id,
                csrfmiddlewaretoken: token
            },
            success: function(response){
                alertify.success(response.status)
                $('.datocarro').load(location.href + " .datocarro");
            }
        });    

    });

    $('.addToWishlist').click(function(e){
        e.preventDefault();

        var product_id = $(this).closest('.product_data').find('.prod_id').val();
        var token = $('input[name=csrfmiddlewaretoken]').val();
        
        $.ajax({
            method: "POST",
            url: "/add-to-wishlist",
            data: {
                'product_id':product_id,
                csrfmiddlewaretoken: token
            },
            success: function(response){
                alertify.success(response.status)
            }
        }); 
    });
    

    $(document).on('click', '.delete-wishlist-item', function(e){

    
        e.preventDefault();

        var product_id = $(this).closest('.product_data').find('.prod_id').val();
        var token = $('input[name=csrfmiddlewaretoken]').val();
        
        $.ajax({
            method: "POST",
            url: "/delete-wishlist-item",
            data: {
                'product_id':product_id,
                csrfmiddlewaretoken: token
            },
            success: function(response){
                alertify.success(response.status)
                $('.limpiarcarro').load(location.href + " .limpiarcarro");
            }
        }); 
    });

    
});





document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("formularioregistro").addEventListener('submit', validarFormulario); 
  });

function validarFormulario(evento) {
evento.preventDefault();
    var usuario = document.getElementById('pnombre').value;
    if(usuario.length == 0) {
        alert('No has escrito nada en el primer nombre');
        return;
    }
    var usuario = document.getElementById('apaterno').value;
    if(usuario.length == 0) {
        alert('No has escrito nada en el primer apellido');
        return;
    }
    var usuario = document.getElementById('amaterno').value;
    if(usuario.length == 0) {
        alert('No has escrito nada en el segundo apellido');
        return;
    }
    var usuario = document.getElementById('direccion').value;
    if(usuario.length == 0) {
        alert('No has escrito nada en la direccion');
        return;
    }
    var usuario = document.getElementById('telefono').value;
    if(usuario.length == 0) {
        alert('No has escrito nada en el telefono');
        return;
    }
    var usuario = document.getElementById('correo').value;
    if(usuario.length == 0) {
        alert('No has escrito nada en el correo');
        return;
    }
this.submit();
}