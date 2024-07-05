document.addEventListener('DOMContentLoaded', function() {
    const questions = document.querySelectorAll('.question');
    const progressBar = document.querySelector('.progress-bar .progress');
    const options = document.querySelectorAll('.option');
    const previousButtons = document.querySelectorAll('.previous-button');
    const nextButtons = document.querySelectorAll('.next-button');
    let currentStep = 0;

    function showQuestion(step) {
        questions.forEach(question => {
            question.style.display = 'none';
        });
        const currentQuestion = document.querySelector(`.question[data-step="${step}"]`);
        if (currentQuestion) {
            currentQuestion.style.display = 'block';
            updateProgressBar(step);
        }
    }

    function updateProgressBar(step) {
        const progress = (step / (questions.length - 1)) * 100;
        progressBar.style.width = `${progress}%`;
    }

    options.forEach(option => {
        option.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            const step = this.closest('.question').getAttribute('data-step');
            const inputName = `question${step}`;

            // Check if hidden input already exists
            let input = document.querySelector(`input[name="${inputName}"]`);
            if (!input) {
                input = document.createElement('input');
                input.type = 'hidden';
                input.name = inputName;
                document.querySelector('form').appendChild(input);
            }
            input.value = value;

            currentStep++;
            if (currentStep < questions.length) {
                showQuestion(currentStep);
            } else {
                document.querySelector('form').submit();
            }
        });
    });

    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            const currentQuestion = this.closest('.question');
            const inputs = currentQuestion.querySelectorAll('input');
            let valid = true;

            inputs.forEach(input => {
                if (input.value.trim() === '') {
                    valid = false;
                }
            });

            if (valid) {
                currentStep++;
                if (currentStep < questions.length) {
                    showQuestion(currentStep);
                } else {
                    document.querySelector('form').submit();
                }
            } else {
                alert('Please fill out all required fields.');
            }
        });
    });

    previousButtons.forEach(button => {
        button.addEventListener('click', function() {
            const previousStep = parseInt(this.getAttribute('data-previous-step'));
            if (previousStep >= 0) {
                currentStep = previousStep;
                showQuestion(currentStep);
            }
        });
    });

    showQuestion(currentStep);
});