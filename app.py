import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import db

FONT_LARGE = ('Microsoft YaHei', 16)
FONT_BIG = ('Microsoft YaHei', 20, 'bold')
FONT_NORMAL = ('Microsoft YaHei', 14)
BG_COLOR = '#f5f7fa'
BTN_COLOR = '#409eff'
BTN_OK = '#67c23a'
BTN_WARN = '#e6a23c'
BTN_DANGER = '#f56c6c'


class ClinicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('窝沟封闭登记系统')
        self.geometry('1100x720')
        self.configure(bg=BG_COLOR)
        self.minsize(900, 600)
        db.init_db()
        self.current_frame = None
        self.show_main_menu()

    def switch_frame(self, frame_cls, **kwargs):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_cls(self, **kwargs)
        self.current_frame.pack(fill='both', expand=True)

    def show_main_menu(self):
        self.switch_frame(MainMenuFrame)


class MainMenuFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOR)
        self.pack_propagate(False)

        tk.Label(self, text='窝沟封闭登记系统', font=FONT_BIG, bg=BG_COLOR, fg='#303133').pack(pady=(60, 10))
        tk.Label(self, text='个体牙科诊所 · 极简版', font=FONT_NORMAL, bg=BG_COLOR, fg='#909399').pack(pady=(0, 60))

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(expand=True)

        style = ttk.Style()
        style.configure('Big.TButton', font=FONT_BIG, padding=40)

        btn1 = tk.Button(btn_frame, text='  新增记录  ', font=FONT_BIG, bg=BTN_OK, fg='white',
                         activebackground='#5daf34', activeforeground='white',
                         relief='flat', width=14, height=3, cursor='hand2',
                         command=lambda: master.switch_frame(AddRecordFrame))
        btn1.grid(row=0, column=0, padx=30, pady=20)

        btn2 = tk.Button(btn_frame, text='查询统计', font=FONT_BIG, bg=BTN_COLOR, fg='white',
                         activebackground='#337ecc', activeforeground='white',
                         relief='flat', width=14, height=3, cursor='hand2',
                         command=lambda: master.switch_frame(SearchFrame))
        btn2.grid(row=0, column=1, padx=30, pady=20)

        tk.Label(self, text='数据保存在本地，完全离线可用', font=FONT_NORMAL, bg=BG_COLOR, fg='#c0c4cc').pack(pady=40)


