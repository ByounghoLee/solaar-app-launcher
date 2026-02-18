#!/usr/bin/env python3
"""Solaar App Launcher - MX Master 3S (GTK3)
그룹 컬럼(가로) + ⠿ 수동 드래그 순서/그룹 이동"""

import os, sys, signal, subprocess, glob, re, atexit

PIDFILE = "/tmp/solaar-app-launcher.pid"

def _toggle_or_start():
    """이미 실행 중이면 종료하고 exit, 아니면 PID 파일 작성"""
    if os.path.exists(PIDFILE):
        try:
            with open(PIDFILE, 'r') as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, signal.SIGTERM)
            os.remove(PIDFILE)
            sys.exit(0)
        except (ProcessLookupError, ValueError):
            # 프로세스가 이미 없음 — 정상 진행
            try: os.remove(PIDFILE)
            except: pass
        except Exception:
            try: os.remove(PIDFILE)
            except: pass
    # PID 파일 작성
    with open(PIDFILE, 'w') as f:
        f.write(str(os.getpid()))
    atexit.register(lambda: os.path.exists(PIDFILE) and os.remove(PIDFILE))

_toggle_or_start()

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib

CONFIG = os.path.expanduser("~/.config/solaar/app-launcher-apps.conf")
ICON_SZ = 24

DEFAULT_CONF = """\
[개발]
VS Code|code|visual-studio-code
Antigravity|antigravity|antigravity
Obsidian|obsidian|obsidian

[시스템]
터미널|gnome-terminal|utilities-terminal
텍스트 편집기|gnome-text-editor|org.gnome.TextEditor
시스템 설정|gnome-control-center|gnome-control-center
시스템 모니터|gnome-system-monitor|org.gnome.SystemMonitor
계산기|gnome-calculator|org.gnome.Calculator
스크린샷|dbus-send --session --print-reply --dest=org.gnome.Shell /org/gnome/Shell org.gnome.Shell.Eval string:'Main.screenshotUI.open()'|applets-screenshooter

[업무/소통]
Zoom|zoom|Zoom
Whale|naver-whale|naver-whale
VMware|vmware|vmware-workstation
"""

_theme = None
def _gt():
    global _theme
    if not _theme: _theme = Gtk.IconTheme.get_default()
    return _theme

def _pb(name, sz=ICON_SZ):
    if not name: return None
    try: return _gt().load_icon(name, sz, Gtk.IconLookupFlags.FORCE_SIZE)
    except: pass
    if os.path.isfile(name):
        try: return GdkPixbuf.Pixbuf.new_from_file_at_scale(name, sz, sz, True)
        except: pass
    for ext in ('svg','png'):
        for b in ('/usr/share/icons/hicolor','/usr/share/pixmaps'):
            for p in glob.glob(os.path.join(b,'**',f'{name}.{ext}'),recursive=True):
                try: return GdkPixbuf.Pixbuf.new_from_file_at_scale(p, sz, sz, True)
                except: pass
    return None

def _ic(name, sz=ICON_SZ):
    p = _pb(name, sz)
    return Gtk.Image.new_from_pixbuf(p) if p else Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)

def load_conf():
    if not os.path.exists(CONFIG):
        os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
        with open(CONFIG,'w') as f: f.write(DEFAULT_CONF)
    gs, cn, ca = [], "기타", []
    with open(CONFIG,'r') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'): continue
            m = re.match(r'^\[(.+)\]$', ln)
            if m:
                if ca or gs: gs.append((cn, ca))
                cn, ca = m.group(1).strip(), []
                continue
            p = ln.split('|')
            ca.append((p[0].strip(), p[1].strip() if len(p)>1 else '', p[2].strip() if len(p)>2 else ''))
    if ca or not gs: gs.append((cn, ca))
    if len(gs)>1 and gs[0]==("기타",[]): gs.pop(0)
    return gs

