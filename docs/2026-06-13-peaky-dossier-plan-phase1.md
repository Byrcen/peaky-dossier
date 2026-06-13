# 浴血黑帮卷宗 — 实现计划 Phase 1:数据驱动的双视图引擎

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭出一个能跑通的垂直切片——按下 PRESS START → 卷宗红线板 → 按暗线筛选 → 点人物/事件翻开卷宗卡 → 进入满屏电影场景逐屏运镜 → 返回板子;全程中英双语、状态持久化。用 5 个样板 beat 打通整条链路。

**Architecture:** 单文件 `index.html`,零依赖,双击即开。内容三数组(`SCENES`/`CHARACTERS`/`THREADS`)+ 板面布局 `BOARD_PINS` 把内容与展示解耦。顶层 `view` 状态在 `BOARD`(导航)与 `SCENE`(沉浸)两个视图间切换。纯逻辑函数(i18n、筛选、排序、持久化、数据完整性)与渲染分离,可独立断言测试。

**Tech Stack:** 原生 HTML/CSS/JS(ES5+,无构建无框架),内联 SVG 像素场景,localStorage,`prefers-reduced-motion`。验证用 Claude 预览器(`preview_*` 工具)。

---

## 测试方式(本项目适配)

零依赖单文件不引入测试框架(违背"双击即开")。改为:

- **纯逻辑**:在 `index.html` 内写一个 `__selftest()` 函数,用 `console.assert` 做断言;**先写断言(失败)→ 再实现 → 断言通过**。开发期保留,Phase 5 可剥离。通过 `preview_eval` 执行 `__selftest()` 读返回值验证。
- **视觉/交互**:用预览器 `preview_start` / `preview_eval`(reload)/ `preview_console_logs`(查 0 报错)/ `preview_snapshot`(查结构)/ `preview_click`(点交互)/ `preview_screenshot`(留证)验证。
- **每个 Task 末尾**:验证通过后 `git commit`。

---

## 文件结构

Phase 1 全部落在单文件 + 一个启动配置:

- 创建 `index.html` — 唯一产物。内部分区(按出现顺序,利于流式与定位):
  1. `<head>`:meta / 字体 link / 内联 `<style>`(变量 + 板面 + 场景 + 卷宗卡 + 标题屏)
  2. `<body>`:`#title`(PRESS START)、`#board`(红线板)、`#scene`(电影场景)、`#dossier`(卷宗卡)骨架
  3. `<script>`:① 数据(`SCENES/CHARACTERS/THREADS/FACTIONS/BOARD_PINS`、`T` i18n 字典)② 纯逻辑(`t/save/load/beatsInOrder/threadOrder/pinsForThread/__selftest`)③ 渲染(`renderBoard/renderStrings/openDossier/renderScene/setView/applyLang`)④ 启动 `boot()`
- 创建 `.claude/launch.json` — 本地预览配置(端口 4790)。
- 数据职责:`SCENES`=剧情 beat(含场景 tableau SVG);`CHARACTERS`=人物(立绘 + 简介);`THREADS`=暗线(板上红线 `pinIds` + 场景顺看 `beatIds`);`BOARD_PINS`=板面"钉了什么、钉在哪"(坐标/旋转/图钉色)。

**Phase 1 只放 5 个样板 beat**(序幕、S1 失窃机枪、S3 Grace 之死、S6 Ruby 之死、S6 烈火重生)+ 1 条暗线(蓝宝石诅咒,连 Grace↔Ruby,板上可见跨季红线)。其余 30 beat、其余暗线、名册/世系树、音频、打磨、og 卡 → **Phase 2–6 各自独立计划**(见文末)。

---

## Task 0:项目骨架 + 启动配置

**Files:**
- Create: `/Users/cry/Desktop/peaky-dossier/index.html`
- Create: `/Users/cry/Desktop/peaky-dossier/.claude/launch.json`

- [ ] **Step 1: 写最小可开的 index.html**

```html
<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>浴血黑帮 · 卷宗 / Peaky Blinders Dossier</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Special+Elite&family=Oswald:wght@500;600&family=Playfair+Display:wght@600;700&display=swap">
<style>
:root{--soot:#14110e;--board:#221c16;--frame:#34281c;--paper:#ece0c0;--ink:#2a2017;--ember:#c2592a;--amber:#e0a64e;--blood:#a3231d;--fog:#7d8287;--string:#7a342b;--brass:#c2922f;--manila:#dac8a0;--serif:Georgia,'Times New Roman',serif;--type:'Special Elite',Courier,monospace;--disp:'Playfair Display',Georgia,serif;--stencil:'Oswald',sans-serif}
*{box-sizing:border-box}
html,body{margin:0;background:#0c0a08;color:#e9dcc3;font-family:var(--serif)}
#app{max-width:1100px;margin:0 auto;position:relative}
.hidden{display:none!important}
</style>
</head>
<body>
<div id="app">
  <section id="title"></section>
  <section id="board" class="hidden"></section>
  <section id="scene" class="hidden"></section>
  <div id="dossier" class="hidden"></div>
</div>
<script>
"use strict";
/* === 数据 === */ /* (Task 1–2) */
/* === 纯逻辑 === */ /* (Task 2,3,8) */
/* === 渲染 === */ /* (Task 4–7,9) */
function boot(){ console.log("peaky-dossier boot ok"); }
boot();
</script>
</body>
</html>
```

- [ ] **Step 2: 写 launch.json**

```json
{
  "configurations": [
    { "name": "peaky", "type": "static", "port": 4790, "root": "." }
  ]
}
```

- [ ] **Step 3: 起预览验证空壳能开、无报错**

用 `preview_start`(root 指向 `/Users/cry/Desktop/peaky-dossier`,port 4790),然后 `preview_console_logs`。
Expected:控制台出现 `peaky-dossier boot ok`,无红色报错。

- [ ] **Step 4: 初始化仓库并提交**

```bash
cd /Users/cry/Desktop/peaky-dossier && git init && git add -A && git commit -m "chore: scaffold peaky-dossier single-file shell"
```

