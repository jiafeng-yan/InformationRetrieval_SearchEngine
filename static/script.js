document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const totalHitsDiv = document.getElementById('total-hits');
    const resultsDiv = document.getElementById('results');

    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    async function performSearch() {
        const query = searchInput.value.trim();
        if (query) {
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: query }),
                });
                const results = await response.json();
                displayResults(results);
            } catch (error) {
                console.error('搜索出错:', error);
            }
        }
    }

    function displayResults(results) {
        if (!results || !results.totalHits || results.totalHits === 0) {
            totalHitsDiv.textContent = '未找到相关结果';
            resultsDiv.innerHTML = ''; // 清空结果区域
            return; // 结束函数
        }
    
        totalHitsDiv.textContent = `共找到 ${results.totalHits} 条结果`;
        resultsDiv.innerHTML = '';
        results.docInfo.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';
            
            // 创建文件路径
            const filePath = `${result.name}.pdf`;
            
            resultItem.innerHTML = `
                <div class="result-title" data-filepath="${filePath}">
                    <span class="docID">#${result.docID}</span> 
                    ${result.title}
                </div>
                <div class="result-author">Author: ${result.author.split(' ').join(' ; ')}</div>
                <div class="result-abstract">
                    <div class="abstract-wrapper">
                        <div class="abstract-content">${result.abstract}</div>
                        <span class="abstract-more">更多</span>
                    </div>
                </div>
            `;
            resultsDiv.appendChild(resultItem);
    
            const abstractWrapper = resultItem.querySelector('.abstract-wrapper');
            const abstractContent = resultItem.querySelector('.abstract-content');
            const moreButton = resultItem.querySelector('.abstract-more');
    
            // 使用 requestAnimationFrame 确保内容已渲染
            requestAnimationFrame(() => {
                if (abstractContent.scrollHeight > abstractContent.clientHeight) {
                    moreButton.style.display = 'inline-block';
                    moreButton.addEventListener('click', function(e) {
                        e.preventDefault();
                        if (abstractContent.classList.contains('expanded')) {
                            abstractContent.classList.remove('expanded');
                            moreButton.textContent = '更多';
                        } else {
                            abstractContent.classList.add('expanded');
                            moreButton.textContent = '收起';
                        }
                    });
                } else {
                    moreButton.style.display = 'none';
                }
            });
    
            // 直接在这里为每个标题添加点击事件处理器
            const titleElement = resultItem.querySelector('.result-title');
            titleElement.style.cursor = 'pointer'; // 添加鼠标指针样式，表明可点击
            titleElement.addEventListener('click', function(e) {
                const clickedFilePath = this.getAttribute('data-filepath');
                openPDF(clickedFilePath);
            });
        });
    }
    
    // function openPDF(filePath) {
    //     console.log('Opening PDF:', filePath);
    //     // 使用 Clipboard API 复制文件路径
    //     navigator.clipboard.writeText(filePath).then(() => {
    //         alert('文件路径已复制到剪贴板：\n' + filePath + '\n\n请在文件资源管理器中粘贴此路径来打开文件。');
    //     }).catch(err => {
    //         console.error('无法复制文件路径: ', err);
    //         // 如果 Clipboard API 不可用，提供备选方案
    //         prompt('无法自动复制文件路径。请手动复制以下路径：', filePath);
    //     });
    // }
    function openPDF(filename) {
        console.log('正在尝试打开文件:', filename);
        // const vmIP = '10.15.240.251';
        // const vmIP = '192.168.1.101';
        const vmIP = '192.168.43.248';
        // const vmIP = '127.0.0.1';
        const url = `http://${vmIP}:5000/pdfs/${filename}`;
        // const url = `E:/files/vitualbox_share/oriPDFs/${filename}`;
        
        // 尝试打开文件
        const newWindow = window.open(url, '_blank');
        
        // 检查是否成功打开窗口
        setTimeout(() => {
            if (!newWindow || newWindow.closed || typeof newWindow.closed == 'undefined') {
                console.error('无法打开文件:', url);
                alert(`无法打开文件。可能是由于网络问题或服务器未响应。\n\n文件名: ${filename}\n\n请确保您已连接到正确的网络，并且服务器正在运行。如果问题持续，请联系系统管理员。`);
            }
        }, 1000);
    }
});