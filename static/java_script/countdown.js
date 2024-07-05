document.addEventListener('DOMContentLoaded', (event) => {
    let scoreElement = document.querySelector('.score');
    let score = parseInt(scoreElement.textContent.match(/\d+/)[0], 10); // Extract score from text

    if (score > 7) {
        scoreElement.classList.add('green');
    } else if (score <= 7 && score > 5) {
        scoreElement.classList.add('yellow');
    } else if (score <= 5 && score > 0) {
        scoreElement.classList.add('red');
    }

    // Countdown logic
    let countdownElement = document.getElementById('countdown');
    let messageElement = document.getElementById('message');
    let progressCircle = document.getElementById('progressCircle');

    let countdown = 20;
    let interval = setInterval(() => {
        countdown--;
        countdownElement.textContent = countdown;

        // Calculate and set the progress for a 20 second timer
        let progress = ((20 - countdown) / 20) * 100;
        progressCircle.style.background = `conic-gradient(#00ff00 ${progress}%, #e0e0e0 ${progress}%)`;

        if (countdown <= 0) {
            clearInterval(interval);
            countdownElement.style.display = 'none';
            progressCircle.style.display = 'none';
            messageElement.style.display = 'block';
        }
    }, 1000);

    // Initialize the progress circle background at the start
    progressCircle.style.background = `conic-gradient(#00ff00 0%, #e0e0e0 0%)`;
});