---

## Task 1:数据模型 + 种子内容 + 完整性自检(test-first)

**Files:**
- Modify: `index.html`(在 `/* === 数据 === */` 处插入数据;在 `/* === 纯逻辑 === */` 处插入 `__selftest`)

- [ ] **Step 1: 先写完整性断言(应当失败,因数据尚未定义)**

在纯逻辑区插入:

```js
function __selftest(){
  var fails=[];
  function ok(c,m){ if(!c){ fails.push(m); console.assert(c,m);} }
  // 数据存在
  ok(Array.isArray(SCENES)&&SCENES.length>=5,"SCENES 至少 5 条");
  ok(Array.isArray(CHARACTERS)&&CHARACTERS.length>=5,"CHARACTERS 至少 5 条");
  ok(Array.isArray(THREADS)&&THREADS.length>=1,"THREADS 至少 1 条");
  ok(Array.isArray(BOARD_PINS)&&BOARD_PINS.length>=5,"BOARD_PINS 至少 5 条");
  // id 唯一
  var sids={}; SCENES.forEach(function(s){ok(!sids[s.id],"SCENE id 重复:"+s.id);sids[s.id]=1;});
  var cids={}; CHARACTERS.forEach(function(c){ok(!cids[c.id],"CHAR id 重复:"+c.id);cids[c.id]=1;});
  // 引用完整:scene.cast 指向真人物
  SCENES.forEach(function(s){(s.cast||[]).forEach(function(id){ok(cids[id],"scene "+s.id+" 引用了不存在的人物 "+id);});});
  // 引用完整:thread.beatIds / pinIds 指向真 scene / pin
  var pids={}; BOARD_PINS.forEach(function(p){pids[p.id]=1;});
  THREADS.forEach(function(t){
    (t.beatIds||[]).forEach(function(id){ok(sids[id],"thread "+t.id+" beatId 无效:"+id);});
    (t.pinIds||[]).forEach(function(id){ok(pids[id],"thread "+t.id+" pinId 无效:"+id);});
  });
  // 引用完整:pin.ref 指向真 scene 或 char
  BOARD_PINS.forEach(function(p){
    if(p.kind==="photo") ok(cids[p.ref],"pin "+p.id+" ref 人物无效:"+p.ref);
    else ok(sids[p.ref],"pin "+p.id+" ref 场景无效:"+p.ref);
  });
  // 双语字段齐全
  SCENES.forEach(function(s){ok(s.titleZh&&s.titleEn&&s.taleZh&&s.taleEn,"scene "+s.id+" 双语字段缺失");});
  return fails.length? ("FAIL("+fails.length+"): "+fails.join(" | ")) : "PASS";
}
```

- [ ] **Step 2: 运行断言确认失败**

`preview_eval` 执行:`typeof SCENES`
Expected:`"undefined"`(数据未定义,`__selftest` 会抛 ReferenceError)。

- [ ] **Step 3: 在数据区写入种子数据**

在 `/* === 数据 === */` 处插入(SVG 场景沿用已验证的概念稿配色):

