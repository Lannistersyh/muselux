#!/usr/bin/env node
'use strict';

// Dependency-free behavior checks. This intentionally models only the DOM APIs
// used by main.js; it does not test browser layout, CSS, or assistive technology.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');

const root = path.resolve(__dirname, '..');
const sourcePaths = ['assets/js/data.js', 'assets/js/render.js', 'assets/js/main.js'];
const sources = sourcePaths.map(file => fs.readFileSync(path.join(root, file), 'utf8'));
const content = JSON.parse(fs.readFileSync(path.join(root, 'tools/content.json'), 'utf8'));
const catalog = content.items.concat(
  ...['bagYears', 'necklaceYears', 'jewelryYears'].map(key =>
    (content[key] || []).flatMap(year => year.entries))
);
const expectedRecords = content.brands.length + catalog.length + content.articles.length;
const checks = [];
const fixturePaths = new Set();
const digest = file => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, file))).digest('hex');

function check(condition, label) {
  assert.ok(condition, label);
  checks.push(label);
}

function decode(value) {
  return value.replace(/&(?:amp|quot|apos|lt|gt|#39|#x27);/g, entity => ({
    '&amp;': '&', '&quot;': '"', '&apos;': "'", '&lt;': '<', '&gt;': '>',
    '&#39;': "'", '&#x27;': "'"
  })[entity]);
}

class Element {
  constructor(tagName, attributes = {}, owner = null) {
    this.tagName = tagName.toLowerCase();
    this.attributes = attributes;
    this.ownerDocument = owner;
    this.children = [];
    this.events = {};
    this.style = {};
    this.hidden = Object.hasOwn(attributes, 'hidden');
    this.disabled = Object.hasOwn(attributes, 'disabled');
    this.value = attributes.value || '';
    this.textContent = '';
    this.dataset = Object.fromEntries(Object.entries(attributes)
      .filter(([key]) => key.startsWith('data-'))
      .map(([key, value]) => [key.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase()), value]));
    this.classList = {
      contains: name => (this.attributes.class || '').split(/\s+/).includes(name),
      toggle: (name, force) => {
        const set = new Set((this.attributes.class || '').split(/\s+/).filter(Boolean));
        const on = force === undefined ? !set.has(name) : force;
        if (on) set.add(name); else set.delete(name);
        this.attributes.class = [...set].join(' ');
        return on;
      },
      add: name => this.classList.toggle(name, true),
      remove: name => this.classList.toggle(name, false)
    };
  }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  getAttribute(name) { return this.attributes[name] ?? null; }
  addEventListener(name, listener) { this.events[name] = listener; }
  matches(selector) {
    if (selector.startsWith('#')) return this.attributes.id === selector.slice(1);
    if (selector.startsWith('.')) return this.classList.contains(selector.slice(1));
    if (/^\[[\w-]+\]$/.test(selector)) return Object.hasOwn(this.attributes, selector.slice(1, -1));
    return this.tagName === selector;
  }
  querySelectorAll(selector) {
    const matches = [];
    for (const child of this.children) {
      if (child.matches(selector)) matches.push(child);
      matches.push(...child.querySelectorAll(selector));
    }
    return matches;
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  closest(selector) { return this.matches(selector) ? this : this.parentElement?.closest(selector) || null; }
  focus() { this.ownerDocument.activeElement = this; }
  scrollIntoView() { this.scrolledIntoView = true; }
  get innerHTML() { return this.html || ''; }
  set innerHTML(html) {
    this.html = html;
    this.children = parse(html, this.ownerDocument).children;
    this.children.forEach(child => { child.parentElement = this; });
  }
}

