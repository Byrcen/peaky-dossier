# 浴血黑帮 · 卷宗 — 推理玩法重构 设计文档

> 把"可导航的叙事百科"升级为"可玩的推理游戏":你以 Campbell 督察的身份,一案一案地建立扳倒谢尔比的卷宗。
> 红线板从「筛选菜单」变成「答题工作台」。单文件零依赖照旧。
> 日期:2026-06-22 · 状态:设计已锁(用户逐节确认),待写实现计划

---

## 0. 一句话

在现有《浴血黑帮·卷宗》(单文件、零依赖、35 幕 + 5 暗线 + 红线板/电影场景双视图)之上,**新增一层推理引擎**:把剧里现成的悬案(谁是眼线、谁杀了 Grace、谁是内鬼、诅咒应在谁……)做成 **7 个按季推进的案子**,玩家**在红线板上亲手动图钉**来破案——whodunit 点凶手照片、因果链依次连红线;答完盖判决章、播揭晓幕、归档。现有自由导航(透镜/家族树/势力图)**始终开放**,作为并行的"档案室"。

---

## 1. 背景:为什么重构

**现状诊断**:当前核心循环 `红线板(菜单) → 选透镜 → 点物件逐幕翻页 → 回板`,本质是一个做得很精致的**可导航叙事百科 / 博物馆导览**——玩家在*读*、在*集齐*,但没有在*玩*。红线是预先画好的(不连线)、每幕只有一个"下一页"物件(不推理)、没有能动性/挑战/后果。

**核心机会**:外壳("Campbell 督察的案卷"+ 红线)承诺的是**侦探破案**,机制给的却是**翻书**。剧本身埋了大量现成悬案(尤其 S5 内鬼 = 剧里的 whodunit)。**让玩家真的去查案**,是把"幻灯片"变"游戏"性价比最高的一刀,且几乎不浪费已有数据。

**已锁定的方向决策**(brainstorm 逐项确认):

| # | 决策 | 选择 |
|---|---|---|
| 方向 | 加机制 vs 加内容 | **A 推理游戏** |
| 核心循环 | — | **看线索 → 连线 → 指认 → 揭晓**,押注作调味 |
| 结构 | 案卷夹 / 沙盒 / 双模式 | **① 按季推进的案卷夹** |
| 机制收敛 | 连线与指认是否合一 | **合一:红线板=唯一答题面**(whodunit 点照片、因果链依次连线) |
| 自由漫游门槛 | 结案才解锁 vs 始终开放 | **始终开放**(更友好,接受可提前剧透的取舍) |
| 铁律 | — | **答案必须能从板上已亮的线索"推"出来**(考"会不会读线索",非"记不记得剧情") |

---

## 2. 框架(fiction):你就是 Campbell,在攒一份卷宗

二十年(1919→1934),玩家以督察身份**逐案建立对谢尔比的指控**。这把现有一切解释通:

- 红线板 = 你的**案卷墙**;红线 = 你的**推断**;卷宗卡 = 证物;揭晓幕 = 证据落地;"判决章" = 结案成色。
- 比"百科导览"多了一个**主体**(你)和一个**目的**(结案)。
- **押注层**不做 Tommy 式赌马皮(会跟侦探框架打架),改叫**"督察的直觉 / call it"**:关键幕揭晓前让你先押,攒一个独立的"直觉准星";赛道赔率的视觉味道留一点点即可。

---

## 3. 核心机制:红线板本身就是答题面

把"连线"和"指认"统一成**同一件事——在板上动图钉**,只有一个交互面,移动端友好(**点选**,不强求拖拽)。

### 3.1 每案的五步循环

```
① 查证  打开线索幕(= 现有 SCENE 播放,案中重命名为"查阅证物")。
         证物 chip 打勾;线索幕用"督察批注"呈现(见 3.3),不剧透答案。
② 推断  在板上动手:
         · whodunit 步 → 点「凶手/内鬼」那张照片(accuse)
         · 因果链 步   → 按因果顺序依次点图钉对,红线自己连出来(connect)
         · 预判 步     → 揭晓前的轻量浮层选项(call it,纯计分)
③ 指控  连错/点错 → 红线弹回 + 短促错误音(可选扣成色);对了 → 锁定 + 拨弦音
④ 判决  Campbell 盖章「CASE CLOSED / COLD CASE」+ 一句"为什么是它"(引用看过的线索)
⑤ 揭晓  播该案揭晓幕(可多幕),seeds/closes 的暗线 note 解锁,本案归档、记成色
```

### 3.2 三种"步"(step)的判定