```js
var FACTIONS=[
 {id:"peaky",nameZh:"浴血黑帮",nameEn:"Peaky Blinders",color:"#caa64a"},
 {id:"crown",nameZh:"王权/警方",nameEn:"Crown & Police",color:"#37475c"},
 {id:"curse",nameZh:"诅咒/吉普赛",nameEn:"Romani / curse",color:"#3e8bd0"}
];
var CHARACTERS=[
 {id:"tommy",nameZh:"汤米·谢尔比",nameEn:"Tommy Shelby",faction:"peaky",seasons:[1,2,3,4,5,6],portrait:"flatcap",
  roleZh:"帮派首脑",roleEn:"Gang leader",bioZh:"战壕归来的谢尔比家掌舵人,帽檐藏刀片。",bioEn:"Razor-capped head of the Shelby family, back from the trenches."},
 {id:"grace",nameZh:"格蕾丝",nameEn:"Grace Shelby",faction:"crown",seasons:[1,2,3],portrait:"woman",
  roleZh:"卧底→挚爱",roleEn:"Informant turned wife",bioZh:"Garrison 的卧底歌女,后成汤米之妻。",bioEn:"The Garrison's undercover singer, later Tommy's wife."},
 {id:"ruby",nameZh:"鲁比",nameEn:"Ruby Shelby",faction:"peaky",seasons:[6],portrait:"child",
  roleZh:"汤米之女",roleEn:"Tommy's daughter",bioZh:"汤米与莉齐的女儿,诅咒的应验者。",bioEn:"Tommy and Lizzie's daughter; where the curse comes due."},
 {id:"polly",nameZh:"波莉",nameEn:"Polly Gray",faction:"peaky",seasons:[1,2,3,4,5],portrait:"woman",
  roleZh:"家族女家长",roleEn:"Matriarch & treasurer",bioZh:"谢尔比家的女家长与账房,Elizabeth Gray。",bioEn:"The family's matriarch and treasurer, Elizabeth Gray."},
 {id:"campbell",nameZh:"坎贝尔督察",nameEn:"Insp. Campbell",faction:"crown",seasons:[1,2],portrait:"police",
  roleZh:"北爱督察",roleEn:"Ulster detective",bioZh:"丘吉尔从贝尔法斯特调来的督察,汤米首个宿敌。",bioEn:"Churchill's detective from Belfast; Tommy's first adversary."}
];
var SCENES=[
 {id:"prologue",season:0,no:"00",year:"1919",titleZh:"凭浴血黑帮之名",titleEn:"By order of the Peaky Blinders",
  taleZh:"战后的小希思,煤烟与马蹄。汤米从战壕归来,帽檐缝着剃刀,眼里是一整座城市的野心。",
  taleEn:"Post-war Small Heath — smoke and hooves. Tommy rides back from the trenches with razors in his cap and a whole city in his eyes.",
  cast:["tommy","polly"],threads:[],art:SVG_PROLOGUE()},
 {id:"s1-guns",season:1,no:"01",year:"1919",titleZh:"失窃的机枪",titleEn:"The stolen guns",
  taleZh:"一只本不该拿的板条箱。运往利比亚的 Lewis 机枪落进帮派手里,惊动了丘吉尔。",
  taleEn:"One crate they were never meant to take. A consignment of Lewis guns bound for Libya falls into gang hands — and reaches Churchill's desk.",
  cast:["tommy","campbell"],threads:[],art:SVG_GUNS()},
 {id:"s3-grace",season:3,no:"15",year:"1924",titleZh:"慈善晚宴的子弹",titleEn:"The bullet at the gala",
  taleZh:"『For Angel!』枪声响起。射向汤米的子弹,击中了格蕾丝。她正戴着那条被诅咒的蓝宝石。",
  taleEn:"'For Angel!' — a single shot. The bullet meant for Tommy finds Grace instead. She is wearing the cursed sapphire.",
  cast:["tommy","grace"],threads:["sapphire"],art:SVG_GRACE()},
 {id:"s6-ruby",season:6,no:"33",year:"1933",titleZh:"鲁比之死",titleEn:"Ruby's death",
  taleZh:"诅咒应验。汤米的女儿鲁比染肺结核夭折;悲恸之下他血洗了下诅咒的营地。",
  taleEn:"The curse comes due. Tommy's daughter Ruby dies of consumption; in grief he massacres the camp that cursed her.",
  cast:["tommy","ruby"],threads:["sapphire"],art:SVG_RUBY()},
 {id:"s6-finale",season:6,no:"35",year:"1934",titleZh:"烈火与重生",titleEn:"Fire and rebirth",
  taleZh:"他识破了假死的诅咒。火烧 Arrow House,骑上白马遁入晨雾——汤米·谢尔比还活着。",
  taleEn:"He sees through the lie of his own death. Arrow House burns; he rides a white horse into the mist — Tommy Shelby is still alive.",
  cast:["tommy"],threads:[],art:SVG_FINALE()}
];
var THREADS=[
 {id:"sapphire",nameZh:"被诅咒的蓝宝石",nameEn:"The cursed sapphire",color:"#3e8bd0",
  pinIds:["pin-grace","pin-ruby"],beatIds:["s3-grace","s6-ruby"],
  noteZh:"格蕾丝的项链辗转克死七岁的康妮,诅咒应验在鲁比身上。",noteEn:"Grace's necklace kills seven-year-old Connie, and the curse comes due on Ruby."}
];
var BOARD_PINS=[
 {id:"pin-tommy",kind:"photo",ref:"tommy",x:50,y:46,rot:-2,tack:"#c0352a"},
 {id:"pin-grace",kind:"photo",ref:"grace",x:26,y:24,rot:3,tack:"#d9cdb0"},
 {id:"pin-polly",kind:"photo",ref:"polly",x:16,y:62,rot:-3,tack:"#b8862b"},
 {id:"pin-campbell",kind:"photo",ref:"campbell",x:14,y:28,rot:2,tack:"#37475c"},
 {id:"pin-ruby",kind:"photo",ref:"ruby",x:76,y:72,rot:-2,tack:"#cf6b86"},
 {id:"pin-guns",kind:"event",ref:"s1-guns",x:74,y:30,rot:2,tack:"#2c2c2c"},
 {id:"pin-finale",kind:"event",ref:"s6-finale",x:86,y:58,rot:-3,tack:"#c2592a"}
];
```

- [ ] **Step 4: 写场景 SVG 工厂(种子 tableau,沿用概念稿)**

在数据区上方插入 5 个返回 SVG 字符串的函数 `SVG_PROLOGUE/SVG_GUNS/SVG_GRACE/SVG_RUBY/SVG_FINALE`。直接复用本仓库概念稿 `peaky_scrollytelling_concept_a` 中对应场景的 `<svg viewBox="0 0 680 560" preserveAspectRatio="xMidYMid slice">…</svg>` 字符串(序幕=工业黎明、guns=仓库板条箱、grace=晚宴红溅、ruby≈雾中田野改作病房冷调、finale=火烧庄园+白马)。每个函数 `return` 该字符串。
> 注:`SVG_RUBY` 暂以"雾中田野"占位场景代用,Phase 5 再画病房专属 tableau。

- [ ] **Step 5: 运行完整性自检,确认 PASS**

`preview_eval`(先 reload)执行:`__selftest()`
Expected:返回 `"PASS"`。

- [ ] **Step 6: 提交**

```bash
cd /Users/cry/Desktop/peaky-dossier && git add -A && git commit -m "feat: seed data model (5 scenes, 5 chars, sapphire thread) + integrity selftest"
```

---

## Task 2:i18n 核心(test-first)

**Files:**
- Modify: `index.html`(数据区加 `T`;纯逻辑区加 `lang`/`t`;`__selftest` 加断言)

- [ ] **Step 1: 在 `__selftest` 末尾(`return` 前)加 i18n 断言**

```js
  ok(t("start")!=="start"&&t("start").length>0,"t(start) 应返回译文");
  lang="en"; ok(t("start")==="Press start","英文 t(start) 应为 Press start");
  lang="zh"; ok(t("nope_key")==="nope_key","缺失 key 应回退为 key 本身");
```

- [ ] **Step 2: 运行,确认失败**

`preview_eval`:`__selftest()`
Expected:返回包含 `t(start)` 的 `FAIL(...)`。

- [ ] **Step 3: 实现 T 字典与 t()**

数据区加:

```js
var T={
 start:{zh:"按下开始",en:"Press start"},
 subtitle:{zh:"谢尔比家二十年 · 六季全剧情",en:"Twenty years of the Shelbys · all six series"},
 board:{zh:"卷宗",en:"The board"},
 allThreads:{zh:"全部线索",en:"All threads"},
 openScene:{zh:"翻开场景",en:"Open the scene"},
 backBoard:{zh:"返回红线板",en:"Back to the board"},
 caseFile:{zh:"案卷",en:"Case file"},
 prev:{zh:"上一幕",en:"Previous"},
 next:{zh:"下一幕",en:"Next"},
 appears:{zh:"出场",en:"Appears"},
 resume:{zh:"继续上次",en:"Resume"}
};
```

