/* Safety gate shared by HY/EN/RU. Answers stay in the page; no data is sent. */
function stopForSafety() {
  if (getAnswer('q0') !== 'clear' || ['q8', 'q9', 'q10'].some(q => getAnswer(q) === 'red')) {
    showSafetyResult('urgent');
    return true;
  }
  if (getAnswer('q1') === 'chest') {
    showSafetyResult('chest');
    return true;
  }
  return false;
}

function showSafetyResult(kind) {
  const copy = safetyCopy;
  document.querySelectorAll('.quiz-step').forEach(step => step.classList.remove('active'));
  const result = document.getElementById('resultScreen');
  result.style.display = 'block';
  result.setAttribute('tabindex', '-1');
  document.getElementById('progressText').textContent = copy.stopped;
  document.getElementById('progressBar').style.width = '0%';
  document.getElementById('resultIcon').textContent = '!';
  document.getElementById('resultTitle').textContent = copy[kind + 'Title'];
  document.getElementById('resultLead').textContent = copy[kind + 'Lead'];
  document.getElementById('resultBox').classList.add('result-warning');
  document.getElementById('resultBoxTitle').textContent = copy[kind + 'Box'];
  document.getElementById('resultBoxText').textContent = copy[kind + 'Text'];
  const actions = document.getElementById('resultActions');
  actions.replaceChildren();
  function addLink(href, text, style) {
    const link = document.createElement('a');
    link.href = href;
    link.className = 'result-link ' + style;
    link.textContent = text;
    actions.append(link);
  }
  addLink('tel:103', copy.call, 'result-primary');
  if (kind === 'chest') addLink('tel:+37491092123', copy.clinic, 'result-secondary');
  const outside = document.createElement('p');
  outside.textContent = copy.outside;
  actions.append(outside);
  result.focus({preventScroll: true});
  result.scrollIntoView({behavior: 'smooth', block: 'start'});
}