- **accuse**:从一排嫌疑人(每个对应一张板上照片)里点中正确者。至少含 1 个**障眼法**嫌疑(剧本身埋的误导,如 S5 的 Michael)。
- **connect**:一组**有向**红线 `[[from,to]...]`,必须**按指定顺序**连对;连错的那一跳闪红重置,不影响已连对的。
- **predict**:揭晓前二选一/三选一的"押注",**只计入直觉准星,不卡关**。

一个案子可含多步(如 S3 = 预判 + 指认 + 连线;S6 = 连线 + 指认)。

### 3.3 关键设计:线索如何"可推而不剧透"

现有 `SCENE.taleZh/En` 是**陈述式旁白**(直接说出发生了什么),会泄底。解法:**case 的证物条目自带一段"督察批注"** `clueZh/clueEn`,以**观察口吻**重述同一幕、**withhold 结论**;沉浸式的原 `tale` 留给"揭晓幕"和"自由浏览"用,不改。

> 例:S1 看 `s1-grace` 时,批注写"加里森新来一名歌女,逢人便打听谢尔比家的事,有人见她进出过警局"——指向但不点名;原幕旁白(她就是眼线)留作 `s1-showdown` 揭晓后才呈现。

这是本次**主要的新增内容工作量**,也是玩法成立的核心。

---

## 4. 案卷夹:7 个案子(复用现有 35 幕 + 5 暗线)

跨季长线**早埋晚收**:板子随通关一格格填满,最后一根线连上即高潮。下表的"步"按发生顺序;`reveal` 为答完所播之幕。约定:**seeds** = 该案答对后系统自动连出该暗线"已确立"的红线;**closes** = 由玩家手连最后一根。

| # | 季 | 案名 | 步(动作) | 答案 / 障眼法 | seeds/closes | reveal |
|---|---|---|---|---|---|---|
| 1 | S1 | 加里森的眼线 | accuse 点凶手 | **Grace**;障眼:Ada(藏秘婚)、Freddie(被通缉) | seeds 子弹 | s1-showdown |
| 2 | S2 | 坟前那一枪 | accuse 点凶手 | **Polly**(为被害复仇);障眼:Tommy、Arthur、Michael | closes 子弹(结案自动连 `polly→campbell`) | s2-polly |
| 3 | S3 | 晚宴上的子弹 | predict 谁中枪 → connect `[grace→sapphire]` | 中枪:**Grace**(障眼:Tommy/Arthur);"For Angel" 凶手归属留到**案4 血仇链**揭晓 | seeds 蓝宝石(玩家手连 `grace→sapphire`) | s3-grace |
| 4 | S4 | 血仇之链 | connect 4 跳有序链 | `Vicente→Grace, Arthur→Vicente, Luca→John, Arthur→Luca`(起因"John 弄瞎 Angel"作给定批注) | closes 血仇 | s4-mp |
| 5 | S5 | 内鬼是谁 | connect `[finn→billygrade, billygrade→swing]` | **Finn 走漏→Billy Grade 告密 IRA**;障眼:**Michael/Gina**(其背叛是商业夺权,非泄密) | seeds 电话 | s5-fog |
| 6 | S6 | 诅咒与假死 | predict 诅咒带走谁 → connect `[sapphire→ruby]` → accuse 谁在骗 | 诅咒落:**Ruby**;假死黑手:**Mosley**(买通 Holford);障眼:Holford/Michael/"他真病了" | closes 蓝宝石 + 电话 | s6-ruby → s6-diagnosis |
| 7 | 终幕 | 两片雾 | connect 镜像 `[grace↔ruby]` | 崩溃之雾 ↔ 重生之雾,首尾呼应 | closes 两片雾 | s6-finale → finale-end |

**逐案细节**(证物幕 + 批注要点 + 预判):

