function addToCart(id,name,price) {
    event.preventDefault()
    fetch('/api/add-cart', {
        method : 'post',
        body : JSON.stringify({
            'id' : id,
            'name': name,
            'price' : price
        }),
        headers: {
            'Content-type' : 'application/json'
        }
    }).then(function(res) {
        return res.json()
    }).then(function(data) {
        // Cập nhật lại con số trên trang giỏ hàng và tổng số sản phẩm
        cart_items = document.getElementsByClassName('cart_counter')
        for (var i = 0;i < cart_items.length;i++)
            cart_items[i].textContent = data['total_quantity']
    }).catch(function(err) {
        console.err(err)
    })
}

function pay() {
    if (confirm('Ban co chac muon thanh toan khong ?') == true) {
         fetch('/api/pay', {
        method : 'post'
    }).then(function(res) {
        return res.json()
    }).then(function(data) {
        if (data.code == 200) {
        //Cap nhat lai trang gio hang
            location.reload()
        }
    }).catch(function(err) {
        console.err(err)
    })
    }
}

function updateCart(id,obj) {

    fetch('/api/update_cart',{
        method : 'put',
        body : JSON.stringify({
            'id': id,
            'quantity': parseInt(obj.value)
        }),
        headers: {
            'Content-type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        // Cập nhật lại con số trên trang giỏ hàng và tổng số sản phẩm
        cart_items = document.getElementsByClassName('cart_counter')
        for (var i = 0;i < cart_items.length;i++)
            cart_items[i].textContent = data['total_quantity']

        totalAmount = document.getElementById('total_amount')
        totalAmount.textContent = new Intl.NumberFormat().format(data['total_amount'])
    }).catch(err=>console.log(err))
}

function removeItem(id,obj) {
    fetch('/api/remove_item',{
        method: 'put',
        body: JSON.stringify({
            'id':id
        }),
        headers: {
            'Content-type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        // Cập nhật lại con số trên trang giỏ hàng và tổng số sản phẩm
        cart_items = document.getElementsByClassName('cart_counter')
        for (var i = 0;i < cart_items.length;i++)
            cart_items[i].textContent = data['total_quantity']

        totalAmount = document.getElementById('total_amount')
        totalAmount.textContent = new Intl.NumberFormat().format(data['total_amount'])

        // Cập nhật lại table cart
        var row = obj.parentNode.parentNode
        row.parentNode.removeChild(row)
    }).catch(err=>console.log(err))
}

function addComment(productId) {
    let comment = document.getElementById('commentId')
    fetch('/api/add_comment',{
        method: 'post',
        body: JSON.stringify({
            'product_id' : productId,
            'content': comment.value
        }),
        headers: {
            'Content-type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        if (data.status !== 201) {
           alert(data.err_msg)
        }
        else if (data.status == 201) {
            comment.value = ""
            commentArea = document.getElementById('commentArea')
            commentArea.innerHTML = getHtmlComment(data.comment) + commentArea.innerHTML
        }
    }).catch(err => console.error(err))
}

function loadComments(productID,page=1) {
    fetch(`/api/products/${productID}/comments?page=${page}`).then(res => res.json()).then(data => {
        commentArea = document.getElementById('commentArea')
        commentArea.innerHTML = ""
        for (let i = 0;i < data.length;i++) {
            commentArea.innerHTML += getHtmlComment(data[i].comment)
        }
    })
}

function getHtmlComment(comment) {
    return `
                <div class="col-md-6 col-xs-12 p-0">
            <p class="font-weight-bolder mb-1">${comment.user_name}</p>
        </div>
        <div class="row">
            <div class="col-md-4">
                <p class="font-italic">${comment.content}</p>
            </div>
            <div class="col-md-2">
                <p class="font-italic">${moment(comment.created_date).locale('vi').fromNow()}</p>
            </div>
        </div>
            `
}
