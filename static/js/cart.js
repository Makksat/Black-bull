var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var productId = this.dataset.product
		var action = this.dataset.action
		console.log('productId:', productId, 'Action:', action)

        console.log('USER:', user)
        if(user === 'AnonymousUser'){
            addCookieItem(productId, action)
        }else{
            updateUserOrder(productId, action)
        }
	}) 
}

function resetCart() {
    cart = {}
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    document.getElementById('cart-total').innerHTML = '0'
}

function addCookieItem(productId, action){
	console.log('Not logged in..')

	if(action == 'add'){
		if(cart[productId] == undefined){
			cart[productId] = {'quantity':1}
		}else{
			cart[productId]['quantity'] += 1
		}
	}

	if(action == 'remove'){
		cart[productId]['quantity'] -= 1

		if(cart[productId]['quantity'] <= 0){
			console.log('Remove Item')
			delete cart[productId]
		}
	}
	console.log('Cart:', cart)
	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"
	location.reload()
}

function updateUserOrder(productId, action){
	console.log('User is logged in, sending data...')

		var url = '/update_item/'

		fetch(url, {
			method:'POST',
			headers:{
				'Content-Type':'application/json',
				'X-CSRFToken':csrftoken,
			}, 
			body:JSON.stringify({'productId':productId, 'action':action})
		})
		.then((response) => {
		   return response.json();
		})
		.then((data) => {
		    console.log('data:', data)
			location.reload()
		});
}