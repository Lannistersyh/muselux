# MuseLux｜品味 · 工艺 · 传奇

一本可以离线阅读的奢侈品小杂志，含英文实物款式栏目与中文品牌、经典设计故事。原生 HTML / CSS / JavaScript，无后端、无登录、无交易。

在线阅读：**https://lannistersyh.github.io/muselux/**  
源码仓库：**https://github.com/Lannistersyh/muselux**

手机可用 Safari、Chrome 或 Edge 直接打开在线地址，也可以分享链接给其他人。网站为公开阅读项目，无需注册账号。

## 打开方式

直接双击本目录的 **index.html**，使用当前版本的 Chrome、Edge 或 Safari 打开。无需安装软件包、启动服务器或运行构建命令。也可以将整个目录复制到另一台电脑后打开。

所有页面已预生成完整 HTML。图片、字体与搜索数据均在本地；断网不会影响正文、插画、品牌筛选和搜索。资料外链需要联网。禁用 JavaScript 时正文和站内链接仍可阅读，筛选、搜索和订阅演示需要 JavaScript。

## 内容与页面

- **40 个品牌档案：36 个商品品牌 + 4 个合作/联名品牌**，覆盖全部单品。新增 LOEWE、Miu Miu、The Row、Diesel、Balenciaga、Alaïa、Saint Laurent、Chloé、David Yurman、Swarovski、FRED、Boucheron、Pomellato、Moynat、Chrome Hearts、Diptyque、Le Labo、Byredo、Maison Francis Kurkdjian、Jo Malone London；Baccarat为晶红香氛创作合作品牌，adidas、Versace、fragment design 单独标注为联名品牌。
- 品牌页包含原创介绍、有来源的历史时间线、设计细节，以及按品类归集的全部本站款式。156 个单品详情与品牌页双向关联；9 条品牌合作/联名同时链接参与品牌。索引、品类筛选和搜索同步收录，品牌卡片数量由完整目录计算。
- **The Style Edit：38 款实物图商品，项链与首饰各 7 款，包包、腕表、丝巾各 5 款，香水 9 款**。每款包含英文介绍、三条设计细节、搭配建议、具体型号或商家挂牌编号、材质尺寸、明确口径的美元参考价及商品/图片来源。首页支持按品类切换，各品类页优先显示本站实物精选，一般品类保留 3–5 个位置；本次银饰扩展后，项链与首饰支持 3–8 款，香水专题扩展至 9 款，保留原有款式。
- **The Bag Yearbook：2022–2026，每年 4 款热门精选 + 2 款限量/限定款，共 30 条年度记录。** 包含实物图、英文设计与搭配介绍、当年入选依据、发行信息和有来源的美元价格。首页与包袋页提供入口，独立页面 `bags-by-year.html` 支持五年份切换和年份直达链接。
- **The Necklace Yearbook / The Jewelry Yearbook：项链与首饰各 30 条年度记录，共新增 60 条。** 两个独立页面同样覆盖 2022–2026，每年各 4 款热门精选 + 2 款限量/限定联名；首饰以戒指、手链和耳饰为主。首页提供三类年鉴入口，品类页与站内搜索同步收录。
- 另保留 28 个经典设计词条，共 **66 个核心单品页**；鞋履与墨镜作为生活配件扩展收录于首饰品类。未核实具体美元型号的经典词条直接提示向美国官方渠道询价，不做汇率猜算。
- 12 篇原创杂志文章，每篇正文至少 800 个中文字；正文不依赖在线加载。
- 6 个品类页：包包、项链、首饰、腕表、丝巾、香水。
- 三类年度栏目共有 90 个英文详情页；全站共 **156 个单品/年度详情页、227 页 HTML**。
- The Style Edit 的 38 张本地首图照片约 3.12 MiB，年度包袋照片另存于 `assets/img/bag-years/`，新增项链与首饰的 60 张实物照片保存于 `assets/img/jewel-years/`；另有 42 个原创 SVG。照片逐款署名并保留原图来源，未声称获得开放图片许可；没有复制第三方文章。

2026-10-28 新增 **女性风格指南 / The Style Atlas**：`womens-style.html`，包含 **Mob Wife（复古强势风）、Napoleon Core（拿破仑风）、千金风** 三个独立详情页。参考不爱吃榴莲的Nana于2026-09-30发布的《请选择Queen B下班风格》（BV1WUao6UEBa，约64秒）。基于实际关键帧与画面标签整理 **9条带时间点的观察、9组品牌对应与9件本站搭配推荐**；13个可读官方设计来源为具体剪裁、扣饰、珠链、套装与手袋特征提供依据。品牌对应属于编辑判断，没有把推荐款式写成视频同款，也没有采纳视频未经核实的媒体趋势判断。

