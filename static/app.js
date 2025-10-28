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
  const fg = (brightness > 200) ? '#000' : '#fff'
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

// set initial theme to saved or default
try{
  const saved = localStorage.getItem('ata_theme_accent')
  if (saved) applyTheme(saved)
  else applyTheme('#5fb3ff')
}catch(e){ applyTheme('#5fb3ff') }

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
    li.style.color = '#222'
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
  paraIndex = 0
  renderDialogue()
  // 加载已有进度
  const p = await apiGet(`/lesson/progress/${section.id}/get`)
  if (p.status && p.status.code===1){
    el('progress-info').textContent = '未登录：保存进度功能受限。'
    el('btn-save-progress').disabled = true
  } else if (p.progress){
    el('progress-info').textContent = `已学习 ${p.progress.percentage}%，用时 ${p.progress.time_spent}s`
    el('btn-save-progress').disabled = false
  } else {
    el('progress-info').textContent = '尚无进度记录'
    el('btn-save-progress').disabled = false
  }
}

function renderDialogue(){
  const content = el('dialogue-content')
  if (!dialogueItems.length){
    content.textContent = '本小节内容为空。'
    el('prev-para').disabled = true
    el('next-para').disabled = true
    return
  }
  // render current item based on its type
  const item = dialogueItems[paraIndex]
  renderItem(item, content)
  el('prev-para').disabled = paraIndex===0
  el('next-para').disabled = paraIndex>=dialogueItems.length-1
}

function renderItem(item, container){
  // container is DOM element
  if (!item) { container.textContent = '' ; return }
  const t = (item.type || 'text')
  container.innerHTML = ''
  if (t === 'text'){
    // item.content may be string or other
    const txt = (typeof item.content !== 'undefined') ? item.content : (item.text || '')
    container.textContent = String(txt)
  } else if (t === 'video'){
    // 播放固定示例视频
    const video = document.createElement('video')
    video.controls = true
    video.style.maxWidth = '100%'
    video.src = '/static/video/example.mp4'
    container.appendChild(video)
  } else if (t === 'problem'){
    // problem.content 必须是 number 或 number[]
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
    // 随机取一个元素（修正边界，确保 idx ∈ [0, arr.length-1]）
    let idx = 0
    if (arr.length > 1) {
      // Math.random() ∈ [0,1)，但极小概率浮点误差可能导致 idx==arr.length
      idx = Math.floor(Math.random() * arr.length)
      if (idx >= arr.length) idx = arr.length - 1
    }
    const problemId = arr[idx]
    // 异步获取问题内容
    container.textContent = '加载中...'
    apiPost('/problem/get', {problem_id: [problemId]}).then(data => {
      // 这里仅做占位，后续处理问题内容
      if (data && data.content && Array.isArray(data.content) && data.content[0]) {
        container.textContent = JSON.stringify(data.content[0], null, 2)
      } else {
        container.textContent = '未获取到问题内容'
      }
    }).catch(e => {
      container.textContent = '获取问题失败'
    })
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
  const saveBtn = el('btn-save-progress')
  if (saveBtn) saveBtn.addEventListener('click', saveProgress)

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
        buttonsHtml +
        `<div class="pop-sep"></div>` +
        `<div class="theme-swatches">` +
          `<div class="theme-swatch" title="浅粉" data-color="#ff9bb3" style="background:#ff9bb3"></div>` +
          `<div class="theme-swatch" title="浅橙" data-color="#ffb36b" style="background:#ffb36b"></div>` +
          `<div class="theme-swatch" title="浅黄" data-color="#ffe28a" style="background:#ffe28a"></div>` +
          `<div class="theme-swatch" title="浅绿" data-color="#8fe39a" style="background:#8fe39a"></div>` +
          `<div class="theme-swatch" title="浅蓝" data-color="#5fb3ff" style="background:#5fb3ff"></div>` +
          `<div class="theme-swatch" title="浅紫" data-color="#c39bff" style="background:#c39bff"></div>` +
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

      // bind theme swatches: clicking changes theme and highlights selection
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
          try{
            const col = (s.dataset.color||'').toLowerCase()
            if (col && currentAccent && col === currentAccent) s.classList.add('selected')
            s.addEventListener('click', async ()=>{
              const c = s.dataset.color
              if (c){
                // apply theme and mark selected
                try{ applyTheme(c) }catch(e){ console.warn('applyTheme err', e) }
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
      }catch(e){console.warn('theme swatch init err', e)}

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
