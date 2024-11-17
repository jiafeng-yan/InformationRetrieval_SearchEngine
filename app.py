import os
from flask import Flask, render_template, request, jsonify, send_file, abort
from flask_cors import CORS
from searchIndex import search
from spellcheck import spell_check_last_word, change_dict
from werkzeug.utils import secure_filename
from initIndex import update_lib, update_stop
import lucene

# source ~/miniconda3/bin/activate

app = Flask(__name__)
CORS(app)

# 本地源文件存放路径
# save_dir = 'E:/files/virtualbox_share/oriPDFs/'
save_dir = '/home/yjf/share/oriPDFs/'

# 设置文件上传的保存路径
upload_folder = './uploads'

_glb_stop_list = []

# 初始化JVM
lucene.initVM(vmargs=['-Djava.awt.headless=true'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdfs/<path:filename>')
def serve_pdf(filename):
    global save_dir

    file_path = os.path.join(save_dir, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='application/pdf')
    else:
        file_path = os.path.join('./uploads', filename)
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='application/pdf')
        else:
            print(file_path)
            abort(404, description="文件未找到")


@app.route('/api/check', methods=['POST'])
def add_check():
    check_list = request.json.get('check')  # 从前端获取查询添加的 check list
    try:
        lucene.getVMEnv().attachCurrentThread()
        if lucene.getVMEnv().isCurrentThreadAttached():
            
            if(change_dict(check_list)):
                return jsonify({'success': '成功修改'})
            else:
                return jsonify({'error': '单词库加载失败'}), 500
        else:
            return jsonify({'error': '无法附加到JVM线程'}), 500
    except Exception as e:
        app.logger.error(f"检查出错: {str(e)}")
        return jsonify({'error': '词添加过程中发生错误'}), 500
    finally:
        # 确保在请求结束时分离当前线程
        if lucene.getVMEnv().isCurrentThreadAttached():
            lucene.getVMEnv().detachCurrentThread()
            

@app.route('/api/stop', methods=['POST'])   # stop
def add_stop():
    global _glb_stop_list

    try:
        stop_list = request.json.get('stop')  # 从前端获取查询添加的 check list
        _glb_stop_list = stop_list.strip().split(';')
        return jsonify({'success': '成功修改'})
    except Exception as e:
        app.logger.error(f"检查出错: {str(e)}")
        return jsonify({'error': '重建索引过程中发生错误'}), 500

    # try:
    #     lucene.getVMEnv().attachCurrentThread()
    #     if lucene.getVMEnv().isCurrentThreadAttached():
            
    #         if(update_stop(stop_list)):
    #             return jsonify({'success': '成功修改'})
    #         else:
    #             return jsonify({'error': '重建索引失败'}), 500
    #     else:
    #         return jsonify({'error': '无法附加到JVM线程'}), 500
    # except Exception as e:
    #     app.logger.error(f"检查出错: {str(e)}")
    #     return jsonify({'error': '重建索引过程中发生错误'}), 500
    # finally:
    #     # 确保在请求结束时分离当前线程
    #     if lucene.getVMEnv().isCurrentThreadAttached():
    #         lucene.getVMEnv().detachCurrentThread()


@app.route('/api/spellcheck', methods=['POST'])
def spellcheck():
    query_text = request.json.get('query')
    stop_list = request.json.get('stop')
    if not query_text:
        return jsonify({'suggestions': []})
    try:
        lucene.getVMEnv().attachCurrentThread()
        if lucene.getVMEnv().isCurrentThreadAttached():
            suggestions = spell_check_last_word(query_text)
            
            return jsonify({'suggestions': suggestions})
        else:
            return jsonify({'error': '无法附加到JVM线程'}), 500
    except Exception as e:
        app.logger.error(f"检查出错: {str(e)}")
        return jsonify({'error': '拼写纠正过程中发生错误'}), 500
    finally:
        # 确保在请求结束时分离当前线程
        if lucene.getVMEnv().isCurrentThreadAttached():
            lucene.getVMEnv().detachCurrentThread()


@app.route('/api/search', methods=['POST'])
def searchFile():
    global _glb_stop_list

    query = request.json.get('query')
    if not query:
        return jsonify({'error': '搜索查询不能为空'}), 400
    print(*_glb_stop_list)

    try:
        # 附加当前线程到JVM
        lucene.getVMEnv().attachCurrentThread()
        if lucene.getVMEnv().isCurrentThreadAttached():
            # 执行搜索
            abstractMaxLen = 1000
            HighlightNum = 10

            result = search(query, 80, abstractMaxLen, HighlightNum, stop_list=_glb_stop_list)     # 返回75个，每页15个结果

            if result is None or not result.get('docInfo'):
                return jsonify({'error': '搜索结果为空'}), 404
            return jsonify(result)
        else:
            return jsonify({'error': '无法附加到JVM线程'}), 500
    # except Exception as e:
    #     app.logger.error(f"搜索出错: {str(e)}")
    #     return jsonify({'error': '搜索过程中发生错误'}), 500
    finally:
        pass
        # 确保在请求结束时分离当前线程
        if lucene.getVMEnv().isCurrentThreadAttached():
            lucene.getVMEnv().detachCurrentThread()


@app.route('/api/file', methods=['POST'])
def add_file():
    global _glb_stop_list

    # 处理文件上传
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    stop_list = _glb_stop_list
    print(file.filename, *stop_list)
    
    # 确保文件名安全
    if file and allowed_file(file.filename):
        # 保存文件到上传目录
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # 文件保存成功后进行后续处理        
        try:
            lucene.getVMEnv().attachCurrentThread()

            if lucene.getVMEnv().isCurrentThreadAttached():
                # 在这里你可以根据上传的文件做相应的处理
                
                if update_lib(file_path, stop_list):  # 假设你需要处理上传的文件
                    return jsonify({'success': '成功添加'})
                else:
                    return jsonify({'error': '文件上传失败'}), 500
            else:
                return jsonify({'error': '无法附加到JVM线程'}), 500
        except Exception as e:
            app.logger.error(f"检查出错: {str(e)}")
            return jsonify({'error': '文件加载过程中发生错误'}), 500
        finally:
            pass
            # 确保在请求结束时分离当前线程
            if lucene.getVMEnv().isCurrentThreadAttached():
                lucene.getVMEnv().detachCurrentThread()
    
    return jsonify({'error': '文件类型不允许'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='192.168.43.248', port=5000)