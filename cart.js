<script>
    document.addEventListener("DOMContentLoaded", function () {
        let cart = JSON.parse(localStorage.getItem("cart")) || [];

        function updateCartUI() {
            console.log("Cart Updated:", cart); // Debugging
            localStorage.setItem("cart", JSON.stringify(cart));
        }

        // Step 1: Fix Event Listeners for Dynamically Loaded Items
        document.addEventListener("click", function (event) {
            if (event.target.classList.contains("add-to-cart")) {
                let button = event.target;
                let item = {
                    id: button.getAttribute("data-id"),
                    name: button.getAttribute("data-name"),
                    price: parseFloat(button.getAttribute("data-price")),
                    image: button.getAttribute("data-image"),
                    quantity: 1
                };

                let cart = JSON.parse(localStorage.getItem("cart")) || [];
                let existingItem = cart.find(cartItem => cartItem.id === item.id);

                if (existingItem) {
                    existingItem.quantity++;
                } else {
                    cart.push(item);
                }

                localStorage.setItem("cart", JSON.stringify(cart));
                console.log("Item added to cart:", item);

                // Update UI (Optional: If you have a cart icon showing item count)
                updateCartUI();
            }
        });

    });
</script>
