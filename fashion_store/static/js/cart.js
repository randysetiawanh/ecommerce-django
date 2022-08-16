var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function(){
        var getProductId = this.dataset.product
        var getAction = this.dataset.action
        console.log('Product ID:', getProductId, 'Action: ', getAction)
        console.log('User: ', user)

        if (user == 'AnonymousUser'){
            addCookieItem(getProductId, getAction)
        }else{
            updateUserOrder(getProductId, getAction)
        }
    })
}

function addCookieItem(getProductId, getAction){
    console.log('User is not authenticated!')

    if(getAction == 'add'){
        if(cart[getProductId] == undefined){
            cart[getProductId] = {'quantity':1}
            alert('Success add product to cart!');
        }else{
            cart[getProductId]['quantity'] += 1
            alert('Success add product to cart!');
        }
    }

    if(getAction == 'remove'){
        cart[getProductId]['quantity'] -= 1
        if(cart[getProductId]['quantity'] <= 0){
            console.log('Product should be deleted!')
            delete cart[getProductId];
            alert('Product deleted from cart!');
        }
    }
    console.log('Cart: ', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload()
}

function updateUserOrder(getProductId, getAction){
    console.log('User is authenticated, sending data...')

        var url = '/update_item/'

        fetch(url, {
            method:'POST',
            headers:{
                'Content-Type':'application/json',
                'X-CSRFToken' : csrftoken,
            }, 
            body:JSON.stringify({
                'getProductId' : getProductId,
                'getAction': getAction,
            })
        })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            location.reload()
            if(getAction == 'add'){
                alert('Success add product to cart!');
            }else if(getAction == 'remove'){
                alert('Success remove product in cart!');
            }
        });
}