// ========== 进度与时间本地存储 ========== //
// 结构: { [sectionId]: { perItemProgress:[], timeSpent:[], lastPara:idx, problemDraft:{}, videoDraft:{} } }
function getProgressStore(sectionId) {
  try {
    const raw = localStorage.getItem('ata_progress_v2')
    if (!raw) return {}
    const all = JSON.parse(raw)
    const uid = currentUserId || 'guest'
    if (!all[uid]) return {}
    return all[uid][sectionId] || {}
  } catch(e) { return {} }
}
function setProgressStore(sectionId, obj) {
  try {
    const raw = localStorage.getItem('ata_progress_v2')
    let all = raw ? JSON.parse(raw) : {}
    const uid = currentUserId || 'guest'
    if (!all[uid]) all[uid] = {}
    all[uid][sectionId] = obj
    localStorage.setItem('ata_progress_v2', JSON.stringify(all))
  } catch(e){}
}

// ========== 进度与时间统计 ========== //
let focusStart = null, focusTimer = null
let timeSpentArr = [] // 当前section每个item的累计时间
let perItemProgress = [] // 当前section每个item的进度百分比
let lastSectionId = null
let lastPara = 0

function startFocusTimer(idx) {
  stopFocusTimer()
  focusStart = Date.now()
  focusTimer = setInterval(()=>{
    if (typeof idx === 'number') {
      timeSpentArr[idx] = (timeSpentArr[idx]||0) + 1
      saveProgressDraft()
      updateProgressInfo()
    }
  }, 1000)
}
function stopFocusTimer() {
  if (focusTimer) clearInterval(focusTimer)
  focusTimer = null
  focusStart = null
}

function updateProgressInfo() {
  // 计算平均进度和总时间
  const avg = perItemProgress.length ? (perItemProgress.reduce((a,b)=>a+b,0)/perItemProgress.length) : 0
  const total = timeSpentArr.reduce((a,b)=>a+b,0)
  el('progress-info').textContent = `${Math.round(avg)}% / ${total}s`
}

function saveProgressDraft() {
  if (!currentSection) return
  const sectionId = currentSection.id
  setProgressStore(sectionId, {
    perItemProgress,
    timeSpent: timeSpentArr,
    lastPara: paraIndex,
    problemDraft: window.problemDraft || {},
    videoDraft: window.videoDraft || {}
  })
}

function loadProgressDraft(sectionId) {
  const store = getProgressStore(sectionId)
  perItemProgress = Array.isArray(store.perItemProgress) ? store.perItemProgress.slice() : []
  timeSpentArr = Array.isArray(store.timeSpent) ? store.timeSpent.slice() : []
  lastPara = typeof store.lastPara === 'number' ? store.lastPara : 0
  window.problemDraft = store.problemDraft || {}
  window.videoDraft = store.videoDraft || {}
}

async function uploadProgress() {
  if (!currentSection) return alert('先选小节')
  // 检查是否登录
  const btn = el('btn-upload-progress');
  if (!currentUsername) {
    if (btn) {
      btn.textContent = '登录后上传';
      btn.disabled = true;
    }
    el('progress-info').textContent = '未登录：无法上传';
    return;
  } else {
    if (btn) {
      btn.textContent = '上传进度';
      btn.disabled = false;
    }
  }
  // 组装payload
  const avg = perItemProgress.length ? (perItemProgress.reduce((a,b)=>a+b,0)/perItemProgress.length) : 0
  const total = timeSpentArr.reduce((a,b)=>a+b,0)
  const draft = getProgressStore(currentSection.id)
  const payload = {
    percentage: Math.round(avg),
    time_spent: total,
    completed_at: null,
    draft: JSON.stringify(draft)
  }
  const r = await apiPost(`/lesson/progress/${currentSection.id}/set`, payload)
  if (r.status && r.status.code===0){
    el('progress-info').textContent = `已上传 ${Math.round(avg)}% / ${total}s`
    const btn = el('btn-upload-progress');
    if (btn) btn.textContent = '上传进度';
  } else if (r.status && r.status.code===1){
    el('progress-info').textContent = '未登录：无法上传'
    const btn = el('btn-upload-progress');
    if (btn) btn.textContent = '登录后上传';
  } else {
    el('progress-info').textContent = '上传失败'
    const btn = el('btn-upload-progress');
    if (btn) btn.textContent = '上传进度';
  }
}
const API_BASE = '/api'

// 简单 fetch 包装，包含 cookie
async function apiPost(path, body){
  const resp = await fetch(API_BASE + path, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    credentials: 'include',
    body: JSON.stringify(body)
  })
  return resp.json()
}
async function apiGet(path){
  const resp = await fetch(API_BASE + path, {credentials:'include'})
  return resp.json()
}

// Theme helpers: expose an API to set theme/accent color from JS
function hexToRgb(hex){
  // support #rrggbb or rrggbb
  const h = hex.replace('#','')
  const r = parseInt(h.substring(0,2),16)
  const g = parseInt(h.substring(2,4),16)
  const b = parseInt(h.substring(4,6),16)
  return {r,g,b}
}

function mixWithWhite(rgb, weight){
  // weight 0..1 how much white to mix
  const r = Math.round(rgb.r + (255 - rgb.r) * weight)
  const g = Math.round(rgb.g + (255 - rgb.g) * weight)
  const b = Math.round(rgb.b + (255 - rgb.b) * weight)
  return {r,g,b}
}

function darken(rgb, weight){
  // weight 0..1 how much to darken towards black
  const r = Math.round(rgb.r * (1 - weight))
  const g = Math.round(rgb.g * (1 - weight))
  const b = Math.round(rgb.b * (1 - weight))
  return {r,g,b}
}

