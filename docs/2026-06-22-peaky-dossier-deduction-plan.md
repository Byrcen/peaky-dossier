# 浴血黑帮·卷宗 — 推理玩法 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有单文件 `index.html` 之上新增一层推理引擎,把 5 条暗线 + 35 幕做成 7 个按季推进的"案子":玩家在红线板上点照片(指认)/依次连线(因果链)破案,答完盖判决章、播揭晓幕、归档;现有自由导航并行常开。

**Architecture:** 纯前端、单文件、零依赖、零构建(这是产品卖点,不可破)。新增 `CASES[]` 数据层 + 推理引擎函数组,让 BOARD 视图按 `boardMode('case'|'free')` 分流:case 态叠加案头/指认/连线/判决,free 态完全复用现有透镜导航。数据与展示解耦,延续现有 `SCENES/THREADS/CHARACTERS` 风格。

**Tech Stack:** 原生 ES5-风格 JS(与现有代码一致,`var` + 函数声明)、内联 SVG 像素件、Web Audio 程序化音效、`localStorage` 持久化、内置 `__selftest()` 数据自检。

**设计依据:** [docs/2026-06-22-peaky-dossier-deduction-design.md](2026-06-22-peaky-dossier-deduction-design.md)

---

## 验证约定(本项目无测试框架,统一这样"跑测试")

本项目没有 pytest/jest;**测试 = 扩展内置 `__selftest()`(纯数据/逻辑断言)+ 浏览器交互验证**。每个任务统一:

- **逻辑/数据任务**:在 `__selftest()` 里加 `ok(条件,"信息")` 断言 → 浏览器打开 `index.html`(或 `preview_start`)→ 看 DevTools 控制台:`__selftest()` 须返回 `"PASS"`、无 `console.assert` 失败。`boot()` 已有 `console.assert(__selftest()==="PASS","selftest")`,失败会在控制台红字报出。可在控制台直接敲 `__selftest()` 看返回值。
- **UI/交互任务**:`preview_start` → `preview_eval: window.location.reload()` → `preview_click`/`preview_snapshot`/`preview_console_logs` 验证 DOM 与行为;视觉改动用 `preview_screenshot`。

**本地起服务**:`python3 -m http.server 4792`(项目目录内),浏览器开 `http://localhost:4792`。

**单文件铁律**:所有代码进 `index.html`,按现有 `/* === 数据 === */`、`/* === 纯逻辑 === */`、`/* === 渲染 === */` 分节插入。**不拆文件、不加依赖、不引构建。**

---

## File Structure

唯一改动文件:

- **Modify: `index.html`** — 全部新增代码进此文件,分区块:
  - `数据`:新增 `CASES[]`;`BOARD_PINS` 补 3 个图钉。
  - `纯逻辑`:`state` 扩展;推理引擎函数(case 流程、连线/指认/预判校验、成色/直觉、提示);`__selftest()` 扩展。
  - `渲染`:`renderBoard` 加 `boardMode` 分流;新增案头/判决浮层/预判浮层/案卷夹/最终裁定屏渲染;`sfx()` 加 4 个音效;新增 CSS 类。
  - `<style>`:案头、嫌疑高亮、连线动画、判决图章、案卷夹、浮层、移动端的样式。
  - `T{}`:新增中英 UI 串。
- **Modify: `README.md`** — 更新玩法说明(最后一个任务)。
- 设计文档已存于 `docs/`,本计划亦然。

---

## 数据事实速查(实现时照此引用,避免拼错 id)

- **场景 id**(节选):`prologue, s1-guns, s1-campbell, s1-grace, s1-freddie, s1-kimber, s1-showdown, s2-garrison, s2-epsom, s2-michael, s2-polly, s3-wedding, s3-russia, s3-grace, s3-tunnel, s4-noose, s4-luca, s4-john, s4-gold, s4-mp, s5-crash, s5-mosley, s5-bonnie, s5-plot, s5-traitor, s5-fog, s6-bodies, s6-boston, s6-curse, s6-diagnosis, s6-ruby, s6-finale, finale-end`。
- **暗线 id**:`changretta`(血仇)、`sapphire`(蓝宝石)、`bullet`(子弹)、`leak`(电话)、`ghosts`(两片雾)。
- **现有图钉**:`pin-tommy,-grace,-arthur,-polly,-john,-ada,-michael,-campbell,-alfie,-luca,-mosley,-aberama,-billygrade,-swing,-ruby,-sapphire`。
- **需新增图钉**:`pin-vicente,-finn,-holford`(其 CHARACTER 已存在:`vicente/finn/holford`)。
- **暗线 → 覆盖案**(用于自动连线/解锁 note 的规则,见 Task 12):某暗线全部 `beatIds` 所在的案都已结 → 该线整条红线连出 + note 解锁。
  - bullet `[s1-campbell,s2-polly]` → 案1+案2 → 案2 结时点亮。
  - changretta `[s3-grace,s4-luca,s4-john,s4-mp]` → 案3+案4 → 案4 结时点亮。
  - sapphire `[s3-grace,s6-curse,s6-ruby]` → 案3+案6 → 案6 结时点亮。
  - leak `[s5-plot,s5-fog,s6-bodies]` → 案5+案6 → 案6 结时点亮。
  - ghosts `[s5-fog,s6-finale]` → 案5+案7 → 案7 结时点亮。

---

# Phase A — 数据层 + state + selftest(地基)

### Task A1: 新增 3 个缺失图钉

**Files:** Modify `index.html`(`BOARD_PINS` 数组,约 452–469 行)

- [ ] **Step 1: 加断言(测试先行)**

在 `__selftest()` 的 `return` 前插入:

```js
  ["pin-vicente","pin-finn","pin-holford"].forEach(function(id){ ok(pids[id],"应存在新图钉 "+id); });
```

- [ ] **Step 2: 运行,确认失败**

浏览器控制台敲 `__selftest()`。Expected: `FAIL(3): 应存在新图钉 pin-vicente | ...`。

- [ ] **Step 3: 实现 — 在 `BOARD_PINS` 数组末尾(`pin-sapphire` 那行后)追加**

```js
 ,{id:"pin-vicente",kind:"photo",ref:"vicente",x:90,y:30,rot:3,tack:"#1c1c1c"}
 ,{id:"pin-finn",kind:"photo",ref:"finn",x:30,y:54,rot:-2,tack:"#b8862b"}
 ,{id:"pin-holford",kind:"photo",ref:"holford",x:54,y:34,rot:2,tack:"#9aa0a8"}
```

- [ ] **Step 4: 运行,确认通过**

控制台 `__selftest()` → Expected: `"PASS"`。`preview_snapshot` 进板后能看到 3 个新照片钉(位置可后续微调)。

- [ ] **Step 5: Commit**

```bash
git add index.html && git commit -m "feat(deduction): add board pins for vicente/finn/holford"
```

---

### Task A2: 扩展 `state`(案件进度 + 直觉)

**Files:** Modify `index.html`(`state` 定义,约 487 行)

`save()` 已序列化整个 `state`;`load()` 已 `for(k in o) state[k]=o[k]`。故只需补默认字段 + 一个"补默认"的归一化(防旧存档缺字段)。

- [ ] **Step 1: 加断言**

`__selftest()` `return` 前:

```js
  ok(state.cases&&typeof state.cases.solved==="object","state.cases.solved 应存在");
  ok(state.instinct&&typeof state.instinct.correct==="number","state.instinct 应存在");
```

- [ ] **Step 2: 运行确认失败** — 控制台 `__selftest()` → `FAIL(2)`。

- [ ] **Step 3: 实现**

把 `state` 定义改为:

```js
var state={lang:"zh",muted:false,lastBeat:null,lastThread:"all",visited:{},
  cases:{solved:{},current:null,step:0,examined:{},connected:{}},
  instinct:{correct:0,total:0}};
```

在 `load()` 函数体末尾(`}catch(e){}` 前)补默认归一(防旧存档):

```js
  if(!state.cases) state.cases={solved:{},current:null,step:0,examined:{},connected:{}};
  if(!state.cases.solved) state.cases.solved={};
  if(!state.cases.examined) state.cases.examined={};
  if(!state.cases.connected) state.cases.connected={};
  if(!state.instinct) state.instinct={correct:0,total:0};
```

- [ ] **Step 4: 运行确认通过** — `__selftest()` → `"PASS"`。

- [ ] **Step 5: Commit**

```bash
git add index.html && git commit -m "feat(deduction): extend state with cases progress + instinct"
```

---

### Task A3: 新增 `CASES[]` 数据(7 案全量,双语)

**Files:** Modify `index.html`(`数据` 区块,`THREADS`/`BOARD_PINS` 之后、`T{}` 之前插入)

**数据模型**:`evidence[{scene,clueZh,clueEn}]`(clue = 不剧透的督察批注);`steps[]` 每步 `kind` ∈ `accuse|connect|predict`:
- `accuse`:`suspects:[pinId...]`(点照片)、`answer:pinId`、`becauseZh/En`。
- `connect`:`links:[[fromPin,toPin]...]`(须按序连对)、`becauseZh/En`。
- `predict`:`beforeScene:sceneId`(揭晓此幕前弹)、`options:[{labelZh,labelEn}...]`、`answer:idx`。
- `revealSeq:[sceneId...]`(答完按序播);`seeds/closes:[threadId...]`(叙事标注,实际点亮由 Task 12 的暗线规则算)。

- [ ] **Step 1: 加断言(校验整张表自洽)**

`__selftest()` `return` 前插入:

