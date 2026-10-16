const {chromium}=require('/Users/lynnchua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),out=path.resolve(__dirname,'../../tmp/autumn-handouts-qa');fs.mkdirSync(out,{recursive:true});
const specs=[['前缀和差分探险/前缀和与差分探险指南.html',12,2],['双指针探险/双指针探险指南.html',12,2],['栈与队列探险/栈与队列探险指南.html',13,1]];
(async()=>{
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const context=await browser.newContext({viewport:{width:1366,height:950},offline:true,acceptDownloads:true});
const page=await context.newPage(),errors=[],results=[];page.on('pageerror',e=>errors.push(e.message));
for(let g=0;g<specs.length;g++){
 const [file,count,labCount]=specs[g];await page.goto(pathToFileURL(path.join(root,file)).href);
 assert.equal(await page.locator('.lesson').count(),count);assert.equal(await page.locator('.lesson:visible').count(),0);assert.equal(await page.locator('[data-lab]').count(),labCount);
 assert.equal(await page.locator('.hint[open],.coach[open]').count(),0);
 await page.screenshot({path:path.join(out,`guide-${g}-home.png`)});
 await page.locator('.toc a[href="#lesson-1"]').click();await page.locator('#lesson-1').waitFor({state:'visible'});
 await page.locator('#note-1').fill('测试记录 <script>不执行</script>：变量角色还要解释。');await page.locator('#stage-1').selectOption('help');await page.reload();
 assert.equal(await page.locator('#note-1').inputValue(),'测试记录 <script>不执行</script>：变量角色还要解释。');assert.equal(await page.locator('#stage-1').inputValue(),'help');assert.match(await page.locator('#progress-label').textContent(),/0 \//);
 const dl=page.waitForEvent('download');await page.locator('#export').click();const download=await dl;const exportPath=path.join(out,`notes-${g}.json`);await download.saveAs(exportPath);const backup=JSON.parse(fs.readFileSync(exportPath,'utf8'));assert.match(backup.notes['1'],/变量角色/);
 backup.notes['1']='另一份草稿';backup.stages['1']='independent';fs.writeFileSync(path.join(out,'incoming.json'),JSON.stringify(backup));await page.locator('#import-file').setInputFiles(path.join(out,'incoming.json'));await page.waitForFunction(()=>document.querySelector('#save-status').textContent.includes('导入完成'));
 assert.match(await page.locator('#note-1').inputValue(),/另一份草稿/);assert.match(await page.locator('#note-1').inputValue(),/变量角色/);assert.equal(await page.locator('#stage-1').inputValue(),'help');
 backup.type='wrong-guide';fs.writeFileSync(path.join(out,'bad.json'),JSON.stringify(backup));await page.locator('#import-file').setInputFiles(path.join(out,'bad.json'));await page.waitForFunction(()=>document.querySelector('#save-status').textContent.includes('未导入'));assert.match(await page.locator('#note-1').inputValue(),/变量角色/);
 for(let i=1;i<=count;i++){
  await page.evaluate(i=>location.hash='lesson-'+i,i);await page.locator('#lesson-'+i).waitFor({state:'visible'});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'desktop overflow '+file+' '+i);
 }
 for(let k=0;k<labCount;k++){
  const lab=page.locator('[data-lab]').nth(k),id=await lab.evaluate(e=>e.closest('.lesson').id);await page.evaluate(id=>location.hash=id,id);await lab.waitFor({state:'visible'});
  const select=lab.locator('select'),choices=await select.locator('option').count();
  for(let c=0;c<choices;c++){await select.selectOption(String(c));let steps=0;while(!await lab.locator('.next').isDisabled()){await lab.locator('.next').click();steps++;assert(steps<100);}assert(steps>0);assert.equal(await page.locator('#stage-1').inputValue(),'help');await lab.locator('.reset').click();assert(await lab.locator('.prev').isDisabled());}
  await lab.locator('.next').click();await lab.locator('.next').click();await page.screenshot({path:path.join(out,`guide-${g}-lab-${k}.png`),fullPage:true});
 }
 await page.evaluate(()=>location.hash='lesson-1');await page.locator('#lesson-1').waitFor({state:'visible'});await page.locator('#lesson-1 .hint').first().locator('summary').click();assert.equal(await page.locator('#lesson-1 .hint[open]').count(),1);
 await page.locator('#all').click();assert.equal(await page.locator('.lesson:visible').count(),count);await page.locator('#all').click();assert.equal(await page.locator('.lesson:visible').count(),1);
 await page.setViewportSize({width:390,height:844});
 for(let i=1;i<=count;i++){await page.evaluate(i=>location.hash='lesson-'+i,i);await page.locator('#lesson-'+i).waitFor({state:'visible'});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'mobile overflow '+file+' '+i);await page.waitForFunction(i=>document.querySelector('#lesson-'+i).getBoundingClientRect().top>=document.querySelector('.toolbar').getBoundingClientRect().bottom-1,i,{timeout:3000});}
 await page.evaluate(()=>location.hash='lesson-1');await page.locator('#lesson-1').waitFor({state:'visible'});await page.screenshot({path:path.join(out,`guide-${g}-mobile.png`),fullPage:true});
 await page.locator('#menu').click();assert(await page.locator('body').evaluate(e=>e.classList.contains('nav-open')));await page.keyboard.press('Escape');assert(!await page.locator('body').evaluate(e=>e.classList.contains('nav-open')));
 await page.setViewportSize({width:1366,height:950});await page.evaluate(()=>window.dispatchEvent(new Event('beforeprint')));await page.emulateMedia({media:'print'});
 assert.equal(await page.locator('.lesson:visible').count(),count);assert.equal(await page.locator('.lab:visible').count(),0);assert.match(await page.locator('#lesson-1 .print-note').textContent(),/变量角色/);assert.equal(await page.locator('#lesson-1 .hint:visible').count(),1);
 await page.pdf({path:path.join(out,`guide-${g}-print.pdf`),printBackground:true,preferCSSPageSize:true});await page.emulateMedia({media:'screen'});
 // Fresh context used only by this QA; clear its sample notes before the next use.
 await page.evaluate(()=>localStorage.clear());results.push({file,stations:count,labs:labCount,result:'passed'});
}
await page.goto(pathToFileURL(path.join(root,'秋季学期讲义/秋季学期讲义总入口.html')).href);await page.screenshot({path:path.join(out,'index-desktop.png'),fullPage:true});await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:path.join(out,'index-mobile.png'),fullPage:true});
const noJs=await browser.newContext({javaScriptEnabled:false,offline:true});const np=await noJs.newPage();await np.goto(pathToFileURL(path.join(root,specs[0][0])).href);assert.equal(await np.locator('.lesson:visible').count(),12);await noJs.close();
assert.deepEqual(errors,[]);await browser.close();const report={date:'2026-10-16',guides:results,pageErrors:errors,index:'passed',offline:'passed',noJavaScript:'full text readable',notes:'persistence, export, safe merge, wrong-guide rejection passed',print:'all lessons, notes, expanded hints only',artifacts:out};fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exit(1);});
