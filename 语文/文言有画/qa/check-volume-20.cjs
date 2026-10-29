const {chromium}=require('/Users/lynnchua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {pathToFileURL}=require('url');
const root=path.resolve(__dirname,'..'),catalog=JSON.parse(fs.readFileSync(path.join(root,'catalog.json'))),book=catalog.find(b=>b.order===20);
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true,reducedMotion:'reduce'});
 const page=await context.newPage(),errors=[],network=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
 const overflow=async label=>{assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),label+' horizontal overflow');};
 const go=async hash=>{await page.evaluate(h=>location.hash=h,hash);await page.waitForFunction(h=>location.hash==='#'+h,hash);await page.waitForTimeout(60)};
 const url=b=>pathToFileURL(path.join(root,b.directory,b.file)).href;
 const report={title:book.title,scenes:9,paragraphs:7,widths:[1440,390,320]};
 try{
  await page.goto(pathToFileURL(path.join(root,'打开书架.html')).href);await page.waitForSelector('.book-card');assert.equal(await page.locator('.book-card').count(),20);
  for(const q of ['木兰','佚名']){await page.locator('#search').fill(q);assert.equal(await page.locator('.book-card').count(),1);assert((await page.locator('.book-card h3').innerText()).includes('20'));}
  await page.locator('#reset').click();await page.locator('#dynasty').selectOption('北朝');assert.equal(await page.locator('.book-card').count(),1);assert(decodeURIComponent(await page.locator('.book-card').getAttribute('href')).includes(book.file));
  await page.locator('#reset').click();await page.screenshot({path:path.join(__dirname,'书架二十册.png'),fullPage:true});
  for(const width of [390,320]){await page.setViewportSize({width,height:844});await overflow('shelf '+width)}
  await page.setViewportSize({width:1440,height:1000});
  await page.goto(url(catalog.find(b=>b.order===19)));await page.waitForSelector('.collection-nav');assert.equal(await page.getByRole('link',{name:'下一篇 · 木兰诗 →'}).count(),1);
  await page.getByRole('link',{name:'下一篇 · 木兰诗 →'}).click();await page.waitForSelector('#scene-cards a');assert.equal(await page.locator('#scene-cards a').count(),9);assert.equal(await page.getByRole('link',{name:'上一篇 · 醉翁亭记'}).count(),1);
  await page.screenshot({path:path.join(__dirname,'木兰诗封面.png'),fullPage:false});
  for(let i=1;i<=9;i++){
   await go('scene-'+i);await page.waitForFunction(i=>document.querySelector('#scene-kicker').textContent.includes('第 '+String(i).padStart(2,'0')+' 幕'),i);
   assert(await page.locator('#scene-image').evaluate(e=>e.complete&&e.naturalWidth>0));assert.equal(await page.locator('.reading-folds details[open]').count(),0);await overflow('scene '+i);
   assert.equal(await page.locator('#scene-text').evaluate(e=>getComputedStyle(e).whiteSpace),'pre-line');
  }
  for(const item of [{scene:2,key:'军帖',pron:'tiě',meaning:'征兵'},{scene:2,key:'市_购买',pron:'shì',meaning:'购买'},{scene:3,key:'市_集市',pron:'shì',meaning:'集市'},{scene:8,key:'帖',pron:'tiē',meaning:'贴'}]){
   await go('scene-'+item.scene);await page.locator('#scene-text [data-word="'+item.key+'"]').first().click();await page.waitForSelector('#word-dialog[open]');assert((await page.locator('#word-pronunciation').innerText()).includes(item.pron));assert((await page.locator('#word-definition').innerText()).includes(item.meaning));await page.locator('#word-dialog .dialog-close').click();
  }
  await go('scene-1');await page.locator('#reader .pinyin-toggle').click();assert(await page.locator('body').evaluate(e=>e.classList.contains('no-pinyin')));await page.locator('#reader .pinyin-toggle').click();
  await page.locator('.reading-folds summary').first().click();assert(await page.locator('#scene-translation').isVisible());await page.locator('#art-button').click();await page.waitForSelector('#art-dialog[open]');await page.locator('#art-dialog .dialog-close').click();
  await go('text');assert.equal(await page.locator('#fulltext-body .original').count(),7);assert.equal(await page.locator('#fulltext-body .original').first().evaluate(e=>getComputedStyle(e).whiteSpace),'pre-line');
  const source=JSON.parse(fs.readFileSync(path.join(root,'木兰诗/source.json')));
  const plain=t=>t.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g,(_,key,label)=>label||source.words[key][2]||key);
  assert.deepEqual(await page.locator('#fulltext-body .original').evaluateAll(es=>es.map(e=>{const clone=e.cloneNode(true);clone.querySelectorAll('rt').forEach(r=>r.remove());return clone.textContent;})),source.textGroups.map(g=>g.map(i=>plain(source.scenes[i].text)).join('')));
  await go('words');await page.locator('#word-search').fill('市');assert.equal(await page.locator('.word-entry').count(),2);await page.locator('#word-search').fill('');await page.locator('#word-scene').selectOption('7');assert(await page.locator('.word-entry').count()>0);
  await go('after');assert.equal(await page.locator('#my-line').inputValue(),'');assert.equal(await page.locator('#my-thought').inputValue(),'');await page.locator('#my-line').fill('QA隔离记录');await page.reload();await page.waitForSelector('#after:not([hidden])');assert.equal(await page.locator('#my-line').inputValue(),'QA隔离记录');const download=page.waitForEvent('download');await page.locator('#export-note').click();assert((await download).suggestedFilename().includes('木兰诗'));
  for(const width of [390,320]){
   await page.setViewportSize({width,height:844});
   for(const view of ['cover',...Array.from({length:9},(_,i)=>'scene-'+(i+1)),'text','words','after','sources']){await go(view);await overflow(view+' '+width)}
   await go('scene-4');await page.screenshot({path:path.join(__dirname,'木兰诗窄屏'+width+'.png'),fullPage:true});
   await page.locator('#reader .size-toggle').click();await overflow('large scene 4 '+width);await go('scene-8');await overflow('large scene 8 '+width);await page.locator('#reader .size-toggle').click();
  }
  assert.deepEqual(errors,[]);assert.deepEqual(network,[]);Object.assign(report,{shelfBooks:20,adjacentLinks:'passed',interactionChecks:'passed',blankNotesAndIsolatedPersistence:'passed',verseLineBreaks:'passed',fulltextMatchesSource:true,errors,externalRequests:network});
  fs.writeFileSync(path.join(__dirname,'browser-report-volume-20.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