```js
  ok(Array.isArray(CASES)&&CASES.length===7,"CASES 应为 7 案");
  var caseIds={};
  CASES.forEach(function(c){
    ok(!caseIds[c.id],"CASE id 重复:"+c.id); caseIds[c.id]=1;
    ok(c.titleZh&&c.titleEn&&c.briefZh&&c.briefEn,"case "+c.id+" 双语标题/简介缺失");
    (c.evidence||[]).forEach(function(e){
      ok(sids[e.scene],"case "+c.id+" 证物场景无效:"+e.scene);
      ok(e.clueZh&&e.clueEn,"case "+c.id+" 证物 "+e.scene+" 批注双语缺失");
    });
    ok((c.steps||[]).length>=1,"case "+c.id+" 至少 1 步");
    (c.steps||[]).forEach(function(st,i){
      if(st.kind==="accuse"){
        ok(st.suspects.indexOf(st.answer)>-1,"case "+c.id+" step"+i+" answer 不在 suspects 内");
        st.suspects.forEach(function(p){ok(pids[p],"case "+c.id+" suspect 图钉无效:"+p);});
        ok(st.becauseZh&&st.becauseEn,"case "+c.id+" step"+i+" because 双语缺失");
      } else if(st.kind==="connect"){
        ok(st.links&&st.links.length>=1,"case "+c.id+" connect 应有 links");
        st.links.forEach(function(L){ok(pids[L[0]]&&pids[L[1]],"case "+c.id+" connect 图钉无效:"+L);});
        ok(st.becauseZh&&st.becauseEn,"case "+c.id+" step"+i+" because 双语缺失");
      } else if(st.kind==="predict"){
        ok(sids[st.beforeScene],"case "+c.id+" predict beforeScene 无效:"+st.beforeScene);
        ok(st.options.length>=2&&st.options[st.answer],"case "+c.id+" predict 选项/答案无效");
      } else ok(false,"case "+c.id+" step"+i+" 未知 kind:"+st.kind);
    });
    (c.revealSeq||[]).forEach(function(id){ok(sids[id],"case "+c.id+" revealSeq 场景无效:"+id);});
    (c.seeds||[]).concat(c.closes||[]).forEach(function(th){
      ok(THREADS.some(function(t){return t.id===th;}),"case "+c.id+" 暗线 id 无效:"+th);
    });
  });
```

- [ ] **Step 2: 运行确认失败** — `__selftest()` → `FAIL(...)`(CASES 未定义)。

- [ ] **Step 3: 实现 — 插入完整 `CASES[]`**