纯逻辑区加:

```js
var lang="zh";
function t(k){ var e=T[k]; return e? (e[lang]||e.zh) : k; }
```

- [ ] **Step 4: 运行,确认 PASS**

`preview_eval`:`(function(){lang="zh";return __selftest();})()`
Expected:`"PASS"`。

- [ ] **Step 5: 提交**

```bash
cd /Users/cry/Desktop/peaky-dossier && git add -A && git commit -m "feat: i18n core (T dict + t() with key fallback)"
```

---

## Task 3:状态持久化 + RESUME(test-first)

**Files:**
- Modify: `index.html`(纯逻辑区加 `state`/`save`/`load`;`__selftest` 加断言)

- [ ] **Step 1: 加持久化断言**

```js
  state.lastBeat="s3-grace"; state.lang="en"; save();
  state.lastBeat=null; state.lang="zh"; load();
  ok(state.lastBeat==="s3-grace","load 应恢复 lastBeat");
  ok(state.lang==="en","load 应恢复 lang");
  localStorage.removeItem("pbd"); // 清理测试副作用
```

- [ ] **Step 2: 运行,确认失败**

`preview_eval`:`__selftest()`
Expected:`FAIL` 含 "load 应恢复 lastBeat"(`state`/`save`/`load` 未定义会先 ReferenceError —— 若如此,Step 3 后再测)。

- [ ] **Step 3: 实现 state/save/load**

```js
var state={lang:"zh",muted:false,lastBeat:null,lastThread:"all",visited:{}};
function save(){ try{ localStorage.setItem("pbd",JSON.stringify(state)); }catch(e){} }
function load(){ try{ var r=localStorage.getItem("pbd"); if(r){ var o=JSON.parse(r); for(var k in o) state[k]=o[k]; lang=state.lang; } }catch(e){} }
```

- [ ] **Step 4: 运行,确认 PASS**

`preview_eval`:`__selftest()`
Expected:`"PASS"`。

- [ ] **Step 5: 提交**

```bash
cd /Users/cry/Desktop/peaky-dossier && git add -A && git commit -m "feat: localStorage state (lang/mute/lastBeat/visited) + selftest"
```

---

## Task 4:卷宗红线板渲染 + 暗线筛选

**Files:**
- Modify: `index.html`(`<style>` 加板面样式;渲染区加 `renderBoard`/`renderStrings`/`pinsForThread`;`boot` 调 `renderBoard`)

- [ ] **Step 1: 加板面 CSS**

在 `<style>` 末尾插入(沿用概念稿 `peaky_dossier_redstring_concept_c`):

```css
#board{padding:0}
.cb{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;padding:8px 10px;background:#17120d;border:1px solid var(--frame);border-bottom:none;border-radius:10px 10px 0 0}
.threads{display:flex;flex-wrap:wrap;gap:6px}
.thb{font-family:var(--stencil);font-size:12px;color:#cdbfa3;background:#241b12;border:1px solid #4a3a28;border-radius:6px;padding:5px 9px;cursor:pointer;display:flex;align-items:center;gap:6px}
.thb.active{color:#1a130c;background:var(--brass);border-color:var(--brass)}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block}
.lang{display:flex;border:1px solid #4a3a28;border-radius:6px;overflow:hidden}
.lang button{font-family:var(--serif);font-size:12px;color:#cdbfa3;background:#241b12;border:none;padding:5px 11px;cursor:pointer}
.lang button.active{background:var(--brass);color:#1a130c}
.bwrap{position:relative;height:520px;background:var(--board);border:1px solid var(--frame);border-radius:0 0 10px 10px;overflow:hidden}
.bframe{position:absolute;inset:7px;border:2px solid var(--frame);border-radius:4px;pointer-events:none}
svg.strings{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1}
.pin{position:absolute;cursor:pointer;transition:opacity .25s;z-index:2}
.pin.dim{opacity:.15}.pin.act .frame,.pin.act .card{outline:2px solid #e3bb50;outline-offset:1px}
.tack{position:absolute;top:-6px;left:50%;transform:translateX(-50%);width:13px;height:13px;border-radius:50%;border:2px solid rgba(0,0,0,.4);z-index:4}
.photo .frame{width:86px;background:var(--paper);padding:5px 5px 0;border:1px solid #b6a47a}
.photo svg{display:block;width:86px;height:84px}
.cap{font-family:var(--type);font-size:11px;color:#2b2117;text-align:center;padding:3px 2px 4px;line-height:1.15}
.event .card{width:150px;background:#ded8c6;border:1px solid #b4ab90;padding:6px 8px;color:#1d1a12}
.ev-k{font-family:var(--stencil);font-size:10px;letter-spacing:1px;color:#7c1f17}
.ev-h{font-family:var(--disp);font-weight:700;font-size:13px;line-height:1.15;margin:2px 0}
```

- [ ] **Step 2: 加像素立绘工厂(沿用概念稿 `fig`)**

渲染区加 `function fig(type){…}`,直接复用概念稿 `peaky_dossier_redstring_concept_c` 的 `fig`(返回 flatcap/woman/police/fedora/child 的 SVG 内层 markup)。

- [ ] **Step 3: 实现 renderBoard / pinsForThread / renderStrings**

