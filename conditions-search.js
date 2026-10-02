(() => {
  const input = document.getElementById('topic-search');
  const cards = Array.from(document.querySelectorAll('.topic'));
  const groups = Array.from(document.querySelectorAll('.topic-group'));
  const status = document.getElementById('search-status');
  const language = document.documentElement.lang;
  const normalise = text => text.normalize('NFKC').toLocaleLowerCase(language).trim();
  input.addEventListener('input', () => {
    const query = normalise(input.value);
    let visible = 0;
    cards.forEach(card => {
      card.hidden = !normalise(card.textContent).includes(query);
      if (!card.hidden) visible++;
    });
    groups.forEach(group => { group.hidden = !group.querySelector('.topic:not([hidden])'); });
    document.getElementById('no-results').hidden = visible !== 0;
    status.textContent = query ? `${visible} / ${cards.length}` : '';
  });
})();
