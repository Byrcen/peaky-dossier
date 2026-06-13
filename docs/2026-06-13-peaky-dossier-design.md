# 浴血黑帮 · 卷宗 / Peaky Blinders Dossier — 设计文档

> 像素风互动叙事:谢尔比家二十年(1919 → 1934),六季全剧情。
> 混合展示范式 =「卷宗红线板」导航中枢 +「电影场景」满屏播放。
> 日期:2026-06-13 · 状态:设计已锁,待写实现计划

---

## 0. 一句话

把《浴血黑帮》S1–S6 的 35 个关键剧情节点做成一个**单文件、零依赖、双击即开**的像素风互动叙事:用一面**侦探红线板**(Campbell 督察的案卷)做非线性导航,点开任意线索即进入**满屏电影感像素场景**逐屏运镜播放;全程**中英双语**。大电影《The Immortal Man》本版不做,数据结构留好接口。

定位(沿用 aegon-timeline 的三合一):**个人兴趣** + **AIPM 作品集案例** + **可玩的互动叙事**。

---

## 1. 为什么是这个范式

候选过 5 种(胶片放映 / 竖向 scrollytelling / 漫画格 / 卷宗红线板 / 互动地图),最终锁**混合**:

- **C 卷宗红线板** 当**导航中枢**:剧情主线本就是「警方调查谢尔比」,框架即剧情;更关键的是——剧里那几条**跨季暗线**(见 §5)在红线板上是「免费」的,**筛选机制本身就是叙事机制**,这是别的范式给不了的。
- **A 竖向电影场景** 当**沉浸播放**:点开某个 beat 时满屏像素场景 + 字幕运镜淡入,补上红线板缺的「沉浸 / 运镜」。

板子负责**结构 + 暗线**,场景负责**沉浸 + 运镜**,两边强项都吃到。

---

## 2. 技术架构

完全复用 aegon-timeline(《血与火》)已验证的工程底座,**唯一关键改造:内容彻底数据化**(aegon 是半硬编码,35 场景一多会难维护)。

- **形态**:单文件 `index.html`,零依赖,双击即开。本地预览 `python3 -m http.server`(在项目目录内起)。
- **内容数据层**(与展示解耦,presentation-agnostic):三个数组 `SCENES[]` / `THREADS[]` / `CHARACTERS[]`(+ `FACTIONS[]`)。换展示皮、加大电影,都只动数据。
- **两个视图模式**:
  - `BOARD`(卷宗红线板)= 导航中枢
  - `SCENE`(电影场景)= 沉浸播放
  - 一个顶层 `view` 状态 + 过渡动画在两者间切换。
- **复用 aegon 子系统**:Web Audio 程序化芯片配乐(分季变调)、localStorage 持久化(进度 / 静音 / 语言 / RESUME)、`prefers-reduced-motion`、移动端响应式、离屏动画暂停(性能)、标题屏 PRESS START、og 分享卡、favicon。
- **i18n**:顶层 `let lang`;`T` 字典存 UI 串;`SCENES/THREADS/CHARACTERS` 每条都带 `*Zh/*En` 字段;`applyLang()` 统一刷新并重建动态 DOM(板子上的标签、卷宗卡、名册)。专名用原著通行英文拼写(Tommy / Arrow House / Garrison …)。

### 数据模型(草案)

```js
SCENE = {
  id,                 // 's3-grace'
  season,             // 0=序幕 1..6 7=终幕
  no,                 // 显示序号 '15'
  titleZh, titleEn,
  year,               // '1924'
  taleZh, taleEn,     // 旁白 / 运镜字幕(2–4 句)
  art,                // 场景渲染规格(像素 tableau id 或内联 SVG/层数据)
  cast: [charId...],  // 出场人物
  threads:[threadId], // 所属暗线
  pin: { kind, labelZh, labelEn }  // 在红线板上的呈现:photo|news|telegram|evidence
}
THREAD = { id, nameZh, nameEn, color, beatIds:[...有序], noteZh, noteEn }
CHARACTER = { id, nameZh, nameEn, faction, seasons:[1..6], roleZh, roleEn, bioZh, bioEn, portrait }
FACTION = { id, nameZh, nameEn, color }
```

