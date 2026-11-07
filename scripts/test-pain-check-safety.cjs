const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
function fixture(lang) {
  const html = fs.readFileSync(path.join(root, `pain-check-${lang}.html`), 'utf8');
  const controller = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).find(s=>s.includes('let currentStep'));
  assert(controller, 'Quiz controller is present');
  for (const step of [0,1,2,3,4,5,6,7,8,9,10]) assert(html.includes(`data-step="${step}"`));
  assert(html.includes('<script src="pain-check-safety.js"></script>'));
  assert(html.includes('<noscript>'));
  const answers = {};
  function element() {
    const classes = new Set();
    return {style:{},textContent:'',children:[],classList:{add:x=>classes.add(x),remove:x=>classes.delete(x),contains:x=>classes.has(x)},setAttribute(){},append(x){this.children.push(x)},replaceChildren(){this.children=[]},scrollIntoView(){},focus(){}};
  }
  const ids = new Map();
  const steps = Array.from({length:11},()=>element());
  steps[0].classList.add('active');
  const errors = steps.map(()=>element());
  steps.forEach((s,i)=>s.querySelector=()=>errors[i]);
  const doc = {
    getElementById(id){if(!ids.has(id))ids.set(id,element());return ids.get(id)},
    createElement:element,
    querySelector(selector){
      if(selector.startsWith('input')){const name=selector.match(/name="([^"]+)"/)[1];return answers[name]?{value:answers[name]}:null}
      const match=selector.match(/data-step="(\d+)"/);if(match)return steps[Number(match[1])];
      throw Error('Unexpected selector '+selector);
    },
    querySelectorAll(selector){
      if(selector==='.quiz-step')return steps;
      if(selector==='.quiz-error')return errors;
      if(selector==='input[type="radio"]')return Object.keys(answers).map(q=>({set checked(v){if(!v)delete answers[q]}}));
      throw Error('Unexpected selector '+selector);
    }
  };
  const context = vm.createContext({document:doc});
  vm.runInContext(fs.readFileSync(path.join(root,'pain-check-safety.js'),'utf8'),context);
  vm.runInContext(controller,context);
  return {answers,steps,errors,ids,run:code=>vm.runInContext(code,context),doc};
}
function noBooking(f) {
  assert(!f.doc.getElementById('resultActions').children.some(x=>(x.href||'').includes('booking')));
  assert(f.doc.getElementById('resultActions').children.some(x=>x.href==='tel:103'));
}
let checks=0;
for(const lang of ['hy','en','ru']) {
  let f=fixture(lang);
  f.run('nextStep()'); assert(f.steps[0].classList.contains('active')); assert.equal(f.errors[0].style.display,'block');checks++;
  for(const response of ['red','unsure']) {
    f=fixture(lang);f.answers.q0=response;f.run('nextStep()');
    assert.equal(f.doc.getElementById('resultScreen').style.display,'block');
    assert(!f.steps.some(s=>s.classList.contains('active')));noBooking(f);
    f.run('restartQuiz()');assert(f.steps[0].classList.contains('active'));assert.deepEqual(f.answers,{});assert.equal(f.doc.getElementById('resultActions').children.length,0);checks++;
  }
  f=fixture(lang);f.answers.q0='clear';f.run('nextStep()');assert(f.steps[1].classList.contains('active'));
  f.run('prevStep()');assert(f.steps[0].classList.contains('active'));checks++;
  f=fixture(lang);f.answers.q0='clear';f.run('nextStep()');f.answers.q1='chest';f.run('nextStep()');noBooking(f);assert.equal(f.doc.getElementById('resultTitle').textContent,f.run('safetyCopy.chestTitle'));checks++;
  for(const q of ['q8','q9','q10']){
    f=fixture(lang);Object.assign(f.answers,{q0:'clear',q1:'back',[q]:'red'});
    assert.equal(f.run('stopForSafety()'),true);noBooking(f);checks++;
  }
  // A normal, fully answered path still produces the existing non-diagnostic orientation.
  f=fixture(lang);Object.assign(f.answers,{q0:'clear',q1:'back',q2:'mechanical',q3:'no',q4:'no',q5:'yes',q6:'no',q7:'short',q8:'no',q9:'no',q10:'no'});
  for(let i=0;i<10;i++)f.run('nextStep()');f.run('showResult()');
  assert.equal(f.doc.getElementById('resultScreen').style.display,'block');
  assert(f.doc.getElementById('resultActions').innerHTML.includes(`booking-${lang}.html`));checks++;
  // A missing safety answer cannot be bypassed by calling the result handler.
  delete f.answers.q0;f.run('showResult()');noBooking(f);checks++;
}
console.log(`Passed ${checks} safety-gate and normal-path regression scenarios across HY/EN/RU.`);
