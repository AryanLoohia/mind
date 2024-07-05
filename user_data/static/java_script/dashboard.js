document.addEventListener('DOMContentLoaded', function() {
    // Fetch user data
    fetch('/api/user_data')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
            } else {
                document.getElementById('name').textContent = `Name: ${data.name}`;
                document.getElementById('phone').textContent = `Phone: ${data.phone}`;
                document.getElementById('gender').textContent = `Gender: ${data.gender}`;
            }
        })
        .catch(error => console.error('Error fetching user data:', error));

    // Fetch user assessments
    fetch('/api/user_assessments')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
            } else {
                const assessmentsBody = document.getElementById('assessments-body');
                data.assessments.forEach(assessment => {
                    const row = document.createElement('tr');
                    const idCell = document.createElement('td');
                    const scoreCell = document.createElement('td');
                    idCell.textContent = assessment.id;
                    scoreCell.textContent = assessment.score;
                    row.appendChild(idCell);
                    row.appendChild(scoreCell);
                    assessmentsBody.appendChild(row);
                });
            }
        })
        .catch(error => console.error('Error fetching assessments:', error));

    // Sidebar toggle functionality
    const toggleButton = document.querySelector(".menu-toggle");
    const sidebar = document.querySelector(".sidebar");

    toggleButton.addEventListener("click", function() {
        sidebar.classList.toggle("collapsed");
    });

    // Initialize the mental well-being chart
    const ctx = document.getElementById('mentalChart').getContext('2d');
    const mentalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            datasets: [{
                label: 'Mental Well-being',
                data: [65, 59, 80, 81, 56, 55, 40],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
