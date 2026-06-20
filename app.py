import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, timedelta
import csv
import shutil
import os
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

    def do_backup(self):
        if not os.path.exists(db.DB_PATH):
            messagebox.showinfo('提示', '当前还没有数据库文件，无需备份')
            return
        default_name = f'窝沟封闭数据备份_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        path = filedialog.asksaveasfilename(
            parent=self,
            title='备份数据库',
            defaultextension='.db',
            initialfile=default_name,
            filetypes=[('数据库备份', '*.db'), ('所有文件', '*.*')],
        )
        if not path:
            return
        try:
            shutil.copy2(db.DB_PATH, path)
            messagebox.showinfo('成功', f'已备份到：\n{path}\n\n建议复制到 U 盘或其他电脑保存。')
        except Exception as e:
            messagebox.showerror('错误', f'备份失败：{str(e)}')

    def do_restore(self):
        path = filedialog.askopenfilename(
            parent=self,
            title='从备份恢复',
            filetypes=[('数据库备份', '*.db'), ('所有文件', '*.*')],
        )
        if not path:
            return
        if not os.path.exists(path):
            messagebox.showerror('错误', '选择的文件不存在')
            return
        msg = ('⚠️ 恢复会覆盖当前所有数据！\n\n'
               '建议先备份当前数据再恢复。\n\n'
               '确认要从所选备份文件恢复吗？')
        if not messagebox.askyesno('确认恢复', msg, icon='warning', default='no', parent=self):
            return
        try:
            if os.path.exists(db.DB_PATH):
                backup_old = db.DB_PATH + '.bak_' + datetime.now().strftime('%Y%m%d_%H%M%S')
                shutil.copy2(db.DB_PATH, backup_old)
            shutil.copy2(path, db.DB_PATH)
            messagebox.showinfo('成功', '数据已恢复！\n\n（当前数据已自动另存为 .bak_ 后缀的备份文件）')
            if self.current_frame is not None:
                self.show_main_menu()
        except Exception as e:
            messagebox.showerror('错误', f'恢复失败：{str(e)}')


class MainMenuFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOR)
        self.pack_propagate(False)

        tk.Label(self, text='窝沟封闭登记系统', font=FONT_BIG, bg=BG_COLOR, fg='#303133').pack(pady=(40, 8))
        tk.Label(self, text='个体牙科诊所 · 极简版', font=FONT_NORMAL, bg=BG_COLOR, fg='#909399').pack(pady=(0, 30))

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(expand=True)

        style = ttk.Style()
        style.configure('Big.TButton', font=FONT_BIG, padding=40)

        btn1 = tk.Button(btn_frame, text='  新增记录  ', font=FONT_BIG, bg=BTN_OK, fg='white',
                         activebackground='#5daf34', activeforeground='white',
                         relief='flat', width=14, height=3, cursor='hand2',
                         command=lambda: master.switch_frame(AddRecordFrame))
        btn1.grid(row=0, column=0, padx=30, pady=15)

        btn2 = tk.Button(btn_frame, text='查询统计', font=FONT_BIG, bg=BTN_COLOR, fg='white',
                         activebackground='#337ecc', activeforeground='white',
                         relief='flat', width=14, height=3, cursor='hand2',
                         command=lambda: master.switch_frame(SearchFrame))
        btn2.grid(row=0, column=1, padx=30, pady=15)

        small_frame = tk.Frame(self, bg=BG_COLOR)
        small_frame.pack(pady=10)
        tk.Button(small_frame, text='💾 备份数据', font=FONT_LARGE, bg='#ffffff', fg='#606266',
                  relief='flat', cursor='hand2', width=12, command=master.do_backup).pack(side='left', padx=10)
        tk.Button(small_frame, text='↩️ 恢复备份', font=FONT_LARGE, bg='#ffffff', fg='#606266',
                  relief='flat', cursor='hand2', width=12, command=master.do_restore).pack(side='left', padx=10)

        tk.Label(self, text='数据保存在本地，完全离线可用', font=FONT_NORMAL, bg=BG_COLOR, fg='#c0c4cc').pack(pady=20)


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
        if not phone:
            messagebox.showwarning('提示', '请填写家长电话，便于后续查询和通知复查')
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
            msg = f'⚠️ 注意：半年内【{name}】同电话 {phone} 已有 {len(dup_list)} 条记录！\n\n'
            for i, r in enumerate(dup_list, 1):
                teeth_info = []
                for p in db.TOOTH_POSITIONS:
                    if r.get(f'tooth{p}_sealed'):
                        teeth_info.append(f'{p}已封')
                teeth_str = '、'.join(teeth_info) if teeth_info else '未封闭'
                days = (datetime.strptime(date_str, '%Y-%m-%d') -
                        datetime.strptime(r['treatment_date'], '%Y-%m-%d')).days
                msg += f"{i}. {r['treatment_date']}（距今 {days} 天）{r.get('doctor_name', '')}\n"
                msg += f"   牙位：{teeth_str}\n"
                if r.get('recheck_result'):
                    msg += f"   上次复查：{r['recheck_result'][:20]}\n"
            msg += '\n确认仍要保存这条新记录吗？'
            if not messagebox.askyesno('重复提醒', msg, icon='warning', default='no'):
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
        self.recheck_results = []
        self.view_mode = 'list'

        top = tk.Frame(self, bg=BG_COLOR)
        top.pack(fill='x', padx=20, pady=15)
        tk.Button(top, text='← 返回', font=FONT_NORMAL, bg='#ffffff', fg='#606266',
                  relief='flat', cursor='hand2', command=master.show_main_menu).pack(side='left')
        tk.Label(top, text='查询统计', font=FONT_BIG, bg=BG_COLOR, fg='#303133').pack(side='left', padx=30)

        view_bar = tk.Frame(self, bg=BG_COLOR)
        view_bar.pack(fill='x', padx=40, pady=(0, 5))
        self.btn_list_view = tk.Button(view_bar, text='明细列表', font=FONT_LARGE, bg=BTN_COLOR, fg='white',
                                       relief='flat', cursor='hand2', width=11, command=self._switch_list_view)
        self.btn_list_view.pack(side='left', padx=4)
        self.btn_summary_view = tk.Button(view_bar, text='月度汇总', font=FONT_LARGE, bg='#ffffff', fg='#606266',
                                          relief='flat', cursor='hand2', width=11, command=self._switch_summary_view)
        self.btn_summary_view.pack(side='left', padx=4)
        self.btn_recheck_view = tk.Button(view_bar, text='复查跟进', font=FONT_LARGE, bg='#ffffff', fg='#606266',
                                          relief='flat', cursor='hand2', width=11, command=self._switch_recheck_view)
        self.btn_recheck_view.pack(side='left', padx=4)

        self.export_menu = tk.Menu(self, tearoff=0)
        self.export_menu.add_command(label='明细 CSV（当前筛选结果）', command=self._export_csv)
        self.export_menu.add_command(label='老板版月度汇总（含明细）', command=self._export_boss_summary)
        self.btn_export = tk.Button(view_bar, text='▼ 导出', font=FONT_LARGE, bg=BTN_WARN, fg='white',
                                    relief='flat', cursor='hand2', width=8)
        self.btn_export.pack(side='right', padx=5)
        self.btn_export.bind('<Button-1>', self._show_export_menu)

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

        self.list_container = tk.Frame(self, bg=BG_COLOR)
        self.summary_container = tk.Frame(self, bg=BG_COLOR)
        self.recheck_container = tk.Frame(self, bg=BG_COLOR)

        # ===== 明细列表 =====
        columns = ('date', 'name', 'birth', 'phone', 'doctor', 'teeth', 'recheck')
        self.tree = ttk.Treeview(self.list_container, columns=columns, show='headings', height=18)
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
        self.tree.tag_configure('recheck', background='#fff1f0', foreground='#cf1322')

        tree_frame = tk.Frame(self.list_container)
        tree_frame.pack(fill='both', expand=True, padx=30, pady=10)
        self.tree.pack(side='left', fill='both', expand=True)
        sb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        sb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind('<Double-1>', self._open_detail)

        tip_bar = tk.Frame(self.list_container, bg=BG_COLOR)
        tip_bar.pack(pady=10)
        tk.Label(tip_bar, text='双击行查看/编辑详情 · 红色行表示有牙位需复查', font=FONT_NORMAL, bg=BG_COLOR, fg='#909399',
                 relief='flat').pack()

        # ===== 月度汇总 =====
        sum_columns = ('doctor', 'children', 'sealed_teeth', 'recheck_count', 'avg_teeth')
        self.summary_tree = ttk.Treeview(self.summary_container, columns=sum_columns, show='headings', height=20)
        self.summary_tree.heading('doctor', text='医生')
        self.summary_tree.heading('children', text='服务儿童数')
        self.summary_tree.heading('sealed_teeth', text='封闭牙数')
        self.summary_tree.heading('recheck_count', text='需复查记录数')
        self.summary_tree.heading('avg_teeth', text='人均封闭牙数')
        self.summary_tree.column('doctor', width=180, anchor='center')
        self.summary_tree.column('children', width=160, anchor='center')
        self.summary_tree.column('sealed_teeth', width=160, anchor='center')
        self.summary_tree.column('recheck_count', width=160, anchor='center')
        self.summary_tree.column('avg_teeth', width=180, anchor='center')
        sum_style = ttk.Style()
        sum_style.configure('Sum.Treeview', font=FONT_LARGE, rowheight=48)
        sum_style.configure('Sum.Treeview.Heading', font=FONT_LARGE)
        self.summary_tree.configure(style='Sum.Treeview')
        self.summary_tree.tag_configure('total', background='#ecf5ff', font=('Microsoft YaHei', 16, 'bold'))

        sum_frame = tk.Frame(self.summary_container)
        sum_frame.pack(fill='both', expand=True, padx=30, pady=10)
        self.summary_tree.pack(side='left', fill='both', expand=True)
        sbs = ttk.Scrollbar(sum_frame, orient='vertical', command=self.summary_tree.yview)
        sbs.pack(side='right', fill='y')
        self.summary_tree.configure(yscrollcommand=sbs.set)
        self.summary_tree.bind('<Double-1>', self._open_doctor_detail)

        sum_tip = tk.Frame(self.summary_container, bg=BG_COLOR)
        sum_tip.pack(pady=10)
        tk.Label(sum_tip, text='选定月份后自动统计 · 双击医生行查看该医生当月明细 · 复查按记录数统计（一条记录只要有牙位需复查就算1条）',
                 font=FONT_NORMAL, bg=BG_COLOR, fg='#909399', relief='flat').pack()

        # ===== 复查跟进 =====
        rc_filter = tk.Frame(self.recheck_container, bg=BG_COLOR)
        rc_filter.pack(fill='x', padx=30, pady=(10, 5))
        tk.Label(rc_filter, text='闭环状态：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').pack(side='left', padx=5)
        self.rc_conclusion_var = tk.StringVar(value='未完成')
        rc_conc_combo = ttk.Combobox(rc_filter, textvariable=self.rc_conclusion_var,
                                     values=['未完成', '已完成', '全部'],
                                     font=FONT_LARGE, width=10, state='readonly')
        rc_conc_combo.pack(side='left', padx=5)
        tk.Label(rc_filter, text='联系状态：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').pack(side='left', padx=(15,5))
        self.rc_status_var = tk.StringVar(value='全部')
        rc_combo = ttk.Combobox(rc_filter, textvariable=self.rc_status_var,
                                values=['全部', '未联系', '已联系'],
                                font=FONT_LARGE, width=10, state='readonly')
        rc_combo.pack(side='left', padx=5)
        tk.Label(rc_filter, text='预约：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').pack(side='left', padx=(15,5))
        self.rc_appt_var = tk.StringVar(value='全部')
        rc_appt_combo = ttk.Combobox(rc_filter, textvariable=self.rc_appt_var,
                                     values=['全部', '未预约', '今天', '本周内', '逾期未到', '已预约'],
                                     font=FONT_LARGE, width=10, state='readonly')
        rc_appt_combo.pack(side='left', padx=5)
        tk.Button(rc_filter, text='刷新', font=FONT_LARGE, bg=BTN_COLOR, fg='white',
                  relief='flat', cursor='hand2', width=8, command=self._load_recheck).pack(side='left', padx=10)
        tk.Button(rc_filter, text='设置预约日期', font=FONT_LARGE, bg=BTN_WARN, fg='white',
                  relief='flat', cursor='hand2', width=14, command=self._set_appointment).pack(side='right', padx=5)
        tk.Button(rc_filter, text='按同电话批量已联系', font=FONT_LARGE, bg='#13c2c2', fg='white',
                  relief='flat', cursor='hand2', width=18, command=self._mark_phone_contacted).pack(side='right', padx=5)
        tk.Button(rc_filter, text='标记已联系', font=FONT_LARGE, bg=BTN_OK, fg='white',
                  relief='flat', cursor='hand2', width=12, command=self._mark_contacted).pack(side='right', padx=5)
        tk.Button(rc_filter, text='标记未联系', font=FONT_LARGE, bg='#ffffff', fg='#606266',
                  relief='flat', cursor='hand2', width=12, command=self._mark_uncontacted).pack(side='right', padx=5)

        rc_columns = ('date', 'name', 'phone', 'doctor', 'teeth', 'appointment', 'contact', 'person', 'note', 'conclusion')
        self.recheck_tree = ttk.Treeview(self.recheck_container, columns=rc_columns, show='headings', height=14, selectmode='extended')
        self.recheck_tree.heading('date', text='治疗日期')
        self.recheck_tree.heading('name', text='儿童姓名')
        self.recheck_tree.heading('phone', text='家长电话')
        self.recheck_tree.heading('doctor', text='医生')
        self.recheck_tree.heading('teeth', text='需复查牙位')
        self.recheck_tree.heading('appointment', text='预约日期')
        self.recheck_tree.heading('contact', text='联系状态')
        self.recheck_tree.heading('person', text='联系人')
        self.recheck_tree.heading('note', text='联系备注/时间')
        self.recheck_tree.heading('conclusion', text='复查结论')
        self.recheck_tree.column('date', width=100, anchor='center')
        self.recheck_tree.column('name', width=90, anchor='center')
        self.recheck_tree.column('phone', width=110, anchor='center')
        self.recheck_tree.column('doctor', width=70, anchor='center')
        self.recheck_tree.column('teeth', width=130, anchor='w')
        self.recheck_tree.column('appointment', width=100, anchor='center')
        self.recheck_tree.column('contact', width=80, anchor='center')
        self.recheck_tree.column('person', width=80, anchor='center')
        self.recheck_tree.column('note', width=210, anchor='w')
        self.recheck_tree.column('conclusion', width=160, anchor='w')
        rc_style = ttk.Style()
        rc_style.configure('Rc.Treeview', font=FONT_NORMAL, rowheight=32)
        rc_style.configure('Rc.Treeview.Heading', font=FONT_LARGE)
        self.recheck_tree.configure(style='Rc.Treeview')
        self.recheck_tree.tag_configure('closed_done', background='#f6ffed', foreground='#389e0d')
        self.recheck_tree.tag_configure('closed_contacted', background='#e6f7ff', foreground='#096dd9')
        self.recheck_tree.tag_configure('appointed', background='#fff7e6', foreground='#d46b08')
        self.recheck_tree.tag_configure('overdue', background='#fff1f0', foreground='#cf1322')
        self.recheck_tree.tag_configure('todo', background='#fafafa', foreground='#606266')

        rc_frame = tk.Frame(self.recheck_container)
        rc_frame.pack(fill='both', expand=True, padx=30, pady=10)
        self.recheck_tree.pack(side='left', fill='both', expand=True)
        rsb = ttk.Scrollbar(rc_frame, orient='vertical', command=self.recheck_tree.yview)
        rsb.pack(side='right', fill='y')
        self.recheck_tree.configure(yscrollcommand=rsb.set)
        self.recheck_tree.bind('<Double-1>', self._open_recheck_detail)

        rc_tip = tk.Frame(self.recheck_container, bg=BG_COLOR)
        rc_tip.pack(pady=10)
        tk.Label(rc_tip, text='红色=未联系 · 绿色=已联系 · 双击行查看详情或补写复查结论',
                 font=FONT_NORMAL, bg=BG_COLOR, fg='#909399', relief='flat').pack()

        self._do_search()
        self._switch_list_view()

    def _show_export_menu(self, event):
        self.export_menu.tk_popup(event.x_root, event.y_root)

    def _switch_list_view(self):
        self.view_mode = 'list'
        self.summary_container.pack_forget()
        self.recheck_container.pack_forget()
        self.list_container.pack(fill='both', expand=True)
        self.btn_list_view.config(bg=BTN_COLOR, fg='white')
        self.btn_summary_view.config(bg='#ffffff', fg='#606266')
        self.btn_recheck_view.config(bg='#ffffff', fg='#606266')

    def _switch_summary_view(self):
        self.view_mode = 'summary'
        self.list_container.pack_forget()
        self.recheck_container.pack_forget()
        self.summary_container.pack(fill='both', expand=True)
        self.btn_list_view.config(bg='#ffffff', fg='#606266')
        self.btn_summary_view.config(bg=BTN_COLOR, fg='white')
        self.btn_recheck_view.config(bg='#ffffff', fg='#606266')
        self._load_summary()

    def _switch_recheck_view(self):
        self.view_mode = 'recheck'
        self.list_container.pack_forget()
        self.summary_container.pack_forget()
        self.recheck_container.pack(fill='both', expand=True)
        self.btn_list_view.config(bg='#ffffff', fg='#606266')
        self.btn_summary_view.config(bg='#ffffff', fg='#606266')
        self.btn_recheck_view.config(bg=BTN_COLOR, fg='white')
        self._load_recheck()

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

    def _need_recheck(self, row):
        return any(row.get(f'tooth{p}_recheck') for p in db.TOOTH_POSITIONS)

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
            tags = ()
            if self._need_recheck(r) and not r.get('recheck_result'):
                tags = ('recheck',)
            self.tree.insert('', 'end', iid=str(r['id']), values=(
                r['treatment_date'],
                r['child_name'],
                r.get('birth_year') or '',
                r.get('parent_phone') or '',
                r.get('doctor_name') or '',
                self._teeth_summary(r),
                remark,
            ), tags=tags)
        total = len(rows)
        sealed_count = sum(1 for r in rows if any(r.get(f'tooth{p}_sealed') for p in db.TOOTH_POSITIONS))
        recheck_count = sum(1 for r in rows if self._need_recheck(r))
        self.stat_label.config(text=f'共 {total} 条记录，已做封闭 {sealed_count} 人，需复查 {recheck_count} 条')
        if self.view_mode == 'summary':
            self._load_summary()
        elif self.view_mode == 'recheck':
            self._load_recheck()

    def _load_summary(self):
        for i in self.summary_tree.get_children():
            self.summary_tree.delete(i)
        y = self.year_var.get()
        m = self.month_var.get()
        if y == '全部' or m == '全部':
            self.summary_tree.insert('', 'end', values=('请先选择具体的年份和月份', '', '', '', ''))
            return
        year = int(y)
        month = int(m)
        summary = db.get_monthly_summary(year, month)
        total_children = 0
        total_sealed = 0
        total_recheck = 0
        for s in summary:
            avg = round(s['sealed_teeth'] / s['children_count'], 1) if s['children_count'] > 0 else 0
            self.summary_tree.insert('', 'end', values=(
                s['doctor_name'],
                s['children_count'],
                s['sealed_teeth'],
                s['recheck_count'],
                avg,
            ), tags=(f"doc_{s.get('doctor_id', 0)}",))
            total_children += s['children_count']
            total_sealed += s['sealed_teeth']
            total_recheck += s['recheck_count']
        if total_children > 0:
            avg_total = round(total_sealed / total_children, 1)
            self.summary_tree.insert('', 'end', values=(
                '合计',
                total_children,
                total_sealed,
                total_recheck,
                avg_total,
            ), tags=('total',))

    def _open_doctor_detail(self, event):
        sel = self.summary_tree.selection()
        if not sel:
            return
        item = sel[0]
        tags = self.summary_tree.item(item, 'tags')
        if not tags or not tags[0].startswith('doc_'):
            return
        doctor_id = int(tags[0].replace('doc_', ''))
        y = self.year_var.get()
        m = self.month_var.get()
        if y == '全部' or m == '全部':
            return
        self.doctor_var.set('全部')
        for d in self.doctor_list:
            if d['id'] == doctor_id:
                self.doctor_var.set(d['name'])
                break
        self._switch_list_view()
        self._do_search()

    def _open_detail(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        rid = int(sel[0])
        DetailDialog(self, rid, on_saved=self._do_search)

    # ===== 复查跟进 =====
    def _load_recheck(self):
        for i in self.recheck_tree.get_children():
            self.recheck_tree.delete(i)
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
        status = self.rc_status_var.get()
        contact_status = None
        if status == '已联系':
            contact_status = 1
        elif status == '未联系':
            contact_status = 0
        conclusion = self.rc_conclusion_var.get()
        conclusion_status = None
        if conclusion == '未完成':
            conclusion_status = 0
        elif conclusion == '已完成':
            conclusion_status = 1
        appt = self.rc_appt_var.get()
        appt_map = {'未预约': 'none', '今天': 'today', '本周内': 'week', '逾期未到': 'overdue', '已预约': 'appointed'}
        appointment_filter = appt_map.get(appt)
        rows = db.get_recheck_list(year=year, month=month, doctor_id=doctor_id,
                                   contact_status=contact_status, child_name=name,
                                   conclusion_status=conclusion_status, appointment_filter=appointment_filter)
        self.recheck_results = rows
        today_str = datetime.now().strftime('%Y-%m-%d')
        for r in rows:
            teeth_parts = []
            for pos in db.TOOTH_POSITIONS:
                if r.get(f'tooth{pos}_recheck'):
                    teeth_parts.append(pos)
            teeth_str = '、'.join(teeth_parts)
            has_conclusion = bool(r.get('recheck_result') and str(r['recheck_result']).strip())
            is_contacted = r.get('contact_status') == 1
            appt_date = r.get('appointment_date') or ''
            overdue = False
            if appt_date and not has_conclusion and appt_date < today_str:
                overdue = True
            if has_conclusion:
                tag = 'closed_done'
                contact_text = '已完成'
            elif overdue:
                tag = 'overdue'
                contact_text = '逾期未到' if is_contacted else '逾期'
            elif appt_date:
                tag = 'appointed'
                contact_text = '已预约'
            elif is_contacted:
                tag = 'closed_contacted'
                contact_text = '已联系'
            else:
                tag = 'todo'
                contact_text = '未联系'
            note_parts = []
            if r.get('contacted_at'):
                note_parts.append(r['contacted_at'][5:16])
            if r.get('contact_note'):
                note_parts.append(str(r['contact_note'])[:12])
            note = ' | '.join(note_parts)
            conclusion_str = (str(r.get('recheck_result') or '')).strip()[:16]
            person = (str(r.get('contact_person') or '')).strip()[:8]
            appt_show = appt_date[:5] if appt_date else ''
            self.recheck_tree.insert('', 'end', iid=str(r['id']), values=(
                r['treatment_date'],
                r['child_name'],
                r.get('parent_phone') or '',
                r.get('doctor_name') or '',
                teeth_str,
                appt_show,
                contact_text,
                person,
                note,
                conclusion_str,
            ), tags=(tag,))
        total = len(rows)
        closed_done = sum(1 for r in rows if r.get('recheck_result') and str(r['recheck_result']).strip())
        today = datetime.now().strftime('%Y-%m-%d')
        overdue_cnt = sum(1 for r in rows if r.get('appointment_date') and not (r.get('recheck_result') and str(r['recheck_result']).strip()) and r['appointment_date'] < today)
        appointed_cnt = sum(1 for r in rows if r.get('appointment_date') and not (r.get('recheck_result') and str(r['recheck_result']).strip()) and r['appointment_date'] >= today)
        todo = total - closed_done - appointed_cnt - overdue_cnt
        self.stat_label.config(text=f'复查跟进共 {total} 条：已完成 {closed_done} 条｜已预约 {appointed_cnt} 条｜逾期 {overdue_cnt} 条｜未处理 {todo} 条')

    def _get_selected_ids_and_phones(self):
        sel = self.recheck_tree.selection()
        ids = []
        phones = set()
        for iid in sel:
            rid = int(iid)
            ids.append(rid)
            for r in self.recheck_results:
                if r['id'] == rid and r.get('parent_phone'):
                    phones.add(r['parent_phone'])
                    break
        return ids, phones

    def _open_recheck_detail(self, event):
        sel = self.recheck_tree.selection()
        if not sel:
            return
        rid = int(sel[0])
        DetailDialog(self, rid, on_saved=self._do_search)

    def _mark_contacted(self):
        sel = self.recheck_tree.selection()
        if not sel:
            messagebox.showinfo('提示', '请先选择要标记的记录（可多选）')
            return
        note = simpledialog.askstring('联系备注', '请输入联系备注（可选，如：家长说下周三来）：', parent=self)
        person = simpledialog.askstring('联系人姓名', '请输入联系人姓名（可选，如：妈妈/爸爸/奶奶）：', parent=self)
        ids = [int(iid) for iid in sel]
        count = db.update_contact_batch(ids, 1, note, person)
        messagebox.showinfo('成功', f'已标记 {count} 条为已联系')
        self._load_recheck()

    def _mark_uncontacted(self):
        sel = self.recheck_tree.selection()
        if not sel:
            messagebox.showinfo('提示', '请先选择要标记的记录（可多选）')
            return
        if not messagebox.askyesno('确认', f'确认将选中的 {len(sel)} 条标记为未联系吗？'):
            return
        ids = [int(iid) for iid in sel]
        db.update_contact_batch(ids, 0, '', '')
        self._load_recheck()

    def _mark_phone_contacted(self):
        sel = self.recheck_tree.selection()
        if not sel:
            messagebox.showinfo('提示', '请先选择记录，同一个电话下的所有记录会一起标记')
            return
        _, phones = self._get_selected_ids_and_phones()
        if not phones:
            messagebox.showwarning('提示', '选中的记录里没有家长电话')
            return
        y = self.year_var.get()
        m = self.month_var.get()
        year = None if y == '全部' else int(y)
        month = None if m == '全部' else int(m)
        note = simpledialog.askstring('联系备注',
                                      f'将对电话 {", ".join(sorted(phones))} 下当前筛选月份的所有需复查记录标记为已联系\n请输入联系备注：',
                                      parent=self)
        person = simpledialog.askstring('联系人姓名', '请输入联系人姓名（如：妈妈）：', parent=self)
        total = 0
        for p in phones:
            total += db.update_contact_by_phone(p, 1, note, person, year=year, month=month)
        messagebox.showinfo('成功', f'涉及 {len(phones)} 个电话，共标记 {total} 条为已联系')
        self._load_recheck()

    def _set_appointment(self):
        sel = self.recheck_tree.selection()
        if not sel:
            messagebox.showinfo('提示', '请先选择要设置预约的记录（可多选）')
            return
        default_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        date_str = simpledialog.askstring('设置预约复查日期',
                                          f'请输入预约日期（格式：YYYY-MM-DD，留空表示取消预约）\n默认：{default_date}',
                                          parent=self, initialvalue=default_date)
        if date_str is None:
            return
        date_str = date_str.strip()
        if date_str:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                messagebox.showwarning('提示', '日期格式错误，应为 YYYY-MM-DD')
                return
        ids = [int(iid) for iid in sel]
        count = db.update_appointment(ids, date_str or None)
        if date_str:
            messagebox.showinfo('成功', f'已为 {count} 条记录设置预约日期：{date_str}')
        else:
            messagebox.showinfo('成功', f'已取消 {count} 条记录的预约日期')
        self._load_recheck()

    # ===== 导出 =====
    def _export_csv(self):
        if not self.current_results:
            messagebox.showinfo('提示', '当前没有可导出的数据')
            return
        default_name = f'窝沟封闭记录_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        path = filedialog.asksaveasfilename(
            parent=self,
            title='导出为 CSV',
            defaultextension='.csv',
            initialfile=default_name,
            filetypes=[('CSV 表格', '*.csv'), ('所有文件', '*.*')],
        )
        if not path:
            return
        headers = [
            '治疗日期', '儿童姓名', '出生年份', '家长电话', '操作医生',
        ]
        for pos in db.TOOTH_POSITIONS:
            headers += [f'{pos}封闭', f'{pos}拍照', f'{pos}复查']
        headers += ['家长反馈', '复查结果', '备注', '联系状态', '联系人', '联系时间', '联系备注', '预约复查日期', '创建时间', '更新时间']
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for r in self.current_results:
                    row = [
                        r.get('treatment_date', ''),
                        r.get('child_name', ''),
                        r.get('birth_year') or '',
                        r.get('parent_phone', ''),
                        r.get('doctor_name', ''),
                    ]
                    for pos in db.TOOTH_POSITIONS:
                        row += [
                            '是' if r.get(f'tooth{pos}_sealed') else '否',
                            '是' if r.get(f'tooth{pos}_photo') else '否',
                            '是' if r.get(f'tooth{pos}_recheck') else '否',
                        ]
                    row += [
                        r.get('parent_feedback', ''),
                        r.get('recheck_result', ''),
                        r.get('remark', ''),
                        '已联系' if r.get('contact_status') == 1 else '未联系',
                        r.get('contact_person') or '',
                        r.get('contacted_at') or '',
                        r.get('contact_note') or '',
                        r.get('appointment_date') or '',
                        r.get('created_at', ''),
                        r.get('updated_at', ''),
                    ]
                    writer.writerow(row)
            messagebox.showinfo('成功', f'已导出 {len(self.current_results)} 条记录到：\n{path}')
        except Exception as e:
            messagebox.showerror('错误', f'导出失败：{str(e)}')

    def _export_boss_summary(self):
        y = self.year_var.get()
        m = self.month_var.get()
        if y == '全部' or m == '全部':
            messagebox.showwarning('提示', '请先选择具体的年份和月份，再导出老板版汇总')
            return
        year = int(y)
        month = int(m)
        default_name = f'{year}年{month}月_窝沟封闭汇总_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        path = filedialog.asksaveasfilename(
            parent=self,
            title='导出老板版月度汇总',
            defaultextension='.csv',
            initialfile=default_name,
            filetypes=[('CSV 表格', '*.csv'), ('所有文件', '*.*')],
        )
        if not path:
            return
        summary = db.get_monthly_summary(year, month)
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([f'{year}年{month}月 窝沟封闭月度汇总'])
                writer.writerow([])

                writer.writerow(['===== 一、医生汇总 ====='])
                writer.writerow(['医生', '服务儿童数', '封闭牙数', '需复查记录数', '人均封闭牙数'])
                total_child = 0
                total_sealed = 0
                total_recheck = 0
                for s in summary:
                    avg = round(s['sealed_teeth'] / s['children_count'], 1) if s['children_count'] > 0 else 0
                    writer.writerow([
                        s['doctor_name'], s['children_count'], s['sealed_teeth'],
                        s['recheck_count'], avg,
                    ])
                    total_child += s['children_count']
                    total_sealed += s['sealed_teeth']
                    total_recheck += s['recheck_count']
                if total_child > 0:
                    avg_total = round(total_sealed / total_child, 1)
                    writer.writerow(['合计', total_child, total_sealed, total_recheck, avg_total])
                writer.writerow([])

                writer.writerow(['===== 二、各医生服务明细 ====='])
                for s in summary:
                    writer.writerow([])
                    writer.writerow([f'【{s["doctor_name"]}】{s["children_count"]}人 / {s["sealed_teeth"]}颗牙 / {s["recheck_count"]}条需复查'])
                    writer.writerow([
                        '治疗日期', '儿童姓名', '出生年', '家长电话',
                        '16封闭', '16拍照', '16复查',
                        '26封闭', '26拍照', '26复查',
                        '36封闭', '36拍照', '36复查',
                        '46封闭', '46拍照', '46复查',
                        '家长反馈', '复查结果', '备注', '联系状态',
                    ])
                    doctor_id = s.get('doctor_id')
                    rows = db.search_records(year=year, month=month, doctor_id=doctor_id)
                    for r in rows:
                        row = [
                            r['treatment_date'], r['child_name'], r.get('birth_year') or '', r.get('parent_phone') or '',
                        ]
                        for pos in db.TOOTH_POSITIONS:
                            row += [
                                '是' if r.get(f'tooth{pos}_sealed') else '否',
                                '是' if r.get(f'tooth{pos}_photo') else '否',
                                '是' if r.get(f'tooth{pos}_recheck') else '否',
                            ]
                        row += [
                            r.get('parent_feedback') or '',
                            r.get('recheck_result') or '',
                            r.get('remark') or '',
                            '已联系' if r.get('contact_status') == 1 else '未联系',
                        ]
                        writer.writerow(row)

                writer.writerow([])
                writer.writerow(['===== 三、预约复查台账（月底催单用）====='])
                writer.writerow([])

                today_str = datetime.now().strftime('%Y-%m-%d')
                recheck_headers = [
                    '医生', '治疗日期', '儿童姓名', '家长电话', '需复查牙位',
                    '预约复查日期', '联系人', '联系时间', '联系备注',
                ]

                writer.writerow(['--- 3.1 未完成且未预约（需立刻打电话）---'])
                writer.writerow(recheck_headers)
                for s in summary:
                    doctor_id = s.get('doctor_id')
                    pending = db.get_recheck_list(year=year, month=month, doctor_id=doctor_id, conclusion_status=0, appointment_filter='none')
                    for r in pending:
                        teeth = '、'.join([p for p in db.TOOTH_POSITIONS if r.get(f'tooth{p}_recheck')])
                        writer.writerow([
                            s['doctor_name'], r['treatment_date'], r['child_name'],
                            r.get('parent_phone') or '', teeth, r.get('appointment_date') or '',
                            r.get('contact_person') or '', r.get('contacted_at') or '',
                            (r.get('contact_note') or '')[:20],
                        ])

                writer.writerow([])
                writer.writerow(['--- 3.2 已预约待到院 ---'])
                writer.writerow(recheck_headers)
                for s in summary:
                    doctor_id = s.get('doctor_id')
                    appointed = db.get_recheck_list(year=year, month=month, doctor_id=doctor_id, conclusion_status=0, appointment_filter='appointed')
                    for r in appointed:
                        if not r.get('appointment_date') or r['appointment_date'] < today_str:
                            continue
                        teeth = '、'.join([p for p in db.TOOTH_POSITIONS if r.get(f'tooth{p}_recheck')])
                        writer.writerow([
                            s['doctor_name'], r['treatment_date'], r['child_name'],
                            r.get('parent_phone') or '', teeth, r.get('appointment_date') or '',
                            r.get('contact_person') or '', r.get('contacted_at') or '',
                            (r.get('contact_note') or '')[:20],
                        ])

                writer.writerow([])
                writer.writerow(['--- 3.3 预约逾期未到（重点催单）---'])
                writer.writerow(recheck_headers)
                for s in summary:
                    doctor_id = s.get('doctor_id')
                    overdue = db.get_recheck_list(year=year, month=month, doctor_id=doctor_id, conclusion_status=0, appointment_filter='overdue')
                    for r in overdue:
                        teeth = '、'.join([p for p in db.TOOTH_POSITIONS if r.get(f'tooth{p}_recheck')])
                        writer.writerow([
                            s['doctor_name'], r['treatment_date'], r['child_name'],
                            r.get('parent_phone') or '', teeth, r.get('appointment_date') or '',
                            r.get('contact_person') or '', r.get('contacted_at') or '',
                            (r.get('contact_note') or '')[:20],
                        ])

                writer.writerow([])
                writer.writerow(['--- 3.4 已完成复查 ---'])
                writer.writerow([
                    '医生', '治疗日期', '儿童姓名', '家长电话', '需复查牙位',
                    '复查结论', '联系人', '联系时间',
                ])
                for s in summary:
                    doctor_id = s.get('doctor_id')
                    done_rows = db.get_recheck_list(year=year, month=month, doctor_id=doctor_id, conclusion_status=1)
                    for r in done_rows:
                        teeth = '、'.join([p for p in db.TOOTH_POSITIONS if r.get(f'tooth{p}_recheck')])
                        writer.writerow([
                            s['doctor_name'], r['treatment_date'], r['child_name'],
                            r.get('parent_phone') or '', teeth,
                            (r.get('recheck_result') or '')[:30],
                            r.get('contact_person') or '', r.get('contacted_at') or '',
                        ])
            messagebox.showinfo('成功', f'老板版汇总已导出到：\n{path}')
        except Exception as e:
            messagebox.showerror('错误', f'导出失败：{str(e)}')