function applyTheme(accentHex){
  if (!accentHex) return
  const root = document.documentElement
  root.style.setProperty('--accent', accentHex)
  const rgb = hexToRgb(accentHex)
  // light variant for chapter background (mostly white)
  const weak = mixWithWhite(rgb, 0.86)
  root.style.setProperty('--chap-bg', `rgb(${weak.r}, ${weak.g}, ${weak.b})`)
  // dialogue background: very faint tint of accent
  root.style.setProperty('--dialogue-bg', `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.06)`)
  // darker accent for small controls like back button
  const d = darken(rgb, 0.16)
  root.style.setProperty('--accent-dark', `rgb(${d.r}, ${d.g}, ${d.b})`)
  // compute readable foreground (black or white) based on perceived brightness
  const brightness = Math.round((rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000)
  const fg = (()=>{
    try {
      return localStorage.getItem('ata_night_mode') === '1'
    } catch(e) { return false }
  })()?
              ((brightness > 180) ? '#333' : '#fff'):
              ((brightness > 200) ? '#444' : '#fff');
  
  root.style.setProperty('--accent-foreground', fg)
  // background gradient: two tints of accent
  const top = mixWithWhite(rgb, 0.7)
  const bottom = mixWithWhite(rgb, 0.92)
  root.style.setProperty('--bg-top', `rgb(${top.r}, ${top.g}, ${top.b})`)
  root.style.setProperty('--bg-bottom', `rgb(${bottom.r}, ${bottom.g}, ${bottom.b})`)
  // set destructive button foreground: slightly lighter on very bright accents
  const destructiveFg = (brightness > 200) ? 'rgba(255,255,255,0.86)' : '#fff'
  root.style.setProperty('--destructive-foreground', destructiveFg)
  // persist selection
  try{ localStorage.setItem('ata_theme_accent', accentHex) }catch(e){/* ignore */}
}

// public API to change theme at runtime
window.setThemeColor = applyTheme


// set initial theme and night mode to saved or default
try {
  // 夜间模式优先
  if (localStorage.getItem('ata_night_mode') === '1') {
    document.body.classList.add('night-mode')
  } else {
    document.body.classList.remove('night-mode')
  }
  const saved = localStorage.getItem('ata_theme_accent')
  if (saved) applyTheme(saved)
  else applyTheme('#5fb3ff')
} catch(e) { applyTheme('#5fb3ff') }

// UI helpers
const el = id => document.getElementById(id)

async function loadCourses(){
  const data = await apiGet('/lesson/course/getAll')
  console.log('loadCourses', data)
  const list = el('course-list')
  if (!list) return console.warn('course-list element not found')
  list.innerHTML = ''
  list.style.display = ''
  const courses = (data && data.courses) ? data.courses : []
  if (!courses.length){
    const li = document.createElement('li')
    li.textContent = '尚无课程或获取失败' 
    li.style.color = '#999'
    list.appendChild(li)
    return
  }
  courses.forEach(c=>{
    const li = document.createElement('li')
    li.textContent = c.name || ('课程 ' + (c.id||'?'))
    // 不设置字体色，交由CSS控制
    li.onclick = ()=>selectCourse(c.id)
    list.appendChild(li)
  })
}

async function checkAuth(){
  try{
    const r = await apiGet('/profile/whoami')
    console.log('profile whoami', r)
    if (r && r.status && r.status.code===0){
      // prefer nickname for display, fallback to username
      currentUserNickname = r.nickname || null
      currentUsername = r.username || null
      currentUserId = r.user_id || null
      // 切换用户时自动刷新本地进度缓存
      // 可选：如需切换用户时清空guest进度，可在此处加逻辑
      // profile fields: avatar and colour
  const avatarPath = r.avatar || null
  currentUserAvatar = avatarPath
      currentUserLastLogin = r.logged_in_at || null
      // render header avatar (avatar API returns path WITHOUT '/static/avatar' prefix)
      const ha = el('header-avatar')
      if (ha){
        if (avatarPath){
          // ensure leading /
          const p = avatarPath.startsWith('/') ? avatarPath : ('/' + avatarPath)
          // include explicit width/height attributes and image-rendering to reduce blur when small images are upscaled
          // note: backend returns avatar path without "/static/avatar" prefix, serve from /avatar/<path>
          ha.innerHTML = `<img src="/avatar${p}" width="34" height="34" style="width:100%;height:100%;object-fit:cover;image-rendering:pixelated;display:block"/>`
          ha.style.display = 'inline-block'
        } else {
          // no avatar for this user, still show placeholder circle
          ha.innerHTML = ''
          ha.style.display = 'inline-block'
        }
      }
      el('user-status').textContent = currentUserNickname || currentUsername || '已登录'
      el('btn-login').style.display='none'
      el('btn-register').style.display='none'
      el('btn-logout').style.display='inline-block'
      const bu = el('btn-unregister'); if (bu) bu.style.display = ''
      // apply theme from profile colour if available
      try{
        const colour = r.colour || null
        if (colour){
          const map = {
            pink: '#ff9bb3',
            orange: '#ffb36b',
            yellow: '#ffe28a',
            green: '#8fe39a',
            blue: '#5fb3ff',
            purple: '#c39bff'
          }
          const hex = map[colour] || null
          if (hex) applyTheme(hex)
        }
      }catch(e){console.warn('applyTheme from profile failed', e)}
      // 登录后恢复上传按钮
      const upbtn = el('btn-upload-progress');
      if (upbtn) { upbtn.textContent = '上传进度'; upbtn.disabled = false; }
      return true
    }
  }catch(e){
    console.warn('checkAuth err', e)
  }
  el('user-status').textContent = '未登录'
  el('btn-login').style.display='inline-block'
  el('btn-register').style.display='inline-block'
  el('btn-logout').style.display='none'
  const bu = el('btn-unregister'); if (bu) bu.style.display = 'none'
  currentUserNickname = null
  currentUsername = null
  currentUserId = null
  currentUserLastLogin = null
    // clear header avatar and hide popover when logged out
  try{ const ha = el('header-avatar'); if (ha){ ha.innerHTML = ''; ha.style.display = 'none' } }catch(e){}
  try{ const pop = el('user-popover'); if (pop){ pop.style.display = 'none'; pop.innerHTML = '' } }catch(e){}
  // 未登录禁用上传按钮
  const upbtn = el('btn-upload-progress');
  if (upbtn) { upbtn.textContent = '登录后上传'; upbtn.disabled = true; }
  return false
}


let currentCourse = null, currentSections = [], currentSection = null
let dialogueItems = [], paraIndex = 0
let currentUsername = null
let currentUserNickname = null
let currentUserId = null
let currentUserLastLogin = null
let currentUserAvatar = null
// when editing nickname inside popover, lock the popover open to avoid mouseleave closing during IME
let isEditingNickname = false

// 题目答题状态缓存：{ [paraIndex]: { answer, submitted, result } }
let problemAnswerCache = {}

async function selectCourse(courseId){
  currentCourse = courseId
  const data = await apiGet(`/lesson/section/${courseId}/getAll`)
  currentSections = data.sections || []
  // render sections into the left sidebar (reuse course-list element)
  const sl = el('course-list'); if (!sl) return; sl.innerHTML = ''
  // update sidebar title and show back button
  const title = el('sidebar-title'); if (title) title.textContent = '小节'
  const back = el('sidebar-back'); if (back) back.style.display = ''
  // Group sections by chapter titles: when encountering a chapter title (is_chap_title==true),
  // create a chapter header and a nested list that holds subsequent sections until the next chapter.
  let currentUl = sl
  currentSections.forEach(s=>{
    if (s.is_chap_title){
      // chapter header (with collapsible behavior). Default: expanded.
      const liChap = document.createElement('li')
      liChap.className = 'chap-title'
      // create a text node for the title
      const titleNode = document.createElement('span')
      titleNode.className = 'chap-title-text'
      titleNode.textContent = s.title

      // caret indicator appended to the right
      const caret = document.createElement('span')
      caret.className = 'chap-caret'
      caret.textContent = '▾' // down arrow = expanded
      caret.style.userSelect = 'none'
      caret.style.marginLeft = '8px'
      caret.style.cursor = 'pointer'

      // layout: use flex to place title left and caret right
      liChap.style.display = 'flex'
      liChap.style.alignItems = 'center'
      liChap.style.justifyContent = 'space-between'
      liChap.appendChild(titleNode)
      liChap.appendChild(caret)

      // create a sibling nested list for the chapter's sections (as a separate element)
      const childUl = document.createElement('ul')
      childUl.className = 'sub-sections'
      childUl.style.display = 'block' // default expanded

      // toggle handler: click caret or title toggles visibility
      const toggle = ()=>{
        if (childUl.style.display === 'none'){
          childUl.style.display = 'block'
          caret.textContent = '▾'
          liChap.classList.remove('collapsed')
        } else {
          childUl.style.display = 'none'
          caret.textContent = '▸'
          liChap.classList.add('collapsed')
        }
      }
      caret.addEventListener('click', (ev)=>{ ev.stopPropagation(); toggle() })
      liChap.addEventListener('click', (ev)=>{ toggle() })

  sl.appendChild(liChap)
  sl.appendChild(childUl)
      currentUl = childUl
    } else {
      const li = document.createElement('li')
      li.textContent = s.title // do not add extra numbering
      li.className = 'section-item'
      li.onclick = ()=>selectSection(s)
      currentUl.appendChild(li)
    }
  })
  el('dialogue-content').textContent = '已加载小节，点击左侧小节开始学习。'
}

function showCourseList(){
  const title = el('sidebar-title'); if (title) title.textContent = '课程'
  const back = el('sidebar-back'); if (back) back.style.display = 'none'
  currentCourse = null
  // reload courses into course-list
  loadCourses()
}

async function selectSection(section){
  currentSection = section
  // content 可能是数组/对象/字符串。按要求规范化为 items 数组
  let raw = section.content
  let items = []
  if (raw === null || raw === undefined) {
    items = []
  } else if (Array.isArray(raw)) {
    items = raw.slice()
  } else {
    // 当作只有一个元素的数组处理
    items = [raw]
  }

  // 规范化每个元素：非object视为{text: ...}；object确保有type属性（默认 text）
  dialogueItems = items.map(it => {
    if (it && typeof it === 'object' && !Array.isArray(it)) {
      // ensure type exists
      if (!('type' in it)) it.type = 'text'
      return it
    }
    // 非 object，视为 text
    return {type: 'text', content: String(it)}
  })

  // 检查本地是否有进度
  let store = getProgressStore(section.id)
  let hasProgress = store && (
    (Array.isArray(store.perItemProgress) && store.perItemProgress.some(x=>x>0)) ||
    (Array.isArray(store.timeSpent) && store.timeSpent.some(x=>x>0)) ||
    (store.lastPara && store.lastPara > 0)
  )

  // 云端进度同步逻辑
  let cloudProgress = null
  let cloudUpdatedAt = 0
  let localUpdatedAt = 0
  try {
    const resp = await apiGet(`/lesson/progress/${section.id}/get`)
    if (resp && resp.status && resp.status.code === 0 && resp.progress) {
      cloudProgress = resp.progress
      cloudUpdatedAt = new Date(cloudProgress.updated_at || cloudProgress.completed_at || 0).getTime()
    }
  } catch(e) { /* ignore */ }
  if (store && store.updated_at) {
    localUpdatedAt = new Date(store.updated_at).getTime()
  }
  // 若云端有进度，比较时间戳
  if (cloudProgress && cloudProgress.draft) {
    let cloudDraft = {}
    try { cloudDraft = JSON.parse(cloudProgress.draft) } catch(e){}
    // 兼容多用户本地结构
    const uid = currentUserId || 'guest'
    if (cloudUpdatedAt > localUpdatedAt) {
      // 云端较新，覆盖本地
      setProgressStore(section.id, { ...cloudDraft, updated_at: cloudProgress.updated_at })
      store = getProgressStore(section.id)
      hasProgress = store && (
        (Array.isArray(store.perItemProgress) && store.perItemProgress.some(x=>x>0)) ||
        (Array.isArray(store.timeSpent) && store.timeSpent.some(x=>x>0)) ||
        (store.lastPara && store.lastPara > 0)
      )
    } else if (localUpdatedAt > cloudUpdatedAt) {
      // 本地较新，自动上传本地进度覆盖云端
      const payload = {
        percentage: store.perItemProgress && store.perItemProgress.length ? Math.round(store.perItemProgress.reduce((a,b)=>a+b,0)/store.perItemProgress.length) : 0,
        time_spent: store.timeSpent && store.timeSpent.length ? store.timeSpent.reduce((a,b)=>a+b,0) : 0,
        completed_at: null,
        draft: JSON.stringify(store)
      }
      await apiPost(`/lesson/progress/${section.id}/set`, payload)
    }
  }

  const container = el('dialogue-content')
  if(hasProgress && container){
    const stemDiv = document.createElement('div')
    stemDiv.className = 'problem-stem'
    const stemText = document.createElement('span')
    stemText.textContent = ' 检测到有保存的学习记录，请选择：'
    stemDiv.appendChild(stemText);
    container.innerHTML = ''
    container.appendChild(stemDiv)
    const form = document.createElement('form')
    form.className = 'problem-form'
    const btnc = document.createElement('button')
    btnc.type = 'button'
    btnc.textContent = '继续学习'
    btnc.onclick = () => {
      loadProgressDraft(section.id)
      if (perItemProgress.length !== dialogueItems.length) perItemProgress = Array(dialogueItems.length).fill(0)
      if (timeSpentArr.length !== dialogueItems.length) timeSpentArr = Array(dialogueItems.length).fill(0)
      paraIndex = (typeof lastPara === 'number' && lastPara >= 0 && lastPara < dialogueItems.length) ? lastPara : 0
      renderDialogue()
      updateProgressInfo()
    }
    form.appendChild(btnc);
    form.appendChild(document.createElement('br'))
    const btnr = document.createElement('button')
    btnr.type = 'button'
    btnr.textContent = '重新开始'
    btnr.onclick = () => {
      // 清除本用户本小节进度
      setProgressStore(section.id, {})
      perItemProgress = Array(dialogueItems.length).fill(0)
      timeSpentArr = Array(dialogueItems.length).fill(0)
      lastPara = 0
      window.problemDraft = {}
      window.videoDraft = {}
      paraIndex = 0
      saveProgressDraft()
      renderDialogue()
      updateProgressInfo()
    }
    form.appendChild(btnr);
    container.appendChild(form);
    return;
  }
  loadProgressDraft(section.id)
  if (perItemProgress.length !== dialogueItems.length) perItemProgress = Array(dialogueItems.length).fill(0)
  if (timeSpentArr.length !== dialogueItems.length) timeSpentArr = Array(dialogueItems.length).fill(0)
  paraIndex = (typeof lastPara === 'number' && lastPara >= 0 && lastPara < dialogueItems.length) ? lastPara : 0
  renderDialogue()
  updateProgressInfo()
}

function renderDialogue(){
  const content = el('dialogue-content')
  if (!dialogueItems.length){
    content.textContent = '本小节内容为空。'
    el('prev-para').disabled = true
    el('next-para').disabled = true
    return
  }
  // 离开前一个对话时保存进度
  if (typeof window._lastParaIdx === 'number' && window._lastParaIdx !== paraIndex) {
    stopFocusTimer();
    saveProgressDraft();
  }
  window._lastParaIdx = paraIndex;
  // render current item based on its type
  const item = dialogueItems[paraIndex]
  renderItem(item, content)
  el('prev-para').disabled = paraIndex===0
  el('next-para').disabled = paraIndex>=dialogueItems.length-1
  startFocusTimer(paraIndex)
}

function renderItem(item, container){

// 显示判分结果
function showJudgeResult(result, container) {
  const div = document.createElement('div');
  div.className = 'judge-result';
  div.style.marginTop = '12px';
  div.innerHTML = `<b>得分：</b>${result.score} / ${result.mscore}` + (result.comment ? `<br/><b>评语：</b>${result.comment}` : '') + (result.std ? `<br/><b>答案：</b>${result.std}` : '');
  container.appendChild(div);
}

  // container is DOM element
  if (!item) { container.textContent = '' ; return }
  const t = (item.type || 'text')
  container.innerHTML = ''
  if (t === 'text'){
    const txt = (typeof item.content !== 'undefined') ? item.content : (item.text || '')
    container.textContent = String(txt)
    // text类型直接100%
    perItemProgress[paraIndex] = 100;
    saveProgressDraft();
    updateProgressInfo();
  } else if (t === 'interaction') {
    // interaction类型，content为题干，UI同简答题
    const stemDiv = document.createElement('div');
    stemDiv.className = 'problem-stem';
    const typeTag = document.createElement('span');
    typeTag.className = 'problem-type-tag';
    typeTag.textContent = '互动';
    stemDiv.appendChild(typeTag);
    const stemText = document.createElement('span');
    stemText.textContent = ' ' + (item.content || '');
    stemDiv.appendChild(stemText);
    container.appendChild(stemDiv);
    // form结构
    const form = document.createElement('form');
    form.className = 'problem-form';
    const input = document.createElement('textarea');
    input.rows = 4;
    input.style.width = '100%';
    input.placeholder = '请输入答案';
    // interaction不做本地缓存
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = '提交';
    let submitted = false;
    btn.onclick = async () => {
      if (submitted) return;
      const val = input.value.trim();
      if (!val) { alert('请输入答案'); return; }
      btn.disabled = true;
      btn.textContent = '判分中...';
      try {
        const judgeReq = { problem: item.content, answer: val };
        const res = await apiPost('/problem/judge/interaction', judgeReq);
        // 适配 InteractionJudgeResponse 格式
        if (res && res.status && res.score) {
          const result = {
            std: res.score.std,
            score: res.score.score,
            mscore: 100,
            comment: res.score.comment
          };
          showJudgeResult(result, container);
          submitted = true;
          btn.disabled = true;
          btn.textContent = '已提交';
          input.disabled = true;
        } else {
          btn.disabled = false;
          btn.textContent = '提交';
          alert('判分失败');
        }
      } catch(e) {
        console.log(e);
        btn.disabled = false;
        btn.textContent = '提交';
        alert('网络错误');
      }
    };
    // interaction不做输入缓存
    form.appendChild(input);
    form.appendChild(document.createElement('br'));
    form.appendChild(btn);
    container.appendChild(form);
    // interaction不做历史结果恢复
  } else if (t === 'video'){
    const video = document.createElement('video')
    video.controls = true
    video.style.maxWidth = '100%'
    video.src = item.content
    // 恢复播放进度
    let vDraft = window.videoDraft || {}
    if (vDraft[paraIndex]) video.currentTime = vDraft[paraIndex]
    video.addEventListener('timeupdate', ()=>{
      // 线性分配进度
      const percent = video.duration ? Math.min(100, Math.round(100 * video.currentTime / video.duration)) : 0;
      perItemProgress[paraIndex] = percent;
      // draft保存当前播放进度
      window.videoDraft = window.videoDraft || {}
      window.videoDraft[paraIndex] = video.currentTime;
      saveProgressDraft();
      updateProgressInfo();
    });
    container.appendChild(video)
  } else if (t === 'problem'){
    let arr = []
    if (typeof item.content === 'number') {
      arr = [item.content]
    } else if (Array.isArray(item.content) && item.content.every(x => typeof x === 'number')) {
      arr = item.content
    } else {
      container.textContent = '非法的 problem.content 类型';
      return
    }
    if (arr.length === 0) {
      container.textContent = '无可用问题';
      return
    }
    let idx = 0
    if (arr.length > 1) {
      idx = Math.floor(Math.random() * arr.length)
      if (idx >= arr.length) idx = arr.length - 1
    }
    const problemId = arr[idx]
    container.textContent = '加载中...'
    apiPost('/problem/get', {problem_id: [problemId]}).then(data => {
      if (data && data.content && Array.isArray(data.content) && data.content[0]) {
        const prob = data.content[0]
        if (prob && typeof prob === 'object' && prob.ptype && prob.problem) {
          // 读取缓存
          const cache = problemAnswerCache[paraIndex] || {}
          renderProblemUI(prob, container, problemId, cache)
        } else {
          container.textContent = '题目数据异常：' + JSON.stringify(prob)
        }
      } else {
        container.textContent = '未获取到问题内容'
      }
    }).catch(e => {
      console.log('getproblem', e)
      container.textContent = '获取问题失败'
    })

// 渲染 problem 题目 UI 并处理提交，支持缓存和恢复答题状态
function renderProblemUI(prob, container, problemId, cache) {
  if (!prob || !prob.ptype || !prob.problem) {
    container.textContent = '题目数据不完整';
    return;
  }
  const ptype = prob.ptype;
  const stem = prob.problem;
  const arms = prob.arms || {};
  // 题型标签
  const typeMap = {
    single_choice: '单选',
    multiple_choice: '多选',
    variable_choice: '不定项',
    blank_filling: '填空',
    brief_response: '简答'
  };
  const typeTag = document.createElement('span');
  typeTag.className = 'problem-type-tag';
  typeTag.textContent = typeMap[ptype] || '题目';
  // 构建题干
  const stemDiv = document.createElement('div');
  stemDiv.className = 'problem-stem';
  stemDiv.appendChild(typeTag);
  const stemText = document.createElement('span');
  stemText.textContent = ' ' + stem;
  stemDiv.appendChild(stemText);
  container.innerHTML = '';
  container.appendChild(stemDiv);

  // 选择题类型
  if (["single_choice", "multiple_choice", "variable_choice"].includes(ptype)) {
    const form = document.createElement('form');
    form.className = 'problem-form';
    const keys = Object.keys(arms);
    if (!keys.length) {
      container.appendChild(document.createTextNode('无可用选项'));
      return;
    }
    // 恢复已选答案
    let selected = (cache && Array.isArray(cache.answer)) ? cache.answer : [];
    // 恢复draft
    if (window.problemDraft && window.problemDraft[paraIndex]) {
      const draft = window.problemDraft[paraIndex];
      if (typeof draft === 'object' && draft !== null && Array.isArray(draft.answer)) {
        selected = draft.answer;
      } else if (Array.isArray(draft)) {
        selected = draft;
      }
    }
    keys.forEach((k, i) => {
      const label = document.createElement('label');
      label.textContent = arms[k];
      label.setAttribute('data-value', k);
      // 高亮选中项
      if (selected.includes(k)) label.classList.add('selected');
      // 选项点击事件
      label.addEventListener('click', (e) => {
        e.preventDefault();
        if (form.querySelector('button[disabled]')) return; // 已提交
        if (ptype === 'single_choice') {
          // 单选：只允许一个
          selected = [k];
        } else {
          // 多选/不定项：切换选中
          if (selected.includes(k)) {
            selected = selected.filter(x => x !== k);
          } else {
            selected = [...selected, k];
          }
        }
        // 更新所有label高亮
        form.querySelectorAll('label').forEach(lab => {
          if (selected.includes(lab.getAttribute('data-value'))) lab.classList.add('selected');
          else lab.classList.remove('selected');
        });
  // 实时缓存
  problemAnswerCache[paraIndex] = { answer: selected.slice(), submitted: false, result: null };
  // draft保存当前选项
  window.problemDraft = window.problemDraft || {}
  window.problemDraft[paraIndex] = { answer: selected.slice() };
  saveProgressDraft();
  updateProgressInfo();
      });
      form.appendChild(label);
    });
    // 提交按钮
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = '提交';
    let submitted = !!(cache && cache.submitted);
    if (submitted) {
      btn.disabled = true;
      btn.textContent = '已提交';
    }
    btn.onclick = async () => {
      if (submitted) return;
      if (!selected.length) {
        alert('请选择至少一项');
        return;
      }
      // 缓存答案
      problemAnswerCache[paraIndex] = { answer: selected.slice(), submitted: false, result: null };
      btn.disabled = true;
      btn.textContent = '判分中...';
      try {
        const judgeReq = [{problem_id: problemId, answer: selected.slice()}];
        const res = await apiPost('/problem/judge', judgeReq);
        if (res && Array.isArray(res) && res[0] && res[0].result) {
          showJudgeResult(res[0].result, container);
          submitted = true;
          btn.disabled = true;
          btn.textContent = '已提交';
          problemAnswerCache[paraIndex] = { answer: selected.slice(), submitted: true, result: res[0].result };
          // 提交后标记为100%
          perItemProgress[paraIndex] = 100;
          // draft保存答案和评分结果
          window.problemDraft = window.problemDraft || {}
          window.problemDraft[paraIndex] = { answer: selected.slice(), submitted: true, result: res[0].result };
          saveProgressDraft();
          updateProgressInfo();
        } else {
          btn.disabled = false;
          btn.textContent = '提交';
          alert('判分失败');
        }
      } catch(e) {
        btn.disabled = false;
        btn.textContent = '提交';
        alert('网络错误');
      }
    };
    form.appendChild(btn);
    container.appendChild(form);
    if (submitted && cache && cache.result) {
      showJudgeResult(cache.result, container);
    }
  } else if (["blank_filling", "brief_response"].includes(ptype)) {
    // 使用与选择题一致的form结构和样式
    const form = document.createElement('form');
    form.className = 'problem-form';
    let input;
    if (ptype === 'brief_response') {
      input = document.createElement('textarea');
      input.rows = 4;
      input.style.width = '100%';
      input.placeholder = '请输入答案';
    } else {
      input = document.createElement('input');
      input.type = 'text';
      input.style.width = '100%';
      input.placeholder = '请输入答案';
    }
    // 恢复输入内容
    if (cache && typeof cache.answer === 'string') {
      input.value = cache.answer;
    }
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = '提交';
    let submitted = !!(cache && cache.submitted);
    if (submitted) {
      btn.disabled = true;
      btn.textContent = '已提交';
    }
    btn.onclick = async () => {
      if (submitted) return;
      const val = input.value.trim();
      if (!val) { alert('请输入答案'); return; }
      // 缓存答案
      problemAnswerCache[paraIndex] = { answer: val, submitted: false, result: null };
      btn.disabled = true;
      btn.textContent = '判分中...';
      try {
        const judgeReq = [{problem_id: problemId, answer: val}];
        const res = await apiPost('/problem/judge', judgeReq);
        if (res && Array.isArray(res) && res[0] && res[0].result) {
          showJudgeResult(res[0].result, container);
          submitted = true;
          btn.disabled = true;
          btn.textContent = '已提交';
          input.disabled = true;
      // 缓存提交状态和结果
      problemAnswerCache[paraIndex] = { answer: val, submitted: true, result: res[0].result };
      // draft保存答案和评分结果
      window.problemDraft = window.problemDraft || {};
      window.problemDraft[paraIndex] = { answer: val, submitted: true, result: res[0].result };
      saveProgressDraft();
        } else {
          btn.disabled = false;
          btn.textContent = '提交';
          alert('判分失败');
        }
      } catch(e) {
        btn.disabled = false;
        btn.textContent = '提交';
        alert('网络错误');
      }
    };
    // 监听输入变化，实时缓存答案（未提交时）
    input.addEventListener('input', () => {
      if (!submitted) {
        problemAnswerCache[paraIndex] = { answer: input.value, submitted: false, result: null };
      }
    });
    form.appendChild(input);
    form.appendChild(document.createElement('br'));
    form.appendChild(btn);
    container.appendChild(form);
    if (submitted && cache && cache.result) {
      showJudgeResult(cache.result, container);
    }
  } else {
    container.appendChild(document.createTextNode('未知题型'));
  }
}


  } else {
    // fallback: render JSON
    container.textContent = JSON.stringify(item, null, 2)
  }
}

// login/register modal
let modalMode = 'login'
function showModal(mode){
  modalMode = mode
  // set appropriate title for each modal mode
  if (mode === 'login') el('modal-title').textContent = '登录'
  else if (mode === 'register') el('modal-title').textContent = '注册'
  else if (mode === 'unregister') el('modal-title').textContent = '注销账户'
  else if (mode === 'changepass') el('modal-title').textContent = '修改密码'
  else el('modal-title').textContent = '登录'
  const m = el('modal')
  if (m){
    m.classList.remove('hidden')
    // 强制使用 inline style 覆盖任何样式冲突
    m.style.display = 'flex'
  }
  // 清空历史输入，避免保留上一轮内容
  const u = el('inp-username'); const p = el('inp-passwd'); const p2 = el('inp-passwd2'); const hint = el('modal-hint'); const labelp2 = el('label-passwd2'); const nicknameEl = el('inp-nickname'); const newp = el('inp-new-passwd'); const newp2 = el('inp-new-passwd2')
  if (u) u.value = ''
  if (p) p.value = ''
  if (p2) p2.value = ''
  if (nicknameEl) nicknameEl.value = ''
  if (newp) newp.value = ''
  if (newp2) newp2.value = ''
  // 如果是注册模式，显示确认密码和提示；否则隐藏
  if (mode === 'register'){
    if (hint) {
      hint.style.display = ''
      hint.innerHTML = '用户名规则：长度 4-32，仅字母、数字、下划线，且不能以数字开头。<br/>注册后用户名不可更改。<br/>密码规则：长度至少 8，且包含 大写、小写、数字、符号 中至少三种。'
    }
    if (labelp2) labelp2.style.display = ''
    // registration no longer requires nickname input: keep nickname hidden
    const labelNick = el('label-nickname'); if (labelNick) labelNick.style.display = 'none'
    // ensure change-password inputs are hidden when entering register mode (in case modal was previously in changepass)
    const labelNew1 = el('label-newpasswd'); const labelNew2 = el('label-newpasswd2')
    if (labelNew1) labelNew1.style.display = 'none'
    if (labelNew2) labelNew2.style.display = 'none'
  } else if (mode === 'unregister'){
    // unregister: show warning, hide confirm
    if (hint) {
      hint.style.display = ''
      hint.innerHTML = '<strong style="color:#c53030">警告：</strong> 注销账户将删除你的账户，此操作不可逆。请输入密码以确认。'
    }
    if (labelp2) labelp2.style.display = 'none'
    // pre-fill username with current username and disable editing if available
    if (u){ u.value = currentUsername || ''; u.disabled = !!currentUsername }
  } else {
    if (hint) hint.style.display = 'none'
    if (labelp2) labelp2.style.display = 'none'
    if (u) u.disabled = false
    const labelNick = el('label-nickname'); if (labelNick) labelNick.style.display = 'none'
    const labelNew1 = el('label-newpasswd'); if (labelNew1) labelNew1.style.display = 'none'
    const labelNew2 = el('label-newpasswd2'); if (labelNew2) labelNew2.style.display = 'none'
  }

  if (mode === 'changepass'){
    // show new password inputs, prefill username and disable
    const labelNew1 = el('label-newpasswd'); const labelNew2 = el('label-newpasswd2')
    if (labelNew1) labelNew1.style.display = ''
    if (labelNew2) labelNew2.style.display = ''
    if (hint){
      hint.style.display = '';
      hint.innerHTML = '请输入当前密码与新密码。<br/>' +
        '密码要求：长度8~32（均包含本数）；应包含大写字母、小写字母、数字、特殊字符中的至少三类；不要与常用词或早期密码相同；建议使用密码管理器保存新密码.'
    }
    if (u){ u.value = currentUsername || ''; u.disabled = true }
    // hide register-only fields
    const labelNick = el('label-nickname'); if (labelNick) labelNick.style.display = 'none'
    if (labelp2) labelp2.style.display = 'none'
  }
}
function hideModal(){
  const m = el('modal')
  if (m){
    m.classList.add('hidden')
    m.style.display = 'none'
  }
  const msg = el('modal-msg')
  if (msg) msg.textContent = ''
}

async function submitModal(){
  const username = el('inp-username').value.trim()
  const passwd = el('inp-passwd').value
  const passwd2El = el('inp-passwd2')
  const passwd2 = passwd2El ? passwd2El.value : ''
  const nicknameEl = el('inp-nickname')
  const nickname = nicknameEl ? nicknameEl.value.trim() : ''
  if (!username || !passwd){ el('modal-msg').textContent = '请填写用户名和密码'; return }
  if (modalMode==='login'){
    const r = await apiPost('/auth/login',{username, passwd})
    if (r.status && r.status.code===0){
      // refresh auth state (will populate username/nickname/avatar from /profile/whoami)
      await checkAuth()
      hideModal()
    } else {
      el('modal-msg').textContent = '登录失败：用户名或密码错误'
    }
  } else if (modalMode === 'register'){
    // 前端合规性校验：与后端文档保持一致
    const usernameOk = validateUsername(username)
    if (!usernameOk){ el('modal-msg').textContent = '用户名不合规：长度 4-32，仅字母/数字/下划线，且不能以数字开头'; return }
    if (passwd !== passwd2){ el('modal-msg').textContent = '两次密码输入不一致'; return }
    const pwdOk = validatePassword(passwd)
    if (!pwdOk.ok){ el('modal-msg').textContent = '密码不合规：' + pwdOk.msg; return }
    // validate nickname
    if (nickname && nickname.length > 64){ el('modal-msg').textContent = '昵称长度不能超过 64 字符'; return }
    const r = await apiPost('/auth/register',{username, passwd, nickname})
    if (r.status && r.status.code===0){
      el('modal-msg').textContent = '注册成功，请使用刚才的账号登录。'
      // 切换到登录模式并清空敏感字段
      modalMode = 'login'
      el('modal-title').textContent = '登录'
      if (passwd2El) passwd2El.value = ''
      el('inp-passwd').value = ''
      // keep username populated to help user login
    } else {
      el('modal-msg').textContent = '注册失败：用户名已存在或服务器错误'
    }
  } else if (modalMode === 'unregister'){
    // unregister flow: username may be prefilled and disabled
    await handleUnregister(username, passwd)
  } else if (modalMode === 'changepass'){
    // change password flow
    const newpass = el('inp-new-passwd') ? el('inp-new-passwd').value : ''
    const newpass2 = el('inp-new-passwd2') ? el('inp-new-passwd2').value : ''
    if (!newpass || !newpass2){ el('modal-msg').textContent = '请填写新密码和确认新密码'; return }
    if (newpass !== newpass2){ el('modal-msg').textContent = '两次新密码输入不一致'; return }
    const ok = validatePassword(newpass)
    if (!ok.ok){ el('modal-msg').textContent = '新密码不合规：' + ok.msg; return }
    // call backend
    const rr = await apiPost('/auth/repasswd', {username, passwd, new_passwd: newpass})
    if (rr.status && rr.status.code===0){
      el('modal-msg').textContent = '密码已修改，所有会话已退出，请重新登录。'
      // sessions deleted server-side; force UI to logged out state
      setTimeout(async ()=>{ hideModal(); await checkAuth(); }, 800)
    } else if (rr.status && rr.status.code===1){
      el('modal-msg').textContent = '原密码错误，修改失败'
    } else if (rr.status && rr.status.code===2){
      el('modal-msg').textContent = '未登录，无法修改密码'
    } else {
      el('modal-msg').textContent = '修改失败，请稍后重试'
    }
  }
}

function validateUsername(u){
  // 长度 4-32，只含字母数字下划线，不以数字开头
  if (!u) return false
  if (u.length < 4 || u.length > 32) return false
  if (/^\d/.test(u)) return false
  if (!/^[A-Za-z0-9_]+$/.test(u)) return false
  return true
}

function validatePassword(p){
  if (!p || p.length < 8) return {ok:false, msg:'长度至少为 8'}
  let categories = 0
  if (/[a-z]/.test(p)) categories++
  if (/[A-Z]/.test(p)) categories++
  if (/[0-9]/.test(p)) categories++
  if (/[^A-Za-z0-9]/.test(p)) categories++
  if (categories < 3) return {ok:false, msg:'请包含大写、小写、数字、符号 中至少三种字符'}
  return {ok:true}
}

// unregister handling (placed after helpers to avoid accidental nesting)
async function handleUnregister(username, passwd){
  try{
    const r = await apiPost('/auth/unregister', {username, passwd})
    if (r.status && r.status.code===0){
      // success: update UI to logged out
      el('modal-msg').textContent = '账户已注销，页面将返回未登录状态。'
      // ensure logout-looking UI
      const us = el('user-status')
      if (us) us.textContent = '未登录'
      el('btn-login').style.display='inline-block'
      el('btn-register').style.display='inline-block'
      el('btn-logout').style.display='none'
      // el('btn-unregister').style.display='none'
      // clear frontend user state immediately to avoid stale UI
      try{ currentUserNickname = null; currentUsername = null; currentUserId = null; currentUserLastLogin = null; currentUserAvatar = null }catch(_){/* ignore */}
      try{ const ha = el('header-avatar'); if (ha){ ha.innerHTML = ''; ha.style.display = 'none' } }catch(_){/* ignore */}
      // hide and clear popover
      const pop = el('user-popover'); if (pop){ pop.style.display = 'none'; pop.innerHTML = '' }
      // refresh server-side state
      await checkAuth()
      // hide modal after short delay
      setTimeout(()=>{ hideModal() }, 800)
      return
    }
    if (r.status && r.status.code===1){
      el('modal-msg').textContent = '密码错误，无法注销。'
      return
    }
    el('modal-msg').textContent = '注销失败，请稍后重试。'
  }catch(e){
    console.error('unregister err', e)
    el('modal-msg').textContent = '网络或服务器错误，注销失败。'
  }
}

async function doLogout(){
  const r = await apiPost('/auth/logout', {})
  if (r.status && r.status.code===0){
    // clear frontend state and hide popover immediately to avoid stale info
    try{ currentUserNickname = null; currentUsername = null; currentUserId = null; currentUserLastLogin = null; currentUserAvatar = null }catch(_){/* ignore */}
    const pop = el('user-popover'); if (pop){ pop.style.display = 'none'; pop.innerHTML = '' }
    try{ const ha = el('header-avatar'); if (ha){ ha.innerHTML = ''; ha.style.display = 'none' } }catch(_){/* ignore */}
    // refresh profile/auth state which will reset header avatar and user vars
    await checkAuth()
  } else {
    alert('登出失败')
  }
}

async function saveProgress(){
  if (!currentSection) return alert('先选小节')
  // 简单示例：将当前阅读进度映射为百分比
  const percentage = Math.round(((paraIndex+1)/Math.max(1, dialogueItems.length))*100)
  const time_spent = 0
  const payload = {percentage, time_spent, completed_at:null, draft: JSON.stringify(dialogueItems)}
  const r = await apiPost(`/lesson/progress/${currentSection.id}/set`, payload)
  if (r.status && r.status.code===0){
    el('progress-info').textContent = `已保存 ${percentage}%`
  } else if (r.status && r.status.code===1){
    el('progress-info').textContent = '未登录：无法保存'
  } else {
    el('progress-info').textContent = '保存失败'
  }
}

function bind(){
  // header buttons
  const btnLogin = el('btn-login')
  const btnRegister = el('btn-register')
  const btnLogout = el('btn-logout')
  const btnUnregister = el('btn-unregister')
  if (btnLogin) btnLogin.addEventListener('click', ()=>showModal('login'))
  if (btnRegister) btnRegister.addEventListener('click', ()=>showModal('register'))
  if (btnLogout) btnLogout.addEventListener('click', ()=>doLogout())
  if (btnUnregister) btnUnregister.addEventListener('click', ()=>showModal('unregister'))

  // sidebar back button (when viewing sections)
  const sidebarBack = el('sidebar-back')
  if (sidebarBack) sidebarBack.addEventListener('click', ()=>{ showCourseList() })

  // modal buttons / overlay
  const modal = el('modal')
  const modalCancel = el('modal-cancel')
  const modalSubmit = el('modal-submit')
  if (modalCancel) modalCancel.addEventListener('click', hideModal)
  if (modalSubmit) modalSubmit.addEventListener('click', submitModal)
  // clicking on overlay (outside inner box) closes modal
  if (modal) modal.addEventListener('click', (evt)=>{
    if (evt.target === modal) hideModal()
  })
  // allow Enter key inside modal to submit
  if (modal) modal.addEventListener('keydown', (evt)=>{
    if (evt.key === 'Enter'){
      evt.preventDefault()
      submitModal()
    }
  })

  // dialogue controls
  const nextBtn = el('next-para')
  const prevBtn = el('prev-para')
  if (nextBtn) nextBtn.addEventListener('click', ()=>{ if (paraIndex<dialogueItems.length-1) paraIndex++, renderDialogue() })
  if (prevBtn) prevBtn.addEventListener('click', ()=>{ if (paraIndex>0) paraIndex--, renderDialogue() })
  const uploadBtn = el('btn-upload-progress')
  if (uploadBtn) uploadBtn.addEventListener('click', uploadProgress)

  // user popover: show username and user id on hover
  const userStatus = el('user-profile')
  const pop = el('user-popover')
  if (userStatus && pop){
    userStatus.addEventListener('mouseenter', (e)=>{
      // populate
      const uname = currentUsername || ''
      const nick = currentUserNickname || ''
      const uid = currentUserId || ''
      // format last login if available
      let lastLoginText = ''
      if (currentUserLastLogin){
        try{
          const dt = new Date(currentUserLastLogin)
          if (!isNaN(dt)) lastLoginText = dt.toLocaleString()
        }catch(_){ lastLoginText = String(currentUserLastLogin) }
      }
      // action buttons: only show change-pass/unregister for logged-in users
      let buttonsHtml = ''
      if (currentUsername){
        buttonsHtml = `<div style="margin-top:8px; margin:0 auto;" >
           <button id="pop-change-pass" class="pop-btn">更改密码</button>
           <button id="pop-unregister" class="pop-btn destructive">删除账户</button>
         </div>`
      } else {
        // 当未登录时，不在悬浮面板显示登录/注册按钮（按要求删除）
        buttonsHtml = ''
      }

      // avatar left, meta right (three lines) and nickname editable
      // if user not logged in, do not show avatars in popover
  let avHtml = ''
  if (currentUsername){
    const ap = currentUserAvatar || ''
    // ensure popover avatar has explicit size and pixelated rendering to avoid blurry upscaling
  avHtml = ap ? `<div class="pop-avatar"><img src="/avatar${ap.startsWith('/')?ap:('/'+ap)}" width="52" height="52" style="width:100%;height:100%;object-fit:cover;image-rendering:pixelated;display:block"/></div>` : `<div class="pop-avatar"></div>`
  }
      const displayNick = nick||uname||'访客'
      pop.innerHTML = `<div style="display:flex;align-items:center;gap:8px">${avHtml}<div class="pop-meta"><div id="pop-nickname-wrap"><strong id="pop-nickname">${displayNick}</strong></div><div class="muted">用户名: ${uname||'-'}</div><div class="muted">用户ID: ${uid||'-'}</div>${lastLoginText?`<div class="muted">上次登录: ${lastLoginText}</div>`:''}</div></div>` +
        `<div class="pop-btn-group">${buttonsHtml}</div>` +
        `<div class="pop-sep"></div>` +
        `<div class="theme-swatches">` +
          `<div class="theme-swatch" title="浅粉" data-color="#ff9bb3" style="background:#ff9bb3"></div>` +
          `<div class="theme-swatch" title="浅橙" data-color="#ffb36b" style="background:#ffb36b"></div>` +
          `<div class="theme-swatch" title="浅黄" data-color="#ffe28a" style="background:#ffe28a"></div>` +
          `<div class="theme-swatch" title="浅绿" data-color="#8fe39a" style="background:#8fe39a"></div>` +
          `<div class="theme-swatch" title="浅蓝" data-color="#5fb3ff" style="background:#5fb3ff"></div>` +
          `<div class="theme-swatch" title="浅紫" data-color="#c39bff" style="background:#c39bff"></div>` +
          `<button id="night-mode-btn" class="theme-swatch" title="夜间模式" style="display:flex;align-items:center;justify-content:center;font-size:1.1em;background:none;border:none;outline:none;cursor:pointer;"></button>` +
        `</div>`

      // show pop to measure
      pop.style.display = 'block'
      pop.style.visibility = 'hidden'
      // compute best position: prefer below, align to right of status
      const rect = userStatus.getBoundingClientRect()
      const popRect = pop.getBoundingClientRect()
      const margin = 8
      // default position below, right-aligned with status
      let left = rect.right - popRect.width
      let top = rect.bottom + margin
      // ensure within viewport
      if (left < margin) left = margin
      if (left + popRect.width > window.innerWidth - margin) left = Math.max(margin, window.innerWidth - popRect.width - margin)
      if (top + popRect.height > window.innerHeight - margin){
        // show above
        top = rect.top - popRect.height - margin
        if (top < margin) top = margin
      }
      pop.style.left = left + 'px'
      pop.style.top = top + 'px'
      pop.style.visibility = 'visible'

      // 主题色切换和夜间模式按钮
      try{
        const swatches = pop.querySelectorAll('.theme-swatch')
        let currentAccent = ''
        try{ currentAccent = (localStorage.getItem('ata_theme_accent') || '').trim().toLowerCase() }catch(e){}
        if (!currentAccent) currentAccent = (getComputedStyle(document.documentElement).getPropertyValue('--accent')||'').trim().toLowerCase()
        // map of known hex -> profile enum name
        const hexToEnum = {
          '#ff9bb3':'pink', '#ffb36b':'orange', '#ffe28a':'yellow', '#8fe39a':'green', '#5fb3ff':'blue', '#c39bff':'purple'
        }
        swatches.forEach(s => {
          // 跳过夜间模式按钮
          if (s.id === 'night-mode-btn') return;
          try{
            const col = (s.dataset.color||'').toLowerCase()
            if (col && currentAccent && col === currentAccent) s.classList.add('selected')
            s.addEventListener('click', async ()=>{
              const c = s.dataset.color
              if (c){
                // 仅切换主题色，不影响夜间模式
                try{ applyTheme(c) }catch(e){ console.warn('applyTheme err', e) }
                // 若夜间模式已开，切换主题色后仍保持夜间模式class
                if (isNightMode()) document.body.classList.add('night-mode')
                swatches.forEach(x=>x.classList.remove('selected'))
                s.classList.add('selected')
                // upload profile colour enum to server
                try{
                  const enumName = hexToEnum[(c||'').toLowerCase()] || null
                  if (enumName){
                    await apiPost('/profile/iamwho', {colour: enumName})
                  }
                }catch(e){ console.warn('upload theme failed', e) }
              }
            })
          }catch(e){console.warn('swatch bind err', e)}
        })
        // 夜间模式按钮
        const nightBtn = pop.querySelector('#night-mode-btn');
        if (nightBtn) {
          function updateNightIcon() {
            nightBtn.innerHTML = isNightMode()
              // 太阳
              ? '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="5.5" stroke="#FFD600" stroke-width="2.5" fill="#FFD600"/><g stroke="#FFD600" stroke-width="2"><line x1="10" y1="2" x2="10" y2="0.5"/><line x1="10" y1="18" x2="10" y2="19.5"/><line x1="2" y1="10" x2="0.5" y2="10"/><line x1="18" y1="10" x2="19.5" y2="10"/><line x1="15.07" y1="4.93" x2="16.14" y2="3.86"/><line x1="4.93" y1="15.07" x2="3.86" y2="16.14"/><line x1="15.07" y1="15.07" x2="16.14" y2="16.14"/><line x1="4.93" y1="4.93" x2="3.86" y2="3.86"/></g></svg>'
              // 弯月
              : '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><path d="M15.5 10.5C15.5 14 12.5 17 9 17C7.5 17 6.1 16.5 5 15.6C8.5 15.2 12 12.2 12 8.5c0-1.2-.3-2.3-.8-3.2C13.7 6.1 15.5 8.1 15.5 10.5Z" fill="#FFD600" stroke="#FFD600" stroke-width="2"/></svg>';
          }
          updateNightIcon();
          nightBtn.addEventListener('click', function(){
            setNightMode(!isNightMode());
            updateNightIcon();
          });
        }
      }catch(e){console.warn('theme swatch/night mode init err', e)}

// 夜间模式辅助函数
function isNightMode() {
  try {
    return localStorage.getItem('ata_night_mode') === '1'
  } catch(e) { return false }
}
function setNightMode(on) {
  if (on) {
    document.body.classList.add('night-mode')
    try { localStorage.setItem('ata_night_mode', '1') } catch(e){}
  } else {
    document.body.classList.remove('night-mode')
    try { localStorage.setItem('ata_night_mode', '0') } catch(e){}
  }
  // 夜间模式切换时刷新--accent-foreground
  try {
    const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent') || '#5fb3ff';
    applyTheme(accent.trim() || '#5fb3ff');
  } catch(e){}
}
// 页面加载时自动应用夜间模式
try {
  if (localStorage.getItem('ata_night_mode') === '1') {
    document.body.classList.add('night-mode')
  }
} catch(e){}

      // make nickname editable in popover
      try{
        const nickWrap = document.getElementById('pop-nickname-wrap')
        // helper to attach click handler to nickname element (callable to reattach after replacing innerHTML)
        const attachNickBinding = ()=>{
          const nickElNow = document.getElementById('pop-nickname')
          if (!nickElNow || !nickWrap) return
          // if not logged in, clicking nickname should open login modal instead of allowing edit
          if (!currentUsername){
            nickElNow.style.cursor = 'pointer'
            nickElNow.addEventListener('click', ()=>{ hideModal(); showModal('login') })
            return
          }
          nickElNow.style.cursor = 'text'
          const onClick = ()=>{
            const cur = nickElNow.textContent || ''
            const input = document.createElement('input')
            input.type = 'text'
            input.id = 'pop-nickname-input'
            input.className = 'nick-edit'
            input.value = cur
            nickWrap.innerHTML = ''
            nickWrap.appendChild(input)
            input.focus()
            isEditingNickname = true
            // support IME composition: only submit on Enter when not composing
            let composing = false
            input.addEventListener('compositionstart', ()=>{ composing = true })
            input.addEventListener('compositionend', ()=>{ composing = false })
            // submit on blur or Enter (but ignore Enter during composition)
            const submitNick = async ()=>{
              console.log('submitNick')
              const v = (input.value || '').trim()
              try{
                const res = await apiPost('/profile/iamwho', {nickname: v})
                if (res && res.status && res.status.code===0){
                  currentUserNickname = v || null
                  el('user-status').textContent = currentUserNickname || currentUsername || '已登录'
                  nickWrap.innerHTML = `<strong id="pop-nickname">${v||currentUsername||'访客'}</strong>`
                } else {
                  // restore
                  nickWrap.innerHTML = `<strong id="pop-nickname">${cur}</strong>`
                }
              }catch(e){
                console.warn('nickname update failed', e)
                nickWrap.innerHTML = `<strong id="pop-nickname">${cur}</strong>`
              }
              // reattach binding after replacing content
              attachNickBinding()
              isEditingNickname = false
            }
            input.addEventListener('blur', submitNick)
            // use keydown and respect composition state to support MS Pinyin and other IMEs reliably
            input.addEventListener('keydown', (ev)=>{ if (ev.key === 'Enter'){ if (!composing){ ev.preventDefault(); submitNick() } else { /* ignore Enter during composition */ } } })
            // allow Esc to cancel editing gracefully
            input.addEventListener('keydown', (ev)=>{ if (ev.key === 'Escape'){ ev.preventDefault(); nickWrap.innerHTML = `<strong id=\"pop-nickname\">${cur}</strong>`; attachNickBinding(); isEditingNickname = false } })
          }
          // remove existing handler to avoid duplicate listeners
          try{ const cleaned = nickElNow.cloneNode(true); nickElNow.parentNode.replaceChild(cleaned, nickElNow) }catch(_){/* ignore */}
          const replaced = document.getElementById('pop-nickname')
          if (replaced) replaced.addEventListener('click', onClick)
        }
        attachNickBinding()
      }catch(e){console.warn('nick edit init err', e)}

      // bind buttons
      const cb = document.getElementById('pop-change-pass')
      const ub = document.getElementById('pop-unregister')
      const lb = document.getElementById('pop-login')
      if (cb) cb.addEventListener('click', ()=>{ showModal('changepass') })
      if (ub) ub.addEventListener('click', ()=>{ showModal('unregister') })
      if (lb) lb.addEventListener('click', ()=>{ hideModal(); showModal('login') })
    })
    userStatus.addEventListener('mouseleave', (e)=>{
      // small timeout to allow moving into pop; keep open while editing nickname or focused inside pop
      setTimeout(()=>{
        const ae = document.activeElement
        const focusedInsidePop = ae && pop.contains(ae)
        if (isEditingNickname || focusedInsidePop) return
        if (!pop.matches(':hover') && !userStatus.matches(':hover')) pop.style.display = 'none'
      }, 200)
    })
    // also hide on pop hover leave
    pop.addEventListener('mouseenter', ()=>{ pop.style.display = 'block' })
    pop.addEventListener('mouseleave', ()=>{
      // don't hide if currently editing nickname or the input still has focus (IME candidate UI may virtually leave the element)
      setTimeout(()=>{
        const ae = document.activeElement
        const focusedInsidePop = ae && pop.contains(ae)
        if (isEditingNickname || focusedInsidePop) return
        pop.style.display = 'none'
      }, 150)
    })
  }
}

window.addEventListener('load', async ()=>{
  bind()
  await checkAuth()
  await loadCourses()
  // 尝试请求首页以便后端把 cookie 或状态更新（如果需要的话）
})
