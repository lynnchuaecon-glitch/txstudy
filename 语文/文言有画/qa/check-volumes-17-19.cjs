const {chromium}=require('/Users/lynnchua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {pathToFileURL}=require('url');
const root=path.resolve(__dirname,'..'),catalog=JSON.parse(fs.readFileSync(path.join(root,'catalog.json')));
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true,reducedMotion:"reduce"});
 const page=await context.newPage();const errors=[],network=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
 const overflow=async label=>{if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)){console.log(label,await page.evaluate(()=>[...document.querySelectorAll('body *')].map(e=>({tag:e.tagName,cls:e.className,w:e.getBoundingClientRect().width,r:e.getBoundingClientRect().right})).filter(x=>x.r>innerWidth+1)));await page.screenshot({path:path.join(__dirname,'overflow-debug.png'),fullPage:true});throw Error(label+' overflow');}};
 const go=async hash=>{await page.evaluate(h=>location.hash=h,hash);await page.waitForFunction(h=>location.hash==='#'+h,hash);await page.waitForTimeout(80)};
 const report={books:[],widths:[1440,390,320]};
 try{
  await page.goto(pathToFileURL(path.join(root,'打开书架.html')).href);await page.waitForSelector('.book-card');assert.equal(await page.locator('.book-card').count(),19);
  for(const b of catalog.slice(-3)){await page.locator('#search').fill(b.title);assert.equal(await page.locator('.book-card').count(),1);assert((await page.locator('.book-card h3').innerText()).includes(String(b.order)));}
  await page.locator('#reset').click();await page.screenshot({path:path.join(__dirname,'书架十九册.png'),fullPage:true});
  for(const b of catalog.slice(-3)){
   await page.goto(pathToFileURL(path.join(root,b.directory,b.file)).href);await page.waitForSelector('#scene-cards a');assert.equal(await page.locator('#scene-cards a').count(),b.sceneCount);
   await page.screenshot({path:path.join(__dirname,b.title+'封面.png'),fullPage:false});
   for(let i=1;i<=b.sceneCount;i++){
    await go('scene-'+i);await page.waitForFunction(i=>document.querySelector('#scene-kicker').textContent.includes('第 '+String(i).padStart(2,'0')+' 幕'),i);
    assert(await page.locator('#scene-image').evaluate(e=>e.complete&&e.naturalWidth>0));
    assert.equal(await page.locator('.reading-folds details[open]').count(),0);await overflow(b.title+i);
   }
   await go('scene-1');await page.locator('#scene-text .word').first().click();await page.waitForSelector('#word-dialog[open]');assert((await page.locator('#word-definition').innerText()).length>0);await page.locator('#word-dialog .dialog-close').click();
   await page.locator('.reading-folds summary').first().click();assert(await page.locator('#scene-translation').isVisible());await page.locator('#art-button').click();await page.waitForSelector('#art-dialog[open]');await page.locator('#art-dialog .dialog-close').click();
   await go('text');if(b.id==='tengwanggexu'){assert.equal(await page.locator('#fulltext-body .appendix-heading').innerText(),'附：《滕王阁诗》');assert.equal(await page.locator('#fulltext-body p').count(),8);}
   await go('words');await page.locator('#word-search').fill(b.id==='cuzhi'?'售':b.id==='tengwanggexu'?'襟':'乐其乐');assert(await page.locator('.word-entry').count()>0);await page.locator('#word-search').fill('');await page.locator('#word-scene').selectOption('0');assert(await page.locator('.word-entry').count()>0);
   await go('after');assert.equal(await page.locator('#my-line').inputValue(),'');await page.locator('#my-line').fill('QA隔离记录');await page.reload();await page.waitForSelector('#after:not([hidden])');assert.equal(await page.locator('#my-line').inputValue(),'QA隔离记录');const download=page.waitForEvent('download');await page.locator('#export-note').click();assert((await download).suggestedFilename().includes(b.title));
   for(const width of [390,320]){
    await page.setViewportSize({width,height:844});
    for(const view of ['cover',...Array.from({length:b.sceneCount},(_,i)=>'scene-'+(i+1)),'text','words','after','sources']){await go(view);await overflow(b.title+' '+view+' '+width);}
    await go('scene-'+(b.id==='cuzhi'?6:3));await page.screenshot({path:path.join(__dirname,b.title+'窄屏'+width+'.png'),fullPage:true});
   }
   await page.setViewportSize({width:1440,height:1000});report.books.push({title:b.title,scenes:b.sceneCount,interactions:'passed'});
  }
  // Shared reader change: every earlier book must still open its prose and scene.
  for(const b of catalog.slice(0,16)){await page.goto(pathToFileURL(path.join(root,b.directory,b.file)).href+'#text');await page.waitForSelector('#fulltext:not([hidden])');assert((await page.locator('#fulltext-body').innerText()).length>0);await go('scene-1');assert(await page.locator('#scene-image').evaluate(e=>e.complete&&e.naturalWidth>0));}
  for(const b of catalog){assert(fs.existsSync(path.join(root,b.directory,b.file)));}
  assert.deepEqual(errors,[]);assert.deepEqual(network,[]);report.errors=errors;report.externalRequests=network;report.previousBooksChecked=16;
  fs.writeFileSync(path.join(__dirname,'browser-report-volumes-17-19.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
