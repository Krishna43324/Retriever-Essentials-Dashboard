/* =====================================================================
   RETRIEVER ESSENTIALS DASHBOARD
   1. Sample data  (REPLACE with real data from your API/database later)
   2. Number crunching
   3. Section builders (Overview + one section per department)
   4. Carousel / navigation
   ===================================================================== */

/* ---------- 1. SAMPLE DATA ---------------------------------------------- */
const USING_SAMPLE_DATA = true;   // set to false once real data is wired in
const STUDENT_BODY = 900;         // total students (sample)

const TYPES = ["First-gen", "Transfer", "Master's", "Doctoral", "Continuing undergrad"];
const TYPE_CUM = [0.24, 0.42, 0.53, 0.58, 1];             // cumulative share of student body
const AGE_BANDS = ["18–19", "20–21", "22–24", "25+"];
const COLLEGES = ["Arts & Social Sciences", "Engineering & IT", "Natural & Math Sciences", "Undeclared / Other"];

/* To ADD A DEPARTMENT: add an object here. A new slide, tab, and header title are created automatically.
   base  = chance a student visits in a typical month
   mult  = how that chance changes for each entry of TYPES
   events: w = how popular (relative), hrs = hours per attendee for workshops (omit if not a workshop) */
const DEPARTMENTS = [
    {
        key: "engagement", short: "Engagement & Belonging", title: "Student Engagement & Belonging",
        desc: "Spaces and programs that help students find community: the Pride Center, The Gathering Space, mentoring, and campus events.",
        base: 0.05, mult: [1.2, 0.6, 0.3, 0.15, 1],
        events: [{ name: "Pride Center drop-in", w: 3 }, { name: "The Gathering Space", w: 4 }, { name: "Welcome Week events", w: 2 },
                 { name: "Peer mentoring circles", w: 2, hrs: 1 }, { name: "Heritage month events", w: 2 }],
        comments: [["The Gathering Space was the first place on campus I felt like I belonged.", "First-gen sophomore"],
                   ["My mentoring circle made the transition to UMBC so much easier.", "Transfer junior"],
                   ["I met my closest friends at a Pride Center event.", "Continuing undergrad"]]
    },
    {
        key: "support", short: "Support & Outreach", title: "Student Support & Outreach",
        desc: "CARE Team check-ins, case management, and outreach that connects students to the resources they need.",
        base: 0.035, mult: [1.5, 1.1, 0.5, 0.3, 0.8],
        events: [{ name: "CARE Team check-in", w: 4 }, { name: "Case management meeting", w: 3 }, { name: "Outreach tabling", w: 3 },
                 { name: "Resource workshops", w: 2, hrs: 1.5 }, { name: "Emergency support referral", w: 1 }],
        comments: [["My CARE Team contact helped me sort out a housing emergency in one week.", "First-gen senior"],
                   ["I didn't know where to start. They pointed me to exactly the right people.", "Master's student"],
                   ["The budgeting workshop changed how I plan my semester.", "Transfer junior"]]
    },
    {
        key: "conduct", short: "Conduct & Standards", title: "Student Conduct & Community Standards",
        desc: "Educational conversations, resolution meetings, and workshops that help students understand community expectations.",
        base: 0.012, mult: [0.9, 0.8, 0.3, 0.15, 1],
        events: [{ name: "Educational conversation", w: 4 }, { name: "Resolution meeting", w: 3 }, { name: "Restorative circle", w: 1 },
                 { name: "Standards workshop", w: 2, hrs: 2 }, { name: "Advising consult", w: 2 }],
        comments: [["The conversation felt fair, and I understood what the policy was for.", "Continuing undergrad"],
                   ["My advisor explained every step of the process clearly.", "First-gen sophomore"],
                   ["The workshop helped me make better choices going forward.", "Transfer junior"]]
    },
    {
        key: "crisp", short: "CRISP", title: "Center for Religion, Spirituality & Pluralism (CRISP)",
        desc: "Interfaith dialogue, reflection spaces, and community gatherings for students of every belief and background.",
        base: 0.022, mult: [0.8, 0.7, 1.1, 1, 1],
        events: [{ name: "Interfaith dialogue", w: 3 }, { name: "Reflection room", w: 4 }, { name: "Chaplain / advisor meeting", w: 2 },
                 { name: "Community meals", w: 3 }, { name: "Spiritual life workshop", w: 2, hrs: 1.5 }],
        comments: [["The reflection room is my quiet reset between classes.", "Doctoral student"],
                   ["Interfaith dialogue helped me understand my roommate's traditions.", "Continuing undergrad"],
                   ["The community meals made me feel at home during exams.", "Master's student"]]
    }
];