三张引用画面分别取自00:09、00:19、00:37，保留作者水印与原视频入口，合计 **82,068字节**；原视频及完整台词未放入网站。品牌对应覆盖Gucci、Versace、Fendi、Dior、Chanel与Van Cleef & Arpels，拿破仑风另提供Balmain军官扣外套的官方延伸阅读；它不是本站新增商品。已有商品的具体型号、美元价格、历史/快照口径和实际日期完整保留。原有 **156条单品及年鉴记录、40品牌、316次图库展示** 均保持；全站现为 **227页HTML**。

入口加入首页、主导航、页脚，相关品牌与九件单品有风格回链。站内搜索新增“穿搭”类型，支持中英文风格名称与关键词。通过 **18项维护回归、98项前端断言、全站静态页面/链接/资源检查、两次构建一致性**；另在实际浏览器检查404像素窄屏的栏目、三详情及搜索，800/1280像素检查拿破仑页布局与导航，无横向溢出，手机菜单和搜索正常。属于代表页面预览，不是所有手机硬件或浏览器的穷尽兼容测试。记录见 `reports/womens-style-validation.json`；内容提交 `2f8c49d10e0df46ec2b9bee60319fe079f086751` 已完成GitHub Pages构建，全部 **235个本轮公开页面与运行/图片资源** 均与本地逐字节一致，见 `reports/womens-style-deployment-validation.json`。

2026-10-27 新增独立 **香氛品牌 / The Perfumery Edit** 栏目：`perfumery.html`，首页、主导航、页脚与香水品类均可进入。首期五家：**Diptyque、Le Labo、Byredo、Maison Francis Kurkdjian、Jo Malone London**，各配一份品牌档案与一款具体容量、浓度的香水。代表作分别为 **Tam Dao EDP 75 ml US$260、Santal 33 EDP 100 ml US$348、Bal d’Afrique EDP 100 ml US$330、Baccarat Rouge 540 EDP 70 ml US$360、Wood Sage & Sea Salt Cologne 100 ml US$175**。前面三款为官网当前结构化美元报价，后面两款保留官方美国页快照口径；Baccarat 官网 USD 报价另对晶红作交叉核对，Jo Malone 加拿大资料仅核对型号与图片，不使用加币价格。

新增 **12 张真实摄影、5 个香水图库与6份品牌档案**，其中 Baccarat 为创作合作品牌，不作为第六家香水专门品牌。每款至少两张不同原始照片，Tam Dao 与 Santal 33 各三张；图片包括背面、喷头、俯拍、手持与原始包装，分别如实标注。新增图片共 **1,272,432 字节**；现为 **156 个图库、316 次图片展示、40 品牌、223 页 HTML**。原有 151 条商品与三类年鉴对象及截止日逐字段保留，未给旧商品推进日期。

本次通过 **15 项维护回归、78 项前端行为断言、全站静态链接/资源检查与两次构建一致性**。新图已逐张完整像素解码并目视核对；未作真实浏览器或手机布局视觉复测。记录见 `reports/perfumery-validation.json`，内容提交 `04d7bee9b54d3c4b70756ab9aa6794228d1b5d2e` 已完成 GitHub Pages 构建，全部 **240 个本轮公开页面及运行/图片资源** 均与本地逐字节一致，见 `reports/perfumery-deployment-validation.json`。

2026-10-27 核实摩奈 Hôtel Moynat 70 cm 真丝方巾 **C30663-0001 / variant 59928339710297** 的美国官网状态已由线上暂不可售变为核验时可售，价格仍为 **US$400**。当前详情已改为带日期的可售说明；2026-10-24 的不可售记录保留为历史快照。只更新这一型号实际复核的报价与库存证据，其余 150 条商品、全部照片、三类年鉴及截止日保持原样。

2026-10-27 更新已通过 211 页检查、13 项维护回归和 66 项前端行为断言；216 个公开页面与运行资源均与本地逐字节一致。记录见 `reports/daily-update-2026-10-27.json`、`reports/daily-deployment-2026-10-27.json`。

