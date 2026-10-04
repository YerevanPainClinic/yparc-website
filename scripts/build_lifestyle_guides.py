#!/usr/bin/env python3
"""Build the patient lifestyle guides and their library listing."""
from pathlib import Path
import json,re,html
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'content/lifestyle-guides.json').read_text())
LABELS={
'hy':{'book':'Ամրագրել խորհրդատվություն','sources':'Բժշկական աղբյուրներ','library':'Օգտակար նյութեր պացիենտների համար','lead':'Հասկանալի հոդվածներ ցավի, շարժման, բուժման և առօրյա սովորությունների մասին։ Ընտրեք ձեզ հետաքրքրող թեման։','read':'Կարդալ հոդվածը','caption':'Թեմատիկ պատկեր։','generated':'Թեմատիկ գեներացված պատկեր։','note':'Նյութը կրթական է և չի փոխարինում անհատական բժշկական գնահատմանը։'},
'en':{'book':'Book a consultation','sources':'Medical sources','library':'Useful Materials for Patients','lead':'Clear articles about pain, movement, treatment and everyday habits. Choose a topic that interests you.','read':'Read article','caption':'Thematic image.','generated':'Thematic generated image.','note':'This educational material does not replace an individual clinical assessment.'},
'ru':{'book':'Записаться на консультацию','sources':'Медицинские источники','library':'Полезные материалы для пациентов','lead':'Понятные статьи о боли, движении, лечении и повседневных привычках. Выберите интересующую тему.','read':'Читать статью','caption':'Тематическое изображение.','generated':'Тематическое сгенерированное изображение.','note':'Материал образовательный и не заменяет индивидуальную медицинскую оценку.'}}
EXTRA_CARDS={
'hy':[['back-pain','Հասկանալ մեջքի ցավը','Պատճառներ, գնահատում և բուժման մոտեցումներ։','images/neck-pain-editorial.webp'],['movement-for-a-stronger-back','Շարժում՝ ավելի ամուր մեջքի համար','Հեշտ վարժություններ և կարճ տեսանյութեր՝ քայլերի բացատրությամբ։','images/rehabilitation-1.jpg'],['healthy-lifestyle-and-pain','Առողջ ապրելակերպը և քրոնիկ ցավը','Քուն, սթրես, սնունդ և փոքր կայուն սովորություններ։','images/healthy-lifestyle-editorial.webp'],['nerve-block','Ի՞նչ է նյարդային բլոկադան','Թիրախային միջամտության նպատակը, ընթացքը և անվտանգության քայլերը։','images/pain-intervention-1.jpg']],
'en':[['back-pain','Understanding Back Pain','Causes, assessment and treatment approaches.','images/neck-pain-editorial.webp'],['movement-for-a-stronger-back','Movement for a Stronger Back','Easy exercises and short demonstrations with written steps.','images/rehabilitation-1.jpg'],['healthy-lifestyle-and-pain','Healthy Lifestyle and Chronic Pain','Sleep, stress, food and small sustainable habits.','images/healthy-lifestyle-editorial.webp'],['nerve-block','What Is a Nerve Block?','The purpose, process and safety measures of a targeted procedure.','images/pain-intervention-1.jpg']],
'ru':[['back-pain','Понимание боли в спине','Причины, оценка и подходы к лечению.','images/neck-pain-editorial.webp'],['movement-for-a-stronger-back','Движение для более крепкой спины','Простые упражнения и короткие видео с пояснениями.','images/rehabilitation-1.jpg'],['healthy-lifestyle-and-pain','Здоровый образ жизни и хроническая боль','Сон, стресс, питание и небольшие устойчивые привычки.','images/healthy-lifestyle-editorial.webp'],['nerve-block','Что такое блокада нерва?','Цель, ход и меры безопасности прицельной процедуры.','images/pain-intervention-1.jpg']]}
CSS='''.article-related{display:grid;gap:12px;padding:22px;background:#f4f8f5;border-radius:14px}.article-related a{text-decoration:underline;font-weight:700}.library-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;padding:40px 0 64px}.library-card{border:1px solid #dce5e0;border-radius:18px;overflow:hidden;background:#fff;display:flex;flex-direction:column}.library-card img{display:block;width:100%;height:210px;object-fit:cover}.library-body{padding:24px;display:flex;flex-direction:column;flex:1}.library-body h2{font-size:27px;line-height:1.25;margin:0 0 12px}.library-body p{color:#52635d;margin:0 0 20px}.library-body a{margin-top:auto;color:#0b4f3c;font-weight:800;text-decoration:underline}.library-card:focus-within{outline:3px solid #b48b35;outline-offset:3px}@media(max-width:1000px){.library-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:600px){.library-grid{grid-template-columns:1fr}}'''
def paragraph(t):
 return '<p>'+re.sub(r'\[(\d(?:,\d)*)\]',lambda m:' '.join(f'<a class="ref" href="#source-{n}">[{n}]</a>' for n in m[1].split(',')),html.escape(t))+'</p>'