const SECTIONS = [
    { key: "overview", short: "Overview", title: "Campus Overview", kicker: "General statistics · last 12 months" },
    ...DEPARTMENTS.map(d => ({ ...d, kicker: "Department statistics · last 12 months" }))
];

/* Last 12 months, ending with the current month */
const SEASON = [0.8, 1, 1.1, 1.1, 0.7, 0.25, 0.2, 0.6, 1.2, 1.3, 1, 0.6];   // Jan..Dec activity level
const MONTHS = Array.from({ length: 12 }, (_, i) => {
    const d = new Date(); d.setDate(1); d.setMonth(d.getMonth() - (11 - i));
    return { label: d.toLocaleString("en-US", { month: "short" }), m: d.getMonth() };
});

function mulberry32(a) {            // small seeded random generator so sample data is stable between reloads
    return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}

/* students: [{id, name, type, standing, age, college, prop}]
   visits:   [{s: studentId, d: departmentKey, m: monthIndex 0-11, e: eventIndex}]  (one row per visit) */
function makeSampleData() {
    const rnd = mulberry32(2026), pick = a => a[Math.floor(rnd() * a.length)];
    const first = ["Ava", "Liam", "Maya", "Noah", "Emma", "Lucas", "Sofia", "Ethan", "Zoe", "Owen", "Aisha", "Diego", "Priya", "Marcus", "Hana", "Omar", "Chloe", "Jamal", "Lena", "Tariq", "Grace", "Mateo", "Nia", "Kai"];
    const last = ["Johnson", "Chen", "Patel", "Garcia", "Davis", "Brown", "Martinez", "Wilson", "Kim", "Lee", "Nguyen", "Okafor", "Singh", "Rossi", "Haddad", "Cohen", "Reyes", "Adams", "Khan", "Moore"];
    const students = Array.from({ length: STUDENT_BODY }, (_, id) => {
        const r = rnd(); let t = 0; while (r > TYPE_CUM[t]) t++;
        const grad = t === 2 || t === 3;
        const standing = grad ? "Graduate" : t === 1 ? pick(["Junior", "Junior", "Senior"]) : pick(["Freshman", "Sophomore", "Junior", "Senior"]);
        const age = grad ? pick(["22–24", "25+", "25+"]) : standing === "Freshman" ? "18–19" : standing === "Sophomore" ? pick(["18–19", "20–21"])
                  : standing === "Junior" ? pick(["20–21", "20–21", "22–24"]) : pick(["20–21", "22–24", "22–24", "25+"]);
        return { id, name: pick(first) + " " + pick(last), type: TYPES[t], standing, age, college: pick(COLLEGES), prop: 0.3 + rnd() * rnd() * 3 };
    });
    const visits = [];
    DEPARTMENTS.forEach(dep => {
        const totalW = dep.events.reduce((a, e) => a + e.w, 0);
        const pickEvent = () => { let x = rnd() * totalW, i = 0; while (x > dep.events[i].w) x -= dep.events[i++].w; return i; };
        students.forEach(s => {
            const mult = dep.mult[TYPES.indexOf(s.type)];
            MONTHS.forEach((mo, mi) => {
                if (rnd() < Math.min(0.9, dep.base * mult * s.prop * SEASON[mo.m])) {
                    let n = 1; while (rnd() < 0.35 && n < 6) n++;
                    for (let k = 0; k < n; k++) visits.push({ s: s.id, d: dep.key, m: mi, e: pickEvent() });
                }
            });
        });
    });
    return { students, visits };
}

const { students: STUDENTS, visits: VISITS } = makeSampleData();

