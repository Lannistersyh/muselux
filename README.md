# MuseLux｜品味 · 工艺 · 传奇

一本可以离线阅读的中文奢侈品小杂志。原生 HTML / CSS / JavaScript，无后端、无登录、无交易。

在线阅读：**https://lannistersyh.github.io/muselux/**  
源码仓库：**https://github.com/Lannistersyh/muselux**

手机可用 Safari、Chrome 或 Edge 直接打开在线地址，也可以分享链接给其他人。网站为公开阅读项目，无需注册账号。

## 打开方式

直接双击本目录的 **index.html**，使用当前版本的 Chrome、Edge 或 Safari 打开。无需安装软件包、启动服务器或运行构建命令。也可以将整个目录复制到另一台电脑后打开。

所有页面已预生成完整 HTML。图片、字体与搜索数据均在本地；断网不会影响正文、插画、品牌筛选和搜索。资料外链需要联网。禁用 JavaScript 时正文和站内链接仍可阅读，筛选、搜索和订阅演示需要 JavaScript。

## 内容与页面

- 15 个品牌：Hermès、Chanel、Louis Vuitton、Dior、Gucci、Prada、Bottega Veneta、Celine、Cartier、Tiffany & Co.、Bvlgari、Van Cleef & Arpels、Rolex、Omega、Fendi。
- 28 个单品词条，附故事、尺寸、材质、辨识线索和带有说明的参考价区间；鞋履与墨镜作为生活配件扩展收录于首饰品类。
- 12 篇原创杂志文章，每篇正文至少 800 个中文字；正文不依赖在线加载。
- 6 个品类页：包包、项链、首饰、腕表、丝巾、香水。
- 首页、品牌索引、搜索、关于与 404，共 **66 页**。
- 42 个原创 SVG 图像文件。无网络产品实物图，无品牌 Logo 图片或第三方文章复制。

## 目录

```
index.html / about.html / brands.html / search.html / 404.html
brand/          品牌页
cat/            六品类聚合页
item/           单品词典
mag/            杂志长文
assets/css/     唯一主样式 main.css
assets/js/      data.js、render.js、main.js
assets/img/     原创概念插画
assets/fonts/   本地字体和对应 OFL 许可证
tools/          可选的内容维护脚本与可编辑数据
reports/        验收记录、页面清单和预览截图
```

## 如何新增一条数据（三行指南）

1. 在 `tools/content.json` 相应的 `brands`、`items` 或 `articles` 数组中复制一条对象，填写唯一 `id` 和正文；品牌同步填写 `classicItems`。
2. 将对应的原创或有权使用的封面保存到 `assets/img/`，并在对象的 `cover` 字段填写路径（单品默认用 `<id>.svg`）。
3. 在本目录运行 `python3 tools/generate.py`，再运行 `python3 tools/validate.py`，完成后双击 `index.html` 查看。

维护脚本只使用 Python 标准库。网站的**浏览与运行不需要 Python**。`seed_content.py` 是初次内容的备份，维护现有内容时直接修改 `content.json`，不要运行 seed 脚本覆盖自己的编辑。`draw_assets.py` 用于重新绘制原始插画，会覆盖同名 SVG；替换图片后不要运行它覆盖新素材。

## 数据脚本与 80 KB 预算

运行时所有数据由普通 `<script src="assets/js/data.js">` 提供，没有 ES Modules，也没有 fetch 本地 JSON。为了保留十二篇长文和十五个品牌的完整内容，同时控制 JavaScript 总体积，生成脚本把可编辑 JSON 编码成 gzip + Base64，并用浏览器内置 `DecompressionStream` 在内存中解码。

解码完成后得到 `window.MUSELUX_DATA`，`window.MUSELUX_READY` 是对应 Promise。Chrome / Edge 80+、Safari 16.4+ 支持所需的原生能力；目标为最新两个大版本。页面正文已经预渲染，数据只为搜索和筛选提供增强。所有外部来源链接都是普通阅读入口，首屏和站内交互不请求网络。

## 图片与字体替换

SVG 表达的是概念、轮廓与阅读气氛，不代表产品实际外观，不能用于真伪判断。替换真实图片时，请使用自有拍摄，或明确允许对应使用方式的品牌官方新闻资料图；保留必要署名与授权记录，不要直接复制电商或杂志图片。

替换图片后保留宽高信息与描述性 alt；如改变文件名，请同步修改内容数据或生成模板。插画源脚本在 `tools/draw_assets.py`。

Oswald 和 Raleway 已本地保存，附 SIL Open Font License。中文标题优先使用 Noto Serif SC，未安装时回退到 macOS 宋体 / STSong / SimSun / serif；正文使用系统中文字体。无需连接 Google Fonts 服务。

## 内容边界与参考资料

品牌历史和材料资料在关于页与文章末尾提供官方或专业机构阅读入口。编辑建议与历史资料分开理解。Lady Dior 的初创年份在不同官方页面有 1994 / 1995 两种表述，词条保留此差异，并明确 1995 年赠予戴安娜王妃的传播节点。

参考价仅帮助理解量级，不是整理当日的精确官方报价、库存或收益承诺；地区、尺寸、材质、年份和二手状态都可能影响价格。品牌与型号的具体参数、供应与价格请以官方渠道为准。

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
