import os
from flask import Flask, render_template, request, jsonify, send_file, abort
from flask_cors import CORS

# from searchIndex import SearchIndex
# import lucene


save_dir = "E:/files/virtualbox_share/oriPDFs/"

app = Flask(__name__)
CORS(app)

# 初始化JVM
# lucene.initVM(vmargs=['-Djava.awt.headless=true'])

# 初始化搜索引擎
# searcher = SearchIndex()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/pdfs/<path:filename>")
def serve_pdf(filename):
    file_path = os.path.join(save_dir, filename)
    print(file_path)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype="application/pdf")
    else:
        abort(404, description="文件未找到")


@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query")
    if not query:
        return jsonify({"error": "搜索查询不能为空"}), 400

    try:
        # 附加当前线程到JVM
        # lucene.getVMEnv().attachCurrentThread()
        # if lucene.getVMEnv().isCurrentThreadAttached():
        # 执行搜索

        # result = searcher.search(query, 20)

        # if result is None or not result.get('docInfo'):
        #     return jsonify({'error': '搜索结果为空'}), 404
        # return jsonify(result)
        docInfo = [
            {
                "title": "Aaaaa",
                "author": "A-a-a",
                "abstract": "A---------------",
                "docID": 1,
                "name": "ycomrsmasmiamiedupublicationskara2007JC004516",  
                'address': 'beijing',  
            },
            {
                "title": "Baaaa",
                "author": "B-a-a",
                "abstract": "B---------------",
                "docID": 2,
                "name": "ycomrsmasmiamiedupublicationskara2007JC004516",   
                'address': 'shanghai',  
            }
        ] * 35

        result = {
            "totalHits": 104,
            'time': 190,
            "docInfo": docInfo,
        }
        return jsonify(result)
        # else:
        #     return jsonify({'error': '无法附加到JVM线程'}), 500
    except Exception as e:
        app.logger.error(f"搜索出错: {str(e)}")
        return jsonify({"error": "搜索过程中发生错误"}), 500
    # finally:
    #     # 确保在请求结束时分离当前线程
    #     if lucene.getVMEnv().isCurrentThreadAttached():
    #         lucene.getVMEnv().detachCurrentThread()


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