/* ---------- 2. NUMBER CRUNCHING ------------------------------------------ */
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const pct = (n, d) => d ? Math.round(n / d * 1000) / 10 : 0;
const fmt = n => n.toLocaleString("en-US");
const argmax = a => a.indexOf(Math.max(...a));
const argmin = a => a.indexOf(Math.min(...a));
const bodyByType = TYPES.map(t => STUDENTS.filter(s => s.type === t).length);

/* Summarize a list of visits (one department, or all of them) */
function summarize(list) {
    const per = new Map(), byMonth = Array(12).fill(0), monthSets = MONTHS.map(() => new Set());
    let hours = 0;
    const hoursByDept = {}, studentsByDept = {};
    list.forEach(v => {
        per.set(v.s, (per.get(v.s) || 0) + 1);
        byMonth[v.m]++;
        monthSets[v.m].add(v.s);
        const dep = DEPARTMENTS.find(d => d.key === v.d), h = dep.events[v.e].hrs || 0;
        hours += h; hoursByDept[v.d] = (hoursByDept[v.d] || 0) + h;
        (studentsByDept[v.d] = studentsByDept[v.d] || new Set()).add(v.s);
    });
    const ids = [...per.keys()];
    const countBy = (key, values) => values.map(x => ids.filter(id => STUDENTS[id][key] === x).length);
    return {
        total: list.length, engaged: ids.length, per, byMonth, hours, hoursByDept, studentsByDept,
        monthlyPct: monthSets.map(s => pct(s.size, STUDENT_BODY)),
        byType: countBy("type", TYPES), byAge: countBy("age", AGE_BANDS), byCollege: countBy("college", COLLEGES)
    };
}

/* Soft, non-alarming observations about where participation could grow */
function reachNotes(byType, engaged) {
    const overall = pct(engaged, STUDENT_BODY);
    const gaps = TYPES.map((t, i) => ({ t, rate: pct(byType[i], bodyByType[i]), n: bodyByType[i] }))
        .filter(g => g.n >= 30 && g.rate < overall * 0.65)
        .sort((a, b) => a.rate / overall - b.rate / overall).slice(0, 2);
    return gaps.map(g => `${g.t} students took part at a lower rate (${g.rate}%) than students overall (${overall}%).`);
}

/* ---------- 3. SECTION BUILDERS ------------------------------------------ */
const C = { gold: "#fdb515", black: "#1a1a1a", gray: "#8a8d91", lgray: "#cfd2d6", pale: "#f6dd8f" };
const PAL = [C.gold, C.black, C.gray, C.lgray, C.pale];
let charts = [], pending = [];

const kpi = (label, value, sub = "") => `<div class="card kpi"><div class="label">${label}</div><div class="value">${value}</div>${sub ? `<div class="sub">${sub}</div>` : ""}</div>`;

function chartCard(id, title, caption, run) {
    pending.push(run);
    return `<div class="card"><h2>${title}</h2><div class="chart-box"><canvas id="${id}"></canvas></div><p class="caption">${caption}</p></div>`;
}

const noLegend = { legend: { display: false } };
const lineChart = (id, labels, data, suffix = "") => () => new Chart(id, {
    type: "line",
    data: { labels, datasets: [{ data, borderColor: C.black, backgroundColor: C.gold + "55", fill: true, tension: 0.3, pointBackgroundColor: C.gold, pointBorderColor: C.black }] },
    options: { plugins: noLegend, scales: { y: { beginAtZero: true, ticks: { callback: v => v + suffix } } } }
});
const barChart = (id, labels, data, o = {}) => () => new Chart(id, {
    type: "bar",
    data: { labels, datasets: [{ data, backgroundColor: o.color || C.gold, borderRadius: 6 }] },
    options: { indexAxis: o.horizontal ? "y" : "x", plugins: noLegend, scales: { [o.horizontal ? "x" : "y"]: { beginAtZero: true, ticks: { precision: 0, callback: v => v + (o.suffix || "") } } } }
});
const donut = (id, labels, data) => () => new Chart(id, {
    type: "doughnut",
    data: { labels, datasets: [{ data, backgroundColor: PAL, borderColor: "#fff", borderWidth: 2 }] },
    options: { plugins: { legend: { position: "bottom" } } }
});

