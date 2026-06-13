# 浴血黑帮卷宗 — 实现计划 Phase 2:铺满内容(全 35 beat)

> 续 Phase 1。引擎已跑通,本期是内容填充 + 季导航。沿用既有数据模型,无架构改动。

**Goal:** 把 5 个样板 beat 扩到全 35 beat(+序幕/终幕),整条谢尔比家史可经「上/下一幕」走完;补全人物名册与 5 条暗线;红线板加季标签,精选钉证物不糊。

**Tech:** 沿用 Phase 1 单文件引擎。新增「像素场景助手库」减少 SVG 重复。

## 关键决定

1. **场景助手库**:加 `bg(bands)`/`figS(x,by,kind,sc,col)`/`fire`/`smoke`/`moon`/`horse`/`windows` 等可复用件;新场景用助手拼,风格统一。**已验证的 5 个老 `SVG_*` 不重构**,只为 30 个新场景服务。
2. **红线板精选**:`BOARD_PINS` 不钉 35 个全事件(会糊),只钉**主要人物**(~12)+ 暗线锚点**关键事件**(~8)。全 35 beat 经场景视图遍历。
3. **季导航**:红线板顶部加季标签(序/S1–S6/全部),按季过滤可见 pin;线索筛选与季筛选二选一(点季清线索,点线索清季)。
4. **时间序 = `SCENES` 数组顺序**:重排 `SCENES` 为完整史序(序幕→S1…S6→终幕),已存在的 5 个 beat 归位。

## 任务

- **T1 场景助手库**:加助手件 + 一个组合壳;不动老场景;自检仍 PASS。
- **T2 序幕+S1(beat 0,1–6)**:补 5 个新 beat(含 s1-guns 归位)+ S1 新人物(Arthur/John/Ada/Finn/Grace/Campbell/Kimber/Danny/Freddie)+ tableau;校验上/下一幕可达、抽查 2 场景。
- **T3 S2(7–12)**:6 beat + 新人物(Alfie/Sabini/Michael/May/Russell/Lizzie)+ tableau;校验。
- **T4 S3(13–18)**:补 5 个(s3-grace 归位)+ 新人物(Hughes/Tatiana/Izabella/Linda/Charlie)+ tableau;校验。
- **T5 S4(19–23)**:5 beat + 新人物(Luca/Aberama/Bonnie/Jessie/Vicente)+ tableau;校验。
- **T6 S5(24–29)**:6 beat + 新人物(Mosley/Gina/Barney/McCavern/Billy Grade/Captain Swing)+ tableau;校验。
- **T7 S6(30–35)+终幕**:补 4 个(s6-ruby/s6-finale 归位)+ 新人物(Jack Nelson/Diana/Holford/Evadne/Duke)+ tableau;校验全 37 面板。
- **T8 暗线 + 精选 BOARD_PINS**:5 条暗线全 `beatIds/pinIds`;扩 `BOARD_PINS` 到精选集;校验每条暗线跨季红线正确。
- **T9 季标签导航**:红线板季过滤;校验按季显示 + 与线索互斥。

每个 T:数据完整性 `__selftest()` 仍 PASS + 预览抽查 + 提交。

## 范围外(留 Phase 3+)

按人物进板、谢尔比家族树/势力图(P3);Web Audio 配乐(P4);#35 放大高潮、真像素立绘、做旧氛围、移动端(P5);og 卡(P6)。
