# gitDiffTool

**gitDiffTool** is a tool to compare two commits of a gitProject and generate the diff into html(generate in output/ dir of current dir). 
You can read the diff in one html page, the list of modified files on one side and the specifics diff-content on the other.

## usage

```
Usage: jDiffTool.py [OPTIONS] [params]

  -d [sCommit] dCommit  : diff two commit(if given one diff with current commit), output the result using html
  -h|--help             : print this usage
  -v|--version          : print the version
```

example
``
jDiffTool.py -d 79809324 341324   # compare tow commit
jDiffTool.py -d 787234            # compare current branch with given commit
jDiffTool.py -d develop           # compare current branch with given branch's name
``

# 中文简介 chinese

**gitDiffTool** 是一个Git代码对比工具，可以对Git项目的两个提交进行对比，对比结果将生成一份html报告(结果生成在当前output/目录下)。
你可以在生成的结果页中查看两次提交间代码的diff，结果页仅为单个html页面，左边栏是两次提交有改动的文件列表，右边栏是改动的具体内容。

## usage

```
Usage: jDiffTool.py [OPTIONS] [params]

  -d [sCommit] dCommit  : diff two commit(if given one diff with current commit), output the result using html
  -h|--help             : print this usage
  -v|--version          : print the version
```

比如
``
jDiffTool.py -d 79809324 341324   # 对比两个commit
jDiffTool.py -d 787234            # 使用某一commit与当前分支对比
jDiffTool.py -d develop           # 使用某一分支与当前分支对比
``
