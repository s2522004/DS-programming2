const AREA_API_URL = "https://www.jma.go.jp/bosai/common/const/area.json";
const FORECAST_BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/";

const areaSelect = document.getElementById('area-select');
const areaNameDisp = document.getElementById('area-name');
const forecastContainer = document.getElementById('forecast-container');

// 1. 地域リストの取得と表示
async function init() {
    try {
        const response = await fetch(AREA_API_URL);
        const data = await response.json();

        // "offices"（都道府県単位のリスト）を取り出し、セレクトボックスに追加
        const offices = data.offices;
        for (const code in offices) {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = offices[code].name;
            areaSelect.appendChild(option);
        }
    } catch (error) {
        console.error("地域リストの取得に失敗しました:", error);
    }
}

// 2. 天気情報の取得と表示
async function fetchWeather(areaCode) {
    try {
        const response = await fetch(`${FORECAST_BASE_URL}${areaCode}.json`);
        const data = await response.json();

        // データの解析（最初のエリアの情報を取得）
        const report = data[0];
        const areaName = report.timeSeries[0].areas[0].area.name;
        const timeSeries = report.timeSeries[0]; // 天気予報の時系列データ

        displayWeather(areaName, timeSeries);
    } catch (error) {
        console.error("天気情報の取得に失敗しました:", error);
    }
}

// 3. 画面への表示処理
function displayWeather(name, timeSeries) {
    areaNameDisp.textContent = `${name} の天気予報`;
    forecastContainer.innerHTML = ''; // 前の予報をクリア

    const dates = timeSeries.timeDefines; // 予報日
    const weathers = timeSeries.areas[0].weathers; // 天気内容

    dates.forEach((date, index) => {
        const div = document.createElement('div');
        div.className = 'forecast-item';
        const formattedDate = new Date(date).toLocaleDateString();

        div.innerHTML = `
            <strong>${formattedDate}</strong>: ${weathers[index]}
        `;
        forecastContainer.appendChild(div);
    });
}

// セレクトボックスが変更された時のイベント
areaSelect.addEventListener('change', (e) => {
    const areaCode = e.target.value;
    if (areaCode) {
        fetchWeather(areaCode);
    }
});

init();