function commentsCard(list) {
    return `<div class="card"><h2>What students are saying</h2>${list.map(c => `<blockquote class="quote"><p>“${esc(c[0])}”</p><cite>— ${esc(c[1])}</cite></blockquote>`).join("")}
        <p class="fineprint">Sample comments. How comments are collected (for example a short post-visit survey) is still to be decided.</p></div>`;
}

function notesCard(notes) {
    const items = notes.length ? notes : ["Participation looks balanced across student groups right now."];
    return `<div class="card notes"><h2>Worth a closer look</h2><ul>${items.map(n => `<li>${n}</li>`).join("")}</ul></div>`;
}

function overviewSection() {
    const s = summarize(VISITS), id = "ov";
    const bodyShare = bodyByType.map(n => pct(n, STUDENT_BODY));
    const engShare = s.byType.map(n => pct(n, s.engaged));
    const avgPct = Math.round(s.monthlyPct.reduce((a, b) => a + b, 0) / 12 * 10) / 10;
    const topT = argmax(s.byType), topA = argmax(s.byAge), topC = argmax(s.byCollege);
    const hrsLabels = DEPARTMENTS.map(d => d.short), hrs = DEPARTMENTS.map(d => s.hoursByDept[d.key] || 0);
    const engByDept = DEPARTMENTS.map(d => (s.studentsByDept[d.key] || new Set()).size);

    const notes = [];
    TYPES.forEach((t, i) => { if (bodyShare[i] >= 4 && engShare[i] < bodyShare[i] * 0.7) notes.push({ gap: engShare[i] / bodyShare[i], text: `${t} students are ${bodyShare[i]}% of the student body but ${engShare[i]}% of engaged students.` }); });
    const gentle = notes.sort((a, b) => a.gap - b.gap).slice(0, 2).map(n => n.text);
    gentle.push(`Engagement is lowest in ${MONTHS[argmin(s.monthlyPct)].label} (${Math.min(...s.monthlyPct)}%), which may be a good window for outreach.`);

    const rows = DEPARTMENTS.map((d, i) => `<tr><td><button class="linklike" data-go="${i + 1}">${esc(d.short)}</button></td><td class="num">${fmt(engByDept[i])}</td><td class="num">${pct(engByDept[i], STUDENT_BODY)}%</td><td class="num">${fmt(VISITS.filter(v => v.d === d.key).length)}</td><td class="num">${hrs[i]}</td></tr>`).join("");

    return `
    <p class="slide-lead">A campus-wide look at who is using our offices, how often, and how engagement changes through the year. Use the arrows or swipe sideways to see each department.</p>
    <section class="kpis">
      ${kpi("Student body", fmt(STUDENT_BODY))}
      ${kpi("Students engaged", fmt(s.engaged), pct(s.engaged, STUDENT_BODY) + "% of student body")}
      ${kpi("Total visits", fmt(s.total), "across all offices")}
      ${kpi("Avg visits per student", (s.total / s.engaged).toFixed(1), "among engaged students")}
      ${kpi("Workshop hours", fmt(s.hours), "collective, all attendees")}
    </section>
    <section class="charts">
      ${chartCard(id + "1", "Student body engaged, by month", `On average ${avgPct}% of students engaged each month, peaking at ${Math.max(...s.monthlyPct)}% in ${MONTHS[argmax(s.monthlyPct)].label}.`, lineChart(id + "1", MONTHS.map(m => m.label), s.monthlyPct, "%"))}
      ${chartCard(id + "2", "Students engaged, by office", `${DEPARTMENTS[argmax(engByDept)].short} reached the most students (${fmt(Math.max(...engByDept))}). A student can use more than one office.`, barChart(id + "2", hrsLabels, engByDept, { horizontal: true }))}
      ${chartCard(id + "3", "Student body vs. engaged students", `${TYPES[topT]} students are the largest engaged group (${engShare[topT]}%). Gold bars show engaged students; gray shows the whole student body.`, () => new Chart(id + "3", {
          type: "bar", data: { labels: TYPES, datasets: [{ label: "Student body", data: bodyShare, backgroundColor: C.lgray, borderRadius: 4 }, { label: "Engaged students", data: engShare, backgroundColor: C.gold, borderRadius: 4 }] },
          options: { plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true, ticks: { callback: v => v + "%" } } } } }))}
      ${chartCard(id + "4", "Engaged students, by age", `Most engaged students are ${AGE_BANDS[topA]} (${pct(s.byAge[topA], s.engaged)}%).`, barChart(id + "4", AGE_BANDS, s.byAge))}
      ${chartCard(id + "5", "Engaged students, by college", `${COLLEGES[topC]} has the most engaged students (${pct(s.byCollege[topC], s.engaged)}%).`, barChart(id + "5", COLLEGES, s.byCollege, { horizontal: true, color: C.black }))}
      ${chartCard(id + "6", "Workshop hours, by office", `Students logged ${fmt(s.hours)} workshop hours in total; ${DEPARTMENTS[argmax(hrs)].short} accounts for the most (${Math.max(...hrs)}).`, barChart(id + "6", hrsLabels, hrs, { color: C.gray }))}
    </section>
    <section class="split" style="margin-top:16px">
      <div class="card"><h2>Offices at a glance</h2><div class="table-wrap"><table><thead><tr><th>Office</th><th class="num">Students</th><th class="num">% of body</th><th class="num">Visits</th><th class="num">Workshop hrs</th></tr></thead><tbody>${rows}</tbody></table></div></div>
      ${commentsCard(DEPARTMENTS.slice(0, 3).map(d => d.comments[0]).concat([DEPARTMENTS[3].comments[0]]))}
    </section>
    ${notesCard(gentle)}`;
}