def save_conf(gs):
    with open(CONFIG,'w') as f:
        for gn, apps in gs:
            f.write(f"[{gn}]\n")
            for n,c,i in apps: f.write(f"{n}|{c}|{i}\n")
            f.write("\n")

def get_installed():
    apps = {}
    for d in ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]:
        for path in glob.glob(os.path.join(d,"*.desktop")):
            try:
                with open(path,'r',errors='replace') as f: ct = f.read()
            except: continue
            if re.search(r'^NoDisplay\s*=\s*true',ct,re.M|re.I): continue
            nk = re.search(r'^Name\[ko\]\s*=\s*(.+)$',ct,re.M)
            ne = re.search(r'^Name\s*=\s*(.+)$',ct,re.M)
            nm = nk or ne
            if not nm: continue
            name = nm.group(1).strip()
            em = re.search(r'^Exec\s*=\s*(.+)$',ct,re.M)
            if not em: continue
            exc = re.sub(r'\s+%[a-zA-Z]','',em.group(1).strip())
            im = re.search(r'^Icon\s*=\s*(.+)$',ct,re.M)
            ico = im.group(1).strip() if im else ''
            if name not in apps: apps[name] = (exc, ico)
    return sorted([(n,c,i) for n,(c,i) in apps.items()], key=lambda x: x[0].lower())

CSS = b"""
window { background-color: #2b2b2b; }
.title-label { font-size: 15px; font-weight: bold; color: #fff; padding: 6px 8px 2px 8px; }
.hint-label { font-size: 10px; color: #888; padding: 0 8px 4px 8px; }
.group-col { background: #333; border-radius: 8px; padding: 4px; }
.group-hdr { font-size: 12px; font-weight: bold; color: #8ab4f8; padding: 4px 8px; background: transparent; border: none; }
.group-hdr:hover { color: #aacfff; }
.app-row { padding: 3px 4px; border-radius: 5px; }
.app-row:hover { background: #444; }
.app-btn { color: #e0e0e0; border: none; background: transparent; padding: 2px 4px; }
.app-btn:hover { background: #555; }
.handle-lbl { color: #555; font-size: 13px; padding: 0 2px; }
.drop-above { border-top: 2px solid #5b9df5; margin-top: -2px; }
.drop-below { border-bottom: 2px solid #5b9df5; margin-bottom: -2px; }
.drag-source-row { opacity: 0.3; }
.action-button { padding: 5px 12px; border-radius: 6px; font-size: 12px; min-height: 28px; }
.add-btn { background: #3a7bd5; color: white; border: none; }
.add-btn:hover { background: #4a8be5; }
.del-btn { background: #d94040; color: white; border: none; }
.del-btn:hover { background: #e95050; }
.back-btn { background: #555; color: white; border: none; }
.back-btn:hover { background: #666; }
.ok-btn { background: #40a040; color: white; border: none; }
.ok-btn:hover { background: #50b050; }
.grp-btn { background: #6a5acd; color: white; border: none; }
.grp-btn:hover { background: #7a6add; }
.search-entry { background: #3a3a3a; color: #e0e0e0; border: 1px solid #555; border-radius: 6px; padding: 6px; }
.edit-entry { background: #3a3a3a; color: #e0e0e0; border: 1px solid #555; border-radius: 4px; padding: 4px 8px; }
.field-label { color: #ccc; font-size: 12px; }
"""


