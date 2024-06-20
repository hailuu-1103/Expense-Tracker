var expensesData2023 = JSON.parse(document.getElementById('expensesData2023').textContent);
var expensesData2024 = JSON.parse(document.getElementById('expensesData2024').textContent);
var currentYear = 2024;  // default to 2024
var chartInstance = null; // to keep track of the chart instance

document.addEventListener('DOMContentLoaded', (event) => {
    renderChart(expensesData2024, 'Năm 2024');
});

function renderChart(data, year) {
    var ctx = document.getElementById('monthlyExpensesChart').getContext('2d');
    if (chartInstance) {
        chartInstance.destroy(); // destroy the existing chart instance
    }
    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'],
            datasets: [{
                label: 'Expenses',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Đơn vị: Triệu VNĐ'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: year
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Chi tiêu theo từng tháng'
                }
            }
        }
    });
}

function switchYear(year) {
    currentYear = year;
    if (year === 2023) {
        renderChart(expensesData2023, 'Năm 2023');
    } else {
        renderChart(expensesData2024, 'Năm 2024');
    }
}

function confirmDelete(expenseId) {
    if (confirm('Are you sure you want to delete this expense?')) {
        window.location.href = '/delete/' + expenseId;
    }
}
