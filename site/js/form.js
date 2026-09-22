/* Mendoza Marketing — the quote form.
 *
 * Loaded on /contact only (build.py's layout() takes `extra_scripts`; contact.py
 * passes this file). Ported from /root/openairgallery-src/site/js/site.js's
 * contact-form block, which is where the shape comes from.
 *
 * Nothing here is load-bearing. The page is finished without it:
 *
 *   no script      the <form> is action="mailto:…" method="post"
 *                  enctype="text/plain", so the button still produces an email
 *                  with the fields in it. Every field, label and option is in
 *                  the server HTML.
 *   script, no
 *   endpoint       (today) submit is taken over and the same brief is handed to
 *                  the visitor's mail app with a subject that names the service
 *                  and the sender — which the static action cannot write.
 *   script and
 *   endpoint       the fields POST to Formspree as JSON and the answer is said
 *                  inline. A failure falls back to the mailto rather than
 *                  swallowing the message.
 *
 * The browser validates first in every case: submit does not fire on a form
 * with an empty required field, and nothing here sets novalidate.
 *
 * The address is read off the form's own action rather than passed in, so
 * there is exactly one place in the build where Drew's email is written into
 * this page — change content.py and the fallback, the JS mailto and the note
 * under the button all move together.
 */
(function () {
  'use strict';

  var form = document.querySelector('#quote-form');
  if (!form) return;                       // every other page of the site

  var CFG = window.MM || {};
  var ENDPOINT = (CFG.form || '').trim();  // content.py FORM_ENDPOINT

  var action = form.getAttribute('action') || '';
  var TO = '';
  if (action.slice(0, 7).toLowerCase() === 'mailto:') {
    try { TO = decodeURIComponent(action.slice(7).split('?')[0]); }
    catch (e) { TO = action.slice(7).split('?')[0]; }
  }

  /* ---- ?service=drones ----------------------------------------------- *
   * Every price card and service CTA links to /contact?service=<slug>, so
   * the form opens on the thing the visitor was just reading. An unknown
   * slug is ignored rather than added to the list: the select offers what
   * Drew actually sells, and a URL is not allowed to invent a service.
   * Without a script the select is still complete and the visitor picks —
   * the query string is a convenience, never the only way the field fills. */
  var sel = form.querySelector('#service');
  var want = '';
  try { want = (new URLSearchParams(location.search).get('service') || '').trim().toLowerCase(); }
  catch (e) {}
  if (want && sel) {
    var opts = Array.prototype.slice.call(sel.options);
    var hit = null;
    for (var i = 0; i < opts.length && !hit; i++) {
      if ((opts[i].getAttribute('data-slug') || '').toLowerCase() === want) hit = opts[i];
    }
    for (var j = 0; j < opts.length && !hit; j++) {
      if (opts[j].value.toLowerCase() === want) hit = opts[j];
    }
    if (hit) hit.selected = true;
  }

  /* ---- the inline answer ---------------------------------------------- */
  var status = form.querySelector('.form-status');
  function say(htmlText, bad) {
    if (!status) return;
    status.innerHTML = htmlText;
    status.className = 'form-status on' + (bad ? ' is-bad' : '');
  }

  function mailHref(subject, body) {
    return 'mailto:' + TO +
           '?subject=' + encodeURIComponent(subject) +
           '&body=' + encodeURIComponent(body);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();                    // the browser has already validated

    var d = {};
    var fd = new FormData(form);
    fd.forEach(function (v, k) { d[k] = typeof v === 'string' ? v : ''; });

    if (d._gotcha) return;                 // a robot filled the hidden field
    delete d._gotcha;

    var name = d.name || '';
    var subject = ('Quote request — ' + (d.service || 'Not sure') +
                   (name ? ' — ' + name : ''));
    var body = [
      'Name: ' + (d.name || '-'),
      'Email: ' + (d.email || '-'),
      'Phone: ' + (d.phone || '-'),
      'Business: ' + (d.business || '-'),
      'Service: ' + (d.service || '-'),
      'Budget: ' + (d.budget || '-'),
      '',
      d.message || ''
    ].join('\n');

    if (!TO && !ENDPOINT) {                // neither route: say so, lose nothing
      say('This form has nowhere to send to yet. Please try again shortly.', true);
      return;
    }

    if (ENDPOINT) {
      var payload = {};
      for (var k in d) if (Object.prototype.hasOwnProperty.call(d, k)) payload[k] = d[k];
      payload._subject = subject;
      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload)
      }).then(function (r) {
        if (r && r.ok) {
          say('Sent — Drew will reply within a business day.');
          form.reset();
        } else {
          failed(subject, body);
        }
      }).catch(function () { failed(subject, body); });
      return;
    }

    // No endpoint: the visitor's own mail app, with the brief already written.
    // location.assign rather than location.href = … so the one navigation this
    // file performs is a call that a test can watch.
    location.assign(mailHref(subject, body));
    say('Your mail app should open with the brief ready to send. If it did ' +
        'not, write to <a href="mailto:' + TO + '">' + TO + '</a>.');
  });

  function failed(subject, body) {
    say('That did not send. Write to <a href="' + mailHref(subject, body) + '">' +
        TO + '</a> and the brief goes with it.', true);
  }
})();