function parse(html, owner) {
  const wrapper = new Element('fixture-root', {}, owner);
  const stack = [wrapper];
  const voidTags = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr']);
  // Fixtures come from our generated HTML. This is not a general HTML parser.
  for (const token of html.matchAll(/<!--[^]*?-->|<![^>]*>|<\/?([a-z][\w:-]*)\b([^>]*?)>/gi)) {
    if (!token[1]) continue;
    const tag = token[1].toLowerCase();
    if (token[0].startsWith('</')) {
      const index = stack.findLastIndex(element => element.tagName === tag);
      if (index > 0) stack.length = index;
      continue;
    }
    const attributes = {};
    for (const attr of token[2].matchAll(/([\w:-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?/g)) {
      attributes[attr[1]] = decode(attr[2] ?? attr[3] ?? attr[4] ?? '');
    }
    const element = new Element(tag, attributes, owner);
    const parent = stack[stack.length - 1];
    element.parentElement = parent;
    parent.children.push(element);
    if (!voidTags.has(tag) && !token[0].endsWith('/>')) stack.push(element);
  }
  for (const select of wrapper.querySelectorAll('select')) {
    const options = select.querySelectorAll('option');
    select.value = (options.find(option => Object.hasOwn(option.attributes, 'selected')) || options[0])?.value || '';
  }
  return wrapper;
}

async function fixture(file, href) {
  fixturePaths.add(file);
  const html = fs.readFileSync(path.join(root, file), 'utf8');
  const document = { events: {}, activeElement: null };
  const dom = parse(html, document);
  document.querySelector = selector => dom.querySelector(selector);
  document.querySelectorAll = selector => dom.querySelectorAll(selector);
  document.addEventListener = (event, listener) => { document.events[event] = listener; };
  document.body = dom.querySelector('body');
  document.documentElement = dom.querySelector('html');
  assert.ok(document.body && document.documentElement, file + ': valid HTML fixture');
  let url = new URL(href || 'https://muselux.test/' + file);
  const location = { get href() { return url.href; }, get search() { return url.search; }, get hash() { return url.hash; } };
  const window = {
    events: {}, innerWidth: 375, scrollY: 0,
    matchMedia: () => ({ matches: true }),
    addEventListener(event, listener) { this.events[event] = listener; },
    scrollTo() {}
  };
  const context = vm.createContext({
    window, document, location,
    history: { replaceState(state, title, value) { url = new URL(value, url); } },
    URL, URLSearchParams, Blob, Response, DecompressionStream, atob, Uint8Array,
    requestAnimationFrame: callback => callback()
  });
  sources.forEach((source, index) => vm.runInContext(source, context, { filename: sourcePaths[index] }));
  await window.MUSELUX_READY;
  await Promise.resolve();
  return {
    window, document, location,
    get(selector) {
      const found = document.querySelector(selector);
      assert.ok(found, file + ': required element ' + selector);
      return found;
    }
  };
}

async function run() {
  let site = await fixture('search.html');
  const data = site.window.MUSELUX_DATA;
  check(data.brands.length === content.brands.length, 'Decoded brand count matches canonical content');
  check(data.items.length === catalog.length, 'Decoded product count includes all annual selections');
  check(site.get('#search-count').textContent === `找到 ${expectedRecords} 条内容`, 'Global search includes every brand, product and article');
  check(site.get('#search-results').querySelectorAll('a').length === Math.min(8, expectedRecords), 'First search page renders eight results');
  for (const query of ['罗意威', '缪缪', '施华洛世奇', 'FRGMT', '阿迪达斯', 'Birkin']) {
    site.get('#search-query').value = query;
    site.get('#search-query').events.input();
    check(!site.get('#search-count').textContent.endsWith('找到 0 条内容'), 'Search lookup: ' + query);
  }
  site.get('#search-query').value = '<img src=x onerror=alert(1)>';
  site.get('#search-query').events.input();
  check(!site.get('#search-results').innerHTML.includes('onerror'), 'Search query HTML remains inert');

  const cartierNecklaces = catalog.filter(item => item.brand === 'cartier' && item.category === 'necklace');
  site = await fixture('search.html', 'https://muselux.test/search.html?type=item&cat=necklace&q=cartier');
  check(site.get('#search-count').textContent.endsWith(`找到 ${cartierNecklaces.length} 条内容`), 'URL query, type and category filters combine');
  const fragmentItems = catalog.filter(item => (item.collaboratorBrands || []).includes('fragment-design'));
  site = await fixture('search.html', 'file:///tmp/muselux/search.html?q=FRGMT&type=item');
  check(site.get('#search-count').textContent.endsWith(`找到 ${fragmentItems.length} 条内容`), 'Offline file URL searches collaboration products');
  site = await fixture('search.html', 'https://muselux.test/search.html?type=invalid&cat=invalid');
  check(site.get('#search-count').textContent === `找到 ${expectedRecords} 条内容`, 'Invalid URL filters fall back to all records');

  site = await fixture('brands.html');
  for (const query of ['FRGMT', 'Alaïa', '罗意威']) {
    site.get('#brand-query').value = query;
    site.get('#brand-query').events.input();
    check(site.get('#brand-count').textContent === '1 个品牌', 'Brand lookup: ' + query);
    check(!site.get('#brand-results').innerHTML.includes('undefined'), 'Brand card has complete fields: ' + query);
  }
  site.get('#brand-query').value = '';
  site.get('#brand-category').value = 'necklace';
  site.get('#brand-category').events.change();
  check(site.get('#brand-results').innerHTML.includes('brand/fendi.html'), 'Necklace brand filter includes Fendi annual selections');

  for (const year of [2022, 2023, 2024, 2025, 2026]) {
    site = await fixture('bags-by-year.html', `file:///tmp/muselux/bags-by-year.html#year-${year}`);
    const panels = site.document.querySelectorAll('[data-year-panel]');
    check(panels.filter(panel => !panel.hidden).length === 1 &&
      panels.find(panel => !panel.hidden).dataset.yearPanel === String(year), 'Year deep link: ' + year);
    const tabs = site.get('.year-tabs');
    const button = tabs.querySelectorAll('button').find(element => element.dataset.year === '2022');
    assert.ok(button, '2022 year control exists');
    tabs.events.click({ target: button });
    check(site.location.hash === '#year-2022', 'Year click updates location: ' + year);
    button.focus();
    tabs.events.keydown({ key: 'ArrowRight', preventDefault() {} });
    check(panels.find(panel => !panel.hidden).dataset.yearPanel === '2026', 'Year keyboard wraps at final button: ' + year);
  }

  const viewSources = fs.readdirSync(path.join(root, 'tools/research')).filter(file => /^product-views-.*\.json$/.test(file));
  const viewRecords = viewSources.flatMap(file => JSON.parse(fs.readFileSync(path.join(root, 'tools/research', file), 'utf8')).records);
  const galleryIds = [content.items.find(item => item.styleEdit && viewRecords.some(record => record.id === item.id))?.id,
    catalog.find(item => item.annualEdit && viewRecords.some(record => record.id === item.id))?.id,
    content.items.find(item => !item.styleEdit && viewRecords.some(record => record.id === item.id))?.id];
  for (const id of galleryIds) {
    assert.ok(id, 'Core, annual and dictionary gallery fixtures available');
    site = await fixture('item/' + id + '.html', 'file:///tmp/muselux/item/' + id + '.html');
    const gallery = site.get('[data-product-gallery]');
    const views = gallery.querySelectorAll('[data-gallery-view]');
    const controls = gallery.querySelector('[data-gallery-controls]');
    const buttons = controls.querySelectorAll('button');
    check(views.length >= 2 && !controls.hidden && !views[0].hidden && views.slice(1).every(view => view.hidden), 'Gallery initializes with one visible photograph: ' + id);
    controls.events.click({target: buttons[1].querySelector('img')});
    check(!views[1].hidden && views[0].hidden && buttons[1].getAttribute('aria-pressed') === 'true', 'Thumbnail image click switches view: ' + id);
    buttons[1].focus();
    controls.events.keydown({key: 'Home', preventDefault() {}});
    check(!views[0].hidden && site.document.activeElement === buttons[0], 'Home key selects and focuses first view: ' + id);
    controls.events.keydown({key: 'ArrowLeft', preventDefault() {}});
    check(!views.at(-1).hidden && site.document.activeElement === buttons.at(-1), 'Arrow key wraps gallery focus: ' + id);
    check(gallery.querySelector('[data-gallery-status]').textContent.startsWith('View ' + views.length + ' of ' + views.length), 'Gallery announces active view: ' + id);
  }

  site = await fixture('index.html');
  const menu = site.get('.menu-toggle');
  const nav = site.get('#main-nav');
  menu.events.click();
  check(nav.classList.contains('open') && menu.getAttribute('aria-expanded') === 'true', 'Mobile menu opens with correct expanded state');
  site.document.events.keydown({ key: 'Escape' });
  check(!nav.classList.contains('open') && menu.getAttribute('aria-expanded') === 'false', 'Escape closes mobile menu');
  menu.events.click();
  site.window.innerWidth = 900;
  site.window.events.resize();
  check(!nav.classList.contains('open'), 'Desktop resize closes mobile menu');
}

const report = {
  passed: false,
  checkedAt: new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date()),
  timezone: 'Asia/Shanghai',
  method: 'Node VM executing actual generated HTML and data.js/render.js/main.js using a dependency-free minimal DOM fixture',
  scope: 'Behavior and offline URL checks only; no browser engine, layout, CSS or assistive-technology verification. No network calls.',
  browserTabsOpened: 0,
  browserTabsRemaining: 0,
  assertions: 0,
  checks,
  sourceHashes: Object.fromEntries(sourcePaths.map(file => [file, digest(file)])),
  contentHash: digest('tools/content.json')
};

(async () => {
  try {
    await run();
    report.passed = true;
  } catch (error) {
    report.error = error.stack || String(error);
    process.exitCode = 1;
  } finally {
    report.assertions = checks.length;
    report.fixtureHashes = Object.fromEntries([...fixturePaths].map(file => [file, digest(file)]));
    fs.writeFileSync(path.join(root, 'reports/frontend-code-validation.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(`${report.passed ? 'PASS' : 'FAIL'} ${report.assertions} frontend assertions; report: reports/frontend-code-validation.json`);
    if (report.error) console.error(report.error);
  }
})();
