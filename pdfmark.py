import PyPDF2
import os
import traceback
import time

'''
针对扫描版pdf添加目录
需要有目录文件，使用\t制表符组织目录
目录和扫描版页码有偏差手动设置起始页码
'''
def setsub(indexs, level):
    #递归方式遍历目录 生成目录树
    sub = []
    for i, index in enumerate(indexs):
        clevel = len(index.split('\t'))
        if clevel == level + 1:
            value, page = index.split('@')
            sub.append([value, page, setsub(indexs[i+1:], level+1)])
        elif clevel > level + 1:
            continue
        else:
            break
    return sub

def settree(indexs):
    res = []
    for i, index in enumerate(indexs):
        level = len(index.split('\t'))
        value, page = index.split('@')
        subtree = setsub(indexs[i+1:], level)
        if level == 1:
            res.append([value, page, subtree])
    return res


def addtag(pdf, filei=None, offset=0):
    # print('*起始页为书籍目录第一页在pdf中对应的页码')
    
    if os.path.splitext(pdf)[1] == '.pdf':
        #对当前pdf检测 是否已有目录 是否有匹配目录文件
        filep = pdf
        title = os.path.splitext(pdf)[0]
        print('当前pdf为 '+title)
        pdfobj = open(filep, 'rb')
        reader = PyPDF2.PdfFileReader(pdfobj)
        outline = reader.outlines
        if outline != []:
            return '当前书籍已有目录！'
            # print(outline)
                
        #识别并读取目录文件
        if not filei:
            filei = title + '.ml'
        if not os.path.exists(filei):
            return '未找到匹配的目录文件'
            
        fi = open(filei, 'r', encoding='utf-8')
        indexs = fi.readlines()

        #建立目录树
        tree = settree(indexs)

        #设置偏置页数
        # offset = input('请输入起始页：')
        writer = PyPDF2.PdfFileWriter()
        for i in range(0, reader.numPages):
            writer.addPage(reader.getPage(i))

        def addmarks(tree, parent):
            for value, page, sub in tree:
                cur = writer.addBookmark(value, int(page)+int(offset)-1, parent)
                if sub != []:
                    addmarks(sub, cur)

        #添加目录 设置信号量 失败不储存
        save = 0
        try:
            addmarks(tree, None)
            save = 1
        except:
            print(traceback.print_exc())
            save = 0
            return (title + ' 失败')
            

        if save == 1:
            if '.pdf' in title:
                title = title.split('.pdf')[0]
            if 'result\\' in title:
                title = title.replace('result\\','')
            try:
                if os.path.exists('result\\' + title + '_ml.pdf'):
                    os.remove('result\\' + title + '_ml.pdf')
                with open('result\\' + title + '_ml.pdf', 'wb') as fout:
                    writer.write(fout)
                print(title + ' 完成')
            except:
                print('请检查文件是否未关闭并重试')
            time.sleep(1)
        pdfobj.close()

if __name__ == '__main__':
    addtag()
