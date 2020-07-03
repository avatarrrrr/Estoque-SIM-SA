/*
//Armazenament do canvas do js 
var ctx = document.getElementById("myChart");

//Variavel que expressa que nosso gráfico será em 2d
var chart = getContext('2d');

//TESTE GRAFICOS 
chart.fillStyle = "red";
chart.fillRect(0,0,100,200);

chart.fillStyle = "blue";
chart.fillRect(0,0,150,200);

*/
//Armazenament do canvas do js 
//GET CONTEX 2D - demonstra que o gráfico tá em 2d

var ctx = document.getElementById('myChart').getContext('2d');

var chart = new Chart(ctx, {

    type: 'bar',
    data: {
        labels: ['January', 'February', 'March'],
        
        
        datasets: [{
            label: 'Gráfico',
            backgroundColor: ['green', 'blue', 'yellow'],
            borderColor: 'rgb(255, 99, 132)',
            data: [50, 10, 5]
        }]
    },

    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }
});