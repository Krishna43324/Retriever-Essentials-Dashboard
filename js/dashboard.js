// ---- Replace this with real data (later: load from a CSV/API/database) ----
const DATA = {
    students: [
        { name: "Ava Johnson", grade: 9, dept: "Math", gpa: 3.8, att: 97 },
        { name: "Liam Chen", grade: 9, dept: "Science", gpa: 3.1, att: 91 },
        { name: "Maya Patel", grade: 10, dept: "English", gpa: 3.5, att: 94 },
        { name: "Noah Garcia", grade: 10, dept: "Math", gpa: 2.4, att: 82 },
        { name: "Emma Davis", grade: 11, dept: "Science", gpa: 3.9, att: 98 },
        { name: "Lucas Brown", grade: 11, dept: "English", gpa: 2.9, att: 88 },
        { name: "Sofia Martinez", grade: 12, dept: "Math", gpa: 3.3, att: 93 },
        { name: "Ethan Wilson", grade: 12, dept: "Science", gpa: 2.2, att: 79 },
        { name: "Zoe Kim", grade: 9, dept: "English", gpa: 3.6, att: 95 },
        { name: "Owen Lee", grade: 10, dept: "Science", gpa: 3.0, att: 90 }
    ],
    attendanceTrend: { labels: ["Apr", "May", "Jun", "Jul", "Aug", "Sep"], values: [94, 93, 91, 95, 92, 93] }
};
const status = s => (s.gpa < 2.5 || s.att < 85) ? "At risk" : (s.gpa < 3.0 || s.att < 90) ? "Watch" : "On track";
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const avg = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0;
let charts = [];

function render() {
    const dept = document.getElementById("dept").value;
    const list = DATA.students.filter(s => dept === "All" || s.dept === dept);
    const st = list.map(status);
    document.getElementById("kpis").innerHTML = [
        ["Total students", list.length],
        ["Average GPA", avg(list.map(s => s.gpa)).toFixed(2)],
        ["Avg attendance", avg(list.map(s => s.att)).toFixed(1) + "%"],
        ["At-risk students", st.filter(x => x === "At risk").length]
    ].map(k => `<div class="card kpi"><div class="label">${k[0]}</div><div class="value">${k[1]}</div></div>`).join("");
    document.getElementById("rows").innerHTML = list.map((s, i) =>
        `<tr><td>${s.name}</td><td>${s.grade}</td><td>${s.dept}</td><td>${s.gpa.toFixed(1)}</td><td>${s.att}%</td><td><span class="pill ${st[i]}">${st[i]}</span></td></tr>`).join("");

    charts.forEach(c => c.destroy());
    Chart.defaults.color = css("--muted");
    Chart.defaults.borderColor = css("--line");
    Chart.defaults.maintainAspectRatio = false;
    const grades = [9, 10, 11, 12];
    const accent = css("--accent"), cols = [css("--good"), css("--warn"), css("--bad")];
    charts = [
        new Chart("c1", { type: "bar", data: { labels: grades.map(g => "Grade " + g), datasets: [{ data: grades.map(g => list.filter(s => s.grade === g).length), backgroundColor: accent, borderRadius: 6 }] }, options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } } }),
        new Chart("c2", { type: "line", data: { labels: DATA.attendanceTrend.labels, datasets: [{ data: DATA.attendanceTrend.values, borderColor: accent, backgroundColor: accent + "33", fill: true, tension: .3 }] }, options: { plugins: { legend: { display: false } }, scales: { y: { min: 80, max: 100 } } } }),
        new Chart("c3", { type: "doughnut", data: { labels: ["On track", "Watch", "At risk"], datasets: [{ data: ["On track", "Watch", "At risk"].map(l => st.filter(x => x === l).length), backgroundColor: cols, borderWidth: 0 }] }, options: { plugins: { legend: { position: "bottom" } } } })
    ];
}

function triggerUploadDataPage() {
    window.location.href = 'UploadData.html';
}

const sel = document.getElementById("dept");
["All", ...new Set(DATA.students.map(s => s.dept))].forEach(d => sel.add(new Option(d === "All" ? "All departments" : d, d)));
sel.addEventListener("change", render);
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
render();