---

## 3. 展示层 A:卷宗红线板(BOARD,导航)

- **画面**:软木板 / 案卷墙。钉着照片(人物)、剪报(事件)、电报、物证(如蓝宝石),图钉固定、略微旋转。**红线**连接相关节点。做旧氛围(见 §6)。
- **三种进入路径**(同一块板,切视角):
  1. **按暗线**:顶部线索按钮(全部 / Changretta 血仇 / 蓝宝石诅咒 / …),点一条 → 只留该线红线、跨季节点全亮、其余压暗。
  2. **按季**:1–6 季切换,板子重排为该季的证物簇。
  3. **按人物**:点人物照片高亮其所有关联线 + 出场 beat。
- **交互**:点任意「证物 / 照片」→ 弹**卷宗卡**(CASE FILE:序号、季 / 年、标题双语、旁白、出场人物 chip、关联暗线 chip)→ 卡上「翻开场景 ▸」进入 SCENE 视图播放该 beat。
- **中 / EN 切换** 常驻;**RESUME** 回到上次看到的 beat。
- 已用概念小样验证交互骨架(`peaky_dossier_redstring_concept_c`)。

## 3'. 展示层 B:电影场景(SCENE,沉浸)

- **画面**:满屏像素 tableau + 电影黑边(letterbox)。进入 / 滚动到位时画面**推近(scale-in)** + 字幕**运镜淡入**(`taleZh/En` 下三分之一,像字幕)。
- **导航**:上一 / 下一 beat(键盘 ← →、点击、或滚轮吸附);「返回红线板」回 BOARD。可在「沿暗线顺看」与「沿时间顺看」两种序间切换(暗线序 = `THREAD.beatIds`;时间序 = `SCENES` 全序)。
- **分季配乐变调** 跟随当前 beat 的 `season`。
- 已用概念小样验证运镜手感(`peaky_scrollytelling_concept_a`)。

---

## 4. 内容:35 个 beat(已逐条对剧核查)

> 核查轮:6 季各派一研究 agent,交叉 Peaky Blinders Fandom wiki + 维基剧集页 + 多家复盘,每个死亡 / 年份 / 人名 ≥2 源。已修正原稿 7 处硬伤(见 §8 核查纪要)。**这是 fiction canon-check,以剧集为准。**

**序幕 · 1919**|小希思,Tommy 战后归来;"By order of the Peaky Blinders"——红马、帽檐刀片、Garrison 酒馆,引出谢尔比一家。

**S1 起家 · 1919**
1. 失窃的机枪 / The stolen guns — 误从 BSA 兵工厂偷走运往利比亚的 Lewis 机枪,惊动丘吉尔
2. 镇压者 Chester Campbell — 北爱 RIC 督察奉丘吉尔之命追枪清剿,错把 Arthur 当头目毒打
3. 卧底歌女 Grace — Grace Burgess 进 Garrison 当歌女,暗为 Campbell 当眼线
4. Freddie 与 Ada — 共产党人 Freddie Thorne 秘娶有孕的 Ada,被 Tommy 与 Campbell 同时追捕
5. 对决 Billy Kimber — Tommy 谋夺赛马场盘口,与赛道大佬 Kimber 由合到裂
6. 赛道摊牌 / The showdown — Kimber 枪杀替 Tommy 挡子弹的 **Danny Whizz-Bang**;Tommy 一枪爆头 **Kimber**,拿下赛道;Grace 身份败露远走伦敦(车站枪伤 Campbell,S2 揭晓)

