document.addEventListener('DOMContentLoaded', function() {
    const imageElement = document.getElementById('dynamic-image');
    const images = [
        imageElement.getAttribute('data-image1'), 
        imageElement.getAttribute('data-image2')
    ];
    let currentIndex = 0;

    function changeImage() {
        currentIndex = (currentIndex + 1) % images.length;
        imageElement.style.left = '-50%'; // Slide image to the left
        setTimeout(function() {
            imageElement.src = images[currentIndex];
            imageElement.style.left = '0'; // Reset image position
        }, 500); // Delay before changing image, adjust as needed
        imageElement.onerror = function() {
            console.error('Error loading ' + imageElement.src);
            this.src = ''; // Hide image or set a default if preferred
        };
    }

    // Set initial image
    imageElement.src = images[0];
    imageElement.onerror = function() {
        console.error('Error loading ' + imageElement.src);
        this.src = ''; // Hide image or set a default if preferred
    };

    setInterval(changeImage, 2000); // Change image every 2 seconds
});
