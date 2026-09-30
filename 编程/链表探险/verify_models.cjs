const assert=require('node:assert/strict');
const {walkIds,insertionState,DoubleModel,circleEvents}=require('./models.js');
let seed=20260924;const rand=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n;};
assert.deepEqual(walkIds(2,{1:0,2:3,3:1}).ids,[2,3,1]);
assert.deepEqual(insertionState('safe',2).ids,[1,3,2]);
assert.deepEqual(insertionState('saved',2).ids,[1,3,2]);
assert.equal(insertionState('unsafe',2).cycle,3);
let mutations=0;
for(let trial=0;trial<100;trial++){
 const m=new DoubleModel([]),slow=[];let serial=2;
 for(let op=0;op<200;op++){
  if(!slow.length||rand(2)===0){const pos=rand(slow.length+1),id=serial++;m.insert(pos===0?0:slow[pos-1],id);slow.splice(pos,0,id);}
  else {const pos=rand(slow.length),id=slow[pos];m.remove(id);slow.splice(pos,1);assert.throws(()=>m.remove(id));}
  assert.equal(m.check(),true);assert.deepEqual(m.forward(),slow);assert.deepEqual(m.backward(),[...slow].reverse());mutations++;
 }
}
for(let n=0;n<=20;n++){
 const m=new DoubleModel(Array.from({length:n},(_,i)=>i+2)),slow=m.forward(),stack=[];
 for(let op=0;op<200;op++){
  if(slow.length&&(!stack.length||rand(2)===0)){const pos=rand(slow.length),old=[...slow],r=m.remove(slow[pos]);slow.splice(pos,1);stack.push({r,old});}
  else if(stack.length){const {r,old}=stack.pop();m.restore(r);slow.splice(0,slow.length,...old);}
  assert.equal(m.check(),true);assert.deepEqual(m.forward(),slow);
 }
}
for(let n=1;n<=30;n++)for(let k=1;k<=100;k++){
 const a=Array.from({length:n},(_,i)=>i+1),out=[];let at=0;
 while(a.length>1){at=(at+k-1)%a.length;out.push(a.splice(at,1)[0]);}
 const e=circleEvents(n,k).at(-1);assert.deepEqual(e.removed,out);assert.deepEqual(e.alive,a);
}
// Verify lesson 26's duplicate tie convention using independent interval enumeration.
function contribution(a){const n=a.length,ids=Array.from({length:n},(_,i)=>i),live=[...ids];let sum=0;
 ids.sort((i,j)=>a[j]-a[i]||j-i);
 for(const i of ids){const p=live.indexOf(i),L=p?live[p-1]:-1,R=p+1<live.length?live[p+1]:n;sum+=a[i]*(i-L)*(R-i);live.splice(p,1);}return sum;}
function brute(a){let s=0;for(let l=0;l<a.length;l++){let min=Infinity;for(let r=l;r<a.length;r++){min=Math.min(min,a[r]);s+=min;}}return s;}
for(let n=1;n<=7;n++)for(let mask=0;mask<3**n;mask++){let x=mask;const a=[];for(let j=0;j<n;j++){a.push(x%3-1);x=Math.floor(x/3);}assert.equal(contribution(a),brute(a));}
assert.equal(contribution([3,1,2]),9);
console.log(`Passed: ${mutations} double-list mutations, undo histories, 3000 circular cases, exhaustive contribution checks (duplicates and negatives).`);