function deptSection(dep) {
    const list = VISITS.filter(v => v.d === dep.key), s = summarize(list), id = dep.key;
    const evCounts = dep.events.map((_, i) => list.filter(v => v.e === i).length);
    const reach = TYPES.map((_, i) => pct(s.byType[i], bodyByType[i]));
    const topE = argmax(evCounts), topT = argmax(s.byType);
    const eligible = reach.map((r, i) => bodyByType[i] >= 30 ? r : null);
    const hi = argmax(eligible.map(r => r ?? -1)), lo = argmin(eligible.map(r => r ?? 1e9));

    const top = [...s.per.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8), max = top.length ? top[0][1] : 1;
    const rows = top.map(([sid, n]) => { const st = STUDENTS[sid];
        return `<tr><td>${esc(st.name)}</td><td>${esc(st.type)}</td><td>${esc(st.standing)}</td><td class="num"><span class="visit-bar" style="width:${Math.round(n / max * 48)}px"></span>${n}</td></tr>`; }).join("");

    return `
    <p class="slide-lead">${esc(dep.desc)}</p>
    <section class="kpis">
      ${kpi("Students engaged", fmt(s.engaged), pct(s.engaged, STUDENT_BODY) + "% of student body")}
      ${kpi("Total visits", fmt(s.total))}
      ${kpi("Avg visits per student", s.engaged ? (s.total / s.engaged).toFixed(1) : "0", "among engaged students")}
      ${kpi("Workshop hours", fmt(s.hours), "collective, all attendees")}
    </section>
    <section class="charts two">
      ${chartCard(id + "1", "Visits by month", `Visits peaked in ${MONTHS[argmax(s.byMonth)].label} (${Math.max(...s.byMonth)}) and were lowest in ${MONTHS[argmin(s.byMonth)].label} (${Math.min(...s.byMonth)}).`, lineChart(id + "1", MONTHS.map(m => m.label), s.byMonth))}
      ${chartCard(id + "2", "Who we serve", `${TYPES[topT]} students make up the largest share of engaged students (${pct(s.byType[topT], s.engaged)}%).`, donut(id + "2", TYPES, s.byType))}
      ${chartCard(id + "3", "Programs & events (visits)", `${dep.events[topE].name} drew the most attendance (${fmt(evCounts[topE])} visits). Workshops added up to ${fmt(s.hours)} hours.`, barChart(id + "3", dep.events.map(e => e.name), evCounts, { horizontal: true, color: C.black }))}
      ${chartCard(id + "4", "Share of each group that took part", `${TYPES[hi]} students took part most (${reach[hi]}%) and ${TYPES[lo]} students least (${reach[lo]}%).`, barChart(id + "4", TYPES, reach, { suffix: "%", color: C.gray }))}
    </section>
    <section class="split" style="margin-top:16px">
      ${commentsCard(dep.comments)}
      <div class="card"><h2>Most frequent visitors</h2><div class="table-wrap"><table><thead><tr><th>Student</th><th>Type</th><th>Standing</th><th class="num">Visits</th></tr></thead><tbody>${rows}</tbody></table></div></div>
    </section>
    ${notesCard(reachNotes(s.byType, s.engaged))}`;
}