```js
var CASES=[
 {id:"c1-mole",season:1,no:"01",
  titleZh:"加里森的眼线",titleEn:"The mole in the Garrison",
  briefZh:"丘吉尔要追回失窃的机枪,坎贝尔在谢尔比家里安插了一双眼睛。是谁?",
  briefEn:"Churchill wants the stolen guns back; Campbell has planted a pair of eyes in the Shelby home. Whose?",
  evidence:[
   {scene:"prologue",clueZh:"战后小希思,谢尔比靠帽檐里的剃刀立威——血亲抱团,外人难入。",clueEn:"Post-war Small Heath: the Shelbys rule with razors in their caps — blood sticks together, outsiders don't get in."},
   {scene:"s1-guns",clueZh:"一箱本不该碰的机枪惊动了丘吉尔,警方急于在帮派内部安一个人。",clueEn:"A crate of guns they never should have touched reaches Churchill — the police badly need someone on the inside."},
   {scene:"s1-campbell",clueZh:"坎贝尔从贝尔法斯特赴任,放话要在帮派里'安一双眼睛'。",clueEn:"Campbell arrives from Belfast, vowing to plant 'a pair of eyes' inside the gang."},
   {scene:"s1-grace",clueZh:"加里森新来一名歌女,逢人便打听谢尔比家的事;有人见她进出过警局。",clueEn:"A new singer turns up at the Garrison, asking about the family — and has been seen coming and going at the police station."},
   {scene:"s1-freddie",clueZh:"共产党人 Freddie 与艾达秘密成婚——这家人自己也藏着秘密。",clueEn:"The communist Freddie has secretly married Ada — this family keeps secrets of its own."}
  ],
  steps:[
   {kind:"accuse",
    promptZh:"坎贝尔安插在谢尔比家的眼线是谁?",promptEn:"Who is Campbell's informant inside the Shelby world?",
    suspects:["pin-grace","pin-ada","pin-polly","pin-john"],answer:"pin-grace",
    becauseZh:"Grace 在警方正需要内线时'恰好'出现,打听家事、又被见进出警局——血亲不会替王权当眼线,外来者才会。",
    becauseEn:"Grace appears just as the police need eyes, asks about the family, and is seen at the station. Blood wouldn't inform for the Crown — the newcomer would."},
   {kind:"predict",beforeScene:"s1-showdown",
    promptZh:"赛道摊牌,Kimber 开枪——谁替 Tommy 挡下这一枪?",promptEn:"At the showdown Kimber fires — who takes the bullet meant for Tommy?",
    options:[{labelZh:"Tommy 自己中枪",labelEn:"Tommy is hit"},{labelZh:"Danny 替他挡枪",labelEn:"Danny shields him"},{labelZh:"无人中枪",labelEn:"No one is hit"}],answer:1}
  ],
  seeds:["bullet"],closes:[],revealSeq:["s1-showdown"]},

 {id:"c2-bullet",season:2,no:"02",
  titleZh:"坟前那一枪",titleEn:"The bullet at the grave",
  briefZh:"假处决之后,坎贝尔倒在血泊里。谁扣了扳机?",
  briefEn:"After the mock execution, Campbell lies dead. Who pulled the trigger?",
  evidence:[
   {scene:"s2-garrison",clueZh:"IRA 炸了加里森,胁迫 Tommy 替他们杀人——四面皆敌。",clueEn:"The IRA bomb the Garrison and blackmail Tommy into killing for them — enemies on every side."},
   {scene:"s2-epsom",clueZh:"坎贝尔与丘吉尔逼 Tommy 在赛马日行刺元帅;坎贝尔握着全家的命门。",clueEn:"Campbell and Churchill force Tommy to assassinate a Field Marshal; Campbell holds the whole family's leash."},
   {scene:"s2-michael",clueZh:"波莉失散的儿子归来——她比谁都清楚坎贝尔对她做过什么,恨意最深。",clueEn:"Polly's lost son returns — she of all people knows what Campbell did to her, and hates him most."}
  ],
  steps:[
   {kind:"accuse",
    promptZh:"坟边枪杀坎贝尔的是谁?",promptEn:"Who shoots Campbell dead at the graveside?",
    suspects:["pin-polly","pin-tommy","pin-arthur","pin-michael"],answer:"pin-polly",
    becauseZh:"动机最私人的人是波莉——坎贝尔施暴于她;Tommy 此刻正被放过、需要他活着办差,没有人比波莉更想要这一枪。",
    becauseEn:"The most personal motive is Polly's — Campbell assaulted her. Tommy is being spared to do a job; no one wants this shot more than she does."}
  ],
  seeds:[],closes:["bullet"],revealSeq:["s2-polly"]},

 {id:"c3-gala",season:3,no:"03",
  titleZh:"晚宴上的子弹",titleEn:"The bullet at the gala",
  briefZh:"募捐晚宴上一声'For Angel!',一枪射向 Tommy。这一夜将牵出两条要命的线。",
  briefEn:"At the charity gala — a cry of 'For Angel!', a shot at Tommy. This night sets two deadly threads in motion.",
  evidence:[
   {scene:"s3-wedding",clueZh:"庄园婚礼上一名俄国奸细对错暗号被当场处决——俄国人很危险,但他们是被你杀的。",clueEn:"At the Arrow House wedding a Russian agent gives the wrong code and is executed — the Russians are dangerous, but it's you killing them."},
   {scene:"s3-russia",clueZh:"白俄一家与神父休斯设局;另有传闻:伦敦一户意大利人记着仇——儿子 Angel 被 John 弄瞎了眼。",clueEn:"The White Russians and Father Hughes are plotting; and word is an Italian family in London nurses a grudge — a son, Angel, was blinded by John Shelby."},
   {scene:"s3-tunnel",clueZh:"Tommy 掘隧道劫走俄国人的珍宝——可这是抢劫,不是当众喊'For Angel'的血亲复仇。",clueEn:"Tommy tunnels in and robs the Russians' treasure — but that's theft, not a public 'For Angel' blood-cry."}
  ],
  steps:[
   {kind:"predict",beforeScene:"s3-grace",
    promptZh:"枪声响起,射向 Tommy 的子弹会打中谁?",promptEn:"A shot rings out. Who does the bullet meant for Tommy hit?",
    options:[{labelZh:"Tommy",labelEn:"Tommy"},{labelZh:"Grace",labelEn:"Grace"},{labelZh:"Arthur",labelEn:"Arthur"}],answer:1},
   {kind:"connect",
    promptZh:"把今晚的线索钉进案卷:Grace 当晚戴着那条会要命的项链——连出这条因果。",promptEn:"Pin tonight's clue: Grace was wearing the necklace that will kill — draw the link.",
    links:[["pin-grace","pin-sapphire"]],
    becauseZh:"Grace 戴着那条蓝宝石。这条'被诅咒'的线从今夜起,会一路走到鲁比。",
    becauseEn:"Grace wears the sapphire. From tonight, this 'cursed' thread runs all the way to Ruby."}
  ],
  seeds:["sapphire"],closes:[],revealSeq:["s3-grace"]},

 {id:"c4-vendetta",season:4,no:"04",
  titleZh:"血仇之链",titleEn:"The vendetta chain",
  briefZh:"西西里人渡海而来。把这场血亲复仇按因果顺序排成一条链。",
  briefEn:"The Sicilians cross the ocean. Reconstruct the blood vendetta, link by link, in order.",
  evidence:[
   {scene:"s4-noose",clueZh:"全家险些上绞架,平安夜被 Tommy 最后一刻赎回——元气大伤。",clueEn:"The family nearly hangs; Tommy buys their pardons on Christmas Eve — badly weakened."},
   {scene:"s4-luca",clueZh:"纽约黑手党卢卡·尚格莱特登门,为死去的父亲维森特与兄弟安吉尔索命。",clueEn:"New York mafioso Luca Changretta arrives to avenge his dead father Vicente and brother Angel."},
   {scene:"s4-john",clueZh:"门廊外机枪齐射,John Shelby 当场殒命。",clueEn:"Machine guns rake the doorstep; John Shelby dies where he stands."},
   {scene:"s4-gold",clueZh:"Tommy 引入吉普赛枪手与拳手金家父子助阵。",clueEn:"Tommy brings in the Romani Golds — gunman and boxer — to even the odds."},
   {scene:"s4-mp",clueZh:"诈死的亚瑟出手了结卢卡;血仇收场。",clueEn:"A faked-dead Arthur finishes Luca; the vendetta ends."}
  ],
  steps:[
   {kind:"connect",
    promptZh:"按因果顺序依次连线,排出整条血仇(起因:John 弄瞎了 Angel):维森特→Grace、亚瑟→维森特、卢卡→John、亚瑟→卢卡。",
    promptEn:"Connect the pins in causal order (origin: John blinded Angel): Vicente→Grace, Arthur→Vicente, Luca→John, Arthur→Luca.",
    links:[["pin-vicente","pin-grace"],["pin-arthur","pin-vicente"],["pin-luca","pin-john"],["pin-arthur","pin-luca"]],
    becauseZh:"John 弄瞎 Angel → 维森特派人杀了 Grace → 亚瑟杀维森特 → 卢卡为父杀 John → 诈死的亚瑟终结卢卡。一报还一报。",
    becauseEn:"John blinds Angel → Vicente's men kill Grace → Arthur kills Vicente → Luca kills John for his father → a faked-dead Arthur ends Luca. Blood for blood."}
  ],
  seeds:["changretta"],closes:["changretta"],revealSeq:["s4-mp"]},

 {id:"c5-leak",season:5,no:"05",
  titleZh:"内鬼是谁",titleEn:"The informant",
  briefZh:"刺杀莫斯利的计划崩了——有人把它捅给了 IRA。顺着泄密的链子连下去。",
  briefEn:"The plot to kill Mosley collapses — someone tipped the IRA. Trace the leak, link by link.",
  evidence:[
   {scene:"s5-crash",clueZh:"华尔街崩盘,迈克尔抗命未套现、害家族巨亏——他与 Tommy 早生嫌隙。",clueEn:"The Crash wipes out the fortune after Michael defies orders — he and Tommy are already at odds."},
   {scene:"s5-mosley",clueZh:"议员 Tommy 周旋于法西斯莫斯利——这是要除掉的目标。",clueEn:"MP Tommy circles the fascist Mosley — the target to be removed."},
   {scene:"s5-bonnie",clueZh:"Billy Boys 钉死 Bonnie,逼反阿贝拉马——刺杀计划随之定下。",clueEn:"The Billy Boys crucify Bonnie, turning Aberama — the assassination plan is set."},
   {scene:"s5-plot",clueZh:"计划部署完毕,却走漏了风声:有人多嘴,把它说给了爱嚼舌的 Billy Grade。",clueEn:"The plan is in place — but it leaks: someone talks, letting it slip to the loose-lipped Billy Grade."},
   {scene:"s5-traitor",clueZh:"迈克尔和美籍妻子吉娜暗中要夺家族权柄——但那是抢钱抢位,不是把刺杀计划卖给 IRA。",clueEn:"Michael and his American wife Gina move to seize the family — but that's about money and power, not selling a plot to the IRA."}
  ],
  steps:[
   {kind:"connect",
    promptZh:"连出泄密的链子:谁先走漏 → 谁告密 IRA。(别被迈克尔的夺权带偏。)",promptEn:"Draw the leak: who lets it slip → who tips the IRA. (Don't be misled by Michael's power grab.)",
    links:[["pin-finn","pin-billygrade"],["pin-billygrade","pin-swing"]],
    becauseZh:"芬恩嘴快,把计划说给了 Billy Grade;Billy Grade 转手告密 IRA(斯温)。迈克尔的背叛是商业夺权,与这次泄密无关——他是障眼法。",
    becauseEn:"Finn lets it slip to Billy Grade; Billy Grade tips the IRA (Swing). Michael's betrayal is a commercial power grab — a red herring, not this leak."},
   {kind:"predict",beforeScene:"s5-fog",
    promptZh:"行刺崩盘,Tommy 独立雾中,枪口抵住自己太阳穴——他开枪了吗?",promptEn:"The plot collapses; alone in the fog, Tommy lifts the pistol to his own temple — does he fire?",
    options:[{labelZh:"开枪了",labelEn:"He fires"},{labelZh:"没有(黑屏,四年后)",labelEn:"No — cut to black, four years on"}],answer:1}
  ],
  seeds:["leak"],closes:[],revealSeq:["s5-fog"]},

 {id:"c6-curse",season:6,no:"06",
  titleZh:"诅咒与假死",titleEn:"The curse and the false death",
  briefZh:"被诅咒的蓝宝石终于应验;而有人正告诉 Tommy:你快死了。",
  briefEn:"The cursed sapphire comes due at last; and someone is telling Tommy he is dying.",
  evidence:[
   {scene:"s6-bodies",clueZh:"IRA 把波莉、阿贝拉马、Barney 的尸体送回——S5 那通告密的电话,代价在此。",clueEn:"The IRA return the bodies of Polly, Aberama and Barney — the price of that S5 phone call comes due."},
   {scene:"s6-boston",clueZh:"戒酒的 Tommy 做着波士顿鸦片生意;迈克尔记恨波莉之死,起了弑兄之心。",clueEn:"Sober Tommy works the Boston opium trade; Michael, blaming him for Polly, wants him dead."},
   {scene:"s6-curse",clueZh:"Grace 的蓝宝石辗转克死了七岁的康妮;Evadne 以此诅咒 Tommy——也将失去七岁的女儿。",clueEn:"Grace's sapphire passes on and kills seven-year-old Connie; Evadne curses Tommy to lose his own daughter at seven."},
   {scene:"s6-diagnosis",clueZh:"霍尔福德医生诊断 Tommy 患'结核瘤'将死;诊断来得'恰逢其时'——背后晃着莫斯利的影子。",clueEn:"Dr. Holford diagnoses a fatal 'tuberculoma'; the diagnosis is suspiciously convenient — Mosley's shadow falls behind it."}
  ],
  steps:[
   {kind:"predict",beforeScene:"s6-ruby",
    promptZh:"诅咒点名一个七岁的孩子。它会带走谁?",promptEn:"The curse names a child of seven. Who does it take?",
    options:[{labelZh:"查理",labelEn:"Charlie"},{labelZh:"鲁比",labelEn:"Ruby"},{labelZh:"无人,只是迷信",labelEn:"No one — just superstition"}],answer:1},
   {kind:"connect",
    promptZh:"把诅咒的最后一环连上:蓝宝石→鲁比。",promptEn:"Draw the curse's final link: the sapphire → Ruby.",
    links:[["pin-sapphire","pin-ruby"]],
    becauseZh:"那条从 Grace 起的蓝宝石,辗转克死康妮,终于应验在七岁的鲁比身上。诅咒收口。",
    becauseEn:"The sapphire that began with Grace, having killed Connie, comes due at last on seven-year-old Ruby. The curse closes."},
   {kind:"accuse",
    promptZh:"有人在 Tommy 的'死讯'背后操盘。是谁?",promptEn:"Someone is behind Tommy's 'death sentence'. Who?",
    suspects:["pin-mosley","pin-holford","pin-michael","pin-tommy"],answer:"pin-mosley",
    becauseZh:"诊断对莫斯利太'方便'了——他买通霍尔福德谎称 Tommy 将死,诱他自尽。霍尔福德只是工具,迈克尔的恨另有出口,Tommy 并非真病。",
    becauseEn:"The diagnosis is far too convenient for Mosley — he bought Holford to tell Tommy he's dying and nudge him to end himself. Holford is the tool; Michael's hate runs elsewhere; Tommy isn't truly ill."}
  ],
  seeds:[],closes:["sapphire","leak"],revealSeq:["s6-ruby","s6-diagnosis"]},

 {id:"c7-fog",season:7,no:"07",
  titleZh:"两片雾",titleEn:"Two fogs",
  briefZh:"Tommy 两次独立雾中。把崩溃的那一片,与重生的那一片,连成首尾呼应。",
  briefEn:"Twice Tommy stands alone in the fog. Link the fog of collapse to the fog of rebirth.",
  evidence:[
   {scene:"s5-fog",clueZh:"第一片雾:他幻见亡妻 Grace,枪口抵住太阳穴——崩溃。",clueEn:"The first fog: he hallucinates his dead wife Grace and lifts the pistol to his temple — collapse."},
   {scene:"s6-finale",clueZh:"第二片雾:鲁比的鬼魂点醒他'你没病,去点火'——重生。",clueEn:"The second fog: Ruby's ghost wakes him — 'you're not ill, go light the fire' — rebirth."}
  ],
  steps:[
   {kind:"connect",
    promptZh:"把两片雾连成镜像:Grace 的幻影(崩溃)↔ 鲁比的鬼魂(重生)。",promptEn:"Mirror the two fogs: Grace's phantom (collapse) ↔ Ruby's ghost (rebirth).",
    links:[["pin-grace","pin-ruby"]],
    becauseZh:"同一片田野,同一场雾。一次让他想死,一次让他活下去——首尾呼应,Tommy·Shelby 还活着。",
    becauseEn:"The same field, the same fog. One nearly kills him, one keeps him alive — bookends. Tommy Shelby is still alive."}
  ],
  seeds:[],closes:["ghosts"],revealSeq:["s6-finale","finale-end"]}
];
```

- [ ] **Step 4: 运行确认通过** — 控制台 `__selftest()` → `"PASS"`(所有 ref/answer/双语校验过)。

- [ ] **Step 5: Commit**

```bash
git add index.html && git commit -m "feat(deduction): add CASES[] — 7 season-gated cases (bilingual, clue notes, steps)"
```

---

# Phase B — 推理引擎(纯逻辑,可在 selftest 断言)

### Task B1: 案件查找 + 进度状态

**Files:** Modify `index.html`(`纯逻辑` 区块,`charById/sceneById/pinById` 附近加同类查找)

- [ ] **Step 1: 加断言**

```js
  ok(typeof caseById==="function"&&caseById("c5-leak").titleEn==="The informant","caseById 应能查到案");
  ok(caseStatus("c1-mole")==="current"||caseStatus("c1-mole")==="solved","首案应为 current(或已解)");
  ok(caseStatus("c7-fog")==="locked"||state.cases.solved["c6-curse"],"末案在前案未解时应 locked");
```

- [ ] **Step 2: 运行确认失败** — `FAIL`(函数未定义)。

- [ ] **Step 3: 实现**

```js
function caseById(id){for(var i=0;i<CASES.length;i++)if(CASES[i].id===id)return CASES[i];}
function caseIndex(id){for(var i=0;i<CASES.length;i++)if(CASES[i].id===id)return i;return -1;}
function caseStatus(id){
  if(state.cases.solved[id])return "solved";
  var i=caseIndex(id);
  if(i===0)return "current";
  return state.cases.solved[CASES[i-1].id]?"current":"locked";
}
function firstUnsolvedCase(){ for(var i=0;i<CASES.length;i++)if(!state.cases.solved[CASES[i].id])return CASES[i].id; return null; }
```

- [ ] **Step 4: 运行确认通过** — `__selftest()` → `"PASS"`。

- [ ] **Step 5: Commit**

```bash
git add index.html && git commit -m "feat(deduction): case lookup + season-gated status"
```

---

### Task B2: 指认/连线/预判校验 + 成色/直觉记账

**Files:** Modify `index.html`(`纯逻辑` 区块)

- [ ] **Step 1: 加断言**

```js
  var _c4=caseById("c4-vendetta").steps[0];
  ok(connectMatches(_c4,[["pin-vicente","pin-grace"],["pin-arthur","pin-vicente"],["pin-luca","pin-john"],["pin-arthur","pin-luca"]]),"正确链应判对");
  ok(!connectMatches(_c4,[["pin-arthur","pin-vicente"],["pin-vicente","pin-grace"]]),"乱序应判错");
  ok(linkExpectedAt(_c4,0,"pin-vicente","pin-grace"),"第0跳应接受 vicente→grace");
  ok(!linkExpectedAt(_c4,0,"pin-arthur","pin-vicente"),"第0跳不应接受 arthur→vicente");
  ok(ratingFromCost(0,0)===3&&ratingFromCost(1,0)===2&&ratingFromCost(0,2)===1,"成色:0错0提示=3,1错=2,2提示=1");
```

- [ ] **Step 2: 运行确认失败** — `FAIL`。

- [ ] **Step 3: 实现**

```js
function accuseCorrect(step,pinId){ return step.kind==="accuse" && pinId===step.answer; }
// connect 逐跳校验:第 n 跳(已连 n 条)是否接受 from→to
function linkExpectedAt(step,n,from,to){ var L=step.links[n]; return !!L && L[0]===from && L[1]===to; }
// 整条链一次性校验(用于自检/重放)
function connectMatches(step,links){
  if(!links||links.length!==step.links.length)return false;
  for(var i=0;i<links.length;i++){ if(links[i][0]!==step.links[i][0]||links[i][1]!==step.links[i][1])return false; }
  return true;
}
function ratingFromCost(wrong,hints){ var r=3-wrong-hints; return r<1?1:r; }
function recordInstinct(ok){ state.instinct.total++; if(ok)state.instinct.correct++; save(); }
```

- [ ] **Step 4: 运行确认通过** — `"PASS"`。

- [ ] **Step 5: Commit**

```bash
git add index.html && git commit -m "feat(deduction): accuse/connect validators + rating/instinct accounting"
```

---

### Task B3: 暗线红线随结案点亮 + 结案记账

**Files:** Modify `index.html`(`纯逻辑` 区块)

- [ ] **Step 1: 加断言**

```js
  // 临时造一个"已结案"环境验证 threadLit,跑完还原
  var _sv=JSON.stringify(state.cases.solved);
  state.cases.solved={"c1-mole":{rating:3},"c2-bullet":{rating:3}};
  ok(threadLit("bullet")===true,"子弹线两案皆结应点亮");
  ok(threadLit("sapphire")===false,"蓝宝石线未结不应点亮");
  state.cases.solved=JSON.parse(_sv);
```

- [ ] **Step 2: 运行确认失败** — `FAIL`。

- [ ] **Step 3: 实现**

```js
// 某暗线全部 beatIds 所在的案都已结 → 该线点亮
function casesCoveringScene(sceneId){
  return CASES.filter(function(c){
    var inEv=(c.evidence||[]).some(function(e){return e.scene===sceneId;});
    var inRev=(c.revealSeq||[]).indexOf(sceneId)>-1;
    return inEv||inRev;
  });
}
function threadLit(thId){
  var th=THREADS.filter(function(x){return x.id===thId;})[0]; if(!th)return false;
  return th.beatIds.every(function(bid){
    var cs=casesCoveringScene(bid);
    return cs.length>0 && cs.some(function(c){return state.cases.solved[c.id];});
  });
}
function litThreads(){ return THREADS.filter(function(t){return threadLit(t.id);}).map(function(t){return t.id;}); }
```

- [ ] **Step 4: 运行确认通过** — `"PASS"`。

- [ ] **Step 5: Commit**

```bash
git add index.html && git commit -m "feat(deduction): threadLit() — strings light up as covering cases close"
```

---

# Phase C — 案头 + 板上交互 + 判决/预判(浏览器验证)

> 这一阶段起以 `preview_*` 验证 DOM/交互。每个任务先 `preview_start`、`reload`,再点击/快照。

### Task C1: `boardMode` 分流 + 案头渲染

**Files:** Modify `index.html`(`renderBoard` 约 578 行;`<style>`;`T{}`)

- [ ] **Step 1: 先加 i18n 串(`T{}` 内追加)**

```js
 ,investigate:{zh:"开始查案",en:"Open the casebook"}
 ,freeBrowse:{zh:"自由浏览",en:"Free browse"}
 ,casebook:{zh:"案卷夹",en:"Casebook"}
 ,examineEvidence:{zh:"查阅证物",en:"Examine evidence"}
 ,evidenceLab:{zh:"证物",en:"Evidence"}
 ,suspectsLab:{zh:"嫌疑人",en:"Suspects"}
 ,accuseHint:{zh:"点一张照片,指认凶手",en:"Tap a photo to name them"}
 ,connectHintT:{zh:"按因果顺序点选图钉,连出红线",en:"Tap pins in causal order to draw the thread"}
 ,callIt:{zh:"押一个",en:"Call it"}
 ,caseClosed:{zh:"CASE CLOSED",en:"CASE CLOSED"}
 ,coldCase:{zh:"COLD CASE",en:"COLD CASE"}
 ,becauseLab:{zh:"为什么",en:"Why"}
 ,revealNow:{zh:"看真相",en:"See what happened"}
 ,reExamine:{zh:"重新查",en:"Re-examine"}
 ,hunch:{zh:"督察的直觉",en:"Campbell's hunch"}
 ,instinctLab:{zh:"直觉准星",en:"Instinct"}
 ,solvedLab:{zh:"已结案",en:"Closed"}
 ,lockedLab:{zh:"未解锁",en:"Locked"}
 ,finalVerdict:{zh:"对 Tommy Shelby 的最终裁定",en:"The verdict on Tommy Shelby"}
```

- [ ] **Step 2: 加 `boardMode` 与案头**

在渲染区块顶部加全局:`var boardMode="free", activeCase=null;`

修改 `renderBoard()` 开头,在拼 `thbtns/sgbtns` 之前分流:

```js
function renderBoard(){
 var el=document.getElementById("board");
 if(boardMode==="case"&&activeCase){ renderCaseBoard(el); return; }
 /* ...原有 free 态逻辑保持不动... */
```

新增 `renderCaseBoard(el)`:渲染"案头"覆盖在板顶,并复用现有图钉层(`#pinlayer`)。最小实现:

```js
function renderCaseBoard(el){
 var c=caseById(activeCase), st=c.steps[state.cases.step]||c.steps[c.steps.length-1];
 var evChips=c.evidence.map(function(e){
   var seen=state.cases.examined[e.scene]?" seen":"";
   return '<button class="evchip'+seen+'" data-ev="'+e.scene+'">'+(state.cases.examined[e.scene]?"✓ ":"")+sceneById(e.scene).no+'</button>';
 }).join("");
 var stepHint = st.kind==="accuse"? t("accuseHint") : st.kind==="connect"? t("connectHintT") : t("callIt");
 var prompt = lang==="zh"? st.promptZh : st.promptEn;
 el.innerHTML='<div id="bwrap"><svg id="strings"></svg><div id="pinlayer"></div></div>'
  +'<div class="casehead">'
  +'<button class="case-back">&#9664; '+t("casebook")+'</button>'
  +'<div class="case-title">'+c.no+' · '+(lang==="zh"?c.titleZh:c.titleEn)+'</div>'
  +'<div class="case-brief">'+(lang==="zh"?c.briefZh:c.briefEn)+'</div>'
  +'<div class="case-ev"><span class="lab">'+t("evidenceLab")+'</span>'+evChips+'</div>'
  +'<div class="case-prompt">'+prompt+'</div>'
  +'<div class="case-stephint">'+stepHint+'</div>'
  +'<button class="case-hunch">'+t("hunch")+' ✦</button>'
  +'</div>';
 // 复用现有图钉渲染:把本案相关图钉高亮、其余压暗
 paintCasePins(c, st);
 el.querySelector(".case-back").onclick=function(){ exitToCasebook(); };
 el.querySelectorAll(".evchip").forEach(function(b){ b.onclick=function(){ examineEvidence(b.dataset.ev); }; });
 el.querySelector(".case-hunch").onclick=function(){ useHunch(); };
}
```

`paintCasePins/examineEvidence/useHunch/exitToCasebook` 在后续任务实现;本任务先给空壳(`function paintCasePins(){}` 等)让页面不报错,样式到位即可。

- [ ] **Step 3: 加最小 CSS(`<style>` 内)**

```css
.casehead{position:absolute;left:0;right:0;top:0;padding:10px 14px;background:linear-gradient(#1a1410ee,#1a141000);z-index:6;pointer-events:none}
.casehead>*{pointer-events:auto}
.case-title{font-family:Oswald,sans-serif;letter-spacing:.04em;color:#e0a64e;font-size:16px}
.case-brief{color:#d9c8a4;font-size:13px;max-width:640px;margin:4px 0 6px}
.case-prompt{color:#fff;font-size:15px;font-weight:600;margin-top:6px}
.case-stephint{color:#9a8f7a;font-size:12px}
.case-ev{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.evchip{background:#2a2018;color:#caa64a;border:1px solid #4a3a24;border-radius:4px;padding:2px 8px;font-size:12px;cursor:pointer}
.evchip.seen{opacity:.6}
.case-back,.case-hunch{background:#241a12;color:#caa64a;border:1px solid #4a3a24;border-radius:4px;padding:3px 10px;font-size:12px;cursor:pointer}
.case-back{position:absolute;right:14px;top:10px}
.case-hunch{margin-top:8px}
```

- [ ] **Step 4: 临时入口验证**

控制台敲:`boardMode="case";activeCase="c1-mole";enterBoard();`(或 `renderBoard()`)。
- `preview_snapshot` Expected: 看到案头"01 · 加里森的眼线"、简介、5 个证物 chip、提问"坎贝尔安插…的眼线是谁?"。

- [ ] **Step 5: Commit**

```bash
git add index.html && git commit -m "feat(deduction): boardMode split + case header render + i18n strings"
```

---

### Task C2: 查阅证物(复用 SCENE 播放)

**Files:** Modify `index.html`(`openScene/renderScene` 约 767 行)

让"查证"复用现有场景播放,但标记为证物、看完回到案板而非走 lens。

- [ ] **Step 1: 实现 `examineEvidence`**

```js
var sceneCtx=null; // {mode:'evidence'|'reveal', caseId, ...}
function examineEvidence(sceneId){
  state.cases.examined[sceneId]=1; save();
  sceneCtx={mode:"evidence",caseId:activeCase};
  curBeat=sceneId; var _sc=sceneById(sceneId); startAmbient(_sc?_sc.season:0); sfx("enter");
  setView("scene"); renderScene(sceneId);
}
```

在 `renderScene()` 里,当 `sceneCtx&&sceneCtx.mode==="evidence"`:把发光物件的标签改为"返回案卷",点它 = `backToCaseBoard()`;隐藏 lens 进度(`prog`)显示证物角标。最小改法——在 `renderScene` 末尾 `el.querySelector(".sc-prop").onclick` 重写:

```js
 if(sceneCtx&&sceneCtx.mode==="evidence"){
   el.querySelector(".sc-prop .lab").innerHTML=(lang==="zh"?"返回案卷":"back to the case")+' &#8594;';
   el.querySelector(".sc-prop").onclick=function(){ sfx("tick"); backToCaseBoard(); };
   var pv=el.querySelector(".sc-prev2"); if(pv)pv.style.display="none";
 }
```

```js
function backToCaseBoard(){ stopAmbient(); var sc=document.getElementById("scene"); sc.classList.add("hidden"); sc.classList.remove("in"); sceneCtx=null; view="board"; document.getElementById("board").classList.remove("hidden"); renderBoard(); }
```

- [ ] **Step 2: 验证** — `preview`:进 c1 案板 → `preview_click` 证物 chip(`.evchip`)→ `preview_snapshot` 看到场景播放、物件标签为"返回案卷" → 点它 → 回案板,该 chip 变 `✓`(seen)。

- [ ] **Step 3: Commit**

```bash
git add index.html && git commit -m "feat(deduction): examine evidence reuses scene player, returns to case board"
```

---

### Task C3: 指认(accuse)— 点嫌疑照片

**Files:** Modify `index.html`(图钉点击分流 + `paintCasePins`)

- [ ] **Step 1: 实现图钉点击分流**

现有 free 态图钉点击走 `openCharFile/openDossier`。在渲染图钉处(`renderBoard` 的 pin 点击绑定)按 `boardMode` 分流;case 态走 `onCasePinTap`:

```js
function paintCasePins(c,st){
  var pl=document.getElementById("pinlayer"); if(!pl)return; pl.innerHTML="";
  var active={}; // 本步可点的图钉
  if(st.kind==="accuse") st.suspects.forEach(function(p){active[p]=1;});
  else if(st.kind==="connect") st.links.forEach(function(L){active[L[0]]=1;active[L[1]]=1;});
  BOARD_PINS.forEach(function(p){
    var d=document.createElement("div");
    d.className="pin "+p.kind+(active[p.id]?" suspect":" dim");
    d.dataset.pin=p.id; d.style.left=p.x+"%"; d.style.top=p.y+"%";
    d.style.transform="rotate("+p.rot+"deg)";
    d.innerHTML=pinInner(p);
    if(active[p.id]) d.onclick=function(){ onCasePinTap(p.id); };
    pl.appendChild(d);
  });
  renderStrings(litThreads().length?"all":"all"); // 已点亮的线照常画(Task C6 完善)
}
function onCasePinTap(pinId){
  var c=caseById(activeCase), st=c.steps[state.cases.step];
  if(st.kind==="accuse") doAccuse(pinId);
  else if(st.kind==="connect") doConnectTap(pinId);
}
```

(`pinInner` 为现有函数,复用其照片/证物内片;`.suspect`/`.dim` 样式见下。)

- [ ] **Step 2: 实现 `doAccuse` + 计错**

```js
var caseCost={wrong:0,hints:0};
function doAccuse(pinId){
  var c=caseById(activeCase), st=c.steps[state.cases.step];
  if(accuseCorrect(st,pinId)){ sfx("stamp"); afterStepCorrect(c,st); }
  else { caseCost.wrong++; sfx("buzz"); flashWrongPin(pinId);
    if(caseCost.wrong>=3){ verdictOverlay(false,(lang==="zh"?"线索不足以定案。":"Not enough to charge."),true); }
  }
}
function flashWrongPin(pinId){ var d=document.querySelector('.pin[data-pin="'+pinId+'"]'); if(d){d.classList.add("wrong");setTimeout(function(){d.classList.remove("wrong");},420);} }
```

`afterStepCorrect`/`verdictOverlay` 在 Task C5 实现;先放占位 `function afterStepCorrect(){} function verdictOverlay(){}` 防报错。

- [ ] **Step 3: CSS**

```css
.pin.dim{opacity:.28;filter:grayscale(.5)}
.pin.suspect{cursor:pointer;box-shadow:0 0 0 2px #caa64a,0 0 16px #caa64a88}
.pin.wrong{animation:pinwrong .42s}
@keyframes pinwrong{0%,100%{transform:translateX(0)}25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}
```

- [ ] **Step 4: 验证** — c1 案板 → `preview_click` `.pin[data-pin="pin-ada"]`(错)→ 看到抖动、`buzz`(`preview_console_logs` 无报错);点 `pin-grace`(对)→ 进入 verdict 流程(此刻占位,后续完善)。

- [ ] **Step 5: Commit**

```bash
git add index.html && git commit -m "feat(deduction): case-mode pin tap + accuse with wrong-shake + soft fail"
```

---

### Task C4: 连线(connect)— 依次点选图钉拉红线

**Files:** Modify `index.html`(`renderStrings` 约 606 行;连线状态机)