2026-10-26 新增 **Chrome Hearts / 克罗心六款经典银饰精选**：Baby Fat 十字吊坠、Dagger 匕首吊坠、Vine Dagger Dog Tag（含 30 英寸球链）、Cemetery Cross 戒指、CH Forever 戒指、7 英寸 Paper Chain 手链。新增 **14 张不同视角实物照片，共 542,592 字节**；每款至少两图，Baby Fat 与 Dog Tag 各三图。首页、项链与首饰页提供克罗心入口，品牌图鉴与中英文搜索同步收录。六款全部为明确署名商家的美元转售挂牌参考，保留具体商品成色与包含物说明，不宣称官方定价、销量名次或限量发行。现为 **151 个实物图库、304 次照片展示、34 品牌、211 页 HTML**，原有 145 条商品及三类年度对象逐字段保留。

Chrome Hearts 更新已通过 211 页静态检查、13 项维护回归与 66 项前端行为断言；全部 230 个本轮公开页面及相关资源与本地逐字节一致。记录见 `reports/chrome-hearts-validation.json`、`reports/chrome-hearts-deployment-validation.json`。

2026-10-24 新增 Hôtel Moynat 棕色 Hobo 包（CI3625-0760，US$2,550）与 70 cm 多色真丝方巾（C30663-0001，US$400；官网当前显示线上暂不可售），并补齐摩奈品牌档案。两款均保留英文介绍、具体材质、尺寸、官方美元价格及不同视角实物照片。它们属于限定联名胶囊，官方未公布生产数量；10 月 23 日为新闻发布日期，未写成首次发售日期。现为 **145 个双视角单品页、290 次照片展示、33 个品牌档案与 204 页 HTML**。原有 143 条商品、三类年度选集及证据截止日保持原样。四张新照片采用完整画面 WebP，共 726,784 字节（约 710 KiB），原始下载摘要和转换方式单独留存。

2026-10-23 补齐全站 **143 个单品详情页的双视角实物图库**，共 286 次照片展示；新增 **129 个独立原图文件**（约 14.51 MiB）。具体商品保留原图并增加侧面、背面、佩戴、内部或不同拍摄角度的细节图；28 个经典系列词条以两张实物照片展示明确标注的代表型号。跨年份相同型号复用已核验图源。详情页支持缩略图、方向键/Home/End，关闭脚本时两图均可阅读，点大图可打开原尺寸本地照片。

2026-10-24 发布已通过全部 204 页检查、11 项维护回归与 58 项前端行为断言；GitHub Pages 公开的 342 个页面与相关资源均与本地逐字节一致。每日资料和发布验收分别见 `reports/daily-update-2026-10-24.json`、`reports/daily-deployment-2026-10-24.json`。

图库来源单独保存在 `tools/research/product-views-*.json`，由 `tools/product_gallery.py` 按单品 ID 读取，不覆盖价格、年份证据或商品核验日期。新增或替换商品必须同步提供匹配型号的第二张照片；经典家族须说明具体代表型号。原始商家未重复制造商编号的两条档案联名照片，图注明确说明以独有联名设计匹配。校验器检查全目录覆盖、型号、尺寸、署名、来源、重复文件与无脚本访问；实际像素解码另记录在 `reports/gallery-image-validation.json`。

## 目录

```
index.html / about.html / brands.html / search.html / 404.html
womens-style.html / style/   女性风格栏目与三篇指南
perfumery.html   香氛品牌专题（保留六品类体系）
bags-by-year.html / necklaces-by-year.html / jewelry-by-year.html
                2022–2026 包袋、项链与首饰年份页
brand/          品牌页
cat/            六品类聚合页
item/           单品词典
mag/            杂志长文
assets/css/     唯一主样式 main.css
assets/js/      data.js、render.js、main.js
assets/img/     原创概念插画；products/、bag-years/、jewel-years/ 与 views/ 为实物照片
assets/fonts/   本地字体和对应 OFL 许可证
tools/          可选的内容维护脚本与可编辑数据
tools/research/ 实物商品与三类年度选集的来源、价格证据与图片权利记录
reports/        验收记录、页面清单、商品来源清单和预览截图
```

## 如何新增一条数据（三行指南）

1. 在 `tools/content.json` 相应的 `brands`、`items` 或 `articles` 数组中复制一条对象，填写唯一 `id` 和正文；单品的 `brand` 必须对应品牌档案，品牌联名另填 `collaboratorBrands`。品牌的 `classicItems` 保留人工精选词条，全部款式关联由生成器自动计算。
2. 将对应的封面保存到 `assets/img/`，文章填写 `cover`；实物单品填写 `image`、固有宽高、`imageSource`、`imageCredit` 与权利说明，经典词条的列表插画默认用 `<id>.svg`，详情实物图库维护于 `tools/research/product-views-*.json`；每条须提供具体代表型号及两张实物照片。
3. 在本目录运行 `python3 tools/generate.py`，再运行 `python3 tools/validate.py`，完成后双击 `index.html` 查看。

