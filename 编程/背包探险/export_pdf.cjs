// Render the standalone lecture with a fresh browser context.
const {chromium}=require('/Users/lynnchua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path=require('node:path');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 await page.goto(require('node:url').pathToFileURL(path.join(__dirname,'背包探险指南.html')).href);
 const output=path.resolve(__dirname,'../../output/pdf/背包探险指南-从0到提高组.pdf');fs.mkdirSync(path.dirname(output),{recursive:true});
 await page.pdf({path:output,format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<div></div>',footerTemplate:'<div style="width:100%;margin:0 16mm;font-size:8px;color:#657468;display:flex;justify-content:space-between"><span>背包探险指南 · 从 0 到提高组</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',preferCSSPageSize:true});
 console.log(output);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