```js
var THC={family:"#6e3b34",sapphire:"#3e8bd0"};
function charById(id){for(var i=0;i<CHARACTERS.length;i++)if(CHARACTERS[i].id===id)return CHARACTERS[i];}
function sceneById(id){for(var i=0;i<SCENES.length;i++)if(SCENES[i].id===id)return SCENES[i];}
function pinById(id){for(var i=0;i<BOARD_PINS.length;i++)if(BOARD_PINS[i].id===id)return BOARD_PINS[i];}
function pinsForThread(thId){ // 返回该暗线相关 pin id 的 map;all 时全 true
 var m={}; if(thId==="all"){BOARD_PINS.forEach(function(p){m[p.id]=1;});return m;}
 var th=THREADS.filter(function(x){return x.id===thId;})[0];
 (th?th.pinIds:[]).forEach(function(id){m[id]=1;}); return m;
}
function pinInner(p){
 if(p.kind==="photo"){var c=charById(p.ref);
  return '<div class="frame"><svg viewBox="0 0 86 84"><rect width="86" height="84" fill="#d3c099"/>'+fig(c.portrait)+'</svg><div class="cap">'+(lang==="zh"?c.nameZh:c.nameEn)+'</div></div>';}
 var s=sceneById(p.ref);
 return '<div class="card"><div class="ev-k">'+(lang==="zh"?s.year:s.year)+' · '+t("caseFile")+' '+s.no+'</div><div class="ev-h">'+(lang==="zh"?s.titleZh:s.titleEn)+'</div></div>';
}
function renderBoard(){
 var el=document.getElementById("board");
 var thbtns='<button class="thb" data-th="all">'+t("allThreads")+'</button>'+THREADS.map(function(th){
  return '<button class="thb" data-th="'+th.id+'"><span class="dot" style="background:'+th.color+'"></span>'+(lang==="zh"?th.nameZh:th.nameEn)+'</button>';
 }).join("");
 el.innerHTML='<div class="cb"><div class="threads">'+thbtns+'</div>'
  +'<div class="lang"><button data-l="zh"'+(lang==="zh"?' class="active"':'')+'>中</button><button data-l="en"'+(lang==="en"?' class="active"':'')+'>EN</button></div></div>'
  +'<div class="bwrap" id="bwrap"><div class="bframe"></div><svg class="strings" id="strings"></svg><div id="pinlayer"></div></div>';
 var pl=el.querySelector("#pinlayer");
 BOARD_PINS.forEach(function(p){
  var d=document.createElement("div");d.className="pin "+p.kind;d.dataset.pin=p.id;
  d.style.left=p.x+"%";d.style.top=p.y+"%";d.style.transform="translate(-50%,-50%) rotate("+p.rot+"deg)";
  d.innerHTML='<span class="tack" style="background:'+p.tack+'"></span>'+pinInner(p);
  d.addEventListener("click",function(){openDossier(pinRefScene(p));});
  pl.appendChild(d);
 });
 el.querySelectorAll(".thb").forEach(function(b){b.addEventListener("click",function(){filterThread(b.dataset.th);});});
 el.querySelectorAll(".lang button").forEach(function(b){b.addEventListener("click",function(){setLang(b.dataset.l);});});
 filterThread(state.lastThread||"all");
}
function pinRefScene(p){ // 该 pin 关联的 beat:event 直接是 scene;photo 取该人物首个出场 beat
 if(p.kind==="event")return p.ref;
 for(var i=0;i<SCENES.length;i++)if((SCENES[i].cast||[]).indexOf(p.ref)>-1)return SCENES[i].id;
 return SCENES[0].id;
}
function renderStrings(thId){
 var w=document.getElementById("bwrap"),svg=document.getElementById("strings");
 if(!w)return; svg.setAttribute("viewBox","0 0 "+w.clientWidth+" "+w.clientHeight);
 var lines=[];
 THREADS.forEach(function(th){ if(thId!=="all"&&th.id!==thId)return;
  for(var i=0;i<th.pinIds.length-1;i++)lines.push({a:th.pinIds[i],b:th.pinIds[i+1],c:th.color});
 });
 var h=lines.map(function(L){var A=pinById(L.a),B=pinById(L.b);if(!A||!B)return"";
  var ax=A.x/100*w.clientWidth,ay=A.y/100*w.clientHeight,bx=B.x/100*w.clientWidth,by=B.y/100*w.clientHeight;
  var mx=(ax+bx)/2,my=(ay+by)/2+22,sw=thId==="all"?1.8:2.6;
  return '<path d="M'+ax+' '+ay+' Q'+mx+' '+my+' '+bx+' '+by+'" fill="none" stroke="'+L.c+'" stroke-width="'+sw+'" stroke-linecap="round"/>'
   +'<circle cx="'+ax+'" cy="'+ay+'" r="2.6" fill="'+L.c+'"/><circle cx="'+bx+'" cy="'+by+'" r="2.6" fill="'+L.c+'"/>';
 }).join("");
 svg.innerHTML=h;
}
function filterThread(thId){
 state.lastThread=thId; save();
 document.querySelectorAll(".thb").forEach(function(b){b.classList.toggle("active",b.dataset.th===thId);});
 var m=pinsForThread(thId);
 document.querySelectorAll(".pin").forEach(function(el){var on=thId==="all"||m[el.dataset.pin];
  el.classList.toggle("dim",thId!=="all"&&!on);el.classList.toggle("act",thId!=="all"&&!!on);});
 renderStrings(thId);
}
```

把 `boot()` 改为:`load(); renderBoard(); document.getElementById("title").classList.add("hidden"); document.getElementById("board").classList.remove("hidden");`(临时直接进板,Task 9 再加标题屏)。`setLang`/`openDossier` 在后续 Task 定义——本步先放占位:`function setLang(l){lang=l;state.lang=l;save();renderBoard();} function openDossier(id){console.log("open",id);}`

- [ ] **Step 4: 预览验证板面**

`preview_eval` reload → `preview_console_logs`(0 报错)→ `preview_snapshot`。
Expected:看到 7 个 pin、顶部线索按钮 + 中/EN;`preview_click` 点 "被诅咒的蓝宝石" 按钮后 `preview_screenshot`,应见 Grace↔Ruby 间一条蓝色红线、其余 pin 变暗。

- [ ] **Step 5: 提交**

```bash
cd /Users/cry/Desktop/peaky-dossier && git add -A && git commit -m "feat: dossier board — pins, red-string threads, thread filter, lang switch"
```

