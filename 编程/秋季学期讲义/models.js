// Small, deterministic models shared by the learning labs and independent checks.
(function(root){
function prefix(a,l,r){
 const s=Array(a.length+1).fill(null);s[0]=0;
 const out=[{s:[...s],at:0,text:'S[0]=0：前零项的总和为零。先预测下一格。'}];
 for(let i=1;i<=a.length;i++){s[i]=s[i-1]+a[i-1];out.push({s:[...s],at:i,text:`登记 S[${i}]：前 ${i-1} 项共 ${s[i-1]}，加第 ${i} 项 ${a[i-1]}，得到 ${s[i]}。`});}
 out.push({s:[...s],at:-1,result:s[r]-s[l-1],text:`查询第 ${l}～${r} 项：S[${r}] − S[${l-1}] = ${s[r]} − ${s[l-1]} = ${s[r]-s[l-1]}。扣掉的是区间开始前的部分。`});return out;
}
function difference(n,ops){
 const d=Array(n+2).fill(0),a=Array(n).fill(null);let running=0;
 const out=[{d:[...d],a:[...a],at:-1,text:'增量差分从全零开始；原数组也设为全零。'}];
 for(const [l,r,v] of ops){d[l]+=v;out.push({d:[...d],a:[...a],at:l,text:`第 ${l}～${r} 项加 ${v}：先在 d[${l}] 登记 ${v}，从这里开始生效。`});d[r+1]-=v;out.push({d:[...d],a:[...a],at:r+1,text:`在 d[${r+1}] 登记 ${-v}：从区间后一格停止本次影响。`});}
 for(let i=1;i<=n;i++){running+=d[i];a[i-1]=running;out.push({d:[...d],a:[...a],at:i,text:`恢复第 ${i} 格：累计增量为 ${running}。d[${i}]=${d[i]} 是变化，不是这一格的最终值。`});}return out;
}
function pair(a,target){
 let l=0,r=a.length-1;const out=[{l,r,text:`从两端开始，目标和 ${target}。先预测和，再决定谁能被安全排除。`}];
 while(l<r){const sum=a[l]+a[r];if(sum===target){out.push({l,r,found:[l,r],text:`${a[l]} + ${a[r]} = ${target}，找到两个不同位置 ${l} 与 ${r}。`});return out;}
 if(sum<target){const old=l;l++;out.push({l,r,text:`刚才下标 ${old} 与 ${r} 的和为 ${sum}，太小；固定 ${old} 配最大的候选也不够，所以排除左端 ${old}。`});}
 else{const old=r;r--;out.push({l,r,text:`刚才下标 ${l} 与 ${old} 的和为 ${sum}，太大；固定 ${old} 配最小的候选也超出，所以排除右端 ${old}。`});}}
 out.push({l,r,found:null,text:'剩余不足两个不同位置，所有可排除的配对已有依据：没有找到。'});return out;
}
function windowSteps(a,k){
 let l=0,sum=0,best=0;const out=[{l,r:-1,sum,best,text:'窗口为空。每次先加入右端，必要时收缩左端，再记录合法长度。'}];
 for(let r=0;r<a.length;r++){
  sum+=a[r];out.push({l,r,sum,best,text:`右端加入 a[${r}]=${a[r]}，当前和 ${sum}；先检查是否合法。`});
  while(l<=r&&sum>k){const old=l;sum-=a[l++];out.push({l,r,sum,best,text:`和超过 ${k}，移出 a[${old}]=${a[old]}；新左端 ${l}，当前和 ${sum}。`});}
  best=Math.max(best,r-l+1);out.push({l,r,sum,best,text:`当前合法长度 ${r-l+1}，已见最大长度 ${best}。${a.some(x=>x<0)?'注意：含负数时“旧起点永远无用”的依据失效；本实验故意展示错误规则。':''}`});
 }return out;
}
function containers(mode){
 const ops=[['push','A'],['push','B'],['peek'],['pop'],['push','C'],['pop'],['pop'],['pop']],q=[],out=[{q:[],text:'容器为空。先预测每一步会查看或取出谁。'}];
 for(const [op,x] of ops){let message='';if(op==='push'){q.push(x);message=`加入 ${x}。`;}else if(!q.length){message='容器为空：本次请求停止，不读取或移除不存在的元素。';}else{const at=mode==='stack'?q.length-1:0;const value=q[at];message=op==='peek'?`查看 ${value}，内容没有改变。`:`取出 ${value}，它不再等待。`;if(op==='pop')q.splice(at,1);}out.push({q:[...q],text:message});}return out;
}
const api={prefix,difference,pair,windowSteps,containers};root.HandoutModels=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
