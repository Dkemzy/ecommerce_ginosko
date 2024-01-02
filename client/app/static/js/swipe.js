// Import TouchSwipe library from CDN
// Make sure to include this before your custom script
// You can find the latest version at https://cdnjs.com/libraries/jquery.touchswipe
// Add this script tag to your HTML head
// <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.touchswipe/1.6.19/jquery.touchSwipe.min.js"></script>

// Swipe functionality for product cards
$(document).ready(function() {
    $(".product-card").swipe({
        swipe: function(event, direction, distance, duration, fingerCount, fingerData) {
            handleSwipe(direction, $(this));
        },
        allowPageScroll: "vertical",
    });

    // Function to handle swipe direction
    function handleSwipe(direction, $element) {
        // Reset card highlighting
        $(".product-card").removeClass("selected");

        // Highlight the selected product in the cart based on swipe direction
        if (direction === "left") {
            $element.addClass("selected");
        } else if (direction === "right") {
            $element.addClass("selected");
        }
    }
});
