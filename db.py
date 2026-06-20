import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clinic.db')

TOOTH_POSITIONS = ['16', '26', '36', '46']
TOOTH_LABELS = {
    '16': '右上第一恒磨牙',
    '26': '左上第一恒磨牙',
    '36': '左下第一恒磨牙',
    '46': '右下第一恒磨牙',
}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    tooth_cols = []
    for pos in TOOTH_POSITIONS:
        tooth_cols.append(f'tooth{pos}_sealed INTEGER DEFAULT 0')
        tooth_cols.append(f'tooth{pos}_photo INTEGER DEFAULT 0')
        tooth_cols.append(f'tooth{pos}_recheck INTEGER DEFAULT 0')
    tooth_sql = ', '.join(tooth_cols)
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_name TEXT NOT NULL,
            birth_year INTEGER,
            parent_phone TEXT,
            treatment_date TEXT NOT NULL,
            doctor_id INTEGER,
            {tooth_sql},
            parent_feedback TEXT,
            recheck_result TEXT,
            remark TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    c.execute("PRAGMA table_info(records)")
    cols = [row['name'] for row in c.fetchall()]
    if 'contact_status' not in cols:
        c.execute('ALTER TABLE records ADD COLUMN contact_status INTEGER DEFAULT 0')
    if 'contacted_at' not in cols:
        c.execute('ALTER TABLE records ADD COLUMN contacted_at TEXT')
    if 'contact_note' not in cols:
        c.execute('ALTER TABLE records ADD COLUMN contact_note TEXT')
    if 'contact_person' not in cols:
        c.execute('ALTER TABLE records ADD COLUMN contact_person TEXT')
    if 'appointment_date' not in cols:
        c.execute('ALTER TABLE records ADD COLUMN appointment_date TEXT')
    c.execute('SELECT COUNT(*) FROM doctors')
    if c.fetchone()[0] == 0:
        for name in ['张医生', '李医生', '王医生']:
            c.execute('INSERT INTO doctors (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()


def get_doctors():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM doctors ORDER BY id')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_doctor(name):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO doctors (name) VALUES (?)', (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()


def find_duplicate(child_name, parent_phone, treatment_date):
    if not child_name or not parent_phone:
        return None
    conn = get_conn()
    c = conn.cursor()
    try:
        td = datetime.strptime(treatment_date, '%Y-%m-%d')
    except ValueError:
        td = datetime.now()
    start = (td - timedelta(days=180)).strftime('%Y-%m-%d')
    end = (td + timedelta(days=180)).strftime('%Y-%m-%d')
    c.execute('''
        SELECT r.*, d.name as doctor_name FROM records r
        LEFT JOIN doctors d ON r.doctor_id = d.id
        WHERE r.child_name = ? AND r.parent_phone = ?
          AND r.treatment_date BETWEEN ? AND ?
        ORDER BY r.treatment_date DESC
        LIMIT 5
    ''', (child_name, parent_phone, start, end))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_record(data):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    keys = ['child_name', 'birth_year', 'parent_phone', 'treatment_date', 'doctor_id']
    for pos in TOOTH_POSITIONS:
        keys += [f'tooth{pos}_sealed', f'tooth{pos}_photo', f'tooth{pos}_recheck']
    keys += ['parent_feedback', 'recheck_result', 'remark',
             'contact_status', 'contacted_at', 'contact_note', 'contact_person', 'appointment_date',
             'created_at', 'updated_at']
    values = []
    for k in ['child_name', 'birth_year', 'parent_phone', 'treatment_date', 'doctor_id']:
        values.append(data.get(k))
    for pos in TOOTH_POSITIONS:
        values.append(int(data.get(f'tooth{pos}_sealed', 0)))
        values.append(int(data.get(f'tooth{pos}_photo', 0)))
        values.append(int(data.get(f'tooth{pos}_recheck', 0)))
    values += [
        data.get('parent_feedback', ''), data.get('recheck_result', ''), data.get('remark', ''),
        int(data.get('contact_status', 0) or 0),
        data.get('contacted_at'), data.get('contact_note', ''), data.get('contact_person', ''),
        data.get('appointment_date'),
        now, now,
    ]
    placeholders = ', '.join(['?'] * len(keys))
    c.execute(f'INSERT INTO records ({", ".join(keys)}) VALUES ({placeholders})', values)
    rid = c.lastrowid
    conn.commit()
    conn.close()
    return rid


def update_record(rid, data):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fields = []
    values = []
    for k in ['child_name', 'birth_year', 'parent_phone', 'treatment_date', 'doctor_id']:
        if k in data:
            fields.append(f'{k} = ?')
            values.append(data[k])
    for pos in TOOTH_POSITIONS:
        for f in ['sealed', 'photo', 'recheck']:
            key = f'tooth{pos}_{f}'
            if key in data:
                fields.append(f'{key} = ?')
                values.append(int(data[key]))
    for k in ['parent_feedback', 'recheck_result', 'remark', 'contact_person', 'appointment_date']:
        if k in data:
            fields.append(f'{k} = ?')
            values.append(data[k])
    fields.append('updated_at = ?')
    values.append(now)
    values.append(rid)
    c.execute(f'UPDATE records SET {", ".join(fields)} WHERE id = ?', values)
    conn.commit()
    conn.close()


def get_record(rid):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        SELECT r.*, d.name as doctor_name FROM records r
        LEFT JOIN doctors d ON r.doctor_id = d.id
        WHERE r.id = ?
    ''', (rid,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def search_records(year=None, month=None, doctor_id=None, child_name=None):
    conn = get_conn()
    c = conn.cursor()
    sql = '''
        SELECT r.*, d.name as doctor_name FROM records r
        LEFT JOIN doctors d ON r.doctor_id = d.id
        WHERE 1=1
    '''
    params = []
    if year and month:
        start = f'{year:04d}-{month:02d}-01'
        if month == 12:
            end = f'{year+1:04d}-01-01'
        else:
            end = f'{year:04d}-{month+1:02d}-01'
        sql += ' AND r.treatment_date >= ? AND r.treatment_date < ?'
        params += [start, end]
    elif year:
        sql += ' AND substr(r.treatment_date, 1, 4) = ?'
        params.append(f'{year:04d}')
    if doctor_id:
        sql += ' AND r.doctor_id = ?'
        params.append(doctor_id)
    if child_name:
        sql += ' AND r.child_name LIKE ?'
        params.append(f'%{child_name}%')
    sql += ' ORDER BY r.treatment_date DESC, r.id DESC'
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_history_by_phone(phone, exclude_id=None):
    if not phone:
        return []
    conn = get_conn()
    c = conn.cursor()
    sql = '''
        SELECT r.*, d.name as doctor_name FROM records r
        LEFT JOIN doctors d ON r.doctor_id = d.id
        WHERE r.parent_phone = ?
    '''
    params = [phone]
    if exclude_id:
        sql += ' AND r.id != ?'
        params.append(exclude_id)
    sql += ' ORDER BY r.treatment_date DESC, r.id DESC'
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_summary(year, month):
    start = f'{year:04d}-{month:02d}-01'
    if month == 12:
        end = f'{year+1:04d}-01-01'
    else:
        end = f'{year:04d}-{month+1:02d}-01'
    conn = get_conn()
    c = conn.cursor()
    sealed_fields = []
    for pos in TOOTH_POSITIONS:
        sealed_fields.append(f'SUM(r.tooth{pos}_sealed)')
    sealed_sql = ', '.join(sealed_fields)
    recheck_expr = ' + '.join([f'COALESCE(r.tooth{p}_recheck, 0)' for p in TOOTH_POSITIONS])
    c.execute(f'''
        SELECT r.doctor_id, d.name as doctor_name,
               COUNT(DISTINCT r.id) as children_count,
               {sealed_sql},
               SUM(CASE WHEN ({recheck_expr}) > 0 THEN 1 ELSE 0 END) as recheck_records
        FROM records r
        LEFT JOIN doctors d ON r.doctor_id = d.id
        WHERE r.treatment_date >= ? AND r.treatment_date < ?
        GROUP BY r.doctor_id, d.name
        ORDER BY children_count DESC
    ''', (start, end))
    rows = c.fetchall()
    result = []
    for row in rows:
        row_dict = dict(row)
        sealed_total = 0
        for pos in TOOTH_POSITIONS:
            key = f'SUM(r.tooth{pos}_sealed)'
            sealed_total += int(row_dict.pop(key, 0) or 0)
        row_dict['sealed_teeth'] = sealed_total
        row_dict['recheck_count'] = int(row_dict.pop('recheck_records', 0) or 0)
        if not row_dict.get('doctor_name'):
            row_dict['doctor_name'] = '未指定'
        result.append(row_dict)
    conn.close()
    return result


def get_recheck_list(year=None, month=None, doctor_id=None, contact_status=None,
                     child_name=None, conclusion_status=None, appointment_filter=None):
    conn = get_conn()
    c = conn.cursor()
    recheck_expr = ' + '.join([f'COALESCE(r.tooth{p}_recheck, 0)' for p in TOOTH_POSITIONS])
    sql = f'''
        SELECT r.*, d.name as doctor_name FROM records r
        LEFT JOIN doctors d ON r.doctor_id = d.id
        WHERE ({recheck_expr}) > 0
    '''
    params = []
    if year and month:
        start = f'{year:04d}-{month:02d}-01'
        if month == 12:
            end = f'{year+1:04d}-01-01'
        else:
            end = f'{year:04d}-{month+1:02d}-01'
        sql += ' AND r.treatment_date >= ? AND r.treatment_date < ?'
        params += [start, end]
    elif year:
        sql += ' AND substr(r.treatment_date, 1, 4) = ?'
        params.append(f'{year:04d}')
    if doctor_id:
        sql += ' AND r.doctor_id = ?'
        params.append(doctor_id)
    if contact_status is not None:
        if contact_status == 0:
            sql += ' AND (r.contact_status = 0 OR r.contact_status IS NULL)'
        else:
            sql += ' AND r.contact_status = ?'
            params.append(contact_status)
    if conclusion_status is not None:
        if conclusion_status == 0:
            sql += " AND (r.recheck_result IS NULL OR TRIM(r.recheck_result) = '')"
        else:
            sql += " AND r.recheck_result IS NOT NULL AND TRIM(r.recheck_result) != ''"
    if appointment_filter:
        today = datetime.now().strftime('%Y-%m-%d')
        dt_today = datetime.strptime(today, '%Y-%m-%d')
        if appointment_filter == 'today':
            sql += ' AND r.appointment_date = ?'
            params.append(today)
        elif appointment_filter == 'week':
            week_end = (dt_today + timedelta(days=7)).strftime('%Y-%m-%d')
            sql += ' AND r.appointment_date >= ? AND r.appointment_date < ?'
            params += [today, week_end]
        elif appointment_filter == 'overdue':
            sql += " AND r.appointment_date IS NOT NULL AND TRIM(r.appointment_date) != '' AND r.appointment_date < ?"
            sql += " AND (r.recheck_result IS NULL OR TRIM(r.recheck_result) = '')"
            params.append(today)
        elif appointment_filter == 'appointed':
            sql += " AND r.appointment_date IS NOT NULL AND TRIM(r.appointment_date) != ''"
        elif appointment_filter == 'none':
            sql += " AND (r.appointment_date IS NULL OR TRIM(r.appointment_date) = '')"
    if child_name:
        sql += ' AND r.child_name LIKE ?'
        params.append(f'%{child_name}%')
    sql += ' ORDER BY COALESCE(r.appointment_date, r.treatment_date) ASC, r.id ASC'
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_contact(record_id, status, note=None, person=None):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if status == 0:
        c.execute('''
            UPDATE records SET contact_status = 0, contacted_at = NULL,
                   contact_note = ?, contact_person = ?, updated_at = ? WHERE id = ?
        ''', (note or '', person or '', now, record_id))
    else:
        c.execute('''
            UPDATE records SET contact_status = 1, contacted_at = ?,
                   contact_note = ?, contact_person = ?, updated_at = ? WHERE id = ?
        ''', (now, note or '', person or '', now, record_id))
    conn.commit()
    conn.close()


def update_contact_batch(record_ids, status, note=None, person=None):
    if not record_ids:
        return 0
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    placeholders = ', '.join(['?'] * len(record_ids))
    if status == 0:
        c.execute(f'''
            UPDATE records SET contact_status = 0, contacted_at = NULL,
                   contact_note = ?, contact_person = ?, updated_at = ? WHERE id IN ({placeholders})
        ''', [note or '', person or '', now] + list(record_ids))
    else:
        c.execute(f'''
            UPDATE records SET contact_status = 1, contacted_at = ?,
                   contact_note = ?, contact_person = ?, updated_at = ? WHERE id IN ({placeholders})
        ''', [now, note or '', person or '', now] + list(record_ids))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected


def update_contact_by_phone(phone, status, note=None, person=None, year=None, month=None):
    if not phone:
        return 0
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    recheck_expr = ' + '.join([f'COALESCE(tooth{p}_recheck, 0)' for p in TOOTH_POSITIONS])
    params = []
    sql_parts = [f'({recheck_expr}) > 0', 'parent_phone = ?']
    params.append(phone)
    if year and month:
        start = f'{year:04d}-{month:02d}-01'
        if month == 12:
            end = f'{year+1:04d}-01-01'
        else:
            end = f'{year:04d}-{month+1:02d}-01'
        sql_parts.append('treatment_date >= ? AND treatment_date < ?')
        params += [start, end]
    where_sql = ' AND '.join(sql_parts)
    if status == 0:
        c.execute(f'''
            UPDATE records SET contact_status = 0, contacted_at = NULL,
                   contact_note = ?, contact_person = ?, updated_at = ? WHERE {where_sql}
        ''', [note or '', person or '', now] + params)
    else:
        c.execute(f'''
            UPDATE records SET contact_status = 1, contacted_at = ?,
                   contact_note = ?, contact_person = ?, updated_at = ? WHERE {where_sql}
        ''', [now, note or '', person or '', now] + params)
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected


def update_appointment(record_ids, appointment_date):
    if not record_ids:
        return 0
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    placeholders = ', '.join(['?'] * len(record_ids))
    if appointment_date:
        c.execute(f'''
            UPDATE records SET appointment_date = ?, updated_at = ? WHERE id IN ({placeholders})
        ''', [appointment_date, now] + list(record_ids))
    else:
        c.execute(f'''
            UPDATE records SET appointment_date = NULL, updated_at = ? WHERE id IN ({placeholders})
        ''', [now] + list(record_ids))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected


def get_phone_summary(phone, ref_date=None):
    if not phone:
        return None
    if ref_date is None:
        ref_date = datetime.now().strftime('%Y-%m-%d')
    try:
        ref = datetime.strptime(ref_date, '%Y-%m-%d')
    except ValueError:
        ref = datetime.now()
    half_start = (ref - timedelta(days=180)).strftime('%Y-%m-%d')
    half_end = (ref + timedelta(days=1)).strftime('%Y-%m-%d')
    conn = get_conn()
    c = conn.cursor()
    recheck_expr = ' + '.join([f'COALESCE(tooth{p}_recheck, 0)' for p in TOOTH_POSITIONS])
    sealed_fields = []
    for pos in TOOTH_POSITIONS:
        sealed_fields.append(f'MAX(tooth{pos}_sealed)')
    pending_expr_parts = []
    for pos in TOOTH_POSITIONS:
        pending_expr_parts.append(
            f"MAX(CASE WHEN tooth{pos}_recheck = 1 AND (recheck_result IS NULL OR TRIM(recheck_result) = '') THEN 1 ELSE 0 END)"
        )
    c.execute(f'''
        SELECT COUNT(DISTINCT id) as total_visits,
               {', '.join(sealed_fields)},
               {', '.join(pending_expr_parts)},
               SUM(CASE WHEN ({recheck_expr}) > 0 AND (recheck_result IS NULL OR TRIM(recheck_result) = '') THEN 1 ELSE 0 END) as pending_count
        FROM records
        WHERE parent_phone = ? AND treatment_date >= ? AND treatment_date < ?
    ''', (phone, half_start, half_end))
    row = c.fetchone()
    result = dict(row) if row else {}
    all_sealed = []
    all_pending = []
    for pos in TOOTH_POSITIONS:
        if int(result.pop(f'MAX(tooth{pos}_sealed)', 0) or 0):
            all_sealed.append(pos)
    for pos in TOOTH_POSITIONS:
        key = f"MAX(CASE WHEN tooth{pos}_recheck = 1 AND (recheck_result IS NULL OR TRIM(recheck_result) = '') THEN 1 ELSE 0 END)"
        if int(result.pop(key, 0) or 0):
            all_pending.append(pos)
    result['sealed_teeth'] = all_sealed
    result['pending_recheck_teeth'] = all_pending
    c.execute('SELECT COUNT(*) FROM records WHERE parent_phone = ?', (phone,))
    result['all_time_visits'] = c.fetchone()[0]
    conn.close()
    return result


def get_family_followup(phone, ref_date=None):
    if not phone:
        return []
    conn = get_conn()
    c = conn.cursor()
    recheck_expr = ' + '.join([f'COALESCE(tooth{p}_recheck, 0)' for p in TOOTH_POSITIONS])
    c.execute(f'''
        SELECT r.*, d.name as doctor_name FROM records r
        LEFT JOIN doctors d ON r.doctor_id = d.id
        WHERE r.parent_phone = ?
        ORDER BY r.treatment_date DESC, r.id DESC
    ''', (phone,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    child_map = {}
    for r in rows:
        name = r.get('child_name') or '未知'
        if name not in child_map:
            pending_teeth = []
            has_pending_record = False
            for pos in TOOTH_POSITIONS:
                if r.get(f'tooth{pos}_recheck') and not (r.get('recheck_result') and str(r['recheck_result']).strip()):
                    pending_teeth.append(pos)
            if pending_teeth:
                has_pending_record = True
            child_map[name] = {
                'child_name': name,
                'last_date': r.get('treatment_date'),
                'last_doctor': r.get('doctor_name') or '',
                'pending_teeth': pending_teeth,
                'has_pending': has_pending_record,
                'appointment_date': r.get('appointment_date'),
                'contacted_at': r.get('contacted_at'),
                'contact_note': r.get('contact_note') or '',
                'contact_person': r.get('contact_person') or '',
                'recheck_result': r.get('recheck_result') or '',
            }
    return sorted(child_map.values(), key=lambda x: x['last_date'] or '', reverse=True)
