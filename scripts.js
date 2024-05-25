// 処理の概要
//1、イベントリスナーの追加
// ボタン（start - button）がクリックされたときに特定の処理を実行するように設定。

// ２，データ取得のためのリクエスト送信
//     / start エンドポイントに対してHTTP GETリクエストを送信。

// ３、データの取得と保存
// サーバーからの応答をJSON形式で受け取り、そのデータをブラウザのローカルストレージに保存。

// ４，データの表示
// 保存したデータをHTMLのテーブルに表示。

document.getElementById('start-button').addEventListener('click', () => {
    fetch('./start')
        .then(response => response.json())
        .then(data => {
            // Store data in local storage
            localStorage.setItem('edinetData', JSON.stringify(data));

            // Display data in table
            displayData(data);

            // Plot data
            plotData(data, "CurrentQuarterDuration", "jpcrp_cor:BasicEarningsLossPerShareSummaryOfBusinessResults", "EPS");
            plotData(data, "CurrentYTDDuration", "jppfs_cor:GrossProfit", "粗利益");
        })
        .catch(error => console.error('Error:', error));
});

// ローカルストレージに入っているデータをプロットする。
function displayData(data) {
    const tableHead = document.querySelector('#data-table thead tr');
    const tableBody = document.querySelector('#data-table tbody');

    // Clear previous table data
    tableHead.innerHTML = '';
    tableBody.innerHTML = '';

    if (data.length > 0) {
        // Create table headers
        Object.keys(data[0]).forEach(key => {
            const th = document.createElement('th');
            th.textContent = key;
            tableHead.appendChild(th);
        });

        // Create table rows
        data.forEach(row => {
            const tr = document.createElement('tr');
            Object.values(row).forEach(value => {
                const td = document.createElement('td');
                td.textContent = value;
                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        });
    }
}
function plotData(data, contextId, elementId, elementJpName) {
    const plotData = data.filter(item => item['要素ID'] === elementId && item['コンテキストID'] === contextId);
    const labels = plotData.map(item => item['会社名']);
    const values = plotData.map(item => parseFloat(item['値']));

    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: elementJpName,
                data: values,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
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
}