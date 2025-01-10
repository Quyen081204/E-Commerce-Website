function analyze_month_stats() {
    fetch('/admin/statsview/api/month_stats',{
        method: 'post',
        body: JSON.stringify({
             'year': document.getElementById('year_input').value
        }),
        headers: {
            'Content-type': 'application/json'
        }
    }).then(res => {
    return res.json()
    }).then(function(data) {
        table = document.getElementById('table_month_stat')
        chart_container = document.getElementById('chart_container')
        chart_container.innerHTML = ""
        canvas = document.createElement('canvas')
        canvas.id = 'myProductMonthChart'
        chart_container.append(canvas)
        const ctx = canvas.getContext('2d')
        let labels = []
        let chart_data = []
        let colors = []
        let borderColors = []
        let red, green, blue

        table.innerHTML = ""
        tr1 = document.createElement('tr')
        th1 = document.createElement('th')
        th2 = document.createElement('th')
        th1.textContent = 'Thang'
        th2.textContent = 'Doanh thu'
        tr1.append(th1,th2)
        table.append(tr1)
        for (var r = 0;r < data.length;r++) {
            tr = document.createElement('tr')
            td1 = document.createElement('td')
            td2 = document.createElement('td')
            td1.textContent = data[r][0]
            labels.push(data[r][0])
            td2.textContent = data[r][1]
            chart_data.push(data[r][1])
            tr.append(td1,td2)
            table.append(tr)
            red = Math.random() * 255
            green = Math.random() * 255
            blue = Math.random() * 255
            colors.push(`rgb(${red},${green},${blue},0.2)`)
            borderColors.push(`rgb(${red},${green},${blue},1)`)
        }

        loadChart(ctx,'bar','Thong ke doanh thu theo thang',labels,chart_data,colors,borderColors)
    }).catch(err => console.log(err))
}

function loadChart(ctx, type,label,labels, data, colors, borderColors) {
                  new Chart(ctx, {
              type: type,
              data: {
                labels: labels,
                datasets: [{
                  label: label,
                  data: data,
                  borderWidth: 1,
                  backgroundColor: colors,
                  borderColor: borderColors
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
              }