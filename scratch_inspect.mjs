import { spawn } from 'node:child_process';
import { writeFile } from 'node:fs/promises';

const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const userDataDir = 'C:\\Users\\Shreyansh\\.gemini\\antigravity-ide\\brain\\e5d297f7-abf7-45f1-a396-8f98b764da01\\scratch\\edge-profile';

console.log('Starting Edge headless...');
const edge = spawn(edgePath, [
  '--headless=new',
  '--remote-debugging-port=9222',
  `--user-data-dir=${userDataDir}`,
  '--disable-gpu',
  '--no-first-run',
  '--no-default-browser-check',
  'http://localhost:5173'
], { stdio: 'ignore' });

// Wait for debugging port
let targets = null;
for (let i = 0; i < 20; i++) {
  await new Promise(r => setTimeout(r, 500));
  try {
    const res = await fetch('http://127.0.0.1:9222/json');
    targets = await res.json();
    if (targets && targets.length > 0) break;
  } catch (e) { }
}

if (!targets || targets.length === 0) {
  console.error('Could not connect to Edge debugger port');
  edge.kill();
  process.exit(1);
}

const pageTarget = targets.find(t => t.type === 'page') || targets[0];
console.log('Found page target:', pageTarget.url);

const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);

let id = 1;
const callbacks = new Map();

function send(method, params = {}) {
  const reqId = id++;
  return new Promise((resolve, reject) => {
    callbacks.set(reqId, { resolve, reject });
    ws.send(JSON.stringify({ id: reqId, method, params }));
  });
}

const consoleLogs = [];

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.id && callbacks.has(msg.id)) {
    callbacks.get(msg.id).resolve(msg.result);
    callbacks.delete(msg.id);
  } else if (msg.method === 'Runtime.consoleAPICalled') {
    consoleLogs.push({
      type: msg.params.type,
      args: msg.params.args.map(a => a.value ?? a.description)
    });
  } else if (msg.method === 'Log.entryAdded') {
    consoleLogs.push(msg.params.entry);
  }
};

await new Promise(resolve => ws.onopen = resolve);

await send('Runtime.enable');
await send('Log.enable');
await send('Page.enable');

// Wait 3 seconds for page and scripts to execute
console.log('Waiting 3 seconds for page execution...');
await new Promise(r => setTimeout(r, 3000));

// Get current URL
const evalUrl = await send('Runtime.evaluate', { expression: 'window.location.href' });
console.log('Current window.location.href:', evalUrl?.result?.value);

// Get page HTML or title
const evalTitle = await send('Runtime.evaluate', { expression: 'document.title' });
console.log('Document title:', evalTitle?.result?.value);

const evalBody = await send('Runtime.evaluate', {
  expression: `JSON.stringify({
    text: document.body.innerText,
    innerHTML: document.body.innerHTML,
    inputs: Array.from(document.querySelectorAll('input')).map(i => ({ type: i.type, name: i.name, placeholder: i.placeholder, id: i.id })),
    buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText)
  })`
});

const bodyInfo = JSON.parse(evalBody?.result?.value || '{}');
console.log('Body Text Snippet:', (bodyInfo.text || '').slice(0, 500));
console.log('Inputs found:', bodyInfo.inputs);
console.log('Buttons found:', bodyInfo.buttons);
console.log('Console logs captured:', JSON.stringify(consoleLogs, null, 2));

// Capture screenshot
const screenshot = await send('Page.captureScreenshot', { format: 'png' });
if (screenshot && screenshot.data) {
  const buf = Buffer.from(screenshot.data, 'base64');
  await writeFile('C:\\Users\\Shreyansh\\.gemini\antigravity-ide\\brain\\e5d297f7-abf7-45f1-a396-8f98b764da01\\scratch\\browser_view.png', buf);
  console.log('Screenshot saved to scratch/browser_view.png');
}

ws.close();
edge.kill();
