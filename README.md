# MuseLux｜品味 · 工艺 · 传奇

一本可以离线阅读的奢侈品小杂志，含英文实物款式栏目与中文品牌、经典设计故事。原生 HTML / CSS / JavaScript，无后端、无登录、无交易。

在线阅读：**https://lannistersyh.github.io/muselux/**  
源码仓库：**https://github.com/Lannistersyh/muselux**

手机可用 Safari、Chrome 或 Edge 直接打开在线地址，也可以分享链接给其他人。网站为公开阅读项目，无需注册账号。

## 打开方式

直接双击本目录的 **index.html**，使用当前版本的 Chrome、Edge 或 Safari 打开。无需安装软件包、启动服务器或运行构建命令。也可以将整个目录复制到另一台电脑后打开。

所有页面已预生成完整 HTML。图片、字体与搜索数据均在本地；断网不会影响正文、插画、品牌筛选和搜索。资料外链需要联网。禁用 JavaScript 时正文和站内链接仍可阅读，筛选、搜索和订阅演示需要 JavaScript。

## 内容与页面

- 15 个品牌：Hermès、Chanel、Louis Vuitton、Dior、Gucci、Prada、Bottega Veneta、Celine、Cartier、Tiffany & Co.、Bvlgari、Van Cleef & Arpels、Rolex、Omega、Fendi。
- **The Style Edit：24 款实物图商品，六类各 4 款**。每款包含英文介绍、三条设计细节、搭配建议、具体型号与材质尺寸、税前美元参考价及官方商品/图片来源。首页支持按品类切换，各品类页优先显示这四款。
- 另保留 28 个经典设计词条，共 **52 个单品页**；鞋履与墨镜作为生活配件扩展收录于首饰品类。未核实具体美元型号的经典词条直接提示向美国官方渠道询价，不做汇率猜算。
- 12 篇原创杂志文章，每篇正文至少 800 个中文字；正文不依赖在线加载。
- 6 个品类页：包包、项链、首饰、腕表、丝巾、香水。
- 首页、品牌索引、搜索、关于与 404，共 **90 页**。
- 24 张本地保存的品牌官方实物照片（约 2.03 MiB），另有 42 个原创 SVG。照片逐款署名并保留原图来源，未声称获得开放图片许可；没有复制第三方文章。

## 目录

```
index.html / about.html / brands.html / search.html / 404.html
brand/          品牌页
cat/            六品类聚合页
item/           单品词典
mag/            杂志长文
assets/css/     唯一主样式 main.css
assets/js/      data.js、render.js、main.js
assets/img/     原创概念插画；products/ 为实物照片
assets/fonts/   本地字体和对应 OFL 许可证
tools/          可选的内容维护脚本与可编辑数据
tools/research/ 24 款商品的官方来源、价格证据与图片权利记录
reports/        验收记录、页面清单、商品来源清单和预览截图
```

## 如何新增一条数据（三行指南）

1. 在 `tools/content.json` 相应的 `brands`、`items` 或 `articles` 数组中复制一条对象，填写唯一 `id` 和正文；品牌同步填写 `classicItems`。
2. 将对应的封面保存到 `assets/img/`，文章填写 `cover`；实物单品填写 `image`、固有宽高、`imageSource`、`imageCredit` 与权利说明，经典插画单品默认用 `<id>.svg`。
3. 在本目录运行 `python3 tools/generate.py`，再运行 `python3 tools/validate.py`，完成后双击 `index.html` 查看。

维护脚本只使用 Python 标准库。网站的**浏览与运行不需要 Python**。`seed_content.py` 是初次内容的备份，维护现有内容时直接修改 `content.json`，不要运行 seed 脚本覆盖自己的编辑。`draw_assets.py` 用于重新绘制原始插画，会覆盖同名 SVG；替换图片后不要运行它覆盖新素材。

## 数据脚本与 80 KB 预算

运行时搜索与筛选所需字段由普通 `<script src="assets/js/data.js">` 提供，没有 ES Modules，也没有 fetch 本地 JSON。完整故事、规格与来源已预渲染到 HTML；数据脚本只发送搜索字段，并编码成 gzip + Base64，用浏览器内置 `DecompressionStream` 在内存中解码。运行时 JavaScript 约 23.3 KiB，低于 80 KiB 预算。

解码完成后得到 `window.MUSELUX_DATA`，`window.MUSELUX_READY` 是对应 Promise。Chrome / Edge 80+、Safari 16.4+ 支持所需的原生能力；目标为最新两个大版本。页面正文已经预渲染，数据只为搜索和筛选提供增强。所有外部来源链接都是普通阅读入口，首屏和站内交互不请求网络。

## 图片与字体替换

SVG 表达的是概念、轮廓与阅读气氛，不代表产品实际外观，不能用于真伪判断。The Style Edit 的 24 张照片下载自所列品牌的官方商品图片，未经过生成式改绘；颜色、型号与图源一同记录于 `tools/research/` 和 `reports/product-sources.json`。照片版权归品牌或相应权利人；公开可见和署名本身不等于开放许可，本站不宣称品牌授权或合作。后续替换请保留来源和权利依据。

替换图片后保留宽高信息与描述性 alt；如改变文件名，请同步修改内容数据或生成模板。插画源脚本在 `tools/draw_assets.py`。

Oswald 和 Raleway 已本地保存，附 SIL Open Font License。中文标题优先使用 Noto Serif SC，未安装时回退到 macOS 宋体 / STSong / SimSun / serif；正文使用系统中文字体。无需连接 Google Fonts 服务。

## 内容边界与参考资料

品牌历史和材料资料在关于页与文章末尾提供官方或专业机构阅读入口。编辑建议与历史资料分开理解。Lady Dior 的初创年份在不同官方页面有 1994 / 1995 两种表述，词条保留此差异，并明确 1995 年赠予戴安娜王妃的传播节点。

The Style Edit 的价格均为 **USD、未含税、图中具体型号的美国零售参考价**。来源核对日为 2026-10-19；16 款有当日官方商品页证据，8 款使用标注时效的官方页面快照，快照说明直接显示在对应卡片和详情中。价格不是库存或结算承诺；请通过详情页官方链接确认最新价格。原人民币区间已从页面移除，未用汇率换算替代。

更新这批商品记录时，先修改 `tools/research/*.json`，运行 `python3 tools/apply_style_edit.py` 合并到 `content.json`，再运行生成与校验脚本。合并器可重复运行，不访问网络、不重新下载图片、不换算货币；原始采集限制仍保留在研究文件中。

固定免责声明：MuseLux 是个人兴趣驱动的非商业内容项目，所有品牌名称与产品名称的权利归其权利人所有；价格信息仅为整理时的公开参考，请以品牌官方渠道为准。

订阅框仅演示输入校验与行内确认，不保存邮箱，也不发送邮件。不存在购物车、下单、支付或账号功能。

## 检查与预览

可运行 `python3 tools/validate.py` 检查全部页面、链接、锚点、图片、内容长度和运行时 JS 体积。浏览器验收使用 Chromium；本机没有把 Safari 和 Edge 都执行一遍，兼容性依据所使用的标准 API 与样式回退。完整结果见 `reports/自检报告.md`。

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