1. **S1 加里森的眼线** — 证物:`prologue`(背景)、`s1-guns`(丘吉尔要追回机枪)、`s1-campbell`(Campbell 需要内线)、`s1-grace`(批注:可疑新人)、`s1-freddie`(障眼:藏秘密的人)。指认正确后自动把 Campbell 标记为"子弹"线起点(他的觊觎将在 S2 招致 Polly 的复仇枪)。预判(开 `s1-showdown` 前):"Kimber 开枪,谁替 Tommy 挡子弹?"→ **Danny**。
2. **S2 坟前那一枪** — 证物:`s2-garrison`(IRA 胁迫)、`s2-epsom`(Campbell+丘吉尔逼刺杀,Lizzie 设饵)、`s2-michael`(Polly 的软肋:失散的儿子);给定批注:Campbell 对 Polly 的觊觎与施暴(S1 背景)。预判(可选):"坟边丘吉尔的人会杀 Tommy 吗?"→ **不会**("他有差事给你")。
3. **S3 晚宴上的子弹** — 证物:`s3-wedding`(婚礼处决俄国奸细=障眼:俄国人很危险)、`s3-russia`(白俄阴谋:Tatiana/Izabella/Hughes)、`s3-tunnel`(劫宝激怒俄国人);**给定批注**补上缺失的血仇前因:"伦敦一户意大利人记着仇——儿子 Angel 被 John 弄瞎"。情感重锤幕,**中段枢纽**:Grace 既牵出血仇、又戴着被诅咒的蓝宝石。
4. **S4 血仇之链** — 证物:`s4-noose`、`s4-luca`、`s4-john`、`s4-gold`、`s4-mp`。纯**连线**案,"连线"手感的橱窗;Arthur 在链中出现两次(杀 Vicente、杀 Luca),connect 模型允许同一图钉复用。
5. **S5 内鬼是谁** — 招牌案。证物:`s5-crash`(Michael 抗命致巨亏 → 埋 Michael 怨恨的障眼)、`s5-mosley`、`s5-bonnie`(逼反 Aberama)、`s5-plot`(批注:"计划走漏了,有人多嘴")、`s5-traitor`(**大障眼:Michael & Gina 夺权,剧故意引你怀疑 Michael**)。批注点明:Michael 的背叛是**钱**,不是泄密。预判(开 `s5-fog` 前):"Tommy 把枪抵住自己太阳穴,他开枪了吗?"→ **没有**(黑屏,四年后)。
6. **S6 诅咒与假死** — 证物:`s6-bodies`(三具尸体=电话线后果)、`s6-boston`(戒酒;Michael 怨恨)、`s6-curse`(蓝宝石辗转克死七岁 Connie,Evadne 下咒)、`s6-diagnosis`(Holford 说将死,背景有 Mosley)。预判(开 `s6-ruby` 前):"诅咒点名一个七岁孩子,会带走谁?"→ **Ruby**。
7. **终幕 两片雾** — 证物:`s5-fog`(崩溃,幻见 Grace)、`s6-finale`(重生,Ruby 鬼魂"你没病,去点火")。镜像**连线**收尾;之后弹"对 Tommy Shelby 的最终裁定"汇总屏 → `finale-end`(不朽之人)预告。

**新增图钉**(部分嫌疑人/连线端点现无 pin):`pin-finn / pin-vicente / pin-danny / pin-holford / pin-evadne / pin-gina`(沿用 `BOARD_PINS` 现有结构与做旧风格)。

---

## 5. 评分与容错(有压力,不劝退)

- **每案成色**:一次答对 = `AIRTIGHT ★★★`;用提示/重试递减(★★ / ★)。
- **直觉准星**:预判正确数 / 总数,单独计,纯荣誉。
- **软失败**:答错只盖「COLD CASE」+ Campbell 嘟囔一句,可重查重判;**错 2–3 次自动揭晓**,绝不卡死(延续现有"无 game over"气质)。
- **提示** `Campbell's hunch`:排除一名嫌疑 / 点亮一条关键线索,扣一颗星。
- 通关汇总屏:案卷完成度 + 各案成色 + 直觉准星 + 收尾文案("Case open. The Immortal Man walks free.")。

---

## 6. 自由浏览始终开放(并行的"档案室")

**不做割裂双模式,也不设门槛**。标题屏给两个并行入口,现有自由导航**原封复用**:

- 标题屏:`开始查案`(→ 案卷夹) · `自由浏览`(→ 现有红线板自由态,始终可进) · `继续`(resume) · 中/EN。
- 板子用一个上下文标志 `boardMode = 'case' | 'free'`:
  - `case`:显示案头(谜题 + 证物 chip + 嫌疑人)、开启 accuse/connect、只激活本案相关图钉。
  - `free`:现有透镜(人物/暗线/季)+ 家族树 + 势力图,**始终开放**。
- **取舍**:自由浏览始终开 → 玩家可提前剧透未结案的谜底。**已接受**(换取随便逛的友好度)。可选打磨:进未结案内容时给一句"这会揭晓未破的案,确定?"软提示(非核心)。

---

## 7. 数据模型(与展示解耦,延续现有风格)

```js
CASE = {
  id, season, no,                  // 'c5-leak', 5, '05'
  titleZh, titleEn,
  briefZh, briefEn,                // 案头框架(Campbell 的话)
  evidence: [                      // 有序证物
    { scene:'s5-plot', clueZh, clueEn }   // clue* = 不剧透的督察批注;原 SCENE.tale 不动
  ],
  steps: [                         // 一或多步,按序
    { kind:'accuse',  promptZh, promptEn, suspects:['pin-..',..], answer:'pin-..', becauseZh, becauseEn },
    { kind:'connect', promptZh, promptEn, links:[['pin-a','pin-b'],..], becauseZh, becauseEn },
    { kind:'predict', promptZh, promptEn, options:[{labelZh,labelEn},..], answer:0 }
  ],
  seeds:[threadId..], closes:[threadId..],
  revealSeq:['s5-fog', ..]         // 答完按序播
}
```

