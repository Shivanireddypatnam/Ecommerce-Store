function increaseQuantity() {
    const quantity = document.getElementById("quantity");
    const max = parseInt(quantity.max);

    let current = parseInt(quantity.value);

    if (current < max) {
        quantity.value = current + 1;
    }
}

function decreaseQuantity() {
    const quantity = document.getElementById("quantity");

    let current = parseInt(quantity.value);

    if (current > 1) {
        quantity.value = current - 1;
    }
}