class ToothWidget(tk.Frame):
    def __init__(self, master, position, label):
        super().__init__(master, bg=BG_COLOR, highlightbackground='#dcdfe6', highlightthickness=1)
        self.position = position
        self.sealed_var = tk.IntVar(value=0)
        self.photo_var = tk.IntVar(value=0)
        self.recheck_var = tk.IntVar(value=0)

        tk.Label(self, text=f'【{position}】{label}', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').pack(pady=(10, 6))

        btn_bar = tk.Frame(self, bg=BG_COLOR)
        btn_bar.pack(pady=6)

        self.btn_sealed = tk.Button(btn_bar, text='未封闭', font=FONT_NORMAL, bg='#ffffff', fg='#606266',
                                    relief='flat', width=8, cursor='hand2', command=self._toggle_sealed)
        self.btn_sealed.pack(side='left', padx=6)

        self.btn_photo = tk.Button(btn_bar, text='未拍照', font=FONT_NORMAL, bg='#ffffff', fg='#606266',
                                   relief='flat', width=8, cursor='hand2', command=self._toggle_photo)
        self.btn_photo.pack(side='left', padx=6)

        self.btn_recheck = tk.Button(btn_bar, text='无需复查', font=FONT_NORMAL, bg='#ffffff', fg='#606266',
                                     relief='flat', width=8, cursor='hand2', command=self._toggle_recheck)
        self.btn_recheck.pack(side='left', padx=6, pady=(0, 10))

    def _toggle_sealed(self):
        if self.sealed_var.get() == 0:
            self.sealed_var.set(1)
            self.btn_sealed.config(text='已封闭', bg=BTN_OK, fg='white')
        else:
            self.sealed_var.set(0)
            self.btn_sealed.config(text='未封闭', bg='#ffffff', fg='#606266')

    def _toggle_photo(self):
        if self.photo_var.get() == 0:
            self.photo_var.set(1)
            self.btn_photo.config(text='已拍照', bg=BTN_COLOR, fg='white')
        else:
            self.photo_var.set(0)
            self.btn_photo.config(text='未拍照', bg='#ffffff', fg='#606266')

    def _toggle_recheck(self):
        if self.recheck_var.get() == 0:
            self.recheck_var.set(1)
            self.btn_recheck.config(text='需复查', bg=BTN_WARN, fg='white')
        else:
            self.recheck_var.set(0)
            self.btn_recheck.config(text='无需复查', bg='#ffffff', fg='#606266')

    def set_state(self, sealed, photo, recheck):
        self.sealed_var.set(0)
        self.photo_var.set(0)
        self.recheck_var.set(0)
        if sealed:
            self._toggle_sealed()
        if photo:
            self._toggle_photo()
        if recheck:
            self._toggle_recheck()

    def get_data(self):
        return {
            f'tooth{self.position}_sealed': self.sealed_var.get(),
            f'tooth{self.position}_photo': self.photo_var.get(),
            f'tooth{self.position}_recheck': self.recheck_var.get(),
        }


class AddRecordFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOR)
        self.tooth_widgets = {}

        top = tk.Frame(self, bg=BG_COLOR)
        top.pack(fill='x', padx=20, pady=15)
        tk.Button(top, text='← 返回', font=FONT_NORMAL, bg='#ffffff', fg='#606266',
                  relief='flat', cursor='hand2', command=master.show_main_menu).pack(side='left')
        tk.Label(top, text='新增记录', font=FONT_BIG, bg=BG_COLOR, fg='#303133').pack(side='left', padx=30)

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(fill='x', padx=40, pady=10)

        tk.Label(form, text='儿童姓名：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=0, sticky='e', padx=10, pady=10)
        self.name_entry = tk.Entry(form, font=FONT_LARGE, width=20)
        self.name_entry.grid(row=0, column=1, sticky='w', pady=10)

        tk.Label(form, text='出生年份：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=2, sticky='e', padx=10, pady=10)
        self.birth_year_entry = tk.Entry(form, font=FONT_LARGE, width=10)
        self.birth_year_entry.grid(row=0, column=3, sticky='w', pady=10)

        tk.Label(form, text='家长电话：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=1, column=0, sticky='e', padx=10, pady=10)
        self.phone_entry = tk.Entry(form, font=FONT_LARGE, width=20)
        self.phone_entry.grid(row=1, column=1, sticky='w', pady=10)

        tk.Label(form, text='治疗日期：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=1, column=2, sticky='e', padx=10, pady=10)
        self.date_entry = tk.Entry(form, font=FONT_LARGE, width=15)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.date_entry.grid(row=1, column=3, sticky='w', pady=10)

        tk.Label(form, text='操作医生：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=2, column=0, sticky='e', padx=10, pady=10)
        self.doctor_var = tk.StringVar()
        self.doctor_combo = ttk.Combobox(form, textvariable=self.doctor_var, font=FONT_LARGE, width=18, state='readonly')
        self._load_doctors()
        self.doctor_combo.grid(row=2, column=1, sticky='w', pady=10)
        tk.Button(form, text='+医生', font=FONT_NORMAL, bg=BTN_WARN, fg='white',
                  relief='flat', cursor='hand2', command=self._add_doctor).grid(row=2, column=2, sticky='w', padx=5)

        tk.Label(self, text='四颗第一恒磨牙情况（点击按钮切换）', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').pack(pady=(20, 10))

        teeth_frame = tk.Frame(self, bg=BG_COLOR)
        teeth_frame.pack(padx=40, pady=10)

        for idx, pos in enumerate(db.TOOTH_POSITIONS):
            row, col = divmod(idx, 2)
            tw = ToothWidget(teeth_frame, pos, db.TOOTH_LABELS[pos])
            tw.grid(row=row, column=col, padx=15, pady=12, sticky='nsew')
            self.tooth_widgets[pos] = tw
        teeth_frame.columnconfigure(0, weight=1)
        teeth_frame.columnconfigure(1, weight=1)

        btn_bar = tk.Frame(self, bg=BG_COLOR)
        btn_bar.pack(pady=30)

        tk.Button(btn_bar, text='清空重置', font=FONT_LARGE, bg='#ffffff', fg='#606266',
                  relief='flat', cursor='hand2', width=12, height=2, command=self._reset).pack(side='left', padx=15)
        tk.Button(btn_bar, text='保 存', font=FONT_BIG, bg=BTN_OK, fg='white',
                  activebackground='#5daf34', activeforeground='white',
                  relief='flat', cursor='hand2', width=14, height=2, command=self._save).pack(side='left', padx=15)

    def _load_doctors(self):
        doctors = db.get_doctors()
        self.doctor_list = doctors
        names = [d['name'] for d in doctors]
        self.doctor_combo['values'] = names
        if names:
            self.doctor_combo.current(0)

    def _add_doctor(self):
        name = simpledialog.askstring('添加医生', '请输入医生姓名：', parent=self)
        if name and name.strip():
            db.add_doctor(name.strip())
            self._load_doctors()
            self.doctor_var.set(name.strip())

    def _reset(self):
        self.name_entry.delete(0, 'end')
        self.birth_year_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        for tw in self.tooth_widgets.values():
            tw.set_state(0, 0, 0)

    def _save(self):
        name = self.name_entry.get().strip()
        birth_year = self.birth_year_entry.get().strip()
        phone = self.phone_entry.get().strip()
        date_str = self.date_entry.get().strip()
        doctor_name = self.doctor_var.get()

        if not name:
            messagebox.showwarning('提示', '请填写儿童姓名')
            return
        if not date_str:
            messagebox.showwarning('提示', '请填写治疗日期')
            return
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning('提示', '日期格式应为 YYYY-MM-DD，例如 2026-06-20')
            return
        birth_year_val = None
        if birth_year:
            try:
                birth_year_val = int(birth_year)
            except ValueError:
                messagebox.showwarning('提示', '出生年份应为数字')
                return
        doctor_id = None
        for d in self.doctor_list:
            if d['name'] == doctor_name:
                doctor_id = d['id']
                break

        dup_list = db.find_duplicate(name, phone, date_str)
        if dup_list:
            msg = f'发现半年内同名同电话记录 {len(dup_list)} 条，是否仍要保存？\n\n'
            for r in dup_list:
                msg += f"· {r['treatment_date']} {r.get('doctor_name', '')}\n"
            if not messagebox.askyesno('重复提醒', msg):
                return

        data = {
            'child_name': name,
            'birth_year': birth_year_val,
            'parent_phone': phone,
            'treatment_date': date_str,
            'doctor_id': doctor_id,
        }
        for tw in self.tooth_widgets.values():
            data.update(tw.get_data())
        db.insert_record(data)
        messagebox.showinfo('成功', '记录已保存！')
        self._reset()


class SearchFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOR)
        self.current_results = []

        top = tk.Frame(self, bg=BG_COLOR)
        top.pack(fill='x', padx=20, pady=15)
        tk.Button(top, text='← 返回', font=FONT_NORMAL, bg='#ffffff', fg='#606266',
                  relief='flat', cursor='hand2', command=master.show_main_menu).pack(side='left')
        tk.Label(top, text='查询统计', font=FONT_BIG, bg=BG_COLOR, fg='#303133').pack(side='left', padx=30)

        filter_frame = tk.Frame(self, bg=BG_COLOR)
        filter_frame.pack(fill='x', padx=30, pady=10)

        cur_year = datetime.now().year
        cur_month = datetime.now().month

        tk.Label(filter_frame, text='年：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=0, sticky='e', padx=5)
        self.year_var = tk.StringVar(value=str(cur_year))
        year_vals = [str(y) for y in range(cur_year - 5, cur_year + 2)]
        self.year_combo = ttk.Combobox(filter_frame, textvariable=self.year_var, values=['全部'] + year_vals,
                                       font=FONT_LARGE, width=8, state='readonly')
        self.year_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        tk.Label(filter_frame, text='月：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=2, sticky='e', padx=5)
        self.month_var = tk.StringVar(value=str(cur_month))
        self.month_combo = ttk.Combobox(filter_frame, textvariable=self.month_var,
                                        values=['全部'] + [str(m) for m in range(1, 13)],
                                        font=FONT_LARGE, width=6, state='readonly')
        self.month_combo.grid(row=0, column=3, sticky='w', padx=5, pady=5)

        tk.Label(filter_frame, text='医生：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=4, sticky='e', padx=5)
        self.doctor_var = tk.StringVar(value='全部')
        self.doctor_combo = ttk.Combobox(filter_frame, textvariable=self.doctor_var, font=FONT_LARGE, width=10, state='readonly')
        self._load_doctors()
        self.doctor_combo.grid(row=0, column=5, sticky='w', padx=5, pady=5)

        tk.Label(filter_frame, text='姓名：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=6, sticky='e', padx=5)
        self.name_entry = tk.Entry(filter_frame, font=FONT_LARGE, width=14)
        self.name_entry.grid(row=0, column=7, sticky='w', padx=5, pady=5)

        tk.Button(filter_frame, text='查询', font=FONT_LARGE, bg=BTN_COLOR, fg='white',
                  activebackground='#337ecc', activeforeground='white',
                  relief='flat', cursor='hand2', width=8, command=self._do_search).grid(row=0, column=8, padx=10)

        self.stat_label = tk.Label(self, text='', font=FONT_NORMAL, bg=BG_COLOR, fg='#606266')
        self.stat_label.pack(anchor='w', padx=40, pady=(5, 5))

        columns = ('date', 'name', 'birth', 'phone', 'doctor', 'teeth', 'recheck')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=18)
        self.tree.heading('date', text='治疗日期')
        self.tree.heading('name', text='儿童姓名')
        self.tree.heading('birth', text='出生年')
        self.tree.heading('phone', text='家长电话')
        self.tree.heading('doctor', text='医生')
        self.tree.heading('teeth', text='封闭/拍照/复查')
        self.tree.heading('recheck', text='备注')
        self.tree.column('date', width=120, anchor='center')
        self.tree.column('name', width=110, anchor='center')
        self.tree.column('birth', width=80, anchor='center')
        self.tree.column('phone', width=140, anchor='center')
        self.tree.column('doctor', width=90, anchor='center')
        self.tree.column('teeth', width=280, anchor='w')
        self.tree.column('recheck', width=220, anchor='w')

        style = ttk.Style()
        style.configure('Treeview', font=FONT_NORMAL, rowheight=32)
        style.configure('Treeview.Heading', font=FONT_LARGE)

        tree_frame = tk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=30, pady=10)
        self.tree.pack(side='left', fill='both', expand=True)
        sb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        sb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind('<Double-1>', self._open_detail)

        btn_bar = tk.Frame(self, bg=BG_COLOR)
        btn_bar.pack(pady=15)
        tk.Button(btn_bar, text='双击行查看/编辑详情', font=FONT_NORMAL, bg=BG_COLOR, fg='#909399',
                  relief='flat').pack()

        self._do_search()

    def _load_doctors(self):
        doctors = db.get_doctors()
        self.doctor_list = doctors
        self.doctor_combo['values'] = ['全部'] + [d['name'] for d in doctors]

    def _teeth_summary(self, row):
        parts = []
        for pos in db.TOOTH_POSITIONS:
            s = '封' if row.get(f'tooth{pos}_sealed') else '·'
            p = '照' if row.get(f'tooth{pos}_photo') else '·'
            r = '复' if row.get(f'tooth{pos}_recheck') else '·'
            parts.append(f'{pos}:{s}{p}{r}')
        return '  '.join(parts)

    def _do_search(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        y = self.year_var.get()
        m = self.month_var.get()
        year = None if y == '全部' else int(y)
        month = None if m == '全部' else int(m)
        doc_name = self.doctor_var.get()
        doctor_id = None
        if doc_name != '全部':
            for d in self.doctor_list:
                if d['name'] == doc_name:
                    doctor_id = d['id']
                    break
        name = self.name_entry.get().strip() or None
        rows = db.search_records(year=year, month=month, doctor_id=doctor_id, child_name=name)
        self.current_results = rows
        for r in rows:
            remark_parts = []
            if r.get('parent_feedback'):
                remark_parts.append('反馈:' + r['parent_feedback'][:10])
            if r.get('recheck_result'):
                remark_parts.append('复查:' + r['recheck_result'][:10])
            if r.get('remark'):
                remark_parts.append(r['remark'][:12])
            remark = ' | '.join(remark_parts)
            self.tree.insert('', 'end', iid=str(r['id']), values=(
                r['treatment_date'],
                r['child_name'],
                r.get('birth_year') or '',
                r.get('parent_phone') or '',
                r.get('doctor_name') or '',
                self._teeth_summary(r),
                remark,
            ))
        total = len(rows)
        sealed_count = sum(1 for r in rows if any(r.get(f'tooth{p}_sealed') for p in db.TOOTH_POSITIONS))
        self.stat_label.config(text=f'共 {total} 条记录，其中已做封闭 {sealed_count} 人')

    def _open_detail(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        rid = int(sel[0])
        DetailDialog(self, rid, on_saved=self._do_search)


class DetailDialog(tk.Toplevel):
    def __init__(self, master, record_id, on_saved=None):
        super().__init__(master)
        self.record_id = record_id
        self.on_saved = on_saved
        self.tooth_widgets = {}
        self.title('记录详情')
        self.geometry('820x720')
        self.configure(bg=BG_COLOR)
        self.transient(master)
        self.grab_set()
        self._load()
        self._build_ui()

    def _load(self):
        self.record = db.get_record(self.record_id)

    def _build_ui(self):
        r = self.record
        tk.Label(self, text=f'记录详情  ID:{r["id"]}', font=FONT_BIG, bg=BG_COLOR, fg='#303133').pack(pady=15)

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(fill='x', padx=30)

        tk.Label(form, text='儿童姓名：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=0, sticky='e', padx=8, pady=6)
        self.name_var = tk.StringVar(value=r['child_name'])
        tk.Entry(form, textvariable=self.name_var, font=FONT_LARGE, width=18).grid(row=0, column=1, sticky='w', pady=6)

        tk.Label(form, text='出生年份：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=2, sticky='e', padx=8, pady=6)
        self.birth_var = tk.StringVar(value=str(r.get('birth_year') or ''))
        tk.Entry(form, textvariable=self.birth_var, font=FONT_LARGE, width=10).grid(row=0, column=3, sticky='w', pady=6)

        tk.Label(form, text='家长电话：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=1, column=0, sticky='e', padx=8, pady=6)
        self.phone_var = tk.StringVar(value=r.get('parent_phone') or '')
        tk.Entry(form, textvariable=self.phone_var, font=FONT_LARGE, width=18).grid(row=1, column=1, sticky='w', pady=6)

        tk.Label(form, text='治疗日期：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=1, column=2, sticky='e', padx=8, pady=6)
        self.date_var = tk.StringVar(value=r['treatment_date'])
        tk.Entry(form, textvariable=self.date_var, font=FONT_LARGE, width=14).grid(row=1, column=3, sticky='w', pady=6)

        tk.Label(form, text='操作医生：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=2, column=0, sticky='e', padx=8, pady=6)
        self.doctor_var = tk.StringVar(value=r.get('doctor_name') or '')
        doctors = db.get_doctors()
        self.doctor_list = doctors
        cb = ttk.Combobox(form, textvariable=self.doctor_var, values=[d['name'] for d in doctors],
                          font=FONT_LARGE, width=16, state='readonly')
        cb.grid(row=2, column=1, sticky='w', pady=6)

        teeth_frame = tk.Frame(self, bg=BG_COLOR)
        teeth_frame.pack(padx=30, pady=15)

        for idx, pos in enumerate(db.TOOTH_POSITIONS):
            row, col = divmod(idx, 2)
            tw = ToothWidget(teeth_frame, pos, db.TOOTH_LABELS[pos])
            tw.grid(row=row, column=col, padx=10, pady=8, sticky='nsew')
            tw.set_state(r.get(f'tooth{pos}_sealed', 0), r.get(f'tooth{pos}_photo', 0), r.get(f'tooth{pos}_recheck', 0))
            self.tooth_widgets[pos] = tw

        extra = tk.LabelFrame(self, text='补充信息（家长反馈、复查结果、备注）', font=FONT_LARGE, bg=BG_COLOR, fg='#303133', padx=10, pady=10)
        extra.pack(fill='x', padx=30, pady=10)

        tk.Label(extra, text='家长反馈：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=0, sticky='ne', padx=5, pady=5)
        self.feedback_text = tk.Text(extra, font=FONT_NORMAL, height=2, width=45)
        self.feedback_text.insert('1.0', r.get('parent_feedback') or '')
        self.feedback_text.grid(row=0, column=1, sticky='w', pady=5)

        tk.Label(extra, text='复查结果：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=1, column=0, sticky='ne', padx=5, pady=5)
        self.recheck_text = tk.Text(extra, font=FONT_NORMAL, height=2, width=45)
        self.recheck_text.insert('1.0', r.get('recheck_result') or '')
        self.recheck_text.grid(row=1, column=1, sticky='w', pady=5)

        tk.Label(extra, text='备    注：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=2, column=0, sticky='ne', padx=5, pady=5)
        self.remark_text = tk.Text(extra, font=FONT_NORMAL, height=3, width=45)
        self.remark_text.insert('1.0', r.get('remark') or '')
        self.remark_text.grid(row=2, column=1, sticky='w', pady=5)

        btn_bar = tk.Frame(self, bg=BG_COLOR)
        btn_bar.pack(pady=20)
        tk.Button(btn_bar, text='取消', font=FONT_LARGE, bg='#ffffff', fg='#606266',
                  relief='flat', cursor='hand2', width=10, height=2, command=self.destroy).pack(side='left', padx=15)
        tk.Button(btn_bar, text='保 存', font=FONT_LARGE, bg=BTN_OK, fg='white',
                  activebackground='#5daf34', activeforeground='white',
                  relief='flat', cursor='hand2', width=10, height=2, command=self._save).pack(side='left', padx=15)

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning('提示', '请填写儿童姓名', parent=self)
            return
        date_str = self.date_var.get().strip()
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning('提示', '日期格式应为 YYYY-MM-DD', parent=self)
            return
        birth_year = None
        if self.birth_var.get().strip():
            try:
                birth_year = int(self.birth_var.get().strip())
            except ValueError:
                messagebox.showwarning('提示', '出生年份应为数字', parent=self)
                return
        doctor_id = None
        for d in self.doctor_list:
            if d['name'] == self.doctor_var.get():
                doctor_id = d['id']
                break
        data = {
            'child_name': name,
            'birth_year': birth_year,
            'parent_phone': self.phone_var.get().strip(),
            'treatment_date': date_str,
            'doctor_id': doctor_id,
            'parent_feedback': self.feedback_text.get('1.0', 'end').strip(),
            'recheck_result': self.recheck_text.get('1.0', 'end').strip(),
            'remark': self.remark_text.get('1.0', 'end').strip(),
        }
        for tw in self.tooth_widgets.values():
            data.update(tw.get_data())
        db.update_record(self.record_id, data)
        messagebox.showinfo('成功', '已保存修改', parent=self)
        if self.on_saved:
            self.on_saved()
        self.destroy()


if __name__ == '__main__':
    app = ClinicApp()
    app.mainloop()
