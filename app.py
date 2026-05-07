from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DATABASE = 'users.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            age INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) as total FROM users')
    total = c.fetchone()['total']
    
    c.execute('SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?', (limit, offset))
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({
        'success': True,
        'data': {
            'list': users,
            'total': total,
            'page': page,
            'limit': limit
        }
    })

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    age = data.get('age')
    
    if not name or not email:
        return jsonify({'success': False, 'message': '姓名和邮箱不能为空'})
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('INSERT INTO users (name, email, age) VALUES (?, ?, ?)', (name, email, age))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return jsonify({'success': True, 'message': '添加成功', 'data': {'id': user_id}})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': '邮箱已存在'})

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    age = data.get('age')
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('''
            UPDATE users SET name=?, email=?, age=?, updated_at=CURRENT_TIMESTAMP WHERE id=?
        ''', (name, email, age, user_id))
        conn.commit()
        if c.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'})
        conn.close()
        return jsonify({'success': True, 'message': '更新成功'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': '邮箱已存在'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    if c.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'message': '用户不存在'})
    conn.close()
    return jsonify({'success': True, 'message': '删除成功'})

@app.route('/api/users/batch', methods=['DELETE'])
def batch_delete():
    data = request.get_json()
    ids = data.get('ids', [])
    
    if not ids:
        return jsonify({'success': False, 'message': '请选择要删除的用户'})
    
    conn = get_db()
    c = conn.cursor()
    placeholders = ','.join(['?'] * len(ids))
    c.execute(f'DELETE FROM users WHERE id IN ({placeholders})', ids)
    conn.commit()
    deleted = c.rowcount
    conn.close()
    return jsonify({'success': True, 'message': f'成功删除 {deleted} 条记录'})

@app.route('/api/users/export', methods=['GET'])
def export_users():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    
    csv_content = 'ID,姓名,邮箱,年龄,创建时间\n'
    for user in users:
        csv_content += f"{user['id']},{user['name']},{user['email']},{user['age'] or ''},{user['created_at']}\n"
    
    from io import StringIO
    output = StringIO(csv_content)
    return send_file(
        output,
        mimetype='text/csv',
        download_name=f'用户列表_{datetime.now().strftime("%Y-%m-%d")}.csv'
    )

@app.route('/api/users/template', methods=['GET'])
def download_template():
    template = '姓名,邮箱,年龄\n张三,zhangsan@example.com,25\n李四,lisi@example.com,30\n'
    from io import StringIO
    output = StringIO(template)
    return send_file(
        output,
        mimetype='text/csv',
        download_name='用户导入模板.csv'
    )

@app.route('/api/users/import', methods=['POST'])
def import_users():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '请上传文件'})
    
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': '只支持 CSV 文件'})
    
    try:
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')[1:]
        errors = []
        success_count = 0
        fail_count = 0
        
        conn = get_db()
        c = conn.cursor()
        
        for i, line in enumerate(lines):
            row_num = i + 2
            parts = line.split(',')
            if len(parts) < 2:
                errors.append(f'第{row_num}行：数据格式错误')
                fail_count += 1
                continue
            
            name = parts[0].strip()
            email = parts[1].strip() if len(parts) > 1 else ''
            age = parts[2].strip() if len(parts) > 2 else None
            
            if not name:
                errors.append(f'第{row_num}行：姓名为空')
                fail_count += 1
                continue
            
            if not email or '@' not in email:
                errors.append(f'第{row_num}行：邮箱格式错误')
                fail_count += 1
                continue
            
            if age:
                try:
                    age = int(age)
                    if age < 0 or age > 150:
                        errors.append(f'第{row_num}行：年龄必须为 0-150 的数字')
                        fail_count += 1
                        continue
                except ValueError:
                    errors.append(f'第{row_num}行：年龄必须为数字')
                    fail_count += 1
                    continue
            
            try:
                c.execute('INSERT INTO users (name, email, age) VALUES (?, ?, ?)', (name, email, age))
                success_count += 1
            except sqlite3.IntegrityError:
                errors.append(f'第{row_num}行：邮箱已存在')
                fail_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'导入完成：成功 {success_count} 条，失败 {fail_count} 条',
            'errors': errors,
            'data': {'successCount': success_count, 'failCount': fail_count}
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'文件解析失败: {str(e)}'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)