---

## Task 5:卷宗卡(Dossier)

**Files:**
- Modify: `index.html`(`<style>` 加卡片样式;渲染区用真 `openDossier` 替换占位)

- [ ] **Step 1: 加卷宗卡 CSS**

```css
#dossier{position:absolute;inset:0;background:rgba(11,8,5,.82);display:flex;align-items:center;justify-content:center;padding:18px;z-index:30}
.dz{width:440px;max-width:100%;background:var(--manila);border:1px solid #9a865d;border-radius:4px;overflow:hidden;font-family:var(--serif)}
.dz-top{position:relative;display:flex;align-items:center;gap:10px;background:#7c1f17;color:#f3dec5;padding:9px 12px;font-family:var(--stencil)}
.dz-no{font-size:12px;letter-spacing:1.5px}.dz-season{font-size:12px;opacity:.85}
.dz-x{margin-left:auto;background:none;border:none;color:#f3dec5;cursor:pointer;font-size:18px}
.dz-b{padding:12px 16px 16px}
.dz-y{font-family:var(--type);font-size:12px;color:#7c1f17}
.dz-tz{font-size:19px;font-weight:700;color:#241a10;margin:2px 0 0}
.dz-te{font-family:var(--stencil);font-size:13px;color:#5a4326;margin:1px 0 8px}
.dz-tx{font-size:14px;line-height:1.6;color:#2f2316;margin:0 0 10px}
.dz-meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:12px}
.chip{font-family:var(--stencil);font-size:11px;background:#c7b485;color:#3a2c14;border:1px solid #ab986a;border-radius:4px;padding:2px 7px}
.dz-go{font-family:var(--stencil);font-size:13px;background:#241a10;color:#e7c98a;border:none;border-radius:5px;padding:8px 14px;cursor:pointer}
```

- [ ] **Step 2: 实现 openDossier(替换占位)**

```js
var curBeat=null;
function openDossier(sceneId){
 var s=sceneById(sceneId); if(!s)return; curBeat=sceneId;
 var cast=(s.cast||[]).map(function(id){var c=charById(id);return '<span class="chip">'+(lang==="zh"?c.nameZh:c.nameEn)+'</span>';}).join("");
 var ths=(s.threads||[]).map(function(id){var th=THREADS.filter(function(x){return x.id===id;})[0];
  return th? '<span class="chip" style="background:'+th.color+';color:#fff;border-color:'+th.color+'">'+(lang==="zh"?th.nameZh:th.nameEn)+'</span>':"";}).join("");
 var d=document.getElementById("dossier");
 d.innerHTML='<div class="dz"><div class="dz-top"><span class="dz-no">'+t("caseFile")+' '+s.no+'</span>'
  +'<span class="dz-season">S'+s.season+' · '+s.year+'</span><button class="dz-x" aria-label="close">&times;</button></div>'
  +'<div class="dz-b"><div class="dz-y">'+s.year+'</div>'
  +'<p class="dz-tz">'+(lang==="zh"?s.titleZh:s.titleEn)+'</p>'
  +'<div class="dz-te">'+(lang==="zh"?s.titleEn:s.titleZh)+'</div>'
  +'<p class="dz-tx">'+(lang==="zh"?s.taleZh:s.taleEn)+'</p>'
  +'<div class="dz-meta"><span class="chip" style="background:none;border:none;color:#5a4326">'+t("appears")+':</span>'+cast+ths+'</div>'
  +'<button class="dz-go">'+t("openScene")+' &#9656;</button></div></div>';
 d.classList.remove("hidden");
 d.onclick=function(e){if(e.target===d)closeDossier();};
 d.querySelector(".dz-x").onclick=closeDossier;
 d.querySelector(".dz-go").onclick=function(){closeDossier();openScene(curBeat);};
}
function closeDossier(){document.getElementById("dossier").classList.add("hidden");}
```

`openScene` 暂占位:`function openScene(id){console.log("scene",id);}`(Task 6 实现)。

- [ ] **Step 3: 预览验证**

reload → `preview_click` 点 Grace 照片 → `preview_snapshot`。
Expected:弹出卷宗卡,标题"慈善晚宴的子弹"、出场 chip(汤米/格蕾丝)、暗线 chip(被诅咒的蓝宝石)、"翻开场景 ▸" 按钮;点 × 或背景关闭。

- [ ] **Step 4: 提交**

```bash
cd /Users/cry/Desktop/peaky-dossier && git add -A && git commit -m "feat: dossier case-file card with cast/thread chips + open-scene button"
```

---

## Task 6:电影场景视图(SCENE)

**Files:**
- Modify: `index.html`(`<style>` 加场景样式;渲染区用真 `openScene`/`renderScene` 替换占位)

- [ ] **Step 1: 加场景 CSS(沿用概念稿 A)**

```css
#scene{position:relative;height:600px;background:#0a0807;border:1px solid var(--frame);border-radius:10px;overflow:hidden}
.sc-art{position:absolute;inset:0;transform:scale(1.08);transition:transform 1.4s ease}
#scene.in .sc-art{transform:scale(1)}
.sc-art svg{width:100%;height:100%;display:block}
.sc-scrim{position:absolute;left:0;right:0;bottom:0;height:260px;background:rgba(8,6,5,.5);z-index:2}
.sc-lb{position:absolute;left:0;right:0;height:36px;background:#000;z-index:3}
.sc-lb.t{top:0}.sc-lb.b{bottom:0}
.sc-tag{position:absolute;top:48px;left:22px;font-family:var(--stencil);font-size:12px;letter-spacing:2px;color:#e7c98a;z-index:4}
.sc-num{position:absolute;top:44px;right:22px;font-family:var(--type);font-size:13px;color:#cbb78c;z-index:4}
.sc-cap{position:absolute;left:0;right:0;bottom:56px;padding:0 30px;z-index:4;opacity:0;transform:translateY(24px);transition:opacity 1s ease,transform 1s ease}
#scene.in .sc-cap{opacity:1;transform:none}
.sc-big{font-family:var(--disp);font-weight:700;font-size:28px;line-height:1.15;color:#f4ead7;margin:0 0 9px}
.sc-small{font-size:15px;line-height:1.6;color:#d9ccb4;max-width:620px;margin:0}
.sc-nav{position:absolute;bottom:46px;right:24px;display:flex;gap:8px;z-index:5}
.sc-nav button,.sc-back{font-family:var(--stencil);font-size:12px;color:#e7c98a;background:rgba(20,16,10,.7);border:1px solid #4a3a28;border-radius:6px;padding:7px 12px;cursor:pointer}
.sc-back{position:absolute;bottom:46px;left:24px;z-index:5}
```

- [ ] **Step 2: 实现 openScene / renderScene**

```js
function seasonLabel(s){var z=["序幕","第一季","第二季","第三季","第四季","第五季","第六季","终幕"][s];
 var e=["Prologue","Series 1","Series 2","Series 3","Series 4","Series 5","Series 6","Finale"][s];
 return (lang==="zh"?z:e);}
function openScene(sceneId){ curBeat=sceneId; state.lastBeat=sceneId; state.visited[sceneId]=1; save();
 setView("scene"); renderScene(sceneId); }
function renderScene(sceneId){
 var s=sceneById(sceneId),el=document.getElementById("scene");
 el.classList.remove("in");
 el.innerHTML='<div class="sc-art">'+s.art+'</div><div class="sc-scrim"></div><div class="sc-lb t"></div><div class="sc-lb b"></div>'
  +'<div class="sc-tag">'+seasonLabel(s.season)+' · '+s.year+'</div><div class="sc-num">'+s.no+'</div>'
  +'<div class="sc-cap"><p class="sc-big">'+(lang==="zh"?s.titleZh:s.titleEn)+'</p><p class="sc-small">'+(lang==="zh"?s.taleZh:s.taleEn)+'</p></div>'
  +'<button class="sc-back">&#9664; '+t("backBoard")+'</button>'
  +'<div class="sc-nav"><button class="sc-prev">'+t("prev")+'</button><button class="sc-next">'+t("next")+'</button></div>';
 el.querySelector(".sc-back").onclick=function(){setView("board");};
 el.querySelector(".sc-prev").onclick=function(){stepScene(-1);};
 el.querySelector(".sc-next").onclick=function(){stepScene(1);};
 requestAnimationFrame(function(){requestAnimationFrame(function(){el.classList.add("in");});});
}
```

`setView`/`stepScene` 在 Task 7/8 实现;本步先占位:`function setView(v){var b=document.getElementById("board"),s=document.getElementById("scene");if(v==="scene"){b.classList.add("hidden");s.classList.remove("hidden");}else{s.classList.add("hidden");b.classList.remove("hidden");}} function stepScene(d){console.log("step",d);}`

- [ ] **Step 3: 预览验证**

reload → 点 Grace 照片 → 卷宗卡点"翻开场景" → `preview_screenshot`。
Expected:进入满屏晚宴场景,黑边 + 标题"慈善晚宴的子弹" + 旁白从下方淡入上移;有"返回红线板""上/下一幕"按钮。

- [ ] **Step 4: 提交**

```bash
cd /Users/cry/Desktop/peaky-dossier && git add -A && git commit -m "feat: cinematic scene view with letterbox + tale reveal + nav buttons"
```

---

## Task 7:视图切换闭环(BOARD ↔ SCENE)

**Files:**
- Modify: `index.html`(渲染区用真 `setView` 替换占位)

- [ ] **Step 1: 实现 setView(带过渡 + 状态)**

```js
var view="board";
function setView(v){
 view=v;
 var b=document.getElementById("board"),s=document.getElementById("scene");
 if(v==="scene"){ b.classList.add("hidden"); s.classList.remove("hidden"); }
 else { s.classList.add("hidden"); s.classList.remove("in"); b.classList.remove("hidden"); }
}
```

- [ ] **Step 2: 预览验证闭环**

reload → 点 pin → 卷宗 → 翻开场景 → 返回红线板 → 板面状态仍在(线索筛选保留)。`preview_console_logs` 0 报错。
Expected:整条 BOARD→Dossier→SCENE→BOARD 链路无报错、来回自如。

- [ ] **Step 3: 提交**

```bash
cd /Users/cry/Desktop/peaky-dossier && git add -A && git commit -m "feat: wire board<->scene view switching"
```

---

## Task 8:导航顺序(时间序 / 暗线序,test-first)

**Files:**
- Modify: `index.html`(纯逻辑区加 `beatsInOrder`/`threadOrder`/`stepScene`;`__selftest` 加断言)

- [ ] **Step 1: 加排序断言**

```js
  var ord=beatsInOrder();
  ok(ord[0]==="prologue"&&ord[ord.length-1]==="s6-finale","时间序应 prologue→finale");
  var to=threadOrder("sapphire");
  ok(to.length===2&&to[0]==="s3-grace"&&to[1]==="s6-ruby","蓝宝石暗线序应 grace→ruby");
```

- [ ] **Step 2: 运行确认失败**

`preview_eval`:`__selftest()`
Expected:`FAIL` 含排序条目(或 ReferenceError)。

- [ ] **Step 3: 实现排序 + stepScene**

```js
function beatsInOrder(){ return SCENES.map(function(s){return s.id;}); } // SCENES 已按时间排好
function threadOrder(thId){ var th=THREADS.filter(function(x){return x.id===thId;})[0]; return th?th.beatIds.slice():[]; }
var navMode="time", navThread=null;
function currentOrder(){ return (navMode==="thread"&&navThread)? threadOrder(navThread) : beatsInOrder(); }
function stepScene(d){
 var o=currentOrder(),i=o.indexOf(curBeat); if(i<0){i=beatsInOrder().indexOf(curBeat);o=beatsInOrder();}
 var n=i+d; if(n<0||n>=o.length)return; openScene(o[n]);
}
```