class AppLauncher(Gtk.Window):
    def __init__(self):
        super().__init__(title="App Launcher")
        self.set_default_size(650, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)
        self.set_keep_above(True)
        cp = Gtk.CssProvider(); cp.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), cp, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.connect("key-press-event", self._key)
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(200)
        self.add(self.stack)
        self.groups = load_conf()

        # Manual drag state
        self._drag_info = None      # (gi, ai) source
        self._drag_start_xy = None  # (x_root, y_root) start pos
        self._dragging = False      # beyond threshold?
        self._drag_popup = None     # floating label
        self._all_rows = []         # [(gi, ai, row_widget), ...]
        self._all_columns = []      # [(gi, column_widget), ...]

        self._build_main()
        self.show_all()

    def _key(self, w, ev):
        if ev.keyval == Gdk.KEY_Escape:
            if self.stack.get_visible_child_name() == "main": Gtk.main_quit()
            else: self._go_main()
            return True
        return False

    def _rm(self, n):
        c = self.stack.get_child_by_name(n)
        if c: self.stack.remove(c)

    # ══════════ MAIN VIEW ══════════
    def _build_main(self):
        self._rm("main")
        self._all_rows = []
        self._all_columns = []

        vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vb.set_margin_top(6); vb.set_margin_bottom(6); vb.set_margin_start(8); vb.set_margin_end(8)

        t = Gtk.Label(label="🖱️ 앱 실행기")
        t.get_style_context().add_class("title-label"); t.set_halign(Gtk.Align.START)
        vb.pack_start(t, False, False, 0)

        h = Gtk.Label(label="클릭: 실행  ·  ⠿ 드래그: 순서/그룹 이동  ·  그룹명 클릭: 이름변경")
        h.get_style_context().add_class("hint-label"); h.set_halign(Gtk.Align.START)
        vb.pack_start(h, False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox.set_homogeneous(True)

        for gi, (gn, apps) in enumerate(self.groups):
            col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            col.get_style_context().add_class("group-col")
            col._gi = gi
            self._all_columns.append((gi, col))

            hdr = Gtk.Button(label=f"📂 {gn}")
            hdr.get_style_context().add_class("group-hdr")
            hdr.set_relief(Gtk.ReliefStyle.NONE)
            hdr.connect("clicked", self._rename_grp, gi)
            col.pack_start(hdr, False, False, 0)

            for ai, (name, cmd, ico) in enumerate(apps):
                row = self._mkrow(gi, ai, name, cmd, ico)
                col.pack_start(row, False, False, 0)

            hbox.pack_start(col, True, True, 0)

        vb.pack_start(hbox, True, True, 0)

        sep = Gtk.Separator(); sep.set_margin_top(4)
        vb.pack_start(sep, False, False, 0)

        bb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        bb.set_halign(Gtk.Align.CENTER)
        for lbl, cls, cb in [("➕ 추가","add-btn",self._show_add),("➖ 삭제","del-btn",self._show_del),("📂 그룹추가","grp-btn",self._add_grp)]:
            b = Gtk.Button(label=lbl); b.get_style_context().add_class("action-button"); b.get_style_context().add_class(cls)
            b.connect("clicked", cb); bb.pack_start(b, True, True, 0)
        vb.pack_start(bb, False, False, 4)

        self.stack.add_named(vb, "main")

    def _mkrow(self, gi, ai, name, cmd, ico):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        row.get_style_context().add_class("app-row")
        row.set_margin_start(2); row.set_margin_end(2)
        row._gi = gi; row._ai = ai

        # ⠿ HANDLE — manual drag via mouse events
        hev = Gtk.EventBox()
        hev.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                       Gdk.EventMask.BUTTON_RELEASE_MASK |
                       Gdk.EventMask.POINTER_MOTION_MASK)
        hl = Gtk.Label(label=" ⠿ ")
        hl.get_style_context().add_class("handle-lbl")
        hev.add(hl)
        hev.connect("button-press-event", self._h_press, gi, ai)
        hev.connect("motion-notify-event", self._h_motion)
        hev.connect("button-release-event", self._h_release)
        hev.connect("realize", lambda w: w.get_window().set_cursor(
            Gdk.Cursor.new_from_name(w.get_display(), "grab")))
        row.pack_start(hev, False, False, 0)

        # APP BUTTON
        btn = Gtk.Button()
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.get_style_context().add_class("app-btn")
        bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        bx.pack_start(_ic(ico, ICON_SZ), False, False, 0)
        lb = Gtk.Label(label=name, xalign=0); lb.set_ellipsize(Pango.EllipsizeMode.END)
        bx.pack_start(lb, True, True, 0)
        btn.add(bx)
        btn.connect("clicked", lambda b, c=cmd: self._launch(c))
        row.pack_start(btn, True, True, 0)

        self._all_rows.append((gi, ai, row))
        return row

    def _launch(self, cmd):
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
        Gtk.main_quit()

    # ── Manual drag: handle events ──
    def _h_press(self, hev, event, gi, ai):
        if event.button != 1:
            return False
        self._drag_info = (gi, ai)
        self._drag_start_xy = (event.x_root, event.y_root)
        self._dragging = False
        return True

    def _h_motion(self, hev, event):
        if self._drag_info is None:
            return False
        sx, sy = self._drag_start_xy
        dx, dy = abs(event.x_root - sx), abs(event.y_root - sy)

        if not self._dragging:
            if dx < 8 and dy < 8:
                return True
            # Start drag — create popup, dim source
            self._dragging = True
            gi, ai = self._drag_info
            name = self.groups[gi][1][ai][0]
            self._drag_popup = Gtk.Window(type=Gtk.WindowType.POPUP)
            self._drag_popup.set_decorated(False)
            self._drag_popup.set_opacity(0.85)
            pl = Gtk.Label(label=f"  ⠿ {name}  ")
            pl.set_margin_top(4); pl.set_margin_bottom(4)
            self._drag_popup.add(pl)
            self._drag_popup.show_all()
            # Dim source row
            for rgi, rai, rw in self._all_rows:
                if rgi == gi and rai == ai:
                    rw.get_style_context().add_class("drag-source-row")

        # Move popup
        if self._drag_popup:
            self._drag_popup.move(int(event.x_root) + 12, int(event.y_root) - 10)

        # Update drop indicator
        self._update_indicator(event.x_root, event.y_root)
        return True

    def _h_release(self, hev, event):
        if self._drag_info is None:
            return False

        if self._dragging:
            self._execute_drop(event.x_root, event.y_root)

        # Cleanup
        self._drag_info = None
        self._dragging = False
        if self._drag_popup:
            self._drag_popup.destroy()
            self._drag_popup = None
        self._clear_indicators()
        return True

    def _get_row_screen_rect(self, row_widget):
        """Get row's screen-coordinates bounding rect"""
        alloc = row_widget.get_allocation()
        gdk_win = row_widget.get_window()
        if gdk_win is None:
            return None
        # get_root_coords translates widget-local coords to screen coords
        rx, ry = gdk_win.get_root_coords(alloc.x, alloc.y)
        return (rx, ry, alloc.width, alloc.height)

    def _get_col_screen_rect(self, col_widget):
        alloc = col_widget.get_allocation()
        gdk_win = col_widget.get_window()
        if gdk_win is None:
            return None
        rx, ry = gdk_win.get_root_coords(alloc.x, alloc.y)
        return (rx, ry, alloc.width, alloc.height)

    def _update_indicator(self, mx, my):
        self._clear_indicators()
        for rgi, rai, rw in self._all_rows:
            rect = self._get_row_screen_rect(rw)
            if rect is None:
                continue
            rx, ry, rw2, rh = rect
            if rx <= mx < rx + rw2 and ry <= my < ry + rh:
                sc = rw.get_style_context()
                mid = ry + rh / 2
                if my < mid:
                    sc.add_class("drop-above")
                else:
                    sc.add_class("drop-below")
                return

    def _clear_indicators(self):
        for _, _, rw in self._all_rows:
            sc = rw.get_style_context()
            sc.remove_class("drop-above")
            sc.remove_class("drop-below")
            sc.remove_class("drag-source-row")

    def _execute_drop(self, mx, my):
        if not self._drag_info:
            return
        sg, sa = self._drag_info

        # Find target row
        target_gi, insert_at = None, None
        for rgi, rai, rw in self._all_rows:
            rect = self._get_row_screen_rect(rw)
            if rect is None:
                continue
            rx, ry, rw2, rh = rect
            if rx <= mx < rx + rw2 and ry <= my < ry + rh:
                mid = ry + rh / 2
                target_gi = rgi
                insert_at = rai if my < mid else rai + 1
                break

        # If no row hit, check if cursor is over a column (empty area → append)
        if target_gi is None:
            for cgi, cw in self._all_columns:
                rect = self._get_col_screen_rect(cw)
                if rect is None:
                    continue
                cx, cy, cw2, ch = rect
                if cx <= mx < cx + cw2 and cy <= my < cy + ch:
                    target_gi = cgi
                    insert_at = len(self.groups[cgi][1])
                    break

        if target_gi is None:
            return

        # Same position? skip
        if sg == target_gi and (sa == insert_at or sa + 1 == insert_at):
            return

        # Execute move
        app = self.groups[sg][1].pop(sa)
        if sg == target_gi and sa < insert_at:
            insert_at -= 1
        insert_at = max(0, min(insert_at, len(self.groups[target_gi][1])))
        self.groups[target_gi][1].insert(insert_at, app)
        save_conf(self.groups)
        self._refresh()

    # ── group ops ──
    def _rename_grp(self, btn, gi):
        d = Gtk.Dialog(title="그룹 이름", parent=self, flags=Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT)
        d.add_button("취소",Gtk.ResponseType.CANCEL); d.add_button("변경",Gtk.ResponseType.OK)
        e = Gtk.Entry(); e.set_text(self.groups[gi][0])
        e.set_margin_top(12); e.set_margin_bottom(12); e.set_margin_start(12); e.set_margin_end(12)
        e.connect("activate", lambda w: d.response(Gtk.ResponseType.OK))
        d.get_content_area().add(e); d.show_all()
        if d.run() == Gtk.ResponseType.OK and e.get_text().strip():
            self.groups[gi] = (e.get_text().strip(), self.groups[gi][1]); save_conf(self.groups); self._refresh()
        d.destroy()

    def _add_grp(self, *a):
        d = Gtk.Dialog(title="그룹 추가", parent=self, flags=Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT)
        d.add_button("취소",Gtk.ResponseType.CANCEL); d.add_button("추가",Gtk.ResponseType.OK)
        e = Gtk.Entry(); e.set_placeholder_text("그룹 이름")
        e.set_margin_top(12); e.set_margin_bottom(12); e.set_margin_start(12); e.set_margin_end(12)
        e.connect("activate", lambda w: d.response(Gtk.ResponseType.OK))
        d.get_content_area().add(e); d.show_all()
        if d.run() == Gtk.ResponseType.OK and e.get_text().strip():
            self.groups.append((e.get_text().strip(),[])); save_conf(self.groups); self._refresh()
        d.destroy()

    def _refresh(self):
        self._build_main(); self.show_all(); self.stack.set_visible_child_name("main")
    def _go_main(self):
        self.groups = load_conf(); self._refresh()

    # ══════════ ADD VIEW ══════════
    def _show_add(self, *a):
        self._rm("add")
        bx = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        bx.set_margin_top(6); bx.set_margin_bottom(6); bx.set_margin_start(10); bx.set_margin_end(10)

        hr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        t = Gtk.Label(label="➕ 프로그램 추가"); t.get_style_context().add_class("title-label")
        hr.pack_start(t, True, True, 0)
        gl = Gtk.Label(label="그룹:"); gl.get_style_context().add_class("field-label"); hr.pack_start(gl, False, False, 0)
        self._acb = Gtk.ComboBoxText()
        for gn, _ in self.groups: self._acb.append_text(gn)
        self._acb.set_active(0); hr.pack_start(self._acb, False, False, 0)
        bx.pack_start(hr, False, False, 0)

        se = Gtk.SearchEntry(); se.set_placeholder_text("🔍 검색..."); se.get_style_context().add_class("search-entry")
        bx.pack_start(se, False, False, 4)

        scr = Gtk.ScrolledWindow(); scr.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC); scr.set_vexpand(True)
        self._alb = Gtk.ListBox(); self._alb.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._alb.set_filter_func(lambda r, s: (not s.get_text()) or s.get_text().lower() in r.app_name.lower() or s.get_text().lower() in r.app_cmd.lower(), se)
        se.connect("search-changed", lambda w: self._alb.invalidate_filter())

        for name, cmd, ico in get_installed():
            row = Gtk.ListBoxRow(); row.app_name=name; row.app_cmd=cmd; row.app_icon=ico
            hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); hb.set_margin_top(2); hb.set_margin_bottom(2); hb.set_margin_start(4)
            hb.pack_start(_ic(ico), False, False, 0)
            nl = Gtk.Label(label=name, xalign=0); nl.set_hexpand(True); hb.pack_start(nl, True, True, 0)
            cl = Gtk.Label(label=cmd, xalign=1); cl.set_opacity(0.5); cl.set_ellipsize(Pango.EllipsizeMode.END); cl.set_max_width_chars(18)
            hb.pack_start(cl, False, False, 0); row.add(hb); self._alb.add(row)
        scr.add(self._alb); bx.pack_start(scr, True, True, 0)

        bb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); bb.set_halign(Gtk.Align.CENTER)
        bk = Gtk.Button(label="← 뒤로"); bk.get_style_context().add_class("action-button"); bk.get_style_context().add_class("back-btn"); bk.connect("clicked", lambda w: self._go_main())
        wb = Gtk.Button(label="🌐 웹사이트"); wb.get_style_context().add_class("action-button"); wb.get_style_context().add_class("grp-btn"); wb.connect("clicked", self._show_web_add)
        nx = Gtk.Button(label="다음 →"); nx.get_style_context().add_class("action-button"); nx.get_style_context().add_class("add-btn"); nx.connect("clicked", self._show_edit)
        bb.pack_start(bk, True, True, 0); bb.pack_start(wb, True, True, 0); bb.pack_start(nx, True, True, 0)
        bx.pack_start(bb, False, False, 4)
        self.stack.add_named(bx, "add"); self.show_all(); self.stack.set_visible_child_name("add"); se.grab_focus()

    def _show_edit(self, *a):
        r = self._alb.get_selected_row()
        if not r: return
        self._rm("edit"); self._eico = r.app_icon; self._egi = self._acb.get_active()
        bx = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        bx.set_margin_top(6); bx.set_margin_bottom(6); bx.set_margin_start(10); bx.set_margin_end(10)
        t = Gtk.Label(label="✏️ 정보 수정"); t.get_style_context().add_class("title-label"); t.set_halign(Gtk.Align.START); bx.pack_start(t, False, False, 0)
        pb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10); pb.set_halign(Gtk.Align.CENTER); pb.set_margin_top(8); pb.set_margin_bottom(8)
        pb.pack_start(_ic(r.app_icon, 48), False, False, 0)
        pl = Gtk.Label(label=r.app_name); pl.get_style_context().add_class("title-label"); pb.pack_start(pl, False, False, 0)
        bx.pack_start(pb, False, False, 0)
        fl = Gtk.Label(label="표시 이름:", xalign=0); fl.get_style_context().add_class("field-label"); bx.pack_start(fl, False, False, 2)
        self._en = Gtk.Entry(); self._en.set_text(r.app_name); self._en.get_style_context().add_class("edit-entry"); bx.pack_start(self._en, False, False, 0)
        cl = Gtk.Label(label="실행 명령:", xalign=0); cl.get_style_context().add_class("field-label"); bx.pack_start(cl, False, False, 2)
        self._ec = Gtk.Entry(); self._ec.set_text(r.app_cmd); self._ec.get_style_context().add_class("edit-entry"); bx.pack_start(self._ec, False, False, 0)
        sp = Gtk.Box(); sp.set_vexpand(True); bx.pack_start(sp, True, True, 0)
        bb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); bb.set_halign(Gtk.Align.CENTER)
        bk = Gtk.Button(label="← 뒤로"); bk.get_style_context().add_class("action-button"); bk.get_style_context().add_class("back-btn"); bk.connect("clicked", lambda w: self._show_add())
        sv = Gtk.Button(label="✔ 추가"); sv.get_style_context().add_class("action-button"); sv.get_style_context().add_class("ok-btn"); sv.connect("clicked", self._do_add)
        bb.pack_start(bk, True, True, 0); bb.pack_start(sv, True, True, 0); bx.pack_start(bb, False, False, 4)
        self.stack.add_named(bx, "edit"); self.show_all(); self.stack.set_visible_child_name("edit")

    def _do_add(self, *a):
        n, c = self._en.get_text().strip(), self._ec.get_text().strip()
        if n and c:
            self.groups[self._egi][1].append((n, c, self._eico)); save_conf(self.groups); self._go_main()

    # ══════════ WEB ADD VIEW ══════════
    def _show_web_add(self, *a):
        self._rm("web_add")
        bx = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        bx.set_margin_top(6); bx.set_margin_bottom(6); bx.set_margin_start(10); bx.set_margin_end(10)

        t = Gtk.Label(label="🌐 웹사이트 추가"); t.get_style_context().add_class("title-label"); t.set_halign(Gtk.Align.START)
        bx.pack_start(t, False, False, 0)

        # 아이콘 미리보기
        pb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10); pb.set_halign(Gtk.Align.CENTER); pb.set_margin_top(8); pb.set_margin_bottom(8)
        pb.pack_start(_ic("web-browser", 48), False, False, 0)
        pl = Gtk.Label(label="Website"); pl.get_style_context().add_class("title-label"); pb.pack_start(pl, False, False, 0)
        bx.pack_start(pb, False, False, 0)

        # 그룹 선택
        gh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        gl = Gtk.Label(label="그룹:"); gl.get_style_context().add_class("field-label"); gh.pack_start(gl, False, False, 0)
        self._wcb = Gtk.ComboBoxText()
        for gn, _ in self.groups: self._wcb.append_text(gn)
        self._wcb.set_active(0); gh.pack_start(self._wcb, True, True, 0)
        bx.pack_start(gh, False, False, 0)

        # 표시 이름
        fl = Gtk.Label(label="표시 이름:", xalign=0); fl.get_style_context().add_class("field-label"); bx.pack_start(fl, False, False, 2)
        self._wn = Gtk.Entry(); self._wn.set_placeholder_text("예: GitHub")
        self._wn.get_style_context().add_class("edit-entry"); bx.pack_start(self._wn, False, False, 0)

        # URL
        ul = Gtk.Label(label="URL:", xalign=0); ul.get_style_context().add_class("field-label"); bx.pack_start(ul, False, False, 2)
        self._wu = Gtk.Entry(); self._wu.set_placeholder_text("https://github.com")
        self._wu.get_style_context().add_class("edit-entry")
        self._wu.connect("activate", lambda w: self._do_web_add())
        bx.pack_start(self._wu, False, False, 0)

        sp = Gtk.Box(); sp.set_vexpand(True); bx.pack_start(sp, True, True, 0)

        bb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); bb.set_halign(Gtk.Align.CENTER)
        bk = Gtk.Button(label="← 뒤로"); bk.get_style_context().add_class("action-button"); bk.get_style_context().add_class("back-btn"); bk.connect("clicked", lambda w: self._show_add())
        sv = Gtk.Button(label="✔ 추가"); sv.get_style_context().add_class("action-button"); sv.get_style_context().add_class("ok-btn"); sv.connect("clicked", self._do_web_add)
        bb.pack_start(bk, True, True, 0); bb.pack_start(sv, True, True, 0); bx.pack_start(bb, False, False, 4)

        self.stack.add_named(bx, "web_add"); self.show_all(); self.stack.set_visible_child_name("web_add")
        self._wn.grab_focus()

    def _do_web_add(self, *a):
        name = self._wn.get_text().strip()
        url = self._wu.get_text().strip()
        if not name or not url:
            return
        # URL에 프로토콜이 없으면 https:// 추가
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        cmd = f"xdg-open {url}"
        gi = self._wcb.get_active()
        self.groups[gi][1].append((name, cmd, "web-browser"))
        save_conf(self.groups)
        self._go_main()

    # ══════════ DELETE VIEW ══════════
    def _show_del(self, *a):
        self._rm("delete")
        bx = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        bx.set_margin_top(6); bx.set_margin_bottom(6); bx.set_margin_start(10); bx.set_margin_end(10)
        t = Gtk.Label(label="➖ 삭제"); t.get_style_context().add_class("title-label"); t.set_halign(Gtk.Align.START); bx.pack_start(t, False, False, 0)
        scr = Gtk.ScrolledWindow(); scr.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC); scr.set_vexpand(True)
        db = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self._dcb = []; self._gcb = []
        for gi, (gn, apps) in enumerate(self.groups):
            gh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6); gh.set_margin_start(4); gh.set_margin_top(6)
            gc = Gtk.CheckButton(); self._gcb.append((gi, gc)); gh.pack_start(gc, False, False, 0)
            gl = Gtk.Label(label=f"📂 {gn}", xalign=0); gl.get_style_context().add_class("group-hdr"); gh.pack_start(gl, True, True, 0)
            db.pack_start(gh, False, False, 0)
            for ai, (name, cmd, ico) in enumerate(apps):
                hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); hb.set_margin_start(24); hb.set_margin_top(2); hb.set_margin_bottom(2)
                cb = Gtk.CheckButton(); self._dcb.append((gi, ai, cb)); hb.pack_start(cb, False, False, 0)
                hb.pack_start(_ic(ico), False, False, 0); hb.pack_start(Gtk.Label(label=name, xalign=0), True, True, 0)
                db.pack_start(hb, False, False, 0)
        scr.add(db); bx.pack_start(scr, True, True, 0)
        bb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); bb.set_halign(Gtk.Align.CENTER)
        bk = Gtk.Button(label="← 뒤로"); bk.get_style_context().add_class("action-button"); bk.get_style_context().add_class("back-btn"); bk.connect("clicked", lambda w: self._go_main())
        cf = Gtk.Button(label="🗑 삭제"); cf.get_style_context().add_class("action-button"); cf.get_style_context().add_class("del-btn"); cf.connect("clicked", self._do_del)
        bb.pack_start(bk, True, True, 0); bb.pack_start(cf, True, True, 0); bx.pack_start(bb, False, False, 4)
        self.stack.add_named(bx, "delete"); self.show_all(); self.stack.set_visible_child_name("delete")

    def _do_del(self, *a):
        grm = {gi for gi, cb in self._gcb if cb.get_active()}
        arm = {}
        for gi, ai, cb in self._dcb:
            if cb.get_active() and gi not in grm: arm.setdefault(gi, set()).add(ai)
        ng = []
        for gi, (gn, apps) in enumerate(self.groups):
            if gi in grm: continue
            ng.append((gn, [a for i, a in enumerate(apps) if i not in arm.get(gi, set())]))
        self.groups = ng if ng else [("기타", [])]
        save_conf(self.groups); self._go_main()


if __name__ == "__main__":
    win = AppLauncher()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