function buildDashboard() {
    charts.forEach(c => c.destroy()); charts = []; pending = [];
    Chart.defaults.color = "#666b73";
    Chart.defaults.borderColor = "#e3e7ef";
    Chart.defaults.maintainAspectRatio = false;
    document.getElementById("carousel").innerHTML = SECTIONS.map(sec =>
        `<section class="slide" id="slide-${sec.key}" aria-label="${esc(sec.title)}">${sec.key === "overview" ? overviewSection() : deptSection(sec)}</section>`).join("");
    pending.forEach(run => charts.push(run()));
}

/* ---------- 4. CAROUSEL / NAVIGATION ------------------------------------- */
const track = document.getElementById("carousel");
const tabsEl = document.getElementById("tabs");
const prevBtn = document.getElementById("prevBtn"), nextBtn = document.getElementById("nextBtn");
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
let index = 0, raf = 0;

tabsEl.innerHTML = SECTIONS.map((s, i) => `<button type="button" class="tab" data-go="${i}">${esc(s.short)}</button>`).join("");

function goTo(i, instant) {
    i = Math.max(0, Math.min(SECTIONS.length - 1, i));
    track.scrollTo({ left: i * track.clientWidth, behavior: instant || reduceMotion ? "auto" : "smooth" });
    if (instant) update(i);
}

function update(i) {
    i = Math.max(0, Math.min(SECTIONS.length - 1, i || 0));
    if (i === index && document.getElementById("sectionTitle").dataset.ready) return;
    index = i;
    const sec = SECTIONS[i], h1 = document.getElementById("sectionTitle");
    h1.dataset.ready = "1";
    h1.textContent = sec.title;
    h1.style.animation = "none"; void h1.offsetWidth; h1.style.animation = "";      // replay the small slide-in
    document.getElementById("sectionKicker").textContent = sec.kicker;
    document.getElementById("sectionCount").textContent = `${i + 1} / ${SECTIONS.length}`;
    document.title = sec.title + " | Retriever Essentials";
    prevBtn.disabled = i === 0; nextBtn.disabled = i === SECTIONS.length - 1;
    tabsEl.querySelectorAll(".tab").forEach((t, k) => t.setAttribute("aria-current", k === i ? "true" : "false"));
    const active = tabsEl.children[i]; if (active && active.scrollIntoView) active.scrollIntoView({ inline: "nearest", block: "nearest" });
    history.replaceState(null, "", "#" + sec.key);
}

track.addEventListener("scroll", () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => update(Math.round(track.scrollLeft / track.clientWidth))); });
window.addEventListener("resize", () => track.scrollTo({ left: index * track.clientWidth, behavior: "auto" }));
prevBtn.addEventListener("click", () => goTo(index - 1));
nextBtn.addEventListener("click", () => goTo(index + 1));
document.addEventListener("click", e => { const b = e.target.closest("[data-go]"); if (b) goTo(Number(b.dataset.go)); });
document.addEventListener("keydown", e => {
    if (/INPUT|SELECT|TEXTAREA/.test(e.target.tagName)) return;
    if (e.key === "ArrowRight") goTo(index + 1); else if (e.key === "ArrowLeft") goTo(index - 1);
});

/* ---------- Page links (unchanged) --------------------------------------- */
function triggerUploadDataPage() { window.location.href = "/frontend/UploadData.html"; }
function triggerDeleteDataPage() { window.location.href = "/frontend/DeleteData.html"; }
function triggerCreateAccountPage() { window.location.href = "/frontend/CreateAccount.html"; }
function triggerCreateChartPage() { window.location.href = "/frontend/CreateChart.html"; }

/* ---------- Start --------------------------------------------------------- */
document.getElementById("samplePill").hidden = !USING_SAMPLE_DATA;
buildDashboard();
const startAt = SECTIONS.findIndex(s => "#" + s.key === location.hash);
goTo(startAt > 0 ? startAt : 0, true);