## 每日更新与代码核验

已在当前聊天创建每日任务“**MuseLux 每日更新与代码核验**”，北京时间每天 **09:00** 执行。此任务通过本地 Codex 桌面应用运行，届时电脑需要开机、应用保持运行且项目文件夹可访问；公开网站的日常访问不依赖电脑开机。

2026-10-23 日更补入 Hublot Classic Fusion Tributo 白金 38 mm 腕表及宇舶品牌档案，保留全部已有单品。官网索引美元参考为 US$30,900，实物照片同时展示两种金色，白金报价对应左侧腕表；图注与规格分别注明。LVMH 10 月 21 日文章为新闻发布日期，不作首次发售日期推断。

每天从品牌官网、官方新闻等一手资料检查六品类，轮换重点品类并优先处理发生变化或失效的来源。有可靠更新才修改商品、美元参考价、限定资料或品牌档案，不为凑每日更新重写内容。限量与限定联名分别标注，历史报价与当前报价分开；2022–2025 年保留档案语境，2026 年每类仍为四款热门加两款特别版。

只有实际核实后才修改来源记录的 `checkedAt`，合并器保留逐条日期；栏目总日期取真实记录中的最大日期。2026 年新增入选证据时，在对应研究文件的年份记录中明确修改 `cutoff`，不能只改价格日期来推进收录范围。历史年度可以引用后来发布的官方年度回顾，资料发布日期仍须不晚于实际核验日期。14 条珠宝记录曾被合并器统一标为 10 月 20 日，现已恢复到原始研究记录的实际 10 月 19 日。

女性风格内容维护于 `tools/womens_styles.json`，由 `tools/womens_styles.py` 生成栏目与详情。视频来源及抽帧摘要在 `tools/research/womens-style-video-evidence.json`，品牌设计证据在 `womens-style-brand-evidence.json`。新指南不修改六品类与产品目录；推荐引用既有精确产品ID，换款或退休商品时同步调整引用。视频标签、可见细节、官方设计事实和编辑匹配理由分别保留，不能把系列文案合并成某一件衣服的全部特征，也不凭画面鉴定材质、价格或同款。

香氛品牌选品与栏目文案维护于 `tools/perfumery.json`，五款活跃商品源为 `tools/research/perfumery-products.json`，品牌源为 `brand-expansion-g.json`，图库源为 `product-views-perfumery.json`，原始图片摘要与来源记录见 `perfumery-evidence.json`。新增香氛仍属于 `fragrance`，不建立第七品类；香水总上限 9，栏目每期 3–5 家。Baccarat 通过 `collaboratorBrands` 关联，当前常规 EDP 不引用早期编号版本的限量身份。

Chrome Hearts 活跃商品源为 `tools/research/chrome-hearts-products.json`，图库源为 `tools/research/product-views-chrome-hearts.json`；另两份 `chrome-hearts-necklaces.json` / `chrome-hearts-jewelry.json` 保留原始分组研究与导出记录，不直接用于日常合并。转售记录须包含 `sellerName`、`itemCondition`、`listingReference`、`priceAsOf`、`availabilityEn`，采用 `priceStatus: resale-ask`；商家挂牌编号不能写成制造商 SKU。`tools/style_policy.py` 统一价格类型与扩展数量范围，卡片、详情与搜索均保留转售口径。

修改研究记录后，按需要运行 `tools/apply_style_edit.py`、`tools/apply_bag_yearbook.py`、`tools/apply_jewel_yearbooks.py`，再运行 `tools/apply_brand_catalog.py`。不要重新播种内容。替换实物款式会同步清理旧的品牌精选引用；生成器仅移除上一份页面清单中已经退休的 HTML，不删除清单外的自有文件。

发布前统一执行：

```bash
python3 tools/check_site.py
```

此命令使用 Python 标准库和 Node.js，无额外软件包。它运行维护回归测试、实际前端脚本的行为检查、语法检查、两次构建一致性、页面清单、品牌关系、JSON-LD、搜索数据与资源摘要核对，并生成 `reports/code-check-validation.json`。失败时停止发布。浏览网站仍无需 Python 或 Node.js。