**S2 进军伦敦 · 1921–22**
7. 炸毁的 Garrison — IRA(Irene O'Donnell)炸酒馆,胁迫 Tommy 替他们杀一名爱尔兰异见者;Peaky 北上
8. 朗姆酒贩 Alfie Solomons — 与 Camden 犹太帮(面包房幌子的朗姆酒坊)结盟又互算
9. 教父 Darby Sabini — 与控制伦敦赛道的意大利人开战;**Arthur 拳台打死少年 Ross**
10. Michael 归来 — Polly 失散多年的儿子 Michael 找上门,被卷入家族生意
11. Epsom 的刺杀 — Campbell + 丘吉尔逼 Tommy 在德比赛马日刺杀陆军元帅 **Field Marshal Henry Russell**;Lizzie 设饵,Tommy 扣下扳机
12. 坟前缓刑 + Polly 的子弹 — 墓坑边假处决,丘吉尔的人反杀同伙放过 Tommy("他有差事给你");**Polly 枪杀 Campbell**(为被强暴复仇);Grace 怀着 Tommy 的孩子归来

**S3 庄园与丧妻 · 1924**
13. 庄园婚礼 — Tommy 娶 Grace,入住 Arrow House;婚礼上俄国奸细对错暗号被当场处决,血溅婚日
14. 白俄阴谋 — 卷入流亡的 Petrovna 一家(主谋姑母 **Izabella**、接头人侄女 **Tatiana**)与"经济联盟"神父 **Father John Hughes** 的局
15. 慈善晚宴的子弹 / Grace 之死 — 募捐晚宴上 Changretta 杀手高喊"For Angel!"开枪,本要杀 Tommy 却击中 **Grace**(她正戴着那条被诅咒的蓝宝石)
16. 隧道劫宝 — 掘河底隧道盗走 Petrovna 珍宝(法贝热彩蛋),搅黄装甲列车军火交易(终幕列车爆炸)
17. 神父的下场 — **Michael 割喉处决 Father Hughes**(为童年被侵犯复仇;Tommy 授意),救回被绑的幼子 Charlie
18. 出卖全家 — 为更高层的交易,Tommy 设局让 Arthur / John / Polly / Michael(及 Ada)悉数被捕,自己独留庄园

**S4 西西里复仇 · 1925–26**
19. 绞架下的圣诞 — 全家面临绞刑,Tommy 最后一刻换来赦免(1925 平安夜)
20. 西西里复仇 Luca Changretta — 纽约黑手党 **Luca Changretta**(为 S3 死的父亲 Vicente、兄弟 Angel)登门血亲复仇
21. 门廊伏击 / John 之死 — 机枪伏击,**John Shelby 当场殒命**,Michael 重伤
22. 金家父子与拳赛 — 引入吉普赛枪手 Aberama Gold 与拳手 Bonnie Gold;**Bonnie 终局拳台击败 Goliath**(Alfie 外甥);工运 Jessie Eden 线
23. 复仇终局 + 当选议员 — **诈死的 Arthur 枪杀 Luca**;Tommy 在海滩枪击患癌的 **Alfie Solomons**;靠出卖共产党名单当选下议院 Labour 议员(Birmingham South)

**S5 萧条与法西斯 · 1929**
24. 华尔街崩盘 — 黑色星期二,Michael 抗命未及时套现,谢尔比巨亏
25. 法西斯 Mosley — 议员 Tommy 遭遇组建 BUF 的 **Oswald Mosley**,被迫虚与委蛇
26. Bonnie 之死 — Glasgow 剃刀帮 Billy Boys 的 **McCavern 把 Bonnie Gold 钉上十字架**,逼反 Aberama
27. 刺杀莫斯利 — Tommy 从疯人院捞出狙击手 **Barney Thomason** 杀 Mosley,Aberama 去杀 McCavern;**Finn 嘴快走漏给 Billy Grade,Billy 密告 IRA**
28. 内鬼与夺权 — Michael 与美籍妻子 Gina 暗中要夺家族权柄(内鬼身份本季成悬案)
29. 雾中枪口 — 行刺崩盘:**Barney 被狙杀、Aberama 被刺死**;Tommy 独立雾中田野,幻见亡妻 Grace,枪口抵住自己太阳穴——黑屏

**S6 终章 · 1933–34**
30. 三具尸体 — 四年后开场:IRA 报复行刺失败,把 **Polly、Aberama、Barney** 的尸体送回(Captain Swing);Polly 于罗姆大篷车火葬(纪念 Helen McCrory)
31. 戒酒与波士顿局 — 戒酒的 Tommy 用政治情报换 Jack Nelson 的鸦片生意,纠缠 IRA;Michael 记恨 Polly 之死欲弑兄
32. 蓝宝石的诅咒 — 那条 Grace 的蓝宝石辗转到 Barwell 家、克死七岁的 Connie;**Evadne Barwell** 诅咒 Tommy 也失去七岁女儿
33. Ruby 之死 — 女儿 **Ruby 染肺结核夭折**;Tommy 血洗 Barwell 营地复仇
34. 假死之局 — Mosley 买通 **Dr. Holford** 谎称 Tommy 患 tuberculoma 将死、诱他自尽;Arthur 戒毒归来、Finn 被逐出家门
35. 烈火与重生 — **Miquelon 岛上 Tommy 一枪打穿 Michael 的眼**;**Ruby 鬼魂**点醒"你没病,去点火";Tommy 识破假诊断,**火烧 Arrow House,骑白马遁入晨雾——他还活着**

**终幕**|留白:不朽之人 The Immortal Man,二战阴云,Tommy 归来——待续(`season:7` 留好接口)。

**高潮处理**:#35 终局做**放大章**(≈《血与火》血龙狂舞的隆重度:火烧庄园 + 骑马遁雾 + Ruby 鬼魂 + 识破假死多屏运镜);#15 Grace 之死做中段情感重锤。

---

## 5. 跨季暗线 / Threads of Fate(红线板核心玩法)

| 暗线 | 跨季 | 链条 |
|---|---|---|
| 🩸 Changretta 血仇 | S3→S4 | John 弄瞎 Angel → Vicente 杀 Grace → Arthur 杀 Vicente → Luca 杀 John → Arthur 杀 Luca |
| 💎 被诅咒的蓝宝石 | S3→S6 | Grace 的项链 → 辗转 Barwell 家克死七岁 Connie → 应验在 Ruby |
| 🔫 Polly 的子弹 | S1→S2 | Campbell 的觊觎与强暴 → Polly 的复仇枪 |
| ☎️ Billy Grade 的电话 | S5→S6 | Finn 走漏 → Billy 密告 IRA → Polly/Aberama/Barney 之死 → S6 揭破 |
| 👻 Tommy 的两片雾 | S5↔S6 | 雾中幻见 Grace(崩溃)↔ 雾中 Ruby 鬼魂(重生)——首尾呼应的两场田野戏 |

(图标仅文档用;widget 内不用 emoji,以颜色 + 文字表达。)

---

## 6. 美术方向

- **像素风**:限定调色板、分块、banded(色带)而非渐变,逐帧 / 立绘像素。
- **调色板**:煤烟黑 `#14110e` / 炉火橙 `#c2592a` / 煤气灯琥珀 `#e0a64e` / 血红 `#a3231d` / 冷夜蓝 `#2b3a4a` / 雾灰 `#7d8287` / 做旧纸 `#d9c8a4`。
- **分季情绪**:S1 工业脏拍暖 → S2–3 高墙华贵 → S4 复仇冷硬 → S5 萧条爵士 → S6 阴冷死亡。
- **氛围**(自有引擎零约束,可比 widget 浓得多):胶片颗粒、钨丝暖光、飘烟、软木纹理、红线投影、letterbox 黑边。
- **卷宗美学**:做旧照片(图钉 + 微旋转)、打字机字体、剪报衬线、电报等宽、红线。
- **人物立绘**:手工像素肖像(还原 Tommy/Grace/Polly… 的辨识度 + 三件套 tweed、扁帽、煤气灯打光),非占位剪影。
- 字体:展示用衬线(Playfair 类)+ 打字机(Special Elite 类)+ 标牌(Oswald 类),并行加载消 FOUT,带系统兜底。

---

## 7. 音频

Web Audio 程序化芯片配乐(无音频文件):**分季主题动机变调**(S1 工业脏 → S5 爵士 → S6 阴冷)。SFX:枪响、火柴 / 划刀、电报机、马蹄、火焰。`localStorage` 静音持久化。**配乐变化需用户亲耳听后给方向(我无法自测音频)。**

---

## 8. 核查纪要(原稿已修正的 7 处硬伤)

1. Grace 死于 **S3E2 慈善募捐晚宴**(非婚宴),凶手是 **Changretta 杀手**(为被 John 弄瞎的 Angel 报仇),非俄国人——接上 S4 复仇线。
2. 割喉 Father Hughes 的是 **Michael**,非 Tommy。
3. **Bonnie Gold 死于 S5**(非 S4);杀 **Luca 的是诈死的 Arthur**(非 Tommy)。
4. S5 泄密是 **Finn→Billy Grade→IRA**,内鬼身份 S5 是悬案、S6 才挑明;Michael/Gina 搞的是商业夺权,**非行刺泄密**。
5. **Polly 死于 S5 终幕(IRA 报复)**,非 S6 被 Billy Boys 杀;S6 开场她已不在(现实:Helen McCrory 2021 病逝)。
6. S6"将死"是 **Mosley 买通 Dr. Holford 的假诊断局**(tuberculoma),非误诊。
7. 结局在 **Miquelon 岛**(非波士顿);**Ruby 鬼魂**点醒 Tommy 识破假死。
> 另:Campbell 全名 Chester(S2 升 Major);**Darby** Sabini(非 Derby);S2 刺杀目标 Field Marshal Henry Russell、幕后 Churchill+Campbell(非 S3 才登场的经济联盟)。

---

## 9. 范围(YAGNI)

**做**:S1–S6 共 35 beat(+ 序幕 / 终幕);5 条暗线;人物名册 + 谢尔比家族树 / 帮派势力图;中英双语;红线板 + 电影场景双视图;分季配乐;持久化 / a11y / 移动端 / 性能;og 分享卡。

**不做(v1)**:大电影《The Immortal Man》(`season:7` 留接口,上映 / 资料明确后补);逐集 / 逐对白级颗粒度;部署对外发布(需用户点头)。

---

## 10. 里程碑(细节交给实现计划)

按 aegon 的分层节奏:
1. **骨架**:数据模型 + BOARD 视图 + SCENE 视图 + 视图切换 + 3–4 个样板 beat 打通。
2. **铺内容**:35 beat 全量中英双语 + 场景 tableau。
3. **导航与暗线**:红线板三路径(暗线 / 季 / 人物)、卷宗卡、名册、家族 / 势力树、RESUME。
4. **音频**:分季芯片配乐 + SFX + 静音持久化。
5. **打磨**:#35 放大高潮、#15 重锤、过渡运镜、性能(离屏暂停)、a11y(键盘 / 焦点 / reduced-motion)、移动端、消 FOUT。
6. **分享**:og.png 1200×630 + meta + favicon。

---

## 11. 风险 / 待办

- **最大成本 = 美术**:35 个像素场景 + 人物立绘是主要工作量(用户已选最沉浸的"逐关键事件超长卷",接受体量)。
- **音频方向**需用户亲耳反馈。
- **大电影**剧情未公开,故本版不做;留接口。
- **项目命名** `peaky-dossier` 暂定,可改。

---

## 12. 资料来源(canon-check)

Peaky Blinders Fandom wiki(peaky-blinders.fandom.com:角色 / 剧集页)、Wikipedia(*Peaky Blinders (series 1–6)* / *List of Peaky Blinders episodes* / *List of Peaky Blinders characters*)、Den of Geek / ScreenRant / Newsweek / TV Guide / Distractify / Netflix Tudum 等复盘。每项死亡 / 年份 / 人名 ≥2 源交叉。
