const assert=require('node:assert/strict');
const M=require('./models.js');
let seed=20261016;const random=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n;};
const last=a=>a[a.length-1];let checks=0;
for(let t=0;t<700;t++){
 const n=1+random(12),a=Array.from({length:n},()=>random(31)-15);
 const l=1+random(n),r=l+random(n-l+1),s=M.prefix(a,l,r);
 assert.equal(last(s).result,a.slice(l-1,r).reduce((x,y)=>x+y,0));checks++;
 const ops=Array.from({length:random(12)},()=>{const x=1+random(n);return [x,x+random(n-x+1),random(15)-7];});
 const slow=Array(n).fill(0);for(const [x,y,v] of ops)for(let i=x-1;i<y;i++)slow[i]+=v;
 assert.deepEqual(last(M.difference(n,ops)).a,slow);checks++;
 const sorted=[...a].sort((x,y)=>x-y),target=random(51)-25;let exists=false;
 for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)if(sorted[i]+sorted[j]===target)exists=true;
 const result=last(M.pair(sorted,target));assert.equal(!!result.found,exists);if(result.found){const [x,y]=result.found;assert(x<y);assert.equal(sorted[x]+sorted[y],target);}checks++;
 const nonnegative=a.map(Math.abs),k=random(40);let best=0;
 for(let x=0;x<n;x++){let sum=0;for(let y=x;y<n;y++){sum+=nonnegative[y];if(sum<=k)best=Math.max(best,y-x+1);}}
 assert.equal(last(M.windowSteps(nonnegative,k)).best,best);checks++;
}
assert.equal(last(M.windowSteps([5,-4],1)).best,1); // Deliberately invalid use, brute force is 2.
for(const mode of ['stack','queue']){
 const trace=M.containers(mode);assert.deepEqual(trace[2].q,['A','B']);assert.deepEqual(trace[3].q,['A','B']);
 assert.deepEqual(trace[4].q,mode==='stack'?['A']:['B']);assert.deepEqual(last(trace).q,[]);assert.match(last(trace).text,/为空/);checks+=4;
}
const report={seed:20261016,randomCases:700,comparisons:checks,intentionalNegativeWindowCounterexample:{algorithm:1,correct:2},result:'passed'};
console.log(JSON.stringify(report,null,2));