- [ ] **Step 1: 实现点选连线状态机**

```js
var connTap=null;          // 第一次点选暂存的 pinId
var caseLinks=[];          // 本步已连对的 [from,to]
function doConnectTap(pinId){
  var c=caseById(activeCase), st=c.steps[state.cases.step];
  if(connTap===null){ connTap=pinId; markPinSelected(pinId,true); return; }
  if(connTap===pinId){ markPinSelected(pinId,false); connTap=null; return; } // 取消
  var from=connTap, to=pinId; markPinSelected(from,false); connTap=null;
  if(linkExpectedAt(st,caseLinks.length,from,to)){
    caseLinks.push([from,to]); sfx("pluck"); drawCaseLink(from,to);
    if(caseLinks.length===st.links.length){ afterStepCorrect(c,st); }
  } else { caseCost.wrong++; sfx("buzz"); flashWrongPin(to); flashWrongPin(from); }
}
function markPinSelected(pinId,on){ var d=document.querySelector('.pin[data-pin="'+pinId+'"]'); if(d)d.classList.toggle("selected",on); }
```

- [ ] **Step 2: 实现 `drawCaseLink`(往 `#strings` SVG 加一条线)**

复用 `renderStrings` 的坐标算法。新增:

```js
function drawCaseLink(from,to){
  var w=document.getElementById("bwrap"),svg=document.getElementById("strings");
  var A=pinById(from),B=pinById(to); if(!A||!B||!svg)return;
  var ax=A.x/100*w.clientWidth,ay=A.y/100*w.clientHeight,bx=B.x/100*w.clientWidth,by=B.y/100*w.clientHeight;
  var mx=(ax+bx)/2,my=(ay+by)/2+22;
  svg.innerHTML+='<path d="M'+ax+' '+ay+' Q'+mx+' '+my+' '+bx+' '+by+'" stroke="#c0352a" stroke-width="2.6" fill="none" class="caseline"/>';
}
```

CSS(连线画出动画):

```css
.pin.selected{box-shadow:0 0 0 3px #c0352a,0 0 18px #c0352acc}
.caseline{stroke-dasharray:600;stroke-dashoffset:600;animation:drawline .5s forwards}
@keyframes drawline{to{stroke-dashoffset:0}}
```

- [ ] **Step 3: 验证** — 进 c4(`activeCase="c4-vendetta"`)→ 依次 `preview_click` `pin-vicente`→`pin-grace`(对,出红线)→ 乱点一对(错,抖动)→ 按正确四跳连完 → 触发 verdict 流程。`preview_screenshot` 看红线。

- [ ] **Step 4: Commit**

```bash
git add index.html && git commit -m "feat(deduction): tap-to-connect state machine + animated red string"
```

---

### Task C5: 判决浮层 + 步进 + 结案

**Files:** Modify `index.html`(浮层渲染 + 流程推进)

- [ ] **Step 1: 实现 `verdictOverlay` + `afterStepCorrect` + `solveCase`**

```js
function afterStepCorrect(c,st){
  var because=lang==="zh"?st.becauseZh:st.becauseEn;
  // predict 步不产生 because;此处仅 accuse/connect 调用
  verdictOverlay(true, because||"", false, function(){
    state.cases.step++; caseLinks=[]; connTap=null; save();
    if(state.cases.step>=c.steps.length){ solveCase(c); }
    else { advanceToStepOrPredict(c); }
  });
}
function advanceToStepOrPredict(c){
  var st=c.steps[state.cases.step];
  if(st.kind==="predict"){ doPredict(c,st); }   // Task C6
  else renderBoard();
}
function solveCase(c){
  var rating=ratingFromCost(caseCost.wrong,caseCost.hints);
  state.cases.solved[c.id]={rating:rating,wrong:caseCost.wrong,hints:caseCost.hints};
  caseCost={wrong:0,hints:0}; save();
  playReveal((c.revealSeq||[]).slice(),function(){
    if(c.id==="c7-fog"){ renderFinalVerdict(); }   // Task D3
    else exitToCasebook();
  });
}
function verdictOverlay(ok,because,autoReveal,onContinue){
  var d=document.getElementById("dossier"); // 复用现有浮层容器
  var stamp=ok?t("caseClosed"):t("coldCase");
  d.className=""; d.innerHTML='<div class="verdict '+(ok?"ok":"cold")+'">'
   +'<div class="stamp">'+stamp+'</div>'
   +(because?'<p class="vbecause"><b>'+t("becauseLab")+':</b> '+because+'</p>':'')
   +'<button class="vbtn">'+(ok?(autoReveal?t("revealNow"):"&#9656;"):(autoReveal?t("revealNow"):t("reExamine")))+'</button></div>';
  d.classList.remove("hidden");
  d.querySelector(".vbtn").onclick=function(){
    d.classList.add("hidden");
    if(ok&&onContinue) onContinue();
    else if(!ok&&autoReveal){ var c=caseById(activeCase); // 软失败到上限:直接结案揭晓
      state.cases.solved[c.id]={rating:1,wrong:caseCost.wrong,hints:caseCost.hints}; caseCost={wrong:0,hints:0}; save();
      playReveal((c.revealSeq||[]).slice(),function(){ c.id==="c7-fog"?renderFinalVerdict():exitToCasebook(); }); }
    else if(!ok){ renderBoard(); } // 重新查
  };
}
function playReveal(seq,done){
  if(!seq.length){ done&&done(); return; }
  var id=seq.shift(); sceneCtx={mode:"reveal",caseId:activeCase};
  curBeat=id; state.visited[id]=1; var _sc=sceneById(id); startAmbient(_sc?_sc.season:0); sfx("enter");
  setView("scene"); renderScene(id);
  var el=document.getElementById("scene");
  el.querySelector(".sc-prop .lab").innerHTML=(lang==="zh"?(seq.length?"继续":"结案归档"):(seq.length?"go on":"file the case"))+' &#8594;';
  el.querySelector(".sc-prop").onclick=function(){ sfx("tick"); playReveal(seq,done); };
}
```

- [ ] **Step 2: CSS(判决图章)**

```css
.verdict{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0a0807ee;z-index:30;text-align:center;padding:24px}
.stamp{font-family:Oswald,sans-serif;font-size:46px;letter-spacing:.08em;border:5px solid currentColor;padding:8px 22px;transform:rotate(-7deg);opacity:0;animation:stampin .35s forwards}
.verdict.ok .stamp{color:#3a8f4a}
.verdict.cold .stamp{color:#a3231d}
@keyframes stampin{0%{opacity:0;transform:rotate(-7deg) scale(2)}80%{opacity:1;transform:rotate(-7deg) scale(.94)}100%{opacity:1;transform:rotate(-7deg) scale(1)}}
.vbecause{color:#d9c8a4;max-width:560px;margin:20px 0;line-height:1.6}
.vbtn{background:#2a1a12;color:#e0a64e;border:1px solid #4a3a24;border-radius:5px;padding:8px 20px;cursor:pointer;font-size:15px}
```

- [ ] **Step 3: 验证** — c1 指认 Grace(对)→ 绿章 `CASE CLOSED` + because → 点继续 → 因 c1 仅 accuse+predict,predict 在揭晓前触发(下一任务);先验证 accuse-only 流程:连对/指认对后出绿章。指认错 3 次 → 红章 `COLD CASE` + "看真相"。

- [ ] **Step 4: Commit**

```bash
git add index.html && git commit -m "feat(deduction): verdict overlay (stamp + because) + step advance + solve/reveal/soft-fail"
```

---

### Task C6: 预判浮层(揭晓前 call it)

**Files:** Modify `index.html`

predict 步绑定在 `beforeScene`:该步推进时,在播 reveal/进入下一步前弹浮层。简化:把 predict 步当作"揭晓前关卡"——`solveCase` 播 `revealSeq` 时,若某 reveal 场景等于某 predict 步的 `beforeScene`,先弹预判。但更稳的做法是按 `steps` 顺序处理(predict 也是一步)。

- [ ] **Step 1: 实现 `doPredict`(predict 步到来时调用)**

```js
function doPredict(c,st){
  var d=document.getElementById("dossier");
  var opts=st.options.map(function(o,i){return '<button class="predopt" data-i="'+i+'">'+(lang==="zh"?o.labelZh:o.labelEn)+'</button>';}).join("");
  d.className=""; d.innerHTML='<div class="predict"><div class="predq">'+(lang==="zh"?st.promptZh:st.promptEn)+'</div><div class="predopts">'+opts+'</div><div class="predtag">'+t("callIt")+'</div></div>';
  d.classList.remove("hidden");
  d.querySelectorAll(".predopt").forEach(function(b){ b.onclick=function(){
    var i=+b.dataset.i, ok=(i===st.answer); recordInstinct(ok);
    b.classList.add(ok?"good":"bad");
    setTimeout(function(){ d.classList.add("hidden");
      state.cases.step++; save();
      if(state.cases.step>=c.steps.length) solveCase(c); else advanceToStepOrPredict(c);
    },650);
  };});
}
```

注意:`advanceToStepOrPredict` 已在 C5 里对 predict 分流;确保第一步若是 predict 也能触发——`openCase`(Task D1)进案后调用 `advanceToStepOrPredict(c)` 而非直接 `renderBoard()`。

- [ ] **Step 2: CSS**

