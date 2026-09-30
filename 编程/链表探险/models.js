'use strict';
// Small teaching models, shared by the browser experiments and local verification.
function walkIds(head,next,end=0){
 const ids=[],seen=new Set();let cur=head;
 while(cur!==end){
  if(seen.has(cur))return {ids,cycle:cur};
  if(!Object.prototype.hasOwnProperty.call(next,cur))return {ids,missing:cur};
  seen.add(cur);ids.push(cur);cur=next[cur];
 }
 return {ids,cycle:null};
}
function insertionState(mode,step){
 const next={1:2,2:0,3:0},log=[];const q=next[1];
 if(step>=1){if(mode==='safe'){next[3]=next[1];log.push('nxt[u] ← nxt[p]：u 先接住旧后继 q。');}
 else {next[1]=3;log.push(mode==='saved'?'已保存 q=2；nxt[p] ← u。':'nxt[p] ← u：p 的后继已变成 u，尚未保存旧 q。');}}
 if(step>=2){if(mode==='safe'){next[1]=3;log.push('nxt[p] ← u：入口路径现在经过新结点。');}
 else if(mode==='saved'){next[3]=q;log.push('nxt[u] ← 保存的 q：虽然先改 p，旧去向仍保留。');}
 else {next[3]=next[1];log.push('nxt[u] ← nxt[p]：读到新值 u，于是 u 指向自己。');}}
 return {next,log,...walkIds(1,next)};
}
class DoubleModel{
 constructor(ids=[2,3,4]){this.next={0:1};this.prev={1:0};this.alive=new Set();for(const id of ids)this.insert(this.prev[1],id);}
 insert(p,u){
  if(p!==0&&!this.alive.has(p))throw Error('前驱必须是 H 或活跃真实结点。');
  if(!Number.isInteger(u)||u<2||this.alive.has(u))throw Error('新编号必须是未在链上的真实结点。');
  const q=this.next[p];this.prev[u]=p;this.next[u]=q;this.next[p]=u;this.prev[q]=u;this.alive.add(u);
  return {u,p,q};
 }
 remove(u){if(!this.alive.has(u))throw Error('该结点不活跃，不能删除哨兵或重复删除。');const p=this.prev[u],q=this.next[u];this.next[p]=q;this.prev[q]=p;this.alive.delete(u);return {u,p,q};}
 restore({u,p,q}){
  if(this.alive.has(u)||this.next[p]!==q||this.prev[q]!==p||(p!==0&&!this.alive.has(p))||(q!==1&&!this.alive.has(q)))throw Error('旧邻居状态不匹配，不能按这条记录恢复。');
  this.prev[u]=p;this.next[u]=q;this.next[p]=u;this.prev[q]=u;this.alive.add(u);
 }
 forward(){return walkIds(this.next[0],this.next,1).ids;}
 backward(){return walkIds(this.prev[1],this.prev,0).ids;}
 check(){const f=walkIds(this.next[0],this.next,1),b=walkIds(this.prev[1],this.prev,0);if(f.cycle!==null||b.cycle!==null||f.ids.length!==this.alive.size||JSON.stringify(f.ids)!==JSON.stringify([...b.ids].reverse()))return false;
  for(const u of f.ids)if(!this.alive.has(u)||this.prev[this.next[u]]!==u||this.next[this.prev[u]]!==u)return false;
  return this.prev[this.next[0]]===0&&this.next[this.prev[1]]===1;
 }
}
function circleEvents(n,k){
 if(!Number.isInteger(n)||n<1||!Number.isInteger(k)||k<1)throw Error('n、k 必须是正整数');
 const next={},prev={};for(let i=1;i<=n;i++){next[i]=i===n?1:i+1;prev[i]=i===1?n:i-1;}
 let count=n,cur=1;const removed=[],events=[];
 const order=()=>{const out=[];let p=cur;for(let i=0;i<count;i++){out.push(p);p=next[p];}return out;};
 events.push({alive:order(),removed:[],cur,text:'第一轮从 1 报 1。先预测第一个出列的人。'});
 while(count>1){const start=cur,steps=(k-1)%count;for(let j=0;j<steps;j++)cur=next[cur];const victim=cur,p=prev[cur],q=next[cur];next[p]=q;prev[q]=p;cur=q;count--;removed.push(victim);
  events.push({alive:order(),removed:[...removed],cur,text:`从 ${start} 报 1；先走 ${k-1} 步（去掉整圈后 ${steps} 步），${victim} 出列。下一位 ${cur} 重新报 1。`});}
 return events;
}
if(typeof module!=='undefined'&&module.exports)module.exports={walkIds,insertionState,DoubleModel,circleEvents};
