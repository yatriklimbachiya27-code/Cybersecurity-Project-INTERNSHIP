/* ==========================================================================
   UPI Transaction Fraud Detection System - Client-side scripting
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Lucide Icons
    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }

    // 2. Auto-fade Flash Alerts
    const alerts = document.querySelectorAll(".alert-container .alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = "0";
            alert.style.transition = "opacity 0.8s ease";
            setTimeout(() => alert.remove(), 800);
        }, 5000);
    });

    // 3. Load Charts (if on Dashboard page)
    const riskChartCtx = document.getElementById("riskDistributionChart");
    const typeChartCtx = document.getElementById("txnTypeChart");
    const modelChartCtx = document.getElementById("modelFraudChart");

    if (riskChartCtx && typeChartCtx && modelChartCtx) {
        fetch("/api/stats")
            .then(res => res.json())
            .then(data => {
                renderCharts(data);
            })
            .catch(err => console.error("Error fetching stats api:", err));
    }

    // 4. Reactive Form Estimator (if on Monitor page)
    initInteractiveEstimator();
});

function renderCharts(apiData) {
    // Shared Chart options for Dark Theme
    const darkLegendColor = "#9ca3af";
    const darkGridColor = "rgba(255, 255, 255, 0.05)";
    
    // Chart 1: Risk Level Distribution (Doughnut)
    new Chart(document.getElementById("riskDistributionChart"), {
        type: "doughnut",
        data: {
            labels: apiData.risk_distribution.labels,
            datasets: [{
                data: apiData.risk_distribution.data,
                backgroundColor: [
                    "#00f2a1", // Low Risk (Neon Green)
                    "#ff9f43", // Medium Risk (Orange)
                    "#ff4a5a"  // High Risk (Red)
                ],
                borderColor: "rgba(7, 9, 19, 0.8)",
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: darkLegendColor, font: { family: "Inter", size: 11 } }
                }
            },
            cutout: "70%"
        }
    });

    // Chart 2: Transaction Type Distribution (Bar)
    new Chart(document.getElementById("txnTypeChart"), {
        type: "bar",
        data: {
            labels: apiData.transaction_types.labels,
            datasets: [{
                label: "Transactions",
                data: apiData.transaction_types.data,
                backgroundColor: [
                    "rgba(138, 112, 255, 0.75)",
                    "rgba(0, 242, 254, 0.75)"
                ],
                borderColor: [
                    "#8a70ff",
                    "#00f2fe"
                ],
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: darkLegendColor, font: { family: "Inter", size: 10 } }
                },
                y: {
                    grid: { color: darkGridColor },
                    ticks: { color: darkLegendColor, font: { family: "Inter", size: 10 } }
                }
            }
        }
    });

    // Chart 3: Model Fraud Detections (Polar Area)
    new Chart(document.getElementById("modelFraudChart"), {
        type: "polarArea",
        data: {
            labels: apiData.model_performance.labels,
            datasets: [{
                data: apiData.model_performance.data,
                backgroundColor: [
                    "rgba(138, 112, 255, 0.35)",
                    "rgba(0, 242, 254, 0.35)",
                    "rgba(255, 159, 67, 0.35)"
                ],
                borderColor: [
                    "#8a70ff",
                    "#00f2fe",
                    "#ff9f43"
                ],
                borderWidth: 1.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: darkLegendColor, font: { family: "Inter", size: 10 } }
                }
            },
            scales: {
                r: {
                    grid: { color: darkGridColor },
                    angleLines: { color: darkGridColor },
                    pointLabels: { color: darkLegendColor },
                    ticks: { display: false }
                }
            }
        }
    });
}

function initInteractiveEstimator() {
    const monitorForm = document.getElementById("monitorForm");
    if (!monitorForm) return;

    const amountInput = document.getElementById("amount");
    const accountAgeInput = document.getElementById("account_age");
    const ipInput = document.getElementById("ip_address");
    const deviceSelect = document.getElementById("device_id");
    const liveIndicator = document.getElementById("liveRiskIndicator");
    const liveMeter = document.getElementById("liveRiskMeter");

    const estimateRisk = () => {
        let score = 0;
        const amount = parseFloat(amountInput.value) || 0;
        const age = parseInt(accountAgeInput.value) || 30;
        const ip = ipInput.value;
        const device = deviceSelect.value;
        
        // 1. Amount factor
        if (amount > 25000) score += 40;
        else if (amount > 10000) score += 20;
        else if (amount > 5000) score += 10;
        
        // 2. Account Age factor
        if (age < 15) score += 25;
        else if (age < 30) score += 10;
        
        // 3. IP address factor (unusual IP prefix - not 192.168.)
        if (ip && !ip.startsWith("192.168.")) {
            score += 15;
        }
        
        // 4. Device factor
        if (device === "DV_NEW_99") {
            score += 20;
        }

        // Clamp
        score = Math.min(100, Math.max(0, score));

        // Color coding
        let color = "#00f2a1"; // Green
        let label = "Low Risk";
        if (score > 70) {
            color = "#ff4a5a"; // Red
            label = "High Risk (Blocked)";
        } else if (score > 35) {
            color = "#ff9f43"; // Orange
            label = "Medium Risk (Flagged)";
        }

        if (liveIndicator && liveMeter) {
            liveIndicator.innerText = `${label} (${score}%)`;
            liveIndicator.style.color = color;
            liveMeter.style.width = `${score}%`;
            liveMeter.style.backgroundColor = color;
            liveMeter.style.boxShadow = `0 0 10px ${color}`;
        }
    };

    // Attach event listeners
    [amountInput, accountAgeInput, ipInput, deviceSelect].forEach(el => {
        if (el) {
            el.addEventListener("input", estimateRisk);
            el.addEventListener("change", estimateRisk);
        }
    });

    // Initial run
    estimateRisk();
}
