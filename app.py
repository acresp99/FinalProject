from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlalchemy import cast, func, Float, Integer

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


class StatePopulation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    state: str
    population: str
    annual_change: str


DB_NAME = "state_pop.db"
engine = create_engine(f"sqlite:///{DB_NAME}")
SQLModel.metadata.create_all(engine)


def get_db_session():
    return Session(engine)


@app.get("/api/states", response_model=list)
def get_states(sort_by: str | None = None, order: str = "asc"):
    """
    Fetch states data from database with optional sorting.
    sort_by: 'state', 'population', 'annual_change'
    order: 'asc' or 'desc'
    """
    stmt = select(StatePopulation)

    if sort_by:
        sort_key = sort_by.lower()
        is_desc = order.lower() == "desc"
        if sort_key == "state":
            stmt = stmt.order_by(StatePopulation.state.desc() if is_desc else StatePopulation.state)
        elif sort_key == "population":
            stmt = stmt.order_by(
                cast(func.replace(StatePopulation.population, ",", ""), Integer).desc()
                if is_desc
                else cast(func.replace(StatePopulation.population, ",", ""), Integer)
            )
        elif sort_key == "annual_change":
            stmt = stmt.order_by(
                cast(func.replace(StatePopulation.annual_change, "%", ""), Float).desc()
                if is_desc
                else cast(func.replace(StatePopulation.annual_change, "%", ""), Float)
            )

    with get_db_session() as session:
        rows = session.exec(stmt).all()

    result = []
    for row in rows:
        result.append(
            {
                "State": row.state,
                "Population": row.population,
                "Annual_Change": row.annual_change,
            }
        )

    return result


@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve the main HTML page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>US State Population Data</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            }
            
            .header p {
                font-size: 1.1em;
                opacity: 0.95;
            }
            
            .content {
                padding: 30px;
            }
            
            .table-wrapper {
                overflow-x: auto;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            
            thead {
                background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
                color: white;
                position: sticky;
                top: 0;
            }
            
            th {
                padding: 16px;
                text-align: left;
                font-weight: 600;
                font-size: 1.05em;
                cursor: pointer;
                user-select: none;
                transition: background-color 0.3s ease;
                position: relative;
            }
            
            th:hover {
                background: linear-gradient(135deg, #00c9e6 0%, #0088dd 100%);
            }
            
            th::after {
                content: '⇅';
                margin-left: 8px;
                opacity: 0.7;
            }
            
            th.asc::after {
                content: '↑';
                opacity: 1;
            }
            
            th.desc::after {
                content: '↓';
                opacity: 1;
            }
            
            tbody tr {
                border-bottom: 1px solid #e0e0e0;
                transition: background-color 0.2s ease;
            }
            
            tbody tr:hover {
                background-color: #f0f8ff;
            }
            
            tbody tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            
            td {
                padding: 14px 16px;
                color: #333;
            }
            
            td:first-child {
                font-weight: 500;
                color: #0099ff;
            }
            
            .pop {
                color: #00a86b;
                font-weight: 500;
            }
            
            .change {
                font-weight: 500;
                text-align: right;
            }
            
            .change.positive {
                color: #00a86b;
            }
            
            .change.negative {
                color: #ff4444;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #0099ff;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .info {
                text-align: center;
                color: #666;
                margin-top: 20px;
                font-size: 0.95em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 US State Population Data</h1>
                <p>Click column headers to sort • All data from 2026</p>
            </div>
            <div class="content">
                <div id="loading" class="loading">
                    <div class="spinner"></div>
                    <p>Loading data...</p>
                </div>
                <div id="table-container" class="table-wrapper" style="display: none;">
                    <table id="data-table">
                        <thead>
                            <tr>
                                <th id="sort-state">State</th>
                                <th id="sort-population">Population</th>
                                <th id="sort-annual-change">Annual Change</th>
                            </tr>
                        </thead>
                        <tbody id="table-body">
                        </tbody>
                    </table>
                </div>
                <div class="info">
                    <p id="record-count"></p>
                </div>
            </div>
        </div>
        
        <script>
            let currentSort = null;
            let currentOrder = 'asc';
            let allData = [];
            
            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                loadData();
                setupSortButtons();
            });
            
            function setupSortButtons() {
                document.getElementById('sort-state').addEventListener('click', () => sortData('state'));
                document.getElementById('sort-population').addEventListener('click', () => sortData('population'));
                document.getElementById('sort-annual-change').addEventListener('click', () => sortData('annual_change'));
            }
            
            function sortData(column) {
                // Toggle order if same column clicked
                if (currentSort === column) {
                    currentOrder = currentOrder === 'asc' ? 'desc' : 'asc';
                } else {
                    currentSort = column;
                    currentOrder = column === 'state' ? 'asc' : 'desc'; // Default: alpha asc, numeric desc
                }
                
                updateSortHeaders();
                loadData();
            }
            
            function updateSortHeaders() {
                document.querySelectorAll('th').forEach(th => {
                    th.classList.remove('asc', 'desc');
                });
                
                if (currentSort === 'state') {
                    document.getElementById('sort-state').classList.add(currentOrder);
                } else if (currentSort === 'population') {
                    document.getElementById('sort-population').classList.add(currentOrder);
                } else if (currentSort === 'annual_change') {
                    document.getElementById('sort-annual-change').classList.add(currentOrder);
                }
            }
            
            function loadData() {
                const params = new URLSearchParams();
                if (currentSort) {
                    params.append('sort_by', currentSort);
                    params.append('order', currentOrder);
                }
                
                fetch('/api/states?' + params.toString())
                    .then(response => response.json())
                    .then(data => {
                        allData = data;
                        renderTable(data);
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('table-container').style.display = 'block';
                        document.getElementById('record-count').textContent = `Total: ${data.length} states`;
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        document.getElementById('loading').innerHTML = '<p>Error loading data</p>';
                    });
            }
            
            function renderTable(data) {
                const tbody = document.getElementById('table-body');
                tbody.innerHTML = '';
                
                data.forEach(row => {
                    const tr = document.createElement('tr');
                    
                    const changeValue = parseFloat(row['Annual_Change']);
                    const changeClass = changeValue > 0 ? 'positive' : 'negative';
                    
                    tr.innerHTML = `
                        <td>${row.State}</td>
                        <td class="pop">${row.Population}</td>
                        <td class="change ${changeClass}">${row.Annual_Change}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        </script>
    </body>
    </html>
    """

