document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const isLoggedIn = false; // Replace with actual login check logic
    const loginLink = document.getElementById('loginLink');
    const loginButton = document.querySelector('.login-button');
    const loggedInImage = document.getElementById('loggedInImage');
    const modal = document.getElementById('loginModal');
    const closeModal = document.querySelector('.modal .close');

    // Function to change login button to image after login
    function changeToImage() {
        if (loginButton && loggedInImage) {
            loginButton.style.display = 'none';
            loggedInImage.style.display = 'inline-block';
        }
    }

    // Check if user is logged in and update UI accordingly
    if (isLoggedIn) {
        if (loginLink) {
            loginLink.href = "dashboard"; // Replace with actual dashboard link
        }
        changeToImage();
    }

    // Open modal or redirect to login page
    if (loginLink) {
        loginLink.addEventListener('click', function(event) {
            if (!isLoggedIn) {
                event.preventDefault();
                if (modal) {
                    modal.style.display = 'block';
                }
            }
        });
    }

    if (loginButton) {
        loginButton.addEventListener('click', function(event) {
            if (!isLoggedIn) {
                event.preventDefault();
                window.location.href = 'login'; // Replace with the actual login page URL
            } else {
                window.location.href = 'dashboard'; // Replace with the actual dashboard page URL
            }
        });
    }

    // Close modal
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            if (modal) {
                modal.style.display = 'none';
            }
        });
    }

    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });

    // Reviews section scroll functionality
    const reviewsContainer = document.getElementById('reviews-container');
    const leftArrow = document.getElementById('left-arrow');
    const rightArrow = document.getElementById('right-arrow');

    const scrollAmount = 300; // Adjust this value based on card width

    if (leftArrow && reviewsContainer) {
        leftArrow.addEventListener('click', () => {
            reviewsContainer.scrollBy({
                top: 0,
                left: -scrollAmount,
                behavior: 'smooth'
            });
        });
    }

    if (rightArrow && reviewsContainer) {
        rightArrow.addEventListener('click', () => {
            reviewsContainer.scrollBy({
                top: 0,
                left: scrollAmount,
                behavior: 'smooth'
            });
        });
    }

    // JavaScript for Hamburger Menu
    const hamburger = document.querySelector('.hamburger');
    const menu = document.querySelector('.menu');
    const closeMenu = document.querySelector('.menu-close');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            menu.style.right = '0';
        });
    }

    if (closeMenu) {
        closeMenu.addEventListener('click', () => {
            menu.style.right = '-100%';
        });
    }
});