并让 `openScene` 接受可选模式:从卷宗"翻开场景"时按时间序(`navMode="time"`);若日后从暗线进入可设 `navMode="thread"`。本步在 `openDossier` 的 go 按钮前加 `navMode="time";navThread=null;`。

- [ ] **Step 4: 运行确认 PASS + 预览翻页**

`preview_eval`:`__selftest()` → `"PASS"`。reload → 进任一场景 → 点"下一幕"应按 prologue→guns→grace→ruby→finale 推进。

- [ ] **Step 5: 提交**

```bash
cd /Users/cry/Desktop/peaky-dossier && git add -A && git commit -m "feat: navigation order (time vs thread) + prev/next stepping + selftest"
```

---

## Task 9:标题屏 PRESS START + RESUME + reduced-motion

**Files:**
- Modify: `index.html`(`<style>` 加标题屏 + reduced-motion;渲染区加 `renderTitle`;改 `boot`)

- [ ] **Step 1: 加 CSS**

```css
#title{height:560px;display:flex;flex-direction:column;align-items:center;justify-content:center;background:var(--soot);border:1px solid var(--frame);border-radius:10px;text-align:center}
.t-h{font-family:var(--disp);font-weight:700;font-size:42px;color:#f4ead7;margin:0 0 6px}
.t-sub{font-family:var(--stencil);font-size:14px;letter-spacing:2px;color:#caa64a;margin-bottom:28px}
.t-start{font-family:var(--stencil);font-size:16px;color:#1a130c;background:var(--brass);border:none;border-radius:6px;padding:12px 26px;cursor:pointer;letter-spacing:1px}
.t-resume{display:block;margin-top:14px;font-family:var(--type);font-size:13px;color:#cbb78c;background:none;border:none;cursor:pointer;text-decoration:underline}
@media (prefers-reduced-motion: reduce){.sc-art,#scene.in .sc-art,.sc-cap,#scene.in .sc-cap{transition:none!important;transform:none!important;opacity:1!important}}
```

- [ ] **Step 2: 实现 renderTitle + 改 boot**

```js
function renderTitle(){
 var el=document.getElementById("title");
 var resume=state.lastBeat? '<button class="t-resume">'+t("resume")+' &#8250;</button>':'';
 el.innerHTML='<h1 class="t-h">浴血黑帮 · 卷宗</h1><div class="t-sub">'+t("subtitle")+'</div>'
  +'<button class="t-start">'+t("start")+' &#9656;</button>'+resume
  +'<div class="lang" style="margin-top:22px"><button data-l="zh"'+(lang==="zh"?' class="active"':'')+'>中</button><button data-l="en"'+(lang==="en"?' class="active"':'')+'>EN</button></div>';
 el.querySelector(".t-start").onclick=function(){enterBoard();};
 var rb=el.querySelector(".t-resume"); if(rb)rb.onclick=function(){enterBoard();openScene(state.lastBeat);};
 el.querySelectorAll(".lang button").forEach(function(b){b.addEventListener("click",function(){lang=b.dataset.l;state.lang=lang;save();renderTitle();});});
}
function enterBoard(){ document.getElementById("title").classList.add("hidden"); renderBoard(); document.getElementById("board").classList.remove("hidden"); view="board"; }
function boot(){ load(); console.assert(__selftest()==="PASS","selftest"); renderTitle(); }
```

把 Task 4 里临时"直接进板"的 boot 改回上面这版(标题屏先行)。

- [ ] **Step 3: 预览验证整条线**

reload → 见标题屏 PRESS START（有 RESUME 当有进度时）→ 点开始进板 → 走通 pin→卷宗→场景→返回 → 切 EN 全站变英文。`preview_console_logs` 0 报错。`preview_screenshot` 留证。

- [ ] **Step 4: 提交**

```bash
cd /Users/cry/Desktop/peaky-dossier && git add -A && git commit -m "feat: title screen (press start + resume) + reduced-motion; Phase 1 vertical slice complete"
```

---

## 自检(对照 spec)

- 双视图引擎(BOARD↔SCENE)✓ Task 4/6/7;数据化三数组 ✓ Task 1;i18n ✓ Task 2;持久化/RESUME ✓ Task 3/9;红线板筛选即玩法 ✓ Task 4;卷宗卡 ✓ Task 5;场景运镜 ✓ Task 6;暗线/时间双序 ✓ Task 8;标题屏/reduced-motion ✓ Task 9。
- **本期不覆盖(转 Phase 2–6)**:其余 30 beat + tableau;其余 4 条暗线;按季/按人物两条进板路径;人物名册 + 谢尔比家族树 / 帮派势力图;Web Audio 分季配乐 + SFX;#35 放大高潮 + 过渡打磨 + 移动端 + 离屏性能 + 消 FOUT;og.png 分享卡。
- 类型一致性:`sceneById/charById/pinById`、`openScene/renderScene/setView/stepScene/openDossier/closeDossier`、`state.lastBeat/lastThread`、`THREAD.pinIds/beatIds` 全程同名。
- `SVG_RUBY` 占位场景已在 Task 1 Step 4 标注,Phase 5 替换——非 placeholder 遗漏,是有意降级。

---

## 后续计划(各自独立成 plan)

- **Phase 2 · 铺内容**:补齐 30 个 beat(数据 + tableau)至全 35;补全人物到完整名册。
- **Phase 3 · 导航与暗线全量**:其余 4 条暗线;按季 / 按人物进板;谢尔比家族树 + 帮派势力图弹窗。
- **Phase 4 · 音频**:Web Audio 分季芯片配乐变调 + SFX(枪响/划刀/电报/马蹄/火焰)+ 静音持久化。
- **Phase 5 · 打磨**:#35 放大高潮 + #15 重锤、过渡运镜、离屏暂停性能、移动端响应式、a11y(键盘/焦点)、消 FOUT、专属 tableau(含 Ruby 病房)。
- **Phase 6 · 分享**:og.png 1200×630 + meta + favicon。