def template(lang,slug,title,lead):
 s=(ROOT/f'nerve-block-{lang}.html').read_text().replace('nerve-block-',slug+'-')
 s=re.sub(r'<title>.*?</title>',f'<title>{html.escape(title)} | YPARC</title>',s)
 s=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{html.escape(lead,quote=True)}">',s)
 return s.replace('</style>',CSS+'</style>')
files=[]
for slug,guide in DATA['guides'].items():
 for lang,d in guide['languages'].items():
  lab=LABELS[lang];s=template(lang,slug,d['title'],d['lead'])
  s=re.sub(r'<h1>.*?</h1>',f'<h1>{d["title"]}</h1>',s,count=1)
  s=re.sub(r'<p class="lead">.*?</p>',f'<p class="lead">{d["lead"]}</p>',s,count=1)
  width,height=(1536,1024) if slug=='weight-and-pain' else (760,1021)
  caption=lab['generated'] if slug=='weight-and-pain' else lab['caption']
  photo=f'<figure class="block-photo"><img src="{guide["image"]}" width="{width}" height="{height}" fetchpriority="high" alt="{d["alt"]}"><figcaption>{caption}</figcaption></figure>'
  s=re.sub(r'<figure class="block-photo">.*?</figure>',photo,s,count=1)
  parts=['<div class="key-message">'+d['quote']+'</div>'];toc=[]
  for sid,title,*paras in d['sections']:
   parts.append(f'<section id="{sid}"><h2>{title}</h2>'+''.join(paragraph(p) for p in paras)+'</section>');toc.append((sid,title))
  related=['physical-activity-and-pain','healthy-lifestyle-and-pain'] if slug=='weight-and-pain' else ['movement-for-a-stronger-back','weight-and-pain']
  titlemap={k:g['languages'][lang]['title'] for k,g in DATA['guides'].items()};titlemap.update({c[0]:c[1] for c in EXTRA_CARDS[lang]})
  parts.append(f'<section id="related"><h2>{d["related"]}</h2><div class="article-related">'+''.join(f'<a href="{k}-{lang}.html">{titlemap[k]} →</a>' for k in related)+f'<a href="pain-library-{lang}.html">{lab["library"]} →</a></div></section>');toc.append(('related',d['related']))
  parts.append(f'<section id="sources"><h2>{lab["sources"]}</h2><ol class="source-list">'+''.join(f'<li id="source-{i}"><a href="{u}" target="_blank" rel="noopener noreferrer">{t}</a></li>' for i,(t,u) in enumerate(guide['sources'],1))+'</ol>'+paragraph(lab['note'])+'</section>');toc.append(('sources',lab['sources']))
  s=re.sub(r'<article>.*?</article>','<article>'+''.join(parts)+'</article>',s,flags=re.S)
  s=re.sub(r'<aside>.*?</aside>','<aside>'+''.join(f'<a href="#{sid}">{t}</a>' for sid,t in toc)+'</aside>',s)
  s=re.sub(r'<section class="cta">.*?</section>',f'<section class="cta"><div class="container"><div><h2>{lab["book"]}</h2><p>{d["cta"]}</p></div><a class="btn" href="booking-{lang}.html">{lab["book"]} →</a></div></section>',s)
  path=f'{slug}-{lang}.html';(ROOT/path).write_text(s);files.append(path)
for lang,lab in LABELS.items():
 s=template(lang,'pain-library',lab['library'],lab['lead'])
 eyebrow=re.search(r'<div class="eyebrow">(.*?)</div>',s)[1]
 hero=f'<section class="hero"><div class="container"><div class="eyebrow">{eyebrow}</div><h1>{lab["library"]}</h1><p class="lead">{lab["lead"]}</p></div></section>'
 s=re.sub(r'<section class="hero">.*?</section>',hero,s,count=1)
 cards=[[slug,g['languages'][lang]['title'],g['languages'][lang]['lead'],g['image']] for slug,g in DATA['guides'].items()]+EXTRA_CARDS[lang]
 # Back pain gets a text-only card, avoiding an unrelated anatomical image.
 markup=''
 for slug,title,desc,img in cards:
  pic='' if slug=='back-pain' else f'<img src="{img}" alt="" loading="lazy">'
  markup+=f'<article class="library-card">{pic}<div class="library-body"><h2>{title}</h2><p>{desc}</p><a href="{slug}-{lang}.html">{lab["read"]} →</a></div></article>'
 s=re.sub(r'<div class="container content">.*?</aside></div>',f'<section class="container library-grid" aria-label="{lab["library"]}">{markup}</section>',s,flags=re.S)
 s=re.sub(r'<section class="cta">.*?</section>','',s)
 path=f'pain-library-{lang}.html';(ROOT/path).write_text(s);files.append(path)
print(json.dumps(files))