只提交本轮自己的、具有实质内容变化或代码修复的文件，保留用户改动。通过检查后推送现有 GitHub main，确认 Pages 构建与受影响的公开文件，再更新验收记录及完整压缩包。无可靠变化时不改日期、不作空提交；网络或来源访问受阻时保留原报价与实际日期，不把访问失败写成下架。

维护脚本只使用 Python 标准库。网站的**浏览与运行不需要 Python**。`seed_content.py` 是初次内容的备份，维护现有内容时直接修改 `content.json`，不要运行 seed 脚本覆盖自己的编辑。`draw_assets.py` 用于重新绘制原始插画，会覆盖同名 SVG；替换图片后不要运行它覆盖新素材。

## 数据脚本与 80 KB 预算

运行时搜索与筛选所需字段由普通 `<script src="assets/js/data.js">` 提供，没有 ES Modules，也没有 fetch 本地 JSON。完整故事、规格与来源已预渲染到 HTML；数据脚本只发送搜索字段，并编码成 gzip + Base64，用浏览器内置 `DecompressionStream` 在内存中解码。运行时 JavaScript 总体积由校验器控制在 80 KiB 以内，当前体积见 `reports/static-validation.json`。

解码完成后得到 `window.MUSELUX_DATA`，`window.MUSELUX_READY` 是对应 Promise。Chrome / Edge 80+、Safari 16.4+ 支持所需的原生能力；目标为最新两个大版本。页面正文已经预渲染，数据只为搜索和筛选提供增强。所有外部来源链接都是普通阅读入口，首屏和站内交互不请求网络。

## 图片与字体替换

SVG 表达的是概念、轮廓与阅读气氛，不代表产品实际外观，不能用于真伪判断。The Style Edit 的 33 张首图照片来自所列品牌的官方商品图片、集团新闻图及明确署名的转售商家实物图库，未经过生成式改绘；颜色、型号与图源一同记录于 `tools/research/` 和 `reports/product-sources.json`。年度照片的来源与权利记录分别见 `reports/bag-yearbook-sources.json` 和 `reports/jewel-yearbook-sources.json`。照片版权归品牌或相应权利人；公开可见和署名本身不等于开放许可，本站不宣称品牌授权或合作。后续替换请保留来源和权利依据。

替换图片后保留宽高信息与描述性 alt；如改变文件名，请同步修改内容数据或生成模板。基础词典插画源脚本在 `tools/draw_assets.py`；12 张杂志封面由 `tools/draw_journal_covers.py` 独立维护。

Oswald 和 Raleway 已本地保存，附 SIL Open Font License。中文标题优先使用 Noto Serif SC，未安装时回退到 macOS 宋体 / STSong / SimSun / serif；正文使用系统中文字体。无需连接 Google Fonts 服务。

## 杂志专题封面

12 篇文章各有独立构图，保存在 `assets/img/journal/`：选包生活清单、双包结构比较、五种珠宝符号、贝壳与珍珠、三种金属切面、皮革样片、流动丝巾、Vintage 档案、放大表盘、收纳养护静物、三种礼物包装和香气试纸。保留共同的字体与刊物标识，主体、配色和叙事随文章变化。插画为原创概念视觉，实物商品照片继续单独署名。

修改封面构图后执行 `python3 tools/draw_journal_covers.py`，再生成和校验网站；此脚本只更新 12 张文章封面及对应 `cover` / `coverAlt` / `coverScene` 字段。基础插画生成器也调用同一封面模块，避免后续重新生成时退回重复双环。正文页完整显示 3:2 画面，CSS 与脚本 URL 使用内容摘要，更新后浏览器可取得新资源。

## 内容边界与参考资料

品牌历史和材料资料在关于页与文章末尾提供官方或专业机构阅读入口。编辑建议与历史资料分开理解。Lady Dior 的初创年份在不同官方页面有 1994 / 1995 两种表述，词条保留此差异，并明确 1995 年赠予戴安娜王妃的传播节点。

The Style Edit 采用 **USD 并逐款标注价格口径**：原有 27 款为具体型号的美国零售参考；新增 6 款 Chrome Hearts 为图中具体商品的商家转售挂牌价，明确标注成色、尺码、含链情况与观察日期，不是品牌官方零售价。初始 24 款的来源核对日为 2026-10-19，其中 16 款有当日官方商品页证据，8 款使用标注时效的官方页面快照；后续新增 Hublot 与两款 Moynat 分别保留各自实际核验日期和价格口径。快照说明直接显示在对应卡片和详情中。价格不是库存或结算承诺；请通过详情页官方链接确认最新价格。原人民币区间已从页面移除，未用汇率换算替代。

