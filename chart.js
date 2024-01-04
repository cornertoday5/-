function getChartData() {
    // フォームデータを取得
    var companyCode = document.getElementById('companyCode').value;
    var startDate = document.getElementById('startDate').value;
    var endDate = document.getElementById('endDate').value;

    // Flask バックエンドにデータを送信
    $.ajax({
        type: 'POST',
        url: '/get_chart_data',
        data: {
            companyCode: companyCode,
            startDate: startDate,
            endDate: endDate
        },
        success: function(response) {
            // 受け取った画像を表示
            $('#chartContainer').html('<img src="data:image/png;base64,' + response + '" alt="Stock Analysis Chart">');
        },
        error: function(error) {
            console.log(error);
        }
    });
}