**state 扩展**(并入现有 `state`,沿用 `localStorage` 的 `save()/load()`):

```js
state.cases   = { solved:{ id:{rating,tries,hints} }, current:null, step:0, examined:{} }
state.instinct= { correct:0, total:0 }
// 现有字段保留:lang, muted, lastBeat, lastThread, visited
```

---

## 8. 重构映射(**单文件零依赖照旧**——这是卖点不能破)

重构是**文件内部模块化 + 新增推理引擎**,**不拆文件、不引构建**(README 头牌就是"双击即开")。按现有 `/* === … === */` 分节继续:

| 区块 | 改动 |
|---|---|
| **数据** | 新增 `CASES[]`;`BOARD_PINS` 补缺失嫌疑人图钉 |
| **推理引擎(新)** | `openCase / renderCaseHeader / examineEvidence / onPinTap(case 内分流) / tryConnect(links) / accuse(pin) / doPredict / showVerdict / archiveCase / updateRating` |
| **案卷夹首屏(新)** | `renderCasebook / caseStatus(id)→locked|current|solved` |
| **BOARD 渲染** | 加 `boardMode`;case 态叠加案头、激活点选/连线;free 态 = 现有逻辑不动 |
| **SCENE 播放** | 复用(= 查证/揭晓);加"揭晓前 predict 浮层"钩子 |
| **标题屏** | 两入口(查案/自由浏览)+ resume |
| **音频** | 复用合成;加 SFX:盖章 thud、错误 buzzer、连线拨弦、查证 tick |
| **美术(SVG/CSS,无文件)** | 橡皮图章 `CASE CLOSED/COLD CASE`、红线连出动画、嫌疑高亮辉光、hunch 手电 |
| **i18n** | 新 UI 串入 `T`(中英);`CASES` 内容双语 |
| **`__selftest` 扩展** | 每案:evidence/reveal 的 scene ref 存在;accuse 的 answer ∈ suspects;connect 的 pin 都存在;seeds/closes 的 thread id 存在;每步可解 |

**复用不动**:SCENE 播放器、Web Audio 底座、i18n 框架、a11y、移动端、离屏暂停、og/favicon。

---

## 9. 范围(YAGNI)

**做**:7 案推理引擎 · 板上 accuse/connect/predict · 判决 + 成色 + 直觉准星 + 提示 + 汇总屏 · 案卷夹首屏 · 自由浏览始终开放 · 全程中英双语 · 单文件 · selftest 扩展 · 必要的新图钉/批注内容。

**不做(v1)**:大电影(留 `season:7` 接口)· 多结局分支 · 拖拽物理(用点选)· 联机/排行榜 · 逐对白颗粒度 · 拆分多文件/引入构建。

---

## 10. 里程碑(细节交给实现计划)

1. **数据先行**:作 `CASES[]`(7 案,双语,含不剧透批注 + because)+ 补图钉;扩展 `__selftest` 并通过。
2. **引擎打通**:推理引擎 + case 态 BOARD(accuse/connect/verdict)端到端跑通 **1–2 个样板案**。
3. **结构成型**:案卷夹首屏 + 按季推进 + resume + 标题两入口 + 自由浏览并行。
4. **铺满**:7 案全量接入;predict 层;成色/直觉准星;最终裁定汇总屏。
5. **打磨**:盖章/连线动画、新 SFX、a11y(键盘 accuse/connect、焦点、reduced-motion)、移动端、消 FOUT、(可选)剧透软提示。
6. **收尾**:更新 README(玩法说明)+ 本 docs;og/favicon 沿用。

---

## 11. 风险 / 待办

- **最大新增成本 = "可推不剧透"的内容**:7 案 × 双语的 `clue` 批注 + `because`,要写到"答案能从线索推出来",这是玩法成立与否的关键,需逐案打磨。
- **机制手感**(点选连线的排序、错误反馈、accuse)需一次试玩校准——手感我无法纯靠读码自测。
- **音频新增 SFX**需用户亲耳给方向(延续现有约束)。
- **剧透取舍**:自由浏览始终开放系用户决策,已接受。
- 关卡推进与"始终开放"并存:确保 case 态只激活本案图钉,不被 free 态的全板渲染干扰。