更新这批商品记录时，先修改 `tools/research/*.json`，运行 `python3 tools/apply_style_edit.py` 合并到 `content.json`，再运行生成与校验脚本。合并器可重复运行，不访问网络、不重新下载图片、不换算货币；原始采集限制仍保留在研究文件中。

年度包袋由 `tools/research/bag-years-*.json` 维护，运行 `python3 tools/apply_bag_yearbook.py` 合并。每年四款热门是依据当年 Lyst 季度需求信号与有日期的时尚报道形成的编辑精选，来源排名保留其原始时期，不是统一的全球年度销量榜。具体照片可能展示该热门包型的后续配色或材质版本，详情明确记录图中型号；限量/限定照片对应所述特别版本。

限量类型分别标注编号版、明确限量版和季节限定系列。季节限定不等于品牌公布固定生产数量。美元价格明确区分当前美国零售参考、发布期价格、报道价格、注明日期的拍卖结果/二手挂牌和未公开报价；没有将转售挂牌价写成原始零售价。2026 年收录截止日为 2026-10-19。

项链与首饰年度数据由 `tools/research/jewel-years-*.json` 维护，运行 `python3 tools/apply_jewel_yearbooks.py` 合并后，再运行生成器与校验器。合并过程保留原有核心商品、包袋年鉴及其他栏目，`reports/jewel-yearbook-sources.json` 汇总新增 60 条的来源与版本证据。当前美国商品参考价格可在 2026-10-20 复核；2026 年入选证据范围仍截至 2026-10-19，二者在详情页分别显示。

`reports/bag-yearbook-sources.json` 保存 30 条年度记录的入选来源、价格依据与版本证明。新增品牌资料保存在 `tools/research/brand-expansion-*.json`，通过 `python3 tools/apply_brand_catalog.py` 合并；新增品牌须先合并档案，再合并相应实物款式。`tools/brand_catalog.py` 每次生成时重新关联核心单品与三类年鉴，自动更新数量、品类和中英文搜索别名；发现没有品牌档案的单品会停止生成，避免再次遗漏。此前 142 条记录及 150 条品牌关联的历史验收见 `reports/brand-catalog-validation.json`；当前 151 条记录及 159 条关联见 `reports/static-validation.json`。

The Row 的成立年份采用现行官网的 2005 年，并保留 CFDA 使用 2006 年的口径差异；Alaïa 区分母公司采用的 1964 年巴黎工作室起点与基金会所记的 1983 年品牌及巴黎首秀阶段，说明直接显示在品牌页。

固定免责声明：MuseLux 是个人兴趣驱动的非商业内容项目，所有品牌名称与产品名称的权利归其权利人所有；价格信息仅为整理时的公开参考，请以品牌官方渠道为准。

订阅框仅演示输入校验与行内确认，不保存邮箱，也不发送邮件。不存在购物车、下单、支付或账号功能。

## 检查与预览

可运行 `python3 tools/validate.py` 检查全部页面、链接、锚点、图片、内容长度和运行时 JS 体积。初版浏览器验收使用 Chromium；年度包袋及项链/首饰更新按照用户选择执行静态检查；包袋首轮的 29 项 DOM 检查记录单独保留。当前三类年度页使用临时 LinkeDOM 加载实际生成的 HTML 和运行脚本，检查五年份切换、直达链接、键盘操作和分品类年度搜索，结果见 `reports/jewel-yearbook-dom-validation.json`。没有新增浏览器标签或声称完成本轮手机视口视觉复测。完整结果见 `reports/自检报告.md`。

如希望用 HTTP 预览，可在本目录运行 `python3 -m http.server 4173`，访问 `http://localhost:4173/`；这只是可选维护方式。

## GitHub Pages 发布与更新

GitHub Pages 从 `main` 分支的根目录发布，`.nojekyll` 保留原生静态文件；推送后由 GitHub 自动更新网站。网站 URL 与仓库地址配置在 `tools/site.json`，生成器据此生成 canonical、Open Graph URL、站点地图，以及适配嵌套路径的 404 页面。

更新内容后，在本目录执行：

```sh
python3 tools/generate.py
python3 tools/validate.py
git add .
git commit -m "Update MuseLux content"
git push origin main
```

`tools/` 是内容维护源码，GitHub Pages 不执行 Python。网页与数据已生成，访问者只需打开链接。