```css
.predict{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0a0807ee;z-index:30;padding:24px;text-align:center}
.predq{color:#fff;font-size:19px;max-width:600px;margin-bottom:22px}
.predopts{display:flex;gap:12px;flex-wrap:wrap;justify-content:center}
.predopt{background:#241a12;color:#e0a64e;border:1px solid #6a5a3a;border-radius:6px;padding:10px 18px;cursor:pointer;font-size:15px}
.predopt.good{background:#1f3a23;color:#7fdc8f;border-color:#3a8f4a}
.predopt.bad{background:#3a1714;color:#e88;border-color:#a3231d}
.predtag{color:#9a8f7a;margin-top:18px;letter-spacing:.1em;font-size:12px}
```

- [ ] **Step 3: 验证** — c1:指认 Grace 对 → predict 步弹"谁替 Tommy 挡子弹?" → 点 Danny → 标绿、计入 instinct(`preview_console_logs`/控制台 `state.instinct`)→ 自动播 `s1-showdown` 揭晓 → 结案回案卷夹。

- [ ] **Step 4: Commit**

```bash
git add index.html && git commit -m "feat(deduction): predict overlay (call it) feeding instinct, gates the reveal"
```

---

# Phase D — 案卷夹 + 标题双入口 + 最终裁定

### Task D1: `openCase` + 进案入口

**Files:** Modify `index.html`

- [ ] **Step 1: 实现 `openCase`/`exitToCasebook`**

```js
function openCase(id){
  if(caseStatus(id)==="locked")return;
  activeCase=id; boardMode="case"; state.cases.current=id;
  // 重放时从头:已结案的重玩重置步进与计错(不影响已记成色)
  state.cases.step=0; caseLinks=[]; connTap=null; caseCost={wrong:0,hints:0}; save();
  document.getElementById("title").classList.add("hidden");
  document.getElementById("scene").classList.add("hidden");
  document.getElementById("board").classList.remove("hidden");
  view="board";
  var c=caseById(id);
  // 若首步是 predict,直接进浮层;否则渲染案板
  if(c.steps[0].kind==="predict"){ renderBoard(); advanceToStepOrPredict(c); }
  else renderBoard();
}
function exitToCasebook(){ boardMode="free"; activeCase=null; sceneCtx=null; renderCasebook(); }
```

- [ ] **Step 2: 验证** — 控制台 `openCase("c2-bullet")` → 案板正常;`openCase("c7-fog")`(前案未解)→ 无反应(locked)。

- [ ] **Step 3: Commit**

```bash
git add index.html && git commit -m "feat(deduction): openCase entry with lock gating + casebook exit"
```

---

### Task D2: 案卷夹首屏

**Files:** Modify `index.html`(新增 `renderCasebook`;新增 `#casebook` 容器到 `<body>`;`<style>`)

- [ ] **Step 1: 加容器** — 在 `<body>` 里 `#board` 旁加 `<div id="casebook" class="hidden"></div>`。

- [ ] **Step 2: 实现 `renderCasebook`**

```js
function renderCasebook(){
  var el=document.getElementById("casebook");
  document.getElementById("title").classList.add("hidden");
  document.getElementById("board").classList.add("hidden");
  document.getElementById("scene").classList.add("hidden");
  el.classList.remove("hidden");
  var inst=state.instinct.total?(" · "+t("instinctLab")+" "+state.instinct.correct+"/"+state.instinct.total):"";
  var cards=CASES.map(function(c){
    var stt=caseStatus(c.id), sv=state.cases.solved[c.id];
    var stars=sv?("★★★".slice(0,sv.rating)+"☆☆☆".slice(0,3-sv.rating)):"";
    var sub=stt==="solved"?(t("solvedLab")+" "+stars):stt==="locked"?t("lockedLab"):"";
    return '<button class="ccard '+stt+'" data-c="'+c.id+'"'+(stt==="locked"?" disabled":"")+'>'
      +'<span class="cno">'+c.no+'</span>'
      +'<span class="cttl">'+(lang==="zh"?c.titleZh:c.titleEn)+'</span>'
      +'<span class="csub">'+sub+'</span></button>';
  }).join("");
  el.innerHTML='<div class="cb-head"><button class="cb-back">&#9664; '+t("board")+'</button>'
   +'<h2>'+t("casebook")+'</h2><div class="cb-inst">'+inst.replace(/^ · /,"")+'</div></div>'
   +'<div class="cb-grid">'+cards+'</div>';
  el.querySelectorAll(".ccard:not(.locked)").forEach(function(b){ b.onclick=function(){ openCase(b.dataset.c); }; });
  el.querySelector(".cb-back").onclick=function(){ boardMode="free"; el.classList.add("hidden"); renderBoard(); document.getElementById("board").classList.remove("hidden"); };
}
```

- [ ] **Step 3: CSS**

```css
#casebook{position:fixed;inset:0;background:#14110e;overflow:auto;padding:20px;z-index:8}
.cb-head{display:flex;align-items:center;gap:16px}
.cb-head h2{font-family:Oswald,sans-serif;color:#e0a64e;letter-spacing:.06em;margin:0}
.cb-inst{color:#9a8f7a;font-size:13px;margin-left:auto}
.cb-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin-top:18px}
.ccard{display:flex;flex-direction:column;gap:6px;text-align:left;background:#1e1812;border:1px solid #3a2c1c;border-radius:8px;padding:14px;cursor:pointer;color:#d9c8a4}
.ccard.current{border-color:#caa64a;box-shadow:0 0 0 1px #caa64a55}
.ccard.solved{opacity:.82}
.ccard.locked{opacity:.4;cursor:not-allowed}
.cno{font-family:Special Elite,monospace;color:#c2592a;font-size:13px}
.cttl{font-size:17px;color:#fff}
.csub{font-size:12px;color:#caa64a}
.cb-back{background:#241a12;color:#caa64a;border:1px solid #4a3a24;border-radius:4px;padding:4px 12px;cursor:pointer}
```

- [ ] **Step 4: 验证** — 控制台 `renderCasebook()` → `preview_snapshot`:7 张卡,c1=current、c2–c7=locked。`preview_click` c1 → 进案板。`preview_resize`(窄屏)→ 网格回流单列。

- [ ] **Step 5: Commit**

```bash
git add index.html && git commit -m "feat(deduction): casebook index screen (status, stars, instinct)"
```

---

### Task D3: 标题双入口 + 最终裁定屏

**Files:** Modify `index.html`(`renderTitle` 约 833 行;新增 `renderFinalVerdict`)

- [ ] **Step 1: 改 `renderTitle` 的按钮区**

把原来的单一 `.t-start`(进板)改为两入口 + resume 路由:

```js
 var resume=state.cases.current? '<button class="t-resume">'+t("resume")+' &#8250;</button>':'';
 el.innerHTML='<div class="t-bg">'+SVG_COVER()+'</div><div class="t-fg"><h1 class="t-h">浴血黑帮 · 卷宗</h1><div class="t-sub">'+t("subtitle")+'</div>'
  +'<button class="t-start">'+t("investigate")+' &#9656;</button>'
  +'<button class="t-free">'+t("freeBrowse")+'</button>'+resume
  +'<div class="lang" style="margin-top:22px">...(原样)...</div></div>';
 el.querySelector(".t-start").onclick=function(){ renderCasebook(); };
 el.querySelector(".t-free").onclick=function(){ boardMode="free"; enterBoard(); };
 var rb=el.querySelector(".t-resume"); if(rb)rb.onclick=function(){ openCase(state.cases.current); };
```

(`.t-free` 复用 `.t-resume` 样式即可。)

- [ ] **Step 2: 实现 `renderFinalVerdict`(案7结后)**

```js
function renderFinalVerdict(){
  var el=document.getElementById("casebook");
  document.getElementById("scene").classList.add("hidden");
  el.classList.remove("hidden");
  var solved=Object.keys(state.cases.solved).length;
  var totRating=CASES.reduce(function(a,c){var s=state.cases.solved[c.id];return a+(s?s.rating:0);},0);
  var line=lang==="zh"?"卷宗已满,指控却终未落槌。Tommy Shelby——那个不朽之人——骑马遁入晨雾,逍遥法外。":"The file is full, yet the charge never lands. Tommy Shelby — the Immortal Man — rides into the mist, and walks free.";
  el.innerHTML='<div class="final"><h2>'+t("finalVerdict")+'</h2>'
   +'<div class="final-stats">'+solved+'/7 · ★ '+totRating+'/21 · '+t("instinctLab")+' '+state.instinct.correct+'/'+state.instinct.total+'</div>'
   +'<p class="final-line">'+line+'</p>'
   +'<button class="vbtn" id="final-done">'+t("casebook")+'</button></div>';
  el.querySelector("#final-done").onclick=function(){ renderCasebook(); };
}
```

CSS:

```css
.final{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0a0807;z-index:30;text-align:center;padding:24px}
.final h2{font-family:Oswald,sans-serif;color:#e0a64e;letter-spacing:.05em}
.final-stats{color:#caa64a;font-family:Special Elite,monospace;margin:10px 0 20px}
.final-line{color:#d9c8a4;max-width:600px;line-height:1.8;font-style:italic}
```

- [ ] **Step 3: 验证** — `preview`:标题屏出现"开始查案 / 自由浏览";点"自由浏览"→ 现有透镜板照常(回归测试:点暗线/季/人物仍工作)。点"开始查案"→ 案卷夹。控制台造 c7 结案 → `renderFinalVerdict()` 出裁定屏。

- [ ] **Step 4: Commit**

```bash
git add index.html && git commit -m "feat(deduction): title two-entry (investigate/free) + resume + final verdict screen"
```

---

