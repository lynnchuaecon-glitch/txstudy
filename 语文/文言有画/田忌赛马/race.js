(() => {
  'use strict';
  const condition = document.getElementById('race-condition');
  if (!condition) return;
  const choices = [1,2,3].map(n => document.getElementById('race-pair'+n));
  const result = document.getElementById('race-result');
  const own = {high:6,middle:4,low:2};
  const names = {high:'上等',middle:'中等',low:'下等'};
  const rankNames = ['上等','中等','下等'];
  const opponents = () => condition.value === 'wide' ? [9,8,7] : [7,5,3];
  const clearResult = () => { result.textContent='安排改变了。先预测，再看看这一排。'; };
  condition.addEventListener('change', () => {
    const values = opponents();
    values.forEach((v,i) => { document.getElementById('opponent-'+(i+1)).textContent=rankNames[i]+' · '+v; });
    document.getElementById('race-strengths').textContent=`田忌：上 6、中 4、下 2。对方：上 ${values[0]}、中 ${values[1]}、下 ${values[2]}。`;
    clearResult();
  });
  choices.forEach(select=>select.addEventListener('change',clearResult));
  document.getElementById('race-run').addEventListener('click', () => {
    const arrangement=choices.map(select=>select.value);
    if(arrangement.some(v=>!Object.hasOwn(own,v))){result.textContent='还有场次没安排。请先为三场各选一匹马。';return;}
    if(new Set(arrangement).size!==3){result.textContent='同一匹马不能出场两次。请让上、中、下三匹各出现一次。';return;}
    let wins=0;const values=opponents();
    const rounds=arrangement.map((key,i)=>{
      const won=own[key]>values[i];if(won)wins++;
      return `第${i+1}场：田忌${names[key]} ${own[key]} ${won?'＞':'＜'} 对方${rankNames[i]} ${values[i]}，田忌${won?'胜':'负'}。`;
    });
    const p=document.createElement('p');p.textContent=`三场合计：田忌 ${wins} 胜、${3-wins} 负。`;
    const list=document.createElement('ol');rounds.forEach(text=>{const li=document.createElement('li');li.textContent=text;list.appendChild(li);});
    const prompt=document.createElement('p');prompt.textContent=condition.value==='wide'?'这组条件下，对方最慢的马也比田忌最快的马快。只改变配对，能改变这个关系吗？':'结果和预测一样吗？请指着具体的两匹马，解释哪一场关系改变了。也可以换一种马力差距再试。';
    result.replaceChildren(p,list,prompt);
  });
  document.getElementById('race-reset').addEventListener('click',()=>{
    choices.forEach(select=>{select.value='';});result.textContent='已清空安排，当前马力条件保留。可以重新想一想。';choices[0].focus();
  });
})();
