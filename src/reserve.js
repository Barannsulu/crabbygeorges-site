/* Crabby George's reservations – reads /reservations/rules.json, builds the form, posts to the booking endpoint. */
(function () {
  var form = document.getElementById('resForm');
  if (!form) return;
  var $ = function (id) { return document.getElementById(id); };
  var TZ = 'America/New_York';
  var rules = null;

  /* ---- shared slot logic (same code runs in the Google Apps Script) ---- */
  function toMin(hm) { var p = hm.split(':'); return Number(p[0]) * 60 + Number(p[1]); }
  function fromMin(m) { var h = Math.floor(m / 60), mm = m % 60; return (h < 10 ? '0' : '') + h + ':' + (mm < 10 ? '0' : '') + mm; }
  function addDays(dateStr, n) { var d = new Date(dateStr + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); }
  function slotsFor(r, dateStr, todayStr, nowMin) {
    if (!r || !r.enabled || !dateStr) return [];
    if (dateStr < todayStr || dateStr > addDays(todayStr, r.maxDaysAhead || 60)) return [];
    var day = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'][new Date(dateStr + 'T12:00:00Z').getUTCDay()];
    var h = r.hours && r.hours[day];
    if (!h) return [];
    var start = toMin(h[0]), end = toMin(h[1]) - (r.lastSeatingBeforeCloseMinutes || 0), step = r.slotMinutes || 30;
    var blocks = (r.closures || []).filter(function (c) { return dateStr >= c.date && dateStr <= (c.until || c.date); });
    var out = [];
    for (var t = start; t <= end; t += step) {
      if (dateStr === todayStr && t < nowMin + (r.minNoticeMinutes || 0)) continue;
      var blocked = blocks.some(function (c) {
        var f = c.from ? toMin(c.from) : 0, to = c.to ? toMin(c.to) : 24 * 60;
        return t >= f && t < to;
      });
      if (!blocked) out.push(fromMin(t));
    }
    return out;
  }
  /* ------------------------------------------------------------------- */

  function nowET() {
    var p = {};
    new Intl.DateTimeFormat('en-US', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false })
      .formatToParts(new Date()).forEach(function (x) { p[x.type] = x.value; });
    return { date: p.year + '-' + p.month + '-' + p.day, min: (Number(p.hour) % 24) * 60 + Number(p.minute) };
  }
  function label12(hm) { var m = toMin(hm), h = Math.floor(m / 60), mm = m % 60; return ((h + 11) % 12 + 1) + ':' + (mm < 10 ? '0' : '') + mm + (h < 12 ? ' AM' : ' PM'); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function say(msg, kind) { var b = $('resMsg'); b.innerHTML = msg; b.className = 'res-msg ' + (kind || ''); b.hidden = !msg; }

  function fillTimes() {
    var n = nowET(), d = $('resDate').value, sel = $('resTime');
    var s = slotsFor(rules, d, n.date, n.min);
    sel.innerHTML = s.length
      ? '<option value="">Choose a time</option>' + s.map(function (t) { return '<option value="' + t + '">' + label12(t) + '</option>'; }).join('')
      : '<option value="">' + (d ? 'No times available this day' : 'Pick a date first') + '</option>';
    var c = (rules.closures || []).filter(function (x) { return d >= x.date && d <= (x.until || x.date) && x.note; });
    $('resDayNote').textContent = c.length ? c.map(function (x) { return x.note; }).join(' ') : '';
  }

  function build(r) {
    rules = r;
    if (!r.enabled || !r.endpoint) {
      form.hidden = true;
      say(esc(r.closedMessage || 'Please call (843) 839-4044 to reserve a table.'), 'warn');
      return;
    }
    if (r.notice) $('resNotice').textContent = r.notice, $('resNotice').hidden = false;
    var n = nowET(), date = $('resDate');
    date.min = n.date; date.max = addDays(n.date, r.maxDaysAhead || 60);
    // default to the first day that still has times
    for (var i = 0; i < 7; i++) { var dd = addDays(n.date, i); if (slotsFor(r, dd, n.date, n.min).length) { date.value = dd; break; } }
    var ps = $('resParty'), opts = '<option value="">Guests</option>';
    for (var k = r.minParty || 1; k <= (r.maxParty || 20); k++) opts += '<option>' + k + '</option>';
    ps.innerHTML = opts;
    $('resLarge').textContent = r.largePartyMessage || '';
    $('resExtra').innerHTML = (r.extraFields || []).map(function (f) {
      var id = 'x_' + f.name, rq = f.required ? ' required' : '', star = f.required ? ' *' : '';
      var ctl = f.type === 'select'
        ? '<select id="' + id + '" name="' + esc(f.name) + '"' + rq + '><option value="">Choose one</option>' + (f.options || []).map(function (o) { return '<option>' + esc(o) + '</option>'; }).join('') + '</select>'
        : f.type === 'checkbox'
          ? '<input id="' + id + '" name="' + esc(f.name) + '" type="checkbox" value="Yes" style="width:auto">'
          : '<input id="' + id + '" name="' + esc(f.name) + '" type="text"' + rq + '>';
      return '<label for="' + id + '">' + esc(f.label) + star + '</label>' + ctl;
    }).join('');
    fillTimes();
    date.addEventListener('change', fillTimes);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var fd = new FormData(form), data = {};
    fd.forEach(function (v, k) { data[k] = v; });
    data.extras = {};
    (rules.extraFields || []).forEach(function (f) { data.extras[f.label] = data[f.name] || ''; delete data[f.name]; });
    var btn = form.querySelector('button[type=submit]');
    btn.disabled = true; btn.textContent = 'Booking…'; say('');
    fetch(rules.endpoint, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(data) })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.ok) throw new Error(res.error || 'Something went wrong');
        form.hidden = true;
        say('<strong>You\'re booked!</strong><br>' + esc(res.summary) + '<br>Confirmation code <strong>' + esc(res.code) + '</strong>.' +
            (data.email ? ' We emailed you a confirmation.' : '') + '<br>Need to change it? Call (843) 839-4044.', 'ok');
        window.scrollTo({ top: $('resMsg').getBoundingClientRect().top + window.scrollY - 120, behavior: 'smooth' });
      })
      .catch(function (err) {
        btn.disabled = false; btn.textContent = 'Reserve my table';
        say(esc(err.message) + ' If it keeps happening, call (843) 839-4044.', 'warn');
        fillTimes();
      });
  });

  fetch('/reservations/rules.json?t=' + Date.now()).then(function (r) { return r.json(); }).then(build)
    .catch(function () { form.hidden = true; say('Please call (843) 839-4044 to reserve a table.', 'warn'); });
})();
