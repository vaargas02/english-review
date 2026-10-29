// Extract the text of every presentation on academy.easypeasyfluent.com/resources.
// How to use: open the Resources page logged in, open DevTools > Console, paste this file, press Enter.
// It downloads easypeasy-materials.txt with the text of every PDF (one block per lesson).
// Hand that file to Claude to add the new lessons to fuente/.
(async () => {
  const opened = [];
  const realOpen = window.open;
  window.open = (u) => { opened.push(String(u)); return null; };
  const buttons = [...document.querySelectorAll('button')].filter(b => b.textContent.trim() === 'View');
  for (const b of buttons) { b.click(); await new Promise(r => setTimeout(r, 300)); }
  window.open = realOpen;
  const materials = opened.map(u => JSON.parse(decodeURIComponent(u.split('material=')[1])));
  const pdfjs = await import('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.mjs');
  pdfjs.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.mjs';
  let out = '';
  for (const m of materials) {
    const data = await (await fetch(m.resource)).arrayBuffer();
    const doc = await pdfjs.getDocument({ data }).promise;
    out += `\n\n######## ${m.name} [${m.material_type}] id=${m.id}\n`;
    for (let i = 1; i <= doc.numPages; i++) {
      const tc = await (await doc.getPage(i)).getTextContent();
      let s = '', y = null;
      for (const it of tc.items) { if (y !== null && Math.abs(it.transform[5] - y) > 2) s += '\n'; else if (s && !s.endsWith(' ')) s += ' '; s += it.str; y = it.transform[5]; }
      out += s.replace(/[ \t]+/g, ' ').trim() + '\n--\n';
    }
  }
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([out], { type: 'text/plain' }));
  a.download = 'easypeasy-materials.txt';
  a.click();
  console.log(`Extracted ${materials.length} presentations`);
})();