# Phase E — 音效 / 提示 / a11y / i18n刷新 / 移动端 / 文档

### Task E1: 新增 4 个音效

**Files:** Modify `index.html`(`sfx()` 约 504 行 `else` 前)

- [ ] **Step 1: 在 `sfx()` 末尾 `else` 之前插入**

```js
 else if(kind==="stamp"){ noise(0.09,0.5,500); tone(150,0.14,"square",0.28,90); }
 else if(kind==="buzz"){ tone(120,0.22,"sawtooth",0.22,80); }
 else if(kind==="pluck"){ tone(520,0.16,"triangle",0.2,360); }
 else if(kind==="tick"){ tone(880,0.05,"square",0.1); }
```

- [ ] **Step 2: 验证(需用户耳朵)** — 取消静音,触发指认对(stamp)、错(buzz)、连线(pluck)、翻页(tick)。**注:音色方向需用户亲耳反馈**(我无法自测音频),先确保不报错、能发声。

- [ ] **Step 3: Commit**

```bash
git add index.html && git commit -m "feat(deduction): sfx for stamp/buzz/pluck/tick"
```

---

### Task E2: 提示(Campbell's hunch)

**Files:** Modify `index.html`

- [ ] **Step 1: 实现 `useHunch`**

```js
function useHunch(){
  var c=caseById(activeCase), st=c.steps[state.cases.step]; if(!st)return;
  caseCost.hints++;
  if(st.kind==="accuse"){
    // 排除一个错误嫌疑:压暗一个非答案图钉
    var wrong=st.suspects.filter(function(p){return p!==st.answer;});
    var victim=wrong[0]; var d=document.querySelector('.pin[data-pin="'+victim+'"]'); if(d){d.classList.add("dim");d.onclick=null;}
    // 从 suspects 临时移除,避免再排同一个
    st.suspects=st.suspects.filter(function(p){return p!==victim;});
  } else if(st.kind==="connect"){
    // 高亮下一跳的起点
    var next=st.links[caseLinks.length]; if(next) markPinSelected(next[0],true);
  }
  sfx("tick");
}
```

(accuse 排除会修改 `st.suspects`——为避免污染数据,改为维护一个 `state` 外的运行期排除集;最简实现:进案时 `c=JSON.parse(JSON.stringify(caseById(id)))` 深拷贝到 `activeCaseData`,所有读取走 `activeCaseData`。在 `openCase` 里加 `activeCaseData=JSON.parse(JSON.stringify(caseById(id)));`,并把 `renderCaseBoard/onCasePinTap/doAccuse/doConnectTap/doPredict/afterStepCorrect` 内的 `caseById(activeCase)` 换成 `activeCaseData`。)

- [ ] **Step 2: 验证** — 案板点"督察的直觉"→ accuse 案压暗一个错误嫌疑;connect 案高亮下一跳起点;成色相应 -1(结案后看星)。

- [ ] **Step 3: Commit**

```bash
git add index.html && git commit -m "feat(deduction): Campbell's hunch hint (eliminate suspect / light next link) at rating cost"
```

---

### Task E3: a11y(键盘 + reduced-motion)

**Files:** Modify `index.html`(`<style>` + 关键按钮/图钉)

- [ ] **Step 1: 键盘可达** — 给 case 态可点图钉加 `tabindex="0"` 与 Enter 触发:在 `paintCasePins` 里 `if(active[p.id]){ d.tabIndex=0; d.setAttribute("role","button"); d.onkeydown=function(e){ if(e.key==="Enter"||e.key===" "){e.preventDefault();onCasePinTap(p.id);} }; }`。浮层按钮本就是 `<button>`,天然可达。

- [ ] **Step 2: reduced-motion** — `<style>` 末尾:

```css
@media (prefers-reduced-motion:reduce){ .caseline{animation:none;stroke-dashoffset:0} .stamp{animation:none;opacity:1} .pin.wrong{animation:none} }
```

- [ ] **Step 3: 验证** — `preview`:Tab 聚焦嫌疑图钉、Enter 指认;模拟 reduced-motion(`preview_eval` 注入 matchMedia 或在系统设置)确认无动画但功能在。

- [ ] **Step 4: Commit**

```bash
git add index.html && git commit -m "a11y(deduction): keyboard accuse/connect + reduced-motion for new animations"
```

---

### Task E4: i18n 全量刷新(切语言重建 case UI)

**Files:** Modify `index.html`(`setLang` 约 647 行)

现有 `setLang` 只 `renderBoard()`。需让其按当前所在屏重建。

- [ ] **Step 1: 改 `setLang`**

```js
function setLang(l){ lang=l; state.lang=l; save();
  if(!document.getElementById("casebook").classList.contains("hidden")) renderCasebook();
  else if(view==="scene"&&sceneCtx) renderScene(curBeat);
  else renderBoard();
}
```

- [ ] **Step 2: 验证** — 在案卷夹/案板/场景三处分别切 EN/中,文案与按钮全切换、无残留中文/英文;`__selftest()` 仍 `"PASS"`。

- [ ] **Step 3: Commit**

```bash
git add index.html && git commit -m "i18n(deduction): setLang rebuilds casebook/scene/board in place"
```

---

### Task E5: 移动端

**Files:** Modify `index.html`(`<style>` 媒体查询)

- [ ] **Step 1: 加响应式**

```css
@media (max-width:560px){
  .case-title{font-size:14px}.case-brief{font-size:12px}.case-prompt{font-size:13px}
  .casehead{padding:8px 10px}
  .cb-grid{grid-template-columns:1fr 1fr}
  .stamp{font-size:34px}.predq{font-size:16px}
  .predopt{padding:9px 14px;font-size:14px}
}
```

- [ ] **Step 2: 验证** — `preview_resize` 至 ~380px:案头不溢出、案卷夹两列、判决/预判浮层可读、图钉可点。

- [ ] **Step 3: Commit**

```bash
git add index.html && git commit -m "responsive(deduction): mobile layout for case header/casebook/overlays"
```

---

### Task E6: 文档 + 全量回归

**Files:** Modify `README.md`;Modify `index.html`(若回归发现问题)

- [ ] **Step 1: 更新 README** — 在"怎么玩"加推理循环说明(开始查案 → 看线索 → 板上连线/指认 → 判决 → 揭晓);"一眼亮点"加"🕵️ 真·查案:板子是答题面,不是菜单";路线图勾上"P7 推理玩法"。保留"双击即开/单文件/零依赖"卖点不变。

- [ ] **Step 2: 全量回归(浏览器)**
- `__selftest()` === `"PASS"`。
- **完整通关一遍** c1→c7:每案能查证、连对/指认对出绿章、错出红章可重查、predict 计入 instinct、结案回案卷夹、暗线随结案点亮、案7后出最终裁定屏。
- **自由浏览回归**:标题→自由浏览→暗线/季/人物筛选、家族树/势力图、RESUME 仍正常(未被 case 改动破坏)。
- 中/EN 全程切换正常;移动端尺寸正常;静音持久化正常。

- [ ] **Step 3: Commit**

```bash
git add README.md index.html && git commit -m "docs(deduction): README gameplay update + full regression pass"
```

---

## Self-Review(写完计划后对照 spec 自查 — 已执行)

**1. Spec coverage**:§2 框架→Task D3 文案/最终裁定;§3 核心机制(查证/连线/指认/判决/揭晓)→C2–C6;§3.3 不剧透批注→A3 的 `clue*` 字段;§4 七案→A3 全量 + C/D 引擎;§5 评分容错(成色/直觉/软失败/提示/汇总)→B2、C5、C6、E2、D3;§6 自由浏览常开→C1 的 `boardMode` 分流 + D3 双入口;§7 数据模型→A2/A3;§8 重构映射(单文件/分区/selftest)→全程 + A1–A3 selftest;§9 美术音频→C3/C4/C5 CSS + E1;§10 i18n→C1/E4;§11 YAGNI→未引入分支/拖拽/联机。**无遗漏。**

**2. Placeholder scan**:占位函数(`paintCasePins/afterStepCorrect/verdictOverlay/useHunch` 等)均在后续任务给出完整实现;无 TODO/TBD 残留。C5 引用的 `renderFinalVerdict` 在 D3 实现、`doPredict` 在 C6 实现——顺序上 C5 先放空壳、后填,已在步骤注明。

**3. Type consistency**:`state.cases.{solved,current,step,examined,connected}`、`caseCost.{wrong,hints}`、`activeCase`(id)/`activeCaseData`(深拷贝对象,E2 起启用)、`boardMode('free'|'case')`、`sceneCtx.{mode,caseId}` 全程一致;函数名 `caseById/caseStatus/openCase/exitToCasebook/renderCasebook/renderCaseBoard/paintCasePins/onCasePinTap/doAccuse/doConnectTap/doPredict/afterStepCorrect/solveCase/verdictOverlay/playReveal/threadLit/ratingFromCost/recordInstinct/useHunch/renderFinalVerdict` 前后一致。

> 注:`activeCase`(字符串 id)与 `activeCaseData`(深拷贝)并存——E2 引入深拷贝后,**C 阶段中所有 `caseById(activeCase)` 读取应统一改为 `activeCaseData`**(E2 Step 1 已说明)。执行 C 阶段时可先用 `caseById(activeCase)`,到 E2 一次性替换;或 D1 起即引入 `activeCaseData` 以免返工(推荐后者)。

---

## Execution Handoff

计划完成,存于 `docs/2026-06-22-peaky-dossier-deduction-plan.md`。两种执行方式择一。