class DetailDialog(tk.Toplevel):
    def __init__(self, master, record_id, on_saved=None):
        super().__init__(master)
        self.record_id = record_id
        self.on_saved = on_saved
        self.tooth_widgets = {}
        self.title('记录详情')
        self.geometry('940x1040')
        self.configure(bg=BG_COLOR)
        self.transient(master)
        self.grab_set()
        self._load()
        self._build_ui()

    def _load(self):
        self.record = db.get_record(self.record_id)

    def _build_ui(self):
        r = self.record
        tk.Label(self, text=f'记录详情  ID:{r["id"]}', font=FONT_BIG, bg=BG_COLOR, fg='#303133').pack(pady=10)

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(fill='x', padx=30)

        tk.Label(form, text='儿童姓名：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=0, sticky='e', padx=8, pady=4)
        self.name_var = tk.StringVar(value=r['child_name'])
        tk.Entry(form, textvariable=self.name_var, font=FONT_LARGE, width=18).grid(row=0, column=1, sticky='w', pady=4)

        tk.Label(form, text='出生年份：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=2, sticky='e', padx=8, pady=4)
        self.birth_var = tk.StringVar(value=str(r.get('birth_year') or ''))
        tk.Entry(form, textvariable=self.birth_var, font=FONT_LARGE, width=10).grid(row=0, column=3, sticky='w', pady=4)

        tk.Label(form, text='家长电话：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=1, column=0, sticky='e', padx=8, pady=4)
        self.phone_var = tk.StringVar(value=r.get('parent_phone') or '')
        tk.Entry(form, textvariable=self.phone_var, font=FONT_LARGE, width=18).grid(row=1, column=1, sticky='w', pady=4)

        tk.Label(form, text='治疗日期：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=1, column=2, sticky='e', padx=8, pady=4)
        self.date_var = tk.StringVar(value=r['treatment_date'])
        tk.Entry(form, textvariable=self.date_var, font=FONT_LARGE, width=14).grid(row=1, column=3, sticky='w', pady=4)

        tk.Label(form, text='操作医生：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=2, column=0, sticky='e', padx=8, pady=4)
        self.doctor_var = tk.StringVar(value=r.get('doctor_name') or '')
        doctors = db.get_doctors()
        self.doctor_list = doctors
        cb = ttk.Combobox(form, textvariable=self.doctor_var, values=[d['name'] for d in doctors],
                          font=FONT_LARGE, width=16, state='readonly')
        cb.grid(row=2, column=1, sticky='w', pady=4)

        teeth_frame = tk.Frame(self, bg=BG_COLOR)
        teeth_frame.pack(padx=30, pady=8)

        for idx, pos in enumerate(db.TOOTH_POSITIONS):
            row, col = divmod(idx, 2)
            tw = ToothWidget(teeth_frame, pos, db.TOOTH_LABELS[pos])
            tw.grid(row=row, column=col, padx=8, pady=6, sticky='nsew')
            tw.set_state(r.get(f'tooth{pos}_sealed', 0), r.get(f'tooth{pos}_photo', 0), r.get(f'tooth{pos}_recheck', 0))
            self.tooth_widgets[pos] = tw

        extra = tk.LabelFrame(self, text='补充信息（家长反馈、复查结果、备注）', font=FONT_LARGE, bg=BG_COLOR, fg='#303133', padx=10, pady=8)
        extra.pack(fill='x', padx=30, pady=8)

        tk.Label(extra, text='家长反馈：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=0, column=0, sticky='ne', padx=5, pady=4)
        self.feedback_text = tk.Text(extra, font=FONT_NORMAL, height=2, width=45)
        self.feedback_text.insert('1.0', r.get('parent_feedback') or '')
        self.feedback_text.grid(row=0, column=1, sticky='w', pady=4)

        tk.Label(extra, text='复查结果：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=1, column=0, sticky='ne', padx=5, pady=4)
        self.recheck_text = tk.Text(extra, font=FONT_NORMAL, height=2, width=45)
        self.recheck_text.insert('1.0', r.get('recheck_result') or '')
        self.recheck_text.grid(row=1, column=1, sticky='w', pady=4)

        tk.Label(extra, text='备    注：', font=FONT_LARGE, bg=BG_COLOR, fg='#303133').grid(row=2, column=0, sticky='ne', padx=5, pady=4)
        self.remark_text = tk.Text(extra, font=FONT_NORMAL, height=2, width=45)
        self.remark_text.insert('1.0', r.get('remark') or '')
        self.remark_text.grid(row=2, column=1, sticky='w', pady=4)

        family = tk.LabelFrame(self, text='同电话家庭随访卡（每个孩子最近一次记录）', font=FONT_LARGE, bg=BG_COLOR, fg='#303133', padx=10, pady=8)
        family.pack(fill='x', padx=30, pady=8)
        fam_cols = ('name', 'last_date', 'doctor', 'pending', 'appointment', 'person', 'note')
        self.family_tree = ttk.Treeview(family, columns=fam_cols, show='headings', height=4)
        self.family_tree.heading('name', text='儿童姓名')
        self.family_tree.heading('last_date', text='最近治疗')
        self.family_tree.heading('doctor', text='医生')
        self.family_tree.heading('pending', text='待复查牙位')
        self.family_tree.heading('appointment', text='预约日期')
        self.family_tree.heading('person', text='联系人')
        self.family_tree.heading('note', text='最近联系备注')
        self.family_tree.column('name', width=100, anchor='center')
        self.family_tree.column('last_date', width=110, anchor='center')
        self.family_tree.column('doctor', width=80, anchor='center')
        self.family_tree.column('pending', width=200, anchor='w')
        self.family_tree.column('appointment', width=110, anchor='center')
        self.family_tree.column('person', width=80, anchor='center')
        self.family_tree.column('note', width=240, anchor='w')
        fam_style = ttk.Style()
        fam_style.configure('Fam.Treeview', font=FONT_NORMAL, rowheight=28)
        fam_style.configure('Fam.Treeview.Heading', font=FONT_NORMAL)
        self.family_tree.configure(style='Fam.Treeview')
        self.family_tree.tag_configure('has_pending', background='#fff7e6', foreground='#d46b08')
        self.family_tree.pack(fill='x', expand=False)
        self._load_family_summary()

        history = tk.LabelFrame(self, text='同电话的历史服务记录（半年内的在前 · 双击查看完整详情）', font=FONT_LARGE, bg=BG_COLOR, fg='#303133', padx=10, pady=8)
        history.pack(fill='both', expand=True, padx=30, pady=8)

        history_cols = ('date', 'name', 'doctor', 'teeth', 'recheck')
        self.history_tree = ttk.Treeview(history, columns=history_cols, show='headings', height=8)
        self.history_tree.heading('date', text='治疗日期')
        self.history_tree.heading('name', text='儿童姓名')
        self.history_tree.heading('doctor', text='医生')
        self.history_tree.heading('teeth', text='牙位/封闭/复查')
        self.history_tree.heading('recheck', text='复查结论')
        self.history_tree.column('date', width=130, anchor='center')
        self.history_tree.column('name', width=100, anchor='center')
        self.history_tree.column('doctor', width=90, anchor='center')
        self.history_tree.column('teeth', width=340, anchor='w')
        self.history_tree.column('recheck', width=180, anchor='w')
        hstyle = ttk.Style()
        hstyle.configure('Hist.Treeview', font=FONT_NORMAL, rowheight=28)
        hstyle.configure('Hist.Treeview.Heading', font=FONT_NORMAL)
        self.history_tree.configure(style='Hist.Treeview')
        self.history_tree.tag_configure('half_year', background='#fff7e6', foreground='#d46b08')
        self.history_tree.tag_configure('older', background='#ffffff', foreground='#606266')
        self.history_tree.tag_configure('sep', background='#e4e7ed')
        self.history_tree.pack(fill='both', expand=True)
        self.history_tree.bind('<Double-1>', self._open_history_detail)

        self._load_history()

        btn_bar = tk.Frame(self, bg=BG_COLOR)
        btn_bar.pack(pady=15)
        tk.Button(btn_bar, text='取消', font=FONT_LARGE, bg='#ffffff', fg='#606266',
                  relief='flat', cursor='hand2', width=10, height=2, command=self.destroy).pack(side='left', padx=15)
        tk.Button(btn_bar, text='保 存', font=FONT_LARGE, bg=BTN_OK, fg='white',
                  activebackground='#5daf34', activeforeground='white',
                  relief='flat', cursor='hand2', width=10, height=2, command=self._save).pack(side='left', padx=15)

    def _load_history(self):
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)
        phone = self.record.get('parent_phone')
        if not phone:
            self.history_tree.insert('', 'end', values=('（无家长电话）', '', '', '', ''))
            return
        history = db.get_history_by_phone(phone, exclude_id=self.record_id)
        if not history:
            self.history_tree.insert('', 'end', values=('（暂无历史记录）', '', '', '', ''))
            return
        current_date = datetime.strptime(self.record['treatment_date'], '%Y-%m-%d')

        half_year_list = []
        older_list = []
        for h in history:
            days_diff = (current_date - datetime.strptime(h['treatment_date'], '%Y-%m-%d')).days
            if 0 <= days_diff <= 180:
                half_year_list.append((h, days_diff))
            else:
                older_list.append((h, days_diff))

        half_year_list.sort(key=lambda x: x[1])
        older_list.sort(key=lambda x: -x[1])

        if half_year_list:
            label_id = self.history_tree.insert('', 'end',
                values=('── 半年内（共{}条）──'.format(len(half_year_list)), '', '', '', ''),
                tags=('sep',))
            self.history_tree.item(label_id, open=False)
            for h, days_diff in half_year_list:
                teeth_parts = []
                for pos in db.TOOTH_POSITIONS:
                    s = '封' if h.get(f'tooth{pos}_sealed') else '·'
                    r = '复' if h.get(f'tooth{pos}_recheck') else '·'
                    teeth_parts.append(f'{pos}:{s}{r}')
                teeth_str = '  '.join(teeth_parts)
                recheck = (h.get('recheck_result') or '')[:20]
                self.history_tree.insert('', 'end', iid=f'h_{h["id"]}', values=(
                    f'{h["treatment_date"]}（{days_diff}天前）',
                    h.get('child_name', ''),
                    h.get('doctor_name') or '',
                    teeth_str,
                    recheck,
                ), tags=('half_year',))

        if older_list:
            label_id = self.history_tree.insert('', 'end',
                values=('── 更早（共{}条）──'.format(len(older_list)), '', '', '', ''),
                tags=('sep',))
            self.history_tree.item(label_id, open=False)
            for h, days_diff in older_list:
                teeth_parts = []
                for pos in db.TOOTH_POSITIONS:
                    s = '封' if h.get(f'tooth{pos}_sealed') else '·'
                    r = '复' if h.get(f'tooth{pos}_recheck') else '·'
                    teeth_parts.append(f'{pos}:{s}{r}')
                teeth_str = '  '.join(teeth_parts)
                recheck = (h.get('recheck_result') or '')[:20]
                self.history_tree.insert('', 'end', iid=f'h_{h["id"]}', values=(
                    h['treatment_date'],
                    h.get('child_name', ''),
                    h.get('doctor_name') or '',
                    teeth_str,
                    recheck,
                ), tags=('older',))

    def _open_history_detail(self, event):
        sel = self.history_tree.selection()
        if not sel:
            return
        iid = sel[0]
        if not iid.startswith('h_'):
            return
        rid = int(iid.replace('h_', ''))
        DetailDialog(self, rid, on_saved=lambda: (self._load_history(), self._load_family_summary(), self._on_child_saved()))

    def _on_child_saved(self):
        if hasattr(self, 'on_saved') and self.on_saved:
            self.on_saved()

    def _load_family_summary(self):
        for i in self.family_tree.get_children():
            self.family_tree.delete(i)
        phone = self.record.get('parent_phone')
        if not phone:
            self.family_tree.insert('', 'end', values=('（未填写家长电话）', '', '', '', '', '', ''))
            return
        fam_list = db.get_family_followup(phone, self.record.get('treatment_date'))
        if not fam_list:
            self.family_tree.insert('', 'end', values=('（暂无家庭记录）', '', '', '', '', '', ''))
            return
        for c in fam_list:
            pending_str = '、'.join(c.get('pending_teeth') or [])
            if c.get('has_pending') and not pending_str:
                pending_str = '有(暂无牙位详情)'
            if not pending_str:
                pending_str = '—'
            tags = ('has_pending',) if c.get('has_pending') else ()
            note_parts = []
            if c.get('contacted_at'):
                note_parts.append(str(c['contacted_at'])[:16])
            if c.get('contact_note'):
                note_parts.append(str(c['contact_note'])[:15])
            note_str = ' | '.join(note_parts) or '—'
            self.family_tree.insert('', 'end', values=(
                c.get('child_name', ''),
                c.get('last_date') or '—',
                c.get('last_doctor') or '—',
                pending_str,
                c.get('appointment_date') or '—',
                c.get('contact_person') or '—',
                note_str,
            ), tags=tags)

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning('提示', '请填写儿童姓名', parent=self)
            return
        phone = self.phone_var.get().strip()
        if not phone:
            messagebox.showwarning('提示', '请填写家长电话', parent=self)
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
            'parent_phone': phone